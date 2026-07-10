#!/usr/bin/env python3
"""Scenario A / I2 acceptance checks over run evidence (IL-T002).

Read-only analysis of artifacts produced by run.sh; every command prints one
JSON document (the evidence number + its inputs) and exits 0 on PASS, 1 on
FAIL. This is evidence tooling only — never a benchmark statistics engine
(that is inferbench IB-T005 scope).

Commands:
  integrity <events.jsonl> [--min-concurrent N]
      Stream-integrity + concurrency: every event ok; server-reported usage
      completion tokens == client-received content chunks (len(itl)+1, or 1
      when a single chunk yields no ITL series); optional max-concurrency
      floor computed from send_ts/end_ts overlap.
  cancel <events.jsonl> <debug-state.json> --expect-phase P --min-chunks N
         [--bound-ms 100]
      3-point cancellation: every mock-observed abort pairs (nearest-neighbor)
      with a client cancel completion within the bound (both hosts share one
      clock); abort phase/chunks as expected; stream conservation holds
      (started == completed + aborted). A client cancel that raced stream
      completion (the mock finished writing before observing the disconnect,
      so no abort exists) is counted explicitly as a race, required to equal
      the mock-side completed-vs-client-ok surplus — a race is not a leak.
  ttft <events.jsonl> <pre.prom> <post.prom> [--tolerance-ms 25]
      Client-vs-gateway TTFT agreement on the scrape delta window:
      0 <= client_mean - gateway_mean <= tolerance; sample counts must match;
      bucket-CDF table reported as supporting data.
  traces <traces.jsonl> [--excerpt-out FILE]
      OTel Collector file-export: count traces carrying the full gateway span
      sequence recv/queue.wait/upstream.connect/ttft/stream.relay/settle;
      write a one-trace excerpt.
"""

import argparse
import json
import re
import sys
from datetime import datetime

SPAN_SEQUENCE = ["recv", "queue.wait", "upstream.connect", "ttft", "stream.relay", "settle"]


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


def cmd_integrity(args):
    evs = load_events(args.events)
    by_status = {}
    for ev in evs:
        by_status[ev["status"]] = by_status.get(ev["status"], 0) + 1
    violations = []
    for ev in evs:
        if ev["status"] != "ok":
            violations.append({"request_id": ev["request_id"], "kind": "non-ok",
                               "status": ev["status"], "error_class": ev.get("error_class")})
            continue
        got = client_chunks(ev)
        if got != ev["output_tokens"]:
            violations.append({"request_id": ev["request_id"], "kind": "chunk-count-mismatch",
                               "usage_output_tokens": ev["output_tokens"],
                               "client_received_chunks": got})
    # max concurrency by sweep over (send_ts, +1) / (end_ts, -1)
    marks = []
    for ev in evs:
        marks.append((ts(ev["send_ts"]), 1))
        marks.append((ts(ev["end_ts"]), -1))
    marks.sort()
    cur = peak = 0
    for _, d in marks:
        cur += d
        peak = max(peak, cur)
    ok = not violations and (args.min_concurrent is None or peak >= args.min_concurrent)
    return emit({
        "check": "integrity",
        "events": len(evs),
        "by_status": by_status,
        "chunk_count_rule": "usage completion_tokens == client content chunks (len(itl)+1 / 1)",
        "violations": violations[:20],
        "violation_count": len(violations),
        "max_concurrent_in_flight": peak,
        "min_concurrent_required": args.min_concurrent,
    }, ok)


def cmd_cancel(args):
    evs = load_events(args.events)
    state = json.load(open(args.debug_state, encoding="utf-8"))
    canceled = [ev for ev in evs if ev["status"] == "canceled"]
    ok_evs = [ev for ev in evs if ev["status"] == "ok"]
    others = [ev for ev in evs if ev["status"] not in ("ok", "canceled")]
    aborts = state.get("aborts") or []
    problems = []
    if others:
        problems.append(f"{len(others)} events neither ok nor canceled")
    # Stream conservation at the mock: every started stream either completed
    # or was observed aborted. A hole here would be a real leak.
    started = state.get("streams_started", 0)
    completed = state.get("streams_completed", 0)
    aborted = state.get("aborts_total", 0)
    if started != completed + aborted:
        problems.append(f"mock stream conservation broken: started {started} != "
                        f"completed {completed} + aborted {aborted}")
    # Completion/cancel races: the client canceled but the mock had already
    # finished writing the whole stream (no abort to observe). Their count
    # must exactly equal the mock-side completed-vs-client-ok surplus.
    races = len(canceled) - aborted
    if races != completed - len(ok_evs):
        problems.append(f"cancel/abort accounting broken: client canceled {len(canceled)} "
                        f"vs mock aborts {aborted}, but mock completed {completed} "
                        f"vs client ok {len(ok_evs)}")
    if races < 0:
        problems.append(f"mock observed {-races} more aborts than client cancels")
    for ab in aborts:
        if ab["phase"] != args.expect_phase:
            problems.append(f"abort phase {ab['phase']} != expected {args.expect_phase}")
        if ab["chunks_sent"] < args.min_chunks:
            problems.append(f"abort chunks_sent {ab['chunks_sent']} < {args.min_chunks}")
    tok_expect = args.expect_tokens
    if tok_expect is not None:
        for ev in canceled:
            cp = ev.get("cancellation_point") or {}
            if cp.get("output_tokens_at_cancel") != tok_expect:
                problems.append(f"{ev['request_id']}: output_tokens_at_cancel "
                                f"{cp.get('output_tokens_at_cancel')} != {tok_expect}")
    # Release deltas: each mock abort paired (greedy nearest-neighbor, each
    # client cancel used at most once) with a client cancel completion.
    ends = sorted(ts(ev["end_ts"]) for ev in canceled)
    abort_times = sorted(ab["at_unix_nano"] / 1e9 for ab in aborts)
    used = [False] * len(ends)
    deltas_ms = []
    for a in abort_times:
        best = None
        for i, e in enumerate(ends):
            if used[i]:
                continue
            if best is None or abs(a - e) < abs(a - ends[best]):
                best = i
        if best is None:
            problems.append("abort with no client cancel to pair with")
            continue
        used[best] = True
        deltas_ms.append(round((a - ends[best]) * 1000, 3))
    over = [d for d in deltas_ms if abs(d) > args.bound_ms]
    if over:
        problems.append(f"{len(over)} release deltas beyond ±{args.bound_ms}ms bound: {over[:5]}")
    doc = {
        "check": "cancel",
        "declared_bound_ms": args.bound_ms,
        "bound_definition": "mock-observed abort timestamp (/debug/state at_unix_nano) within "
                            "bound of the client-side cancel completion (event end_ts); k-th "
                            "sorted abort paired with k-th sorted cancel; same-host clock",
        "events": len(evs),
        "client_canceled": len(canceled),
        "client_ok_completed_before_trigger": len(ok_evs),
        "completion_race_count": races,
        "completion_race_note": "client cancels the mock never observed because the stream "
                                "was already fully written (completed at engine); verified "
                                "against mock completed-vs-client-ok surplus — race, not leak",
        "mock": {k: state.get(k) for k in
                 ("requests_total", "streams_started", "streams_completed", "aborts_total")},
        "abort_phases": sorted({ab["phase"] for ab in aborts}),
        "expected_phase": args.expect_phase,
        "release_delta_ms": {
            "count": len(deltas_ms),
            "min": min(deltas_ms) if deltas_ms else None,
            "median": sorted(deltas_ms)[len(deltas_ms) // 2] if deltas_ms else None,
            "max": max(deltas_ms) if deltas_ms else None,
        },
        "problems": problems,
    }
    return emit(doc, not problems and len(canceled) > 0)


PROM_RE = re.compile(
    r'^inference_ttft_seconds(_bucket|_sum|_count)\{([^}]*)\}\s+([0-9.eE+-]+)\s*$')


def parse_ttft(path):
    buckets, total_sum, total_count = {}, 0.0, 0.0
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = PROM_RE.match(line)
            if not m:
                continue
            kind, labels, value = m.group(1), m.group(2), float(m.group(3))
            if 'model="mock-8b"' not in labels or 'backend="mock"' not in labels:
                continue
            if kind == "_bucket":
                le = re.search(r'le="([^"]+)"', labels).group(1)
                buckets[le] = buckets.get(le, 0.0) + value
            elif kind == "_sum":
                total_sum += value
            else:
                total_count += value
    return buckets, total_sum, total_count


def cmd_ttft(args):
    evs = load_events(args.events)
    client = [ev["ttft_seconds"] for ev in evs
              if ev["status"] == "ok" and ev.get("ttft_seconds") is not None]
    pre_b, pre_s, pre_c = parse_ttft(args.pre)
    post_b, post_s, post_c = parse_ttft(args.post)
    gw_count = post_c - pre_c
    gw_mean = (post_s - pre_s) / gw_count if gw_count else None
    cl_mean = sum(client) / len(client) if client else None
    cdf = []
    for le in sorted(set(pre_b) | set(post_b), key=lambda x: float("inf") if x == "+Inf" else float(x)):
        d = post_b.get(le, 0) - pre_b.get(le, 0)
        bound = float("inf") if le == "+Inf" else float(le)
        cl_frac = sum(1 for t in client if t <= bound) / len(client) if client else None
        cdf.append({"le": le, "gateway_fraction": round(d / gw_count, 4) if gw_count else None,
                    "client_fraction": round(cl_frac, 4) if cl_frac is not None else None})
    diff_ms = (cl_mean - gw_mean) * 1000 if cl_mean is not None and gw_mean is not None else None
    problems = []
    if gw_count != len(client):
        problems.append(f"population mismatch: gateway observed {gw_count}, client ok events {len(client)}")
    if diff_ms is None:
        problems.append("no samples")
    elif not (0 <= diff_ms <= args.tolerance_ms):
        problems.append(f"client_mean - gateway_mean = {diff_ms:.3f}ms outside declared [0, {args.tolerance_ms}]ms")
    doc = {
        "check": "ttft-agreement",
        "measurement_points": {
            "gateway": "complete client request read at gateway -> first upstream response "
                       "body byte at gateway (inference_ttft_seconds, Contract 2)",
            "client": "scheduled send (CO-safe basis, inferbench) -> first response body "
                      "byte at client (raw-event ttft_seconds)",
        },
        "declared_tolerance": f"0ms <= client_mean - gateway_mean <= {args.tolerance_ms}ms; "
                              "justification: same-host loopback/bridge transit (<1ms RTT), "
                              "gateway request-read+dispatch overhead, and client send-slip "
                              "on the scheduled-send basis (IB-T004 calibration measured "
                              "client TTFT-minus-configured p50 within [-2,+15]ms)",
        "gateway": {"count": gw_count, "mean_s": round(gw_mean, 6) if gw_mean else None},
        "client": {"count": len(client), "mean_s": round(cl_mean, 6) if cl_mean else None,
                   "p50_s": round(sorted(client)[len(client) // 2], 6) if client else None,
                   "p95_s": round(sorted(client)[int(0.95 * (len(client) - 1))], 6) if client else None},
        "client_minus_gateway_mean_ms": round(diff_ms, 3) if diff_ms is not None else None,
        "bucket_cdf": cdf,
        "problems": problems,
    }
    return emit(doc, not problems)


def cmd_traces(args):
    traces = {}
    total_spans = 0
    with open(args.traces, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            doc = json.loads(line)
            for rs in doc.get("resourceSpans", []):
                for ss in rs.get("scopeSpans", []):
                    for sp in ss.get("spans", []):
                        total_spans += 1
                        traces.setdefault(sp["traceId"], []).append({
                            "name": sp["name"], "spanId": sp["spanId"],
                            "parentSpanId": sp.get("parentSpanId", ""),
                            "startTimeUnixNano": int(sp["startTimeUnixNano"]),
                            "endTimeUnixNano": int(sp["endTimeUnixNano"]),
                        })
    complete = {tid: spans for tid, spans in traces.items()
                if set(SPAN_SEQUENCE) <= {s["name"] for s in spans}}
    excerpt = None
    if complete:
        tid = sorted(complete)[0]
        spans = sorted(complete[tid], key=lambda s: s["startTimeUnixNano"])
        excerpt = {"traceId": tid, "spans": spans,
                   "span_order_by_start": [s["name"] for s in spans]}
        if args.excerpt_out:
            with open(args.excerpt_out, "w", encoding="utf-8") as f:
                json.dump(excerpt, f, indent=2)
    doc = {
        "check": "traces",
        "required_span_sequence": SPAN_SEQUENCE,
        "total_spans": total_spans,
        "total_traces": len(traces),
        "traces_with_full_sequence": len(complete),
        "excerpt_written_to": args.excerpt_out if complete else None,
        "excerpt_span_order": excerpt["span_order_by_start"] if excerpt else None,
    }
    return emit(doc, bool(complete))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("integrity")
    s.add_argument("events")
    s.add_argument("--min-concurrent", type=int, default=None)

    s = sub.add_parser("cancel")
    s.add_argument("events")
    s.add_argument("debug_state")
    s.add_argument("--expect-phase", required=True)
    s.add_argument("--min-chunks", type=int, default=0)
    s.add_argument("--expect-tokens", type=int, default=None)
    s.add_argument("--bound-ms", type=float, default=100.0)

    s = sub.add_parser("ttft")
    s.add_argument("events")
    s.add_argument("pre")
    s.add_argument("post")
    s.add_argument("--tolerance-ms", type=float, default=25.0)

    s = sub.add_parser("traces")
    s.add_argument("traces")
    s.add_argument("--excerpt-out", default=None)

    args = p.parse_args()
    return {"integrity": cmd_integrity, "cancel": cmd_cancel,
            "ttft": cmd_ttft, "traces": cmd_traces}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
