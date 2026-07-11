#!/usr/bin/env python3
"""Scenario B / I3 acceptance checks + run-support tooling (IL-T003).

Read-only analysis of artifacts produced by run.sh (plus two small run-time
helpers: the /slots poller and the CPU-contention sampler). Every check
command prints one JSON document (the evidence number + its inputs) and
exits 0 on PASS, 1 on FAIL. This is evidence tooling only — never a
benchmark statistics engine (that is inferbench IB-T005/T006 scope; all
published percentiles come from the inferbench analysis pipeline).

Check commands:
  integrity <events.jsonl>
      Stream-integrity: every event ok; server-reported usage completion
      tokens == client-received content chunks (len(itl)+1, or 1 when a
      single chunk yields no ITL series). Scenario A's exact rule, plus one
      ENGINE-specific allowance measured against llama-server 8f114a9
      (preflight probe 2026-07-11): a completion the model ends by EOS
      counts the stop token in usage.completion_tokens but emits no content
      delta for it, so chunks == usage-1 is correct framing for EOS-stopped
      streams (chunks == usage for cap-stopped ones). Both populations are
      counted; any other deficit is a violation.
  derive-slo --calib DIR [--calib DIR ...] --out FILE [--headroom 1.5]
      Derive the scenario SLO from the calibration probes' measured
      per-request maxima (TTFT / e2e-from-scheduled-send / max stall),
      threshold = max * headroom rounded UP to 2 significant digits.
      Measured provenance only (slo.schema.json normative rule).
  cancel-llama <events.jsonl> <slots-poll.jsonl> --llama-log FILE
               [--bound-ms 2500]
      Cancellation vs the real engine: every client-canceled request has a
      'cancel task' line in the llama-server log (count equality); every
      cancel pairs (greedy nearest-neighbor) with an observed slot release
      (/slots is_processing true->false transition) within the declared
      bound; no slot left processing at the end. The bound is the ENGINE's
      decode-batch-boundary release granularity + 25 ms poll quantization,
      NOT gateway propagation latency (see IG-T005 @74f2372 for the direct
      1.25-5.24 ms mid-stream measurement).
  failover <events.jsonl> <timeline.json> <mock-debug-state.json>
      Failover semantics per segment: streams accepted before the SIGKILL
      and still in flight end as typed upstream_error (count == in-flight
      at kill, no more, no less); requests dispatched while llama-server is
      down are served by the mock (attributed by ITL/TTFT signature AND
      conservation against mock /debug/state) with zero errors; traffic
      returns to llama-server after restart.
  ttft-compare <direct.benchmark-result.json> <gw.benchmark-result.json>
               [--bound-ms 100] [--events-direct F --events-gw F]
      Gateway-overhead hypothesis check: pipeline pooled TTFT p50 (gw) -
      p50 (direct) < bound. Optional paired per-request delta (same seed =>
      same workload_item prompts) reported as a labeled DIAGNOSTIC only —
      it is not a pipeline statistic and is never quoted as a result.
  contention <contention.log> --phase NAME
      Per-phase interval-CPU summary (mean/max %CPU per process, load avg)
      from the sample-contention log. Informational: always PASS; the
      numbers feed the run's threats-to-validity statements.

Run-time helpers (run until SIGTERM, no PASS/FAIL semantics):
  poll-slots --url URL --out FILE [--interval-ms 25]
  sample-contention --out FILE [--interval-s 5] [--names a,b,...]
"""

import argparse
import json
import math
import os
import re
import signal
import sys
import time
import urllib.request
from datetime import datetime, timezone


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def load_events(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def emit(doc, ok):
    doc["result"] = "PASS" if ok else "FAIL"
    json.dump(doc, sys.stdout, indent=2)
    print()
    return 0 if ok else 1


def client_chunks(ev):
    itl = ev.get("itl")
    if itl and itl.get("series_seconds") is not None:
        return len(itl["series_seconds"]) + 1
    return 1 if ev["output_tokens"] >= 1 else 0


def max_stall(ev):
    itl = ev.get("itl")
    if not itl:
        return None
    if itl.get("series_seconds"):
        return max(itl["series_seconds"])
    return itl.get("max_stall_seconds")


def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


# --------------------------------------------------------------------------
# integrity (same rule as Scenario A checks.py)
# --------------------------------------------------------------------------

def cmd_integrity(args):
    evs = load_events(args.events)
    by_status = {}
    for ev in evs:
        by_status[ev["status"]] = by_status.get(ev["status"], 0) + 1
    violations = []
    exact = eos_deficit = 0
    for ev in evs:
        if ev["status"] != "ok":
            violations.append({"request_id": ev["request_id"], "kind": "non-ok",
                               "status": ev["status"], "error_class": ev.get("error_class")})
            continue
        got = client_chunks(ev)
        if got == ev["output_tokens"]:
            exact += 1
        elif got == ev["output_tokens"] - 1:
            eos_deficit += 1  # EOS stop token counted in usage, never streamed
        else:
            violations.append({"request_id": ev["request_id"], "kind": "chunk-count-mismatch",
                               "usage_output_tokens": ev["output_tokens"],
                               "client_received_chunks": got})
    out_tokens = sorted(ev["output_tokens"] for ev in evs if ev["status"] == "ok")
    return emit({
        "check": "integrity",
        "events": len(evs),
        "by_status": by_status,
        "chunk_count_rule": ("usage completion_tokens == client content chunks "
                             "(len(itl)+1 / 1), OR == chunks+1 for EOS-stopped streams "
                             "(llama-server counts the stop token in usage but emits no "
                             "content delta for it — measured 8f114a9 framing)"),
        "chunk_accounting": {"exact": exact, "eos_stop_deficit_1": eos_deficit},
        "violations": violations[:20],
        "violation_count": len(violations),
        "realized_output_tokens": {
            "note": "real model: EOS may end a completion before the directed max_tokens cap",
            "min": out_tokens[0] if out_tokens else None,
            "median": median(out_tokens),
            "max": out_tokens[-1] if out_tokens else None,
        },
    }, not violations)


# --------------------------------------------------------------------------
# derive-slo
# --------------------------------------------------------------------------

def round_up_2sig(x):
    if x <= 0:
        return 0.0
    exp = math.floor(math.log10(x))
    q = 10 ** (exp - 1)
    return round(math.ceil(x / q) * q, max(0, -(exp - 1)))


def cmd_derive_slo(args):
    maxima = {"ttft_seconds": 0.0, "e2e_duration_seconds": 0.0, "max_stall_seconds": 0.0}
    sources = []
    n_ok = 0
    for d in args.calib:
        evs = [e for e in load_events(os.path.join(d, "events.jsonl")) if e["status"] == "ok"]
        man = json.load(open(os.path.join(d, "manifest.json"), encoding="utf-8"))
        n_ok += len(evs)
        for ev in evs:
            if ev.get("ttft_seconds") is not None:
                maxima["ttft_seconds"] = max(maxima["ttft_seconds"], ev["ttft_seconds"])
            maxima["e2e_duration_seconds"] = max(
                maxima["e2e_duration_seconds"], ts(ev["end_ts"]) - ts(ev["scheduled_send_ts"]))
            st = max_stall(ev)
            if st is not None:
                maxima["max_stall_seconds"] = max(maxima["max_stall_seconds"], st)
        sources.append(f"{man['run_id']} ({man['workload_ref']['name']} v"
                       f"{man['workload_ref']['version']} seed {man['workload_ref']['seed']}, "
                       f"{len(evs)} ok events)")
    today = datetime.now(timezone.utc).date().isoformat()
    src = ("measured this session from the Scenario B calibration probes through the composed "
           "inferbench->infergate->llama-server path (evidence/i3/raw/runs/): " + "; ".join(sources)
           + f". Threshold = measured per-request maximum x{args.headroom} headroom, rounded up "
             "to 2 significant digits.")
    objectives = []
    thresholds = {}
    for sig in ("ttft_seconds", "e2e_duration_seconds", "max_stall_seconds"):
        thr = round_up_2sig(maxima[sig] * args.headroom)
        thresholds[sig] = {"measured_max": round(maxima[sig], 6), "threshold": thr}
        objectives.append({
            "signal": sig, "statistic": "max", "comparator": "<=",
            "threshold": thr, "unit": "seconds",
            "provenance": {"basis": "measured", "as_of": today, "source": src,
                           "notes": f"measured calibration maximum {maxima[sig]:.3f} s"},
        })
    slo = {
        "slo_id": "scenario-b-llamacpp-cpu-shakedown",
        "version": "1.0.0",
        "scope": "model-serving",
        "description": (
            "Scenario B / I3 methodology-shakedown SLO for goodput@SLO computation only: "
            "thresholds are derived from same-host calibration probe maxima (x"
            f"{args.headroom} headroom) against llama.cpp on a 4-core CPU. This is NOT a "
            "production or comparison target; it exists so the goodput machinery is exercised "
            "end-to-end on real events (same honest construction as inferbench's "
            "mock-loopback-baseline SLO)."),
        "applies_to": {"workload_ref": "scenario-b CPU-adapted workloads "
                                       "(chat-short-cpu, shared-prefix-cpu) on this host"},
        "objectives": objectives,
        "notes": ("Per-request evaluation: statistic 'max' objectives read as per-request "
                  "bounds (how the analyzer applies them). max_stall_seconds doubles as the "
                  "stall-rate threshold. Re-derive when host, engine build, model, or rates "
                  "change."),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(slo, f, indent=2)
        f.write("\n")
    return emit({
        "check": "derive-slo",
        "calib_runs": args.calib,
        "ok_events_used": n_ok,
        "headroom": args.headroom,
        "derivation": thresholds,
        "written_to": args.out,
    }, n_ok > 0 and all(v["threshold"] > 0 for v in thresholds.values()))


# --------------------------------------------------------------------------
# poll-slots / sample-contention (run-time helpers)
# --------------------------------------------------------------------------

def cmd_poll_slots(args):
    stop = {"flag": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.update(flag=True))
    signal.signal(signal.SIGINT, lambda *_: stop.update(flag=True))
    with open(args.out, "a", buffering=1, encoding="utf-8") as f:
        while not stop["flag"]:
            t0 = time.time()
            try:
                with urllib.request.urlopen(args.url, timeout=2) as resp:
                    slots = json.loads(resp.read())
                processing = sorted(s["id"] for s in slots if s.get("is_processing"))
                f.write(json.dumps({"ts": round(t0, 6), "processing": processing}) + "\n")
            except Exception as e:  # server restarting/killed: record the gap
                f.write(json.dumps({"ts": round(t0, 6), "error": str(e)[:120]}) + "\n")
            time.sleep(max(0.0, args.interval_ms / 1000 - (time.time() - t0)))
    return 0


def read_proc_cpu(names):
    ticks = {}
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/stat", "rb") as f:
                st = f.read().decode("utf-8", "replace")
            comm = st[st.index("(") + 1:st.rindex(")")]
            if comm not in names:
                continue
            rest = st[st.rindex(")") + 2:].split()
            ticks[comm] = ticks.get(comm, 0) + int(rest[11]) + int(rest[12])  # utime+stime
        except OSError:
            continue
    return ticks


def cmd_sample_contention(args):
    names = set(args.names.split(","))
    hz = os.sysconf("SC_CLK_TCK")
    stop = {"flag": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.update(flag=True))
    signal.signal(signal.SIGINT, lambda *_: stop.update(flag=True))
    prev, prev_t = read_proc_cpu(names), time.time()
    with open(args.out, "a", buffering=1, encoding="utf-8") as f:
        while not stop["flag"]:
            time.sleep(args.interval_s)
            cur, cur_t = read_proc_cpu(names), time.time()
            dt = cur_t - prev_t
            load1 = open("/proc/loadavg").read().split()[0]
            fields = " ".join(
                f"{n}={100 * (cur.get(n, 0) - prev.get(n, 0)) / hz / dt:.1f}"
                for n in sorted(names))
            f.write(f"{cur_t:.3f} load={load1} {fields}\n")
            prev, prev_t = cur, cur_t
    return 0


def cmd_contention(args):
    start = end = None
    samples = []
    for line in open(args.log, encoding="utf-8"):
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "MARK":
            if parts[2] == "start" and parts[3] == args.phase:
                start = float(parts[1])
            elif parts[2] == "end" and parts[3] == args.phase:
                end = float(parts[1])
            continue
        samples.append((float(parts[0]),
                        {k: float(v) for k, v in (p.split("=") for p in parts[1:])}))
    if start is None:
        return emit({"check": "contention", "phase": args.phase,
                     "error": "no start marker"}, False)
    window = [s for t, s in samples if start <= t <= (end or float("inf"))]
    agg = {}
    for s in window:
        for k, v in s.items():
            agg.setdefault(k, []).append(v)
    return emit({
        "check": "contention",
        "phase": args.phase,
        "samples": len(window),
        "interval_cpu_percent": {
            k: {"mean": round(sum(v) / len(v), 1), "max": round(max(v), 1)}
            for k, v in sorted(agg.items()) if k != "load"},
        "loadavg_1min": {"mean": round(sum(agg.get("load", [0])) / max(1, len(agg.get("load", []))), 2),
                         "max": round(max(agg.get("load", [0])), 2)},
        "note": "interval CPU from /proc/<pid>/stat utime+stime deltas, 100% = one core",
    }, bool(window))


# --------------------------------------------------------------------------
# cancel-llama
# --------------------------------------------------------------------------

def slot_releases(poll_path):
    """is_processing true->false transitions per slot: (t_last_true, t_first_false)."""
    releases = []
    busy = {}  # slot id -> ts of last sample where it was processing
    for line in open(poll_path, encoding="utf-8"):
        rec = json.loads(line)
        if "processing" not in rec:
            continue
        now = set(rec["processing"])
        for sid, t_busy in list(busy.items()):
            if sid not in now:
                releases.append({"slot": sid, "after": t_busy, "by": rec["ts"]})
                del busy[sid]
        for sid in now:
            busy[sid] = rec["ts"]
    return releases, busy


def cmd_cancel_llama(args):
    evs = load_events(args.events)
    canceled = [ev for ev in evs if ev["status"] == "canceled"]
    ok_evs = [ev for ev in evs if ev["status"] == "ok"]
    others = [ev for ev in evs if ev["status"] not in ("ok", "canceled")]
    problems = []
    if others:
        problems.append(f"{len(others)} events neither ok nor canceled")
    if not canceled:
        problems.append("no canceled events — nothing verified")
    log_text = open(args.llama_log, encoding="utf-8", errors="replace").read()
    cancel_lines = log_text.count("cancel task")
    if cancel_lines != len(canceled):
        problems.append(f"llama-server 'cancel task' log lines {cancel_lines} != "
                        f"client canceled {len(canceled)}")
    for ev in canceled:
        cp = ev.get("cancellation_point") or {}
        if cp.get("output_tokens_at_cancel") != 8:
            problems.append(f"{ev['request_id']}: output_tokens_at_cancel "
                            f"{cp.get('output_tokens_at_cancel')} != 8")
    releases, still_busy = slot_releases(args.slots_poll)
    if still_busy:
        problems.append(f"slots still processing at end of poll: {still_busy}")
    # Pair every request end (ok completions also free their slot) with the
    # nearest observed release; then judge the bound on the canceled ones.
    ends = ([("canceled", ts(ev["end_ts"])) for ev in canceled]
            + [("ok", ts(ev["end_ts"])) for ev in ok_evs])
    ends.sort(key=lambda x: x[1])
    used = [False] * len(releases)
    deltas_ms = []
    for kind, e in ends:
        best, best_d = None, None
        for i, r in enumerate(releases):
            if used[i]:
                continue
            mid = (r["after"] + r["by"]) / 2
            d = mid - e
            if best is None or abs(d) < abs(best_d):
                best, best_d = i, d
        if best is None:
            problems.append(f"a {kind} request end has no slot release to pair with")
            continue
        used[best] = True
        if kind == "canceled":
            deltas_ms.append(round(best_d * 1000, 1))
    over = [d for d in deltas_ms if d > args.bound_ms or d < -2 * args.poll_interval_ms]
    if over:
        problems.append(f"{len(over)} release deltas beyond bound "
                        f"[-{2 * args.poll_interval_ms}, {args.bound_ms}]ms: {over[:5]}")
    doc = {
        "check": "cancel-llama",
        "declared_bound_ms": args.bound_ms,
        "bound_definition": (
            "midpoint of the /slots is_processing true->false transition window (poll "
            f"interval {args.poll_interval_ms} ms) minus client-side cancel completion "
            "(event end_ts); greedy nearest-neighbor pairing over ALL request ends (ok "
            "completions also release their slot); same-host clock. The bound covers the "
            "ENGINE's decode-batch-boundary release granularity — a cancel landing inside "
            "a concurrent slot's prefill ubatch is noticed only when that ubatch completes "
            "(IG-T005 @74f2372 measured the gateway-propagation component directly at "
            "1.25-5.24 ms mid-stream)"),
        "events": len(evs),
        "client_canceled": len(canceled),
        "client_ok_completed_before_trigger": len(ok_evs),
        "eos_race_note": ("ok events are completions the model ended by EOS before the "
                          "8-token cancel trigger fired — realized-cancel accounting, "
                          "mirroring Scenario A"),
        "llama_log_cancel_task_lines": cancel_lines,
        "slot_releases_observed": len(releases),
        "release_delta_ms": {
            "count": len(deltas_ms),
            "min": min(deltas_ms) if deltas_ms else None,
            "median": median(deltas_ms),
            "max": max(deltas_ms) if deltas_ms else None,
            "all": sorted(deltas_ms),
        },
        "problems": problems,
    }
    return emit(doc, not problems)


# --------------------------------------------------------------------------
# failover
# --------------------------------------------------------------------------

def served_by(ev, mock_itl_s=0.030):
    """Attribute an ok event to an engine by timing signature: the mock
    streams at a constant configured ITL (30 ms) after a constant 300 ms
    TTFT; llama-server on this host decodes at >=40 ms/token with >=~0.2 s
    prefill. ITL median is the primary signal, TTFT the fallback."""
    itl = ev.get("itl") or {}
    series = itl.get("series_seconds")
    if series:
        m = median(series)
        return "mock" if m is not None and m < mock_itl_s + 0.008 else "llamacpp"
    t = ev.get("ttft_seconds")
    return "mock" if t is not None and t < 0.9 else "llamacpp"


def cmd_failover(args):
    evs = load_events(args.events)
    tl = json.load(open(args.timeline, encoding="utf-8"))
    kill, listening = ts(tl["kill_ts"]), ts(tl["listening_ts"])
    mock = json.load(open(args.mock_state, encoding="utf-8"))
    problems = []
    segments = {"pre_kill": [], "downtime": [], "post_restart": []}
    errors, sheds = [], []
    for ev in evs:
        send = ts(ev["send_ts"])
        if ev["status"] == "shed":
            sheds.append(ev)
            continue
        if ev["status"] == "error":
            errors.append(ev)
            continue
        if ev["status"] != "ok":
            problems.append(f"{ev['request_id']}: unexpected status {ev['status']}")
            continue
        seg = ("pre_kill" if send < kill else
               "downtime" if send < listening else "post_restart")
        segments[seg].append(ev)
    # (1) typed errors are exactly the streams in flight at the kill.
    in_flight = [ev for ev in evs if ts(ev["send_ts"]) < kill < ts(ev["end_ts"])]
    for ev in errors:
        if ev.get("error_class") not in ("upstream_error", "upstream_timeout"):
            problems.append(f"{ev['request_id']}: error_class {ev.get('error_class')} "
                            "not an upstream taxonomy value")
        if not (ts(ev["send_ts"]) < kill < ts(ev["end_ts"]) + 0.5):
            problems.append(f"{ev['request_id']}: error outside the kill transition "
                            f"(send {ev['send_ts']}, end {ev['end_ts']})")
    if len(errors) != len(in_flight):
        problems.append(f"typed errors {len(errors)} != streams in flight at kill "
                        f"{len(in_flight)} (in-flight ids "
                        f"{[e['request_id'] for e in in_flight]})")
    if sheds:
        problems.append(f"{len(sheds)} shed events (expected 0)")
    # (2) engine attribution by timing signature per segment.
    attribution = {}
    for seg, sevs in segments.items():
        att = {"mock": 0, "llamacpp": 0}
        for ev in sevs:
            att[served_by(ev)] += 1
        ttfts = sorted(ev["ttft_seconds"] for ev in sevs if ev.get("ttft_seconds") is not None)
        attribution[seg] = {"ok": len(sevs), **att,
                            "ttft_p50_s": round(median(ttfts), 3) if ttfts else None}
    if attribution["pre_kill"]["mock"]:
        problems.append(f"{attribution['pre_kill']['mock']} pre-kill ok events attributed "
                        "to the mock (expected llamacpp only)")
    if attribution["downtime"]["llamacpp"]:
        problems.append(f"{attribution['downtime']['llamacpp']} downtime ok events "
                        "attributed to llamacpp (it was dead)")
    if attribution["post_restart"]["mock"]:
        problems.append(f"{attribution['post_restart']['mock']} post-restart ok events "
                        "attributed to the mock (expected llamacpp again)")
    if not segments["downtime"]:
        problems.append("no ok events during the downtime window — fallback not exercised")
    if not segments["post_restart"]:
        problems.append("no ok events after restart — recovery not demonstrated")
    # (3) conservation against the mock's own counters.
    mock_completed = mock.get("streams_completed", 0)
    if mock_completed != len(segments["downtime"]):
        problems.append(f"mock streams_completed {mock_completed} != downtime ok count "
                        f"{len(segments['downtime'])} (attribution vs conservation mismatch)")
    doc = {
        "check": "failover",
        "timeline": {"kill_ts": tl["kill_ts"], "listening_ts": tl["listening_ts"],
                     "downtime_seconds": round(listening - kill, 1)},
        "events": len(evs),
        "typed_upstream_errors": {
            "count": len(errors),
            "bound": "== streams accepted before the kill and still in flight "
                     f"({len(in_flight)}); never failed over after acceptance",
            "request_ids": [e["request_id"] for e in errors],
            "error_classes": sorted({e.get("error_class") for e in errors}),
        },
        "segments": attribution,
        "attribution_method": ("ok events attributed by timing signature (mock: constant "
                               "30 ms ITL / 300 ms TTFT; llama-server: >=40 ms/token, "
                               ">=0.2 s prefill), cross-checked by conservation against "
                               "mock /debug/state streams_completed"),
        "mock_debug_state": {k: mock.get(k) for k in
                             ("requests_total", "streams_started", "streams_completed",
                              "aborts_total")},
        "problems": problems,
    }
    return emit(doc, not problems)


# --------------------------------------------------------------------------
# ttft-compare
# --------------------------------------------------------------------------

def cmd_ttft_compare(args):
    direct = json.load(open(args.direct, encoding="utf-8"))
    gw = json.load(open(args.gw, encoding="utf-8"))

    def p50(res):
        return res["pooled_percentiles"]["tables"]["ttft_seconds"]["p50"]

    d, g = p50(direct), p50(gw)
    delta_ms = (g - d) * 1000
    doc = {
        "check": "ttft-compare",
        "hypothesis": f"via-gateway pooled TTFT p50 - engine-direct pooled TTFT p50 "
                      f"< {args.bound_ms} ms (identical workload version+seed, fresh "
                      "llama-server per arm, single run per arm)",
        "pipeline_pooled_p50_s": {"engine_direct": d, "via_gateway": g},
        "delta_ms": round(delta_ms, 1),
        "bound_ms": args.bound_ms,
        "source": "pooled percentiles from the inferbench analysis pipeline result files "
                  "only (no re-computation here)",
    }
    if args.events_direct and args.events_gw:
        de = {ev["workload_item"]: ev for ev in load_events(args.events_direct)
              if ev["status"] == "ok" and ev.get("ttft_seconds") is not None}
        ge = {ev["workload_item"]: ev for ev in load_events(args.events_gw)
              if ev["status"] == "ok" and ev.get("ttft_seconds") is not None}
        pairs = [(ge[k]["ttft_seconds"] - de[k]["ttft_seconds"]) * 1000
                 for k in sorted(set(de) & set(ge))]
        doc["paired_diagnostic"] = {
            "label": "DIAGNOSTIC ONLY — per-request pairing by workload_item (same seed => "
                     "same prompt+schedule); not a pipeline statistic, never quotable as a "
                     "result",
            "pairs": len(pairs),
            "delta_ms_median": round(median(pairs), 1) if pairs else None,
            "delta_ms_p90": round(sorted(pairs)[int(0.9 * (len(pairs) - 1))], 1) if pairs else None,
            "delta_ms_min": round(min(pairs), 1) if pairs else None,
            "delta_ms_max": round(max(pairs), 1) if pairs else None,
        }
    return emit(doc, delta_ms < args.bound_ms)


# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("integrity")
    s.add_argument("events")

    s = sub.add_parser("derive-slo")
    s.add_argument("--calib", action="append", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--headroom", type=float, default=1.5)

    s = sub.add_parser("poll-slots")
    s.add_argument("--url", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--interval-ms", type=float, default=25)

    s = sub.add_parser("sample-contention")
    s.add_argument("--out", required=True)
    s.add_argument("--interval-s", type=float, default=5)
    s.add_argument("--names", default="llama-server,gateway,mock-backend,inferbench")

    s = sub.add_parser("contention")
    s.add_argument("log")
    s.add_argument("--phase", required=True)

    s = sub.add_parser("cancel-llama")
    s.add_argument("events")
    s.add_argument("slots_poll")
    s.add_argument("--llama-log", required=True)
    s.add_argument("--bound-ms", type=float, default=2500)
    s.add_argument("--poll-interval-ms", type=float, default=25)

    s = sub.add_parser("failover")
    s.add_argument("events")
    s.add_argument("timeline")
    s.add_argument("mock_state")

    s = sub.add_parser("ttft-compare")
    s.add_argument("direct")
    s.add_argument("gw")
    s.add_argument("--bound-ms", type=float, default=100)
    s.add_argument("--events-direct")
    s.add_argument("--events-gw")

    args = p.parse_args()
    return {
        "integrity": cmd_integrity,
        "derive-slo": cmd_derive_slo,
        "poll-slots": cmd_poll_slots,
        "sample-contention": cmd_sample_contention,
        "contention": cmd_contention,
        "cancel-llama": cmd_cancel_llama,
        "failover": cmd_failover,
        "ttft-compare": cmd_ttft_compare,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
