#!/usr/bin/env bash
# Scenario A / I2 acceptance run (IL-T002): bring-up, smoke, the four
# acceptance workload phases, evidence capture, teardown. Requires build.sh
# to have run first (images + .build/inferbench + contracts bundle present).
#
# Usage: scenarios/a/run.sh <out-dir>
#
# Fails loudly (set -e): a failed phase stops the run and leaves the partial
# evidence in <out-dir> — failed runs are evidence too, never deleted.
set -euo pipefail

OUT=${1:?out dir required}
HERE=$(cd "$(dirname "$0")" && pwd)
BUILD="$HERE/.build"
GW=http://127.0.0.1:18080
MOCK=http://127.0.0.1:18081

mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
mkdir -p "$OUT/logs" "$OUT/raw" "$OUT/runs"
RUNLOG="$OUT/logs/run.log"
log() { echo "[$(date -u +%FT%T.%3NZ)] $*" | tee -a "$RUNLOG"; }

compose() { docker compose -f "$HERE/compose.yaml" "$@"; }
scrape() { curl -fsS "$GW/metrics" >"$OUT/raw/metrics-$1.prom"; log "metrics scraped: $1"; }

wait_healthy() {
  for _ in $(seq 1 100); do
    if curl -fsS "$GW/healthz" >/dev/null 2>&1 && curl -fsS "$MOCK/healthz" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.2
  done
  log "stack did not become healthy"; return 1
}

bench() { # bench <name> <workload-file> [extra inferbench args...]
  local name=$1 workload=$2; shift 2
  log "inferbench run: $name (workload $workload)"
  "$BUILD/inferbench" run \
    --workload "$workload" \
    --manifest "$HERE/facts/$name.facts.json" \
    --target "$GW" \
    --out "$OUT/runs/$name" \
    --stream \
    --run-id "i2-$name" \
    --request-timeout 120s \
    "$@" 2>&1 | tee -a "$RUNLOG"
}

restart_mock() {
  # Fresh mock process => /debug/state counters start clean for the next
  # cancellation point. One throwaway non-stream request afterwards flushes
  # any stale gateway->mock keep-alive connection (recorded, not hidden).
  log "restarting mock-backend (reset /debug/state)"
  compose restart mock-backend >>"$RUNLOG" 2>&1
  wait_healthy
  curl -fsS -X POST "$GW/v1/chat/completions" \
    -H 'Content-Type: application/json' \
    -d '{"model":"mock-8b","messages":[{"role":"user","content":"connection flush"}],"max_tokens":1}' \
    >/dev/null
  log "keep-alive flush request done"
}

# --- bring-up -----------------------------------------------------------------
log "bring-up: docker compose up -d"
rm -rf "$HERE/out/otel" && mkdir -p "$HERE/out/otel"
compose up -d 2>&1 | tee -a "$RUNLOG"
wait_healthy
log "stack healthy (gateway $GW, mock $MOCK)"
compose ps 2>&1 | tee -a "$RUNLOG"

# --- smoke (before the pre-run metrics scrape, so it never contaminates the
# --- TTFT-agreement scrape window) ---------------------------------------------
{
  echo "== GET /healthz";  curl -fsS "$GW/healthz"; echo
  echo "== GET /readyz";   curl -fsS "$GW/readyz"; echo
  echo "== GET /v1/models"; curl -fsS "$GW/v1/models"; echo
  echo "== POST /v1/chat/completions (non-stream)"
  curl -fsS -X POST "$GW/v1/chat/completions" -H 'Content-Type: application/json' \
    -d '{"model":"mock-8b","messages":[{"role":"user","content":"smoke"}],"max_tokens":16,"seed":7}'
  echo
} >"$OUT/logs/smoke.log" 2>&1
curl -fsSN -X POST "$GW/v1/chat/completions" -H 'Content-Type: application/json' \
  -d '{"model":"mock-8b","messages":[{"role":"user","content":"smoke stream"}],"max_tokens":16,"seed":7,"stream":true,"stream_options":{"include_usage":true}}' \
  >"$OUT/raw/smoke-stream.chat-completion-stream.sse"
log "smoke complete (logs/smoke.log, raw/smoke-stream.chat-completion-stream.sse)"

# --- (a) seeded canonical workload + (d) TTFT-agreement window ------------------
scrape 00-pre-chat-short
bench chat-short "$BUILD/workloads/chat-short.json"
scrape 01-post-chat-short

# --- (b) 100 concurrent streams -------------------------------------------------
bench concurrency-100 "$HERE/workloads/concurrency-100.json"
scrape 02-post-concurrency

# --- (c) 3-point cancellation ----------------------------------------------------
for point in cancel-pre-first-token cancel-mid-stream cancel-near-completion; do
  restart_mock
  bench "$point" "$HERE/workloads/$point.json"
  curl -fsS "$MOCK/debug/state" >"$OUT/runs/$point/debug-state.json"
  log "mock /debug/state captured for $point"
done

# --- final capture + teardown -----------------------------------------------------
scrape 03-final
log "waiting 8s for span batch export + collector file flush"
sleep 8
for svc in gateway mock-backend otel-collector; do
  compose logs --no-color "$svc" >"$OUT/logs/$svc.log" 2>&1
done
log "teardown: docker compose down"
compose down 2>&1 | tee -a "$RUNLOG"
cp "$HERE/out/otel/traces.jsonl" "$OUT/raw/traces.jsonl"
cp "$BUILD/build-info.txt" "$OUT/logs/build-info.txt"

# --- contract validation (pinned kit, serving-contracts@8d81492) -------------------
KIT="$BUILD/contracts-bundle/kit/contracts-validate.py"
{
  for run in chat-short concurrency-100 cancel-pre-first-token cancel-mid-stream cancel-near-completion; do
    echo "== raw-event: runs/$run/events.jsonl"
    python3 "$KIT" --bundle "$BUILD/contracts-bundle" validate --schema raw-event "$OUT/runs/$run/events.jsonl"
    echo "== benchmark-run: runs/$run/manifest.json"
    python3 "$KIT" --bundle "$BUILD/contracts-bundle" validate --schema benchmark-run "$OUT/runs/$run/manifest.json"
  done
  echo "== workload: scenario-local workload files"
  python3 "$KIT" --bundle "$BUILD/contracts-bundle" validate --schema workload \
    "$HERE/workloads/"*.json "$BUILD/workloads/chat-short.json"
  echo "== api.stream-event: smoke SSE transcript"
  python3 "$KIT" --bundle "$BUILD/contracts-bundle" validate --schema api.stream-event \
    "$OUT/raw/smoke-stream.chat-completion-stream.sse"
} 2>&1 | tee "$OUT/logs/kit-validate.log"

# --- acceptance checks --------------------------------------------------------------
CHK="$HERE/checks.py"
{
  echo "== integrity: chat-short"
  python3 "$CHK" integrity "$OUT/runs/chat-short/events.jsonl"
  echo "== integrity + concurrency: concurrency-100"
  python3 "$CHK" integrity "$OUT/runs/concurrency-100/events.jsonl" --min-concurrent 100
  echo "== cancel point 1: pre-first-token"
  python3 "$CHK" cancel "$OUT/runs/cancel-pre-first-token/events.jsonl" \
    "$OUT/runs/cancel-pre-first-token/debug-state.json" \
    --expect-phase pre_first_token --min-chunks 0 --expect-tokens 0
  echo "== cancel point 2: mid-stream"
  python3 "$CHK" cancel "$OUT/runs/cancel-mid-stream/events.jsonl" \
    "$OUT/runs/cancel-mid-stream/debug-state.json" \
    --expect-phase mid_stream --min-chunks 9 --expect-tokens 8
  echo "== cancel point 3: near-completion"
  python3 "$CHK" cancel "$OUT/runs/cancel-near-completion/events.jsonl" \
    "$OUT/runs/cancel-near-completion/debug-state.json" \
    --expect-phase mid_stream --min-chunks 241 --expect-tokens 240
  echo "== ttft agreement (chat-short scrape delta)"
  python3 "$CHK" ttft "$OUT/runs/chat-short/events.jsonl" \
    "$OUT/raw/metrics-00-pre-chat-short.prom" "$OUT/raw/metrics-01-post-chat-short.prom"
  echo "== traces"
  python3 "$CHK" traces "$OUT/raw/traces.jsonl" --excerpt-out "$OUT/raw/trace-excerpt.json"
} 2>&1 | tee "$OUT/logs/checks.log"

log "scenario A run complete; evidence in $OUT"
