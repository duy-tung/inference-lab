# evidence/i2 — notes (Scenario A / IL-T002, run of 2026-07-10)

Dated observations for the I2 evidence set. Layout per `docs/interfaces.md` §4; run
directories live under `raw/runs/<run-id>/` (inferbench output: `manifest.json`,
`events.jsonl`, `run.log`, plus the mock's `debug-state.json` for cancellation runs).
`reports/` is intentionally absent: the benchmark report generator is IB-T006 (I3 scope) —
these runs are correctness evidence, not benchmarks.

## 2026-07-10 — run observations

- **Archive format:** `events.jsonl` for `chat-short` (5.8 MB) and `concurrency-100`
  (5.3 MB) and the collector trace export `traces.jsonl` (19 MB) are stored gzipped
  (lossless; `gunzip` to re-derive). Everything else is plain text.
- **Completion/cancel race (near-completion point):** 1 of 13 client cancels
  (request `i2-cancel-near-completion-r1-000041`, cancel at token 240) has no mock abort:
  the mock had already written the remaining chunks + `[DONE]` before observing the
  disconnect (`streams_completed=188` vs 187 client-ok). Stream conservation is exact
  (188 completed + 12 aborted = 200 started), so this is the documented race at the
  completion boundary, **not** a cancellation leak. First analysis used index-paired
  deltas and mis-flagged this as FAIL; per the I2 failure-handling rule ("measurement
  disagreement → check measurement-point definitions before suspecting code") the pairing
  in `scenarios/a/checks.py` was corrected to nearest-neighbor with explicit race
  accounting — the raw artifacts were untouched.
- **Keep-alive flush requests:** after each mock restart (fresh `/debug/state` counters per
  cancellation point), `run.sh` sends one recorded non-stream request through the gateway
  to retire any stale gateway→mock keep-alive connection. These 3 requests appear in the
  mock's `requests_total` and in the trace totals; they are outside every check window.
- **Trace totals conserve exactly:** 7831 traces = 4830 (chat-short) + 2736
  (concurrency-100) + 30 + 30 + 200 (cancellation runs) + 2 smoke + 3 flush; 7801 carry
  the full 6-span sequence, and the 30-trace difference is exactly the pre-first-token
  cancels, which never open `ttft`/`stream.relay` spans.
- **Schedule health:** max send slip 67.1 ms (chat-short), 37.6 ms (near-completion run) —
  all under the 100 ms watchdog; no run was invalidated.
- **Mock determinism note:** the mock caps generation at 256 tokens and samples the
  per-request length seeded-uniform in 1..min(max_tokens,256); the scenario-local
  workloads document how their triggers interact with that (see each workload file's
  description).

## Deviations affecting this evidence

- **D-001 — no PostgreSQL usage write** (checklist item 7): infergate@5d69aeb predates
  IG-T007/T008. Scenario A re-runs with PostgreSQL when IG-T008 lands; the usage-write
  criterion stays open until then.
- **D-002 — local FROM-scratch images** (registry blob CDNs blocked by the egress proxy);
  digests recorded are local content-addressed image IDs (assumption A-005).
- **D-003 — OTel Collector built via ocb v0.156.0** from pinned released modules instead
  of the unreachable upstream contrib image.

Full deviation records: `docs/implementation-notes.md`.

## Defects filed upstream

None. No component misbehaved in this run.
