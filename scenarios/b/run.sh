#!/usr/bin/env bash
# Scenario B / I3 acceptance run (IL-T003): calibration + SLO derivation,
# the paired chat-short arms (engine-direct, via-gateway), shared-prefix,
# live cancellation vs llama.cpp, mock<->llama.cpp failover, contract
# validation, analysis + benchmark report #0, and acceptance checks.
# Requires build.sh to have run first.
#
# HOST PROCESSES, not containers (decision A-007, docs/implementation-notes.md):
# llama-server (prebuilt, pinned commit), gateway, mock-backend, and
# inferbench all run on this host. Ports: gateway 18080, llama-server 18082,
# mock 18083.
#
# Usage: scenarios/b/run.sh <out-dir>       (e.g. evidence/i3)
#
# PHASES env (default "all"): space-separated subset of
#   calib direct gw sharedprefix cancel failover validate analysis checks
# — used to RESUME an interrupted attempt without re-running completed,
# self-contained phases (each measured phase gets its own fresh llama-server
# and its own gateway instance, so phases are independent). Resumes are
# visible in logs/run.log.
#
# Fails loudly (set -e) on run/bring-up/validation errors; acceptance CHECKS
# are collected (a failing check never destroys the evidence of the others)
# and reported at the end — failed runs are evidence too, never deleted.
set -euo pipefail

do_phase() { # do_phase <name>: 0 when the phase is selected
  case " ${PHASES:-all} " in
    *" all "*|*" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

OUT=${1:?out dir required}
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
BUILD="$HERE/.build"
GW=http://127.0.0.1:18080
LLAMA=http://127.0.0.1:18082
MOCK=http://127.0.0.1:18083
MODEL_ID=qwen2.5-1.5b-instruct-q4_k_m
MODEL_FILE=/home/user/tools/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
LLAMA_BIN_DIR=/home/user/tools/llama.cpp/build/bin

mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
RELOUT=${OUT#"$ROOT"/}
mkdir -p "$OUT/logs" "$OUT/raw/runs" "$OUT/raw/slo" "$OUT/raw/results" "$OUT/reports"
RUNLOG="$OUT/logs/run.log"
CONTLOG="$OUT/logs/contention.log"
log() { echo "[$(date -u +%FT%T.%3NZ)] $*" | tee -a "$RUNLOG"; }
mark() { echo "MARK $(date +%s.%N) $1 $2" >>"$CONTLOG"; }

export PYTHONPATH="$BUILD/src/inferbench/analysis/src"
KIT="$BUILD/contracts-bundle/kit/contracts-validate.py"
CHK="$HERE/checks.py"

# --- process management --------------------------------------------------------
LLAMA_PID="" GW_PID="" MOCK_PID="" CONT_PID="" POLL_PID=""

port_must_be_free() { # port_must_be_free <url> <what>
  if curl -fsS --max-time 2 "$1" >/dev/null 2>&1; then
    log "FATAL: $2 already answering at $1 — a stale process owns the port; refusing to start"
    return 1
  fi
}

start_llama() { # start_llama <phase-tag>
  local tag=$1
  port_must_be_free "$LLAMA/health" "an engine"
  # exec inside the subshell so $! IS the llama-server pid (a fresh engine
  # per phase and the failover SIGKILL both depend on killing the real pid).
  (cd "$LLAMA_BIN_DIR" && exec env LD_LIBRARY_PATH=. ./llama-server \
    -m "$MODEL_FILE" --host 127.0.0.1 --port 18082 -np 2 -c 8192 -t 4 \
    -a "$MODEL_ID" --metrics --slots --no-webui --log-timestamps) \
    >"$OUT/logs/llama-server-$tag.log" 2>&1 &
  LLAMA_PID=$!
  for _ in $(seq 1 240); do
    if curl -fsS "$LLAMA/health" >/dev/null 2>&1; then
      kill -0 "$LLAMA_PID" 2>/dev/null || { log "FATAL: port healthy but our llama-server ($tag, pid $LLAMA_PID) is dead"; return 1; }
      grep -q "listening on" "$OUT/logs/llama-server-$tag.log" || { log "FATAL: llama-server $tag never logged 'listening on'"; return 1; }
      log "llama-server up ($tag, pid $LLAMA_PID)"; return 0
    fi
    sleep 0.5
  done
  log "llama-server did not become healthy ($tag)"; return 1
}
stop_llama() {
  [ -n "$LLAMA_PID" ] && kill "$LLAMA_PID" 2>/dev/null && wait "$LLAMA_PID" 2>/dev/null || true
  LLAMA_PID=""
  for _ in $(seq 1 20); do
    curl -fsS --max-time 2 "$LLAMA/health" >/dev/null 2>&1 || return 0
    sleep 0.5
  done
  log "FATAL: llama-server port still answering after stop"; return 1
}

start_gateway() { # start_gateway <config-file> <log-tag>
  port_must_be_free "$GW/healthz" "a gateway"
  "$BUILD/gateway" -addr 127.0.0.1:18080 -config "$1" \
    >"$OUT/logs/gateway-$2.log" 2>&1 & GW_PID=$!
  for _ in $(seq 1 100); do
    if curl -fsS "$GW/healthz" >/dev/null 2>&1; then
      kill -0 "$GW_PID" 2>/dev/null || { log "FATAL: port healthy but our gateway ($2, pid $GW_PID) is dead"; return 1; }
      log "gateway up ($2, pid $GW_PID, config $1)"; return 0
    fi
    sleep 0.2
  done
  log "gateway did not become healthy"; return 1
}
stop_gateway() { [ -n "$GW_PID" ] && kill "$GW_PID" 2>/dev/null && wait "$GW_PID" 2>/dev/null || true; GW_PID=""; }

cleanup() {
  stop_gateway; stop_llama
  [ -n "$MOCK_PID" ] && kill "$MOCK_PID" 2>/dev/null || true
  [ -n "$CONT_PID" ] && kill "$CONT_PID" 2>/dev/null || true
  [ -n "$POLL_PID" ] && kill "$POLL_PID" 2>/dev/null || true
}
trap cleanup EXIT

bench() { # bench <name> <workload-file> <facts-file> <target>
  local name=$1 workload=$2 facts=$3 target=$4
  log "inferbench run: $name (workload $workload -> $target)"
  mark start "$name"
  "$BUILD/inferbench" run \
    --workload "$workload" \
    --manifest "$HERE/facts/$facts" \
    --target "$target" \
    --out "$OUT/raw/runs/$name" \
    --stream \
    --model "$MODEL_ID" \
    --run-id "i3-$name" \
    --request-timeout 240s \
    2>&1 | tee -a "$RUNLOG"
  mark end "$name"
  cp "$workload" "$OUT/raw/runs/$name/workload.json"
}

scrape() { # scrape <tag> <url>
  curl -fsS "$2/metrics" >"$OUT/raw/metrics-$1.prom"; log "metrics scraped: $1"
}

# --- phase 0: host facts + contention sampler ----------------------------------
{
  echo "scenario-b run $(date -u +%FT%TZ)"
  echo "uname: $(uname -srmo)"
  echo "cpus: $(nproc) x $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ //')"
  echo "mem:  $(grep MemTotal /proc/meminfo)"
  echo "python: $(python3 --version)"
} >"$OUT/logs/host-facts.txt"
python3 "$CHK" sample-contention --out "$CONTLOG" --interval-s 5 \
  --names llama-server,gateway,mock-backend,inferbench & CONT_PID=$!
log "contention sampler started (pid $CONT_PID); phases selected: ${PHASES:-all}"
SLO="$OUT/raw/slo/scenario-b-llamacpp-cpu-shakedown.slo.json"

# --- phase 1: calibration probes + SLO derivation (via gateway) -----------------
if do_phase calib; then
start_llama calib
start_gateway "$HERE/config/gateway-llamacpp.json" main
{
  echo "== GET /healthz";  curl -fsS "$GW/healthz"; echo
  echo "== GET /readyz";   curl -fsS "$GW/readyz"; echo
  echo "== GET /v1/models"; curl -fsS "$GW/v1/models"; echo
  echo "== POST /v1/chat/completions (non-stream)"
  curl -fsS -X POST "$GW/v1/chat/completions" -H 'Content-Type: application/json' \
    -d "{\"model\":\"$MODEL_ID\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with one short sentence: what is a benchmark?\"}],\"max_tokens\":48}"
  echo
} >"$OUT/logs/smoke.log" 2>&1
curl -fsSN -X POST "$GW/v1/chat/completions" -H 'Content-Type: application/json' \
  -d "{\"model\":\"$MODEL_ID\",\"messages\":[{\"role\":\"user\",\"content\":\"Count from one to five in words.\"}],\"max_tokens\":48,\"stream\":true,\"stream_options\":{\"include_usage\":true}}" \
  >"$OUT/raw/smoke-stream.chat-completion-stream.sse"
log "smoke complete (logs/smoke.log, raw/smoke-stream.chat-completion-stream.sse)"

bench chat-short-cpu-calib   "$HERE/workloads/chat-short-cpu-calib.json"   chat-short-cpu-calib.facts.json   "$GW"
bench shared-prefix-cpu-calib "$HERE/workloads/shared-prefix-cpu-calib.json" shared-prefix-cpu-calib.facts.json "$GW"

python3 "$CHK" derive-slo \
  --calib "$OUT/raw/runs/chat-short-cpu-calib" \
  --calib "$OUT/raw/runs/shared-prefix-cpu-calib" \
  --out "$SLO" 2>&1 | tee "$OUT/logs/derive-slo.log"
stop_gateway; stop_llama
fi

# --- phase 2: chat-short-cpu, ENGINE-DIRECT arm (fresh llama-server) ------------
if do_phase direct; then
start_llama direct
bench chat-short-cpu-direct "$HERE/workloads/chat-short-cpu.json" chat-short-cpu-direct.facts.json "$LLAMA"
scrape post-direct-llama "$LLAMA"
stop_llama
fi

# --- phase 3: chat-short-cpu, VIA-GATEWAY arm (fresh llama-server) --------------
if do_phase gw; then
start_llama gw
start_gateway "$HERE/config/gateway-llamacpp.json" main2
scrape pre-gw-gateway "$GW"
bench chat-short-cpu-gw "$HERE/workloads/chat-short-cpu.json" chat-short-cpu-gw.facts.json "$GW"
scrape post-gw-gateway "$GW"
scrape post-gw-llama "$LLAMA"
stop_llama; stop_gateway
fi

# --- phase 4: shared-prefix-cpu via gateway (fresh llama-server + gateway) ------
if do_phase sharedprefix; then
start_llama sharedprefix
start_gateway "$HERE/config/gateway-llamacpp.json" sharedprefix
bench shared-prefix-cpu "$HERE/workloads/shared-prefix-cpu.json" shared-prefix-cpu.facts.json "$GW"
scrape post-sharedprefix-gateway "$GW"
scrape post-sharedprefix-llama "$LLAMA"
stop_llama; stop_gateway
fi

# --- phase 5: live cancellation vs llama.cpp (fresh llama-server, clean log) ----
if do_phase cancel; then
start_llama cancel
start_gateway "$HERE/config/gateway-llamacpp.json" cancel
python3 "$CHK" poll-slots --url "$LLAMA/slots" --out "$OUT/raw/slots-poll-cancel.jsonl" \
  --interval-ms 25 & POLL_PID=$!
log "slots poller started (pid $POLL_PID, 25 ms)"
bench cancel-mid-stream-cpu "$HERE/workloads/cancel-mid-stream-cpu.json" cancel-mid-stream-cpu.facts.json "$GW"
sleep 2  # let the poller observe the final release
kill "$POLL_PID" && wait "$POLL_PID" 2>/dev/null || true; POLL_PID=""
log "llama-server 'cancel task' log lines: $(grep -c 'cancel task' "$OUT/logs/llama-server-cancel.log" || true)"
stop_llama
stop_gateway
fi

# --- phase 6: mock<->llama.cpp failover through the gateway ---------------------
if do_phase failover; then
start_llama failover-1
port_must_be_free "$MOCK/healthz" "a mock backend"
"$BUILD/mock-backend" -addr 127.0.0.1:18083 -seed 42 -ttft 300ms -itl 30ms -error-rate 0 \
  >"$OUT/logs/mock-backend.log" 2>&1 & MOCK_PID=$!
for _ in $(seq 1 50); do curl -fsS "$MOCK/healthz" >/dev/null 2>&1 && break; sleep 0.2; done
log "mock-backend up (pid $MOCK_PID)"
start_gateway "$HERE/config/gateway-failover.json" failover

bench chat-short-failover "$HERE/workloads/chat-short-failover.json" chat-short-failover.facts.json "$GW" &
BENCH_PID=$!
BSTART=$(date +%s)
# T+100s minimum, then kill as soon as a slot is processing (mid-stream kill).
while [ $(( $(date +%s) - BSTART )) -lt 100 ]; do sleep 1; done
for _ in $(seq 1 120); do
  if curl -fsS "$LLAMA/slots" 2>/dev/null | python3 -c 'import json,sys; sys.exit(0 if any(s.get("is_processing") for s in json.load(sys.stdin)) else 1)'; then
    break
  fi
  sleep 0.5
done
KILL_TS=$(date -u +%FT%T.%3NZ)
kill -9 "$LLAMA_PID"; LLAMA_PID=""
log "llama-server SIGKILLed at $KILL_TS (slot was processing)"
# T+240s: restart the engine; recovery is per-request primary-first selection.
while [ $(( $(date +%s) - BSTART )) -lt 240 ]; do sleep 1; done
start_llama failover-2
LISTEN_TS=$(date -u +%FT%T.%3NZ)
log "llama-server healthy again at $LISTEN_TS"
printf '{"kill_ts": "%s", "listening_ts": "%s"}\n' "$KILL_TS" "$LISTEN_TS" \
  >"$OUT/raw/failover-timeline.json"
wait "$BENCH_PID"
curl -fsS "$MOCK/debug/state" >"$OUT/raw/mock-debug-state-failover.json"
log "llama-server (restarted) chat-completion log lines: $(grep -c 'POST /v1/chat/completions' "$OUT/logs/llama-server-failover-2.log" || true)"
stop_llama; stop_gateway
kill "$MOCK_PID" 2>/dev/null || true; MOCK_PID=""
fi

kill "$CONT_PID" 2>/dev/null || true; CONT_PID=""
cp "$BUILD/build-info.txt" "$OUT/logs/build-info.txt"
cp "$BUILD/llamacpp.backend-capability.json" "$OUT/raw/llamacpp.backend-capability.json"

# --- phase 7: contract validation (pinned kit, serving-contracts v0.2.0) --------
if do_phase validate; then
RUNS="chat-short-cpu-calib shared-prefix-cpu-calib chat-short-cpu-direct chat-short-cpu-gw shared-prefix-cpu cancel-mid-stream-cpu chat-short-failover"
{
  for run in $RUNS; do
    echo "== raw-event: raw/runs/$run/events.jsonl"
    python3 "$KIT" --bundle "$BUILD/contracts-bundle" validate --schema raw-event "$OUT/raw/runs/$run/events.jsonl"
    echo "== benchmark-run: raw/runs/$run/manifest.json"
    python3 "$KIT" --bundle "$BUILD/contracts-bundle" validate --schema benchmark-run "$OUT/raw/runs/$run/manifest.json"
  done
  echo "== workload: scenario-b workload files"
  python3 "$KIT" --bundle "$BUILD/contracts-bundle" validate --schema workload "$HERE/workloads/"*.json
  echo "== slo: derived scenario SLO"
  python3 "$KIT" --bundle "$BUILD/contracts-bundle" validate --schema slo "$SLO"
  echo "== backend-capability: pinned llama.cpp descriptor (infergate@74f2372)"
  python3 "$KIT" --bundle "$BUILD/contracts-bundle" validate --schema backend-capability "$OUT/raw/llamacpp.backend-capability.json"
  echo "== api.stream-event: smoke SSE transcript (gateway -> llama.cpp path)"
  python3 "$KIT" --bundle "$BUILD/contracts-bundle" validate --schema api.stream-event "$OUT/raw/smoke-stream.chat-completion-stream.sse"
} 2>&1 | tee "$OUT/logs/kit-validate.log"
fi

# --- phase 8: contention summaries -> analysis threats -> reports ----------------
cd "$ROOT"
contention_brief() { # contention_brief <phase>
  python3 "$CHK" contention "$CONTLOG" --phase "$1" | python3 -c '
import json, sys
d = json.load(sys.stdin)
c = d["interval_cpu_percent"]
print(", ".join(k + " mean " + str(v["mean"]) + "% / max " + str(v["max"])
                + "% of one core" for k, v in c.items() if v["max"] > 0.5))'
}

T_COLOC_TMPL="single-host client+server co-location: llama-server (-t 4), infergate, and inferbench share one 4-core host; measured interval-CPU during this run: %s. Client-side timing competes with the engine for CPU."
T_SAMPLE="single repetition, small sample (CPU-adapted rate): bootstrap CIs are wide and cross-run dispersion does not exist; numbers are a methodology shakedown, not a performance claim"
T_RATE="arrival rate CPU-adapted from same-day single-stream calibration (evidence/i3/logs/rate-calibration.log); results characterize this host + engine build + quantized model only"
T_SLO="SLO thresholds derived from same-host calibration probe maxima (x1.5 headroom, seeds distinct from the measured runs): goodput@SLO exercises the machinery, it is not an external target"
T_ARM="paired arm ran minutes apart against its own fresh llama-server process (OS page cache warm in both arms after calibration); arm-to-arm drift is not controlled beyond that"

BUNDLE_REL="${HERE#"$ROOT"/}/.build/contracts-bundle"

analyze_and_report() { # analyze_and_report <run-name> <result-id> <extra-threat...>
  local run=$1 rid=$2; shift 2
  local cont; cont=$(contention_brief "$run")
  local -a targs=()
  local t
  for t in "$(printf "$T_COLOC_TMPL" "$cont")" "$T_SAMPLE" "$T_RATE" "$T_SLO" "$@"; do
    targs+=(--threat "$t")
  done
  python3 -m inferbench_analysis analyze \
    --bundle "$BUNDLE_REL" \
    --run "$RELOUT/raw/runs/$run" \
    --slo "$RELOUT/raw/slo/scenario-b-llamacpp-cpu-shakedown.slo.json" \
    --result-id "$rid" \
    "${targs[@]}" \
    --out "$RELOUT/raw/results/$rid.benchmark-result.json" 2>&1 | tee "$OUT/logs/analyze-$run.log"
  python3 -m inferbench_analysis report \
    --bundle "$BUNDLE_REL" \
    --run "$RELOUT/raw/runs/$run" \
    --slo "$RELOUT/raw/slo/scenario-b-llamacpp-cpu-shakedown.slo.json" \
    --result-id "$rid" \
    "${targs[@]}" \
    --out "$RELOUT/reports" 2>&1 | tee "$OUT/logs/report-$run.log"
}

if do_phase analysis; then
analyze_and_report chat-short-cpu-direct i3-chat-short-cpu-direct "$T_ARM"
analyze_and_report chat-short-cpu-gw     i3-chat-short-cpu-gw     "$T_ARM"
analyze_and_report shared-prefix-cpu     i3-shared-prefix-cpu \
  "prefix-cache reuse depends on llama-server slot LCP selection with only 2 slots; group-interleaved arrivals can evict a cached prefix — cache effectiveness here is a property of this configuration, not of the workload"

{
  echo "== benchmark-result: analysis outputs"
  python3 "$KIT" --bundle "$BUNDLE_REL" validate --schema benchmark-result \
    "$OUT/raw/results/"*.benchmark-result.json
} 2>&1 | tee -a "$OUT/logs/kit-validate.log"
fi

# --- phase 9: acceptance checks (collected; all always run) ----------------------
if ! do_phase checks; then log "checks phase not selected; stopping here"; exit 0; fi
FAILED=()
run_check() { # run_check <label> <cmd...>
  local label=$1; shift
  echo "== $label" | tee -a "$OUT/logs/checks.log"
  if ! "$@" 2>&1 | tee -a "$OUT/logs/checks.log"; then
    FAILED+=("$label")
  fi
}
: >"$OUT/logs/checks.log"
for run in chat-short-cpu-calib shared-prefix-cpu-calib chat-short-cpu-direct chat-short-cpu-gw shared-prefix-cpu; do
  run_check "integrity: $run" python3 "$CHK" integrity "$OUT/raw/runs/$run/events.jsonl"
done
for phase in chat-short-cpu-direct chat-short-cpu-gw shared-prefix-cpu cancel-mid-stream-cpu chat-short-failover; do
  run_check "contention: $phase" python3 "$CHK" contention "$CONTLOG" --phase "$phase"
done
run_check "cancel-llama" python3 "$CHK" cancel-llama \
  "$OUT/raw/runs/cancel-mid-stream-cpu/events.jsonl" \
  "$OUT/raw/slots-poll-cancel.jsonl" \
  --llama-log "$OUT/logs/llama-server-cancel.log"
run_check "failover" python3 "$CHK" failover \
  "$OUT/raw/runs/chat-short-failover/events.jsonl" \
  "$OUT/raw/failover-timeline.json" \
  "$OUT/raw/mock-debug-state-failover.json"
run_check "ttft-compare (gateway-overhead hypothesis)" python3 "$CHK" ttft-compare \
  "$OUT/raw/results/i3-chat-short-cpu-direct.benchmark-result.json" \
  "$OUT/raw/results/i3-chat-short-cpu-gw.benchmark-result.json" \
  --events-direct "$OUT/raw/runs/chat-short-cpu-direct/events.jsonl" \
  --events-gw "$OUT/raw/runs/chat-short-cpu-gw/events.jsonl"

if [ ${#FAILED[@]} -gt 0 ]; then
  log "scenario B run complete WITH FAILED CHECKS: ${FAILED[*]} (evidence in $OUT)"
  exit 1
fi
log "scenario B run complete; all checks PASS; evidence in $OUT"
