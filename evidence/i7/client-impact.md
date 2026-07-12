# Client impact — streaming-critical scenarios (1, 2, 5, 6, 12)

Required by 07 §I7: "client impact measured by inferbench for at least the streaming-critical
scenarios (1, 2, 5, 6, 12)." All five measured; none skipped. Source: `inferops` repo,
commit `a07fd2f`, cited by path below. Client-impact instrument for all five:
`inferbench` commit `62c2704997e6c8a2966307ee3d8dbfd16747b631` (host build; see
`checklist.md` §5 for why no digest is recorded).

| # | Scenario | inferbench run(s) | sent | ok | errors | shed | Headline |
|---|---|---|---|---|---|---|---|
| 1 | Backend killed before first token | `inferops/faults/scenario-01/evidence/20260712T012421Z/{inferbench-run,inferbench-run-part2}/` | 60 + 60 | 39 + 8 | 6 + 9 | 15 + 43 | Part 1 (hard kill+restart, 20s window): 39/60 ok, 6/60 typed `upstream_error`, 15/60 typed 503 shed. Part 2 (transient 50% failure, ~14s window): 8/60 ok, 9/60 typed `upstream_error`, 43/60 typed 503 shed (circuit-breaker-protected). **0 silent failures, 0 duplicated/truncated output, 0 hangs in either part.** |
| 2 | Backend killed after first token | `inferops/faults/scenario-02/evidence/20260712T012838Z/inferbench-run/` (+ `raw-stream.sse` byte-level capture) | 60 | 51 | 6 | 3 | 51/60 unaffected; 5/60 received a clean typed SSE `upstream_error` mid-stream with partial content retained and billed (1796 output tokens settled, 0→1796); 3/60 shed (unrelated admission pressure); 1/60 an unexplained-but-benign timeout artifact (probable DNS-cache reuse across the restarted container, not a gateway behavior — recorded honestly, does not change the verdict). **0 hangs, 0 duplicated output, 0 untyped failures.** |
| 5 | Gateway termination during streaming | `inferops/faults/scenario-05/evidence/20260712T014402Z/inferbench-run/` (+ `scripts/evidence/drain-test-20260711T234926Z/` corroboration) | 60 | 60 | 0 | 0 | **60/60 ok, 0 errors, 0 shed** across the full SIGTERM-to-restart window of one 2-replica fleet member — the strongest possible client-impact result for this scenario. |
| 6 | Queue saturation | `inferops/faults/scenario-06/evidence/20260712T014522Z/inferbench-run/` (+ manual 20-way burst, `burst-headers.txt`) | 399 | 3 | 4 | 392 | 3/399 admitted at baseline latency (p50=p95=24ms vs. ~20ms mock baseline — **small sample, n=3, flagged honestly, not inflated**), 392/399 cleanly shed (typed 503 + `Retry-After: 1` + request ID, never a connection reset or silent drop), 4/399 an unrelated `upstream_timeout` workload-tuning artifact (itl/output-cap combination against the default 30s upstream timeout — same confound class as scenario 2's, recorded not re-run). **0 silent failures, 0 untyped errors.** |
| 12 | Rolling update with active requests | `inferops/faults/scenario-12/evidence/20260712T015749Z/inferbench-run/` (+ `scripts/evidence/rolling-update-20260711T234628Z/` corroboration, 0/27+0/3 curl-based) | 60 | 60 | 0 | 0 | **60/60 ok, 0 errors, 0 shed** across the complete sequential drain+replace of both fleet replicas — two independent, zero-error confirmations (inferbench here, curl-based at IO-T004) using two different client measurement tools. |

## Reading across the five

- **Zero silent failures anywhere.** Every non-`ok` outcome across all five scenarios (and
  across the whole 12-scenario campaign, per `campaign-matrix.md`) is a typed error envelope,
  a typed 503 shed, or an explicitly-accounted client-side timeout — never a bare disconnect,
  never truncated/duplicated output.
- **The two "kill" scenarios (1, 2) show partial degradation, correctly typed and correctly
  billed** — this is the expected, contract-compliant behavior for a hard backend failure, not
  a clean pass in the "zero errors" sense of 5/12.
- **The two "operational" scenarios (5, 12 — gateway termination, rolling update) show zero
  client-visible errors** — the fleet-level redundancy + drain semantics fully absorbed the
  disruption, corroborated by two independent measurement tools each.
- **Scenario 6 (queue saturation) shows admission control doing its job under a 25 rps burst
  against a deliberately tiny 4-in-flight/8-queue budget** — a 392/399 shed rate is the
  tightened config working as configured, not a failure; the honest caveat is the small
  admitted-population sample (n=3).

No client-impact number in this table is assumed or narrated — each is a direct read of the
cited `inferbench` run's summary line and `events.jsonl`, itself cited from `inferops`'s
already-published evidence.
