# evidence/i3 — notes (Scenario B / IL-T003, runs of 2026-07-11)

Dated observations for the I3 evidence set. Layout per `docs/interfaces.md` §4; run
directories live under `raw/runs/<run-id>/` (inferbench output: `manifest.json`,
`events.jsonl`, `run.log`, `workload.json`). `reports/` holds the three IB-T006 benchmark
reports (report #0, in three arms). See `checklist.md` for the full session history
(three separate work sessions; two aborted attempts preserved under `aborted/`).

## 2026-07-11 — run observations

- **Rate calibration:** the canonical `chat-short` (8 rps) / `shared-prefix` (6 rps)
  workloads are sized for a GPU-class target; this host is 4 CPU cores. CPU-adapted rates
  (0.08 / 0.04 rps) were derived from direct single-stream/two-stream probes against the
  pinned engine before any measured run — see `logs/rate-calibration.log` for the raw probe
  output and the derivation arithmetic (target ~0.5 utilization against 2 slots).
- **EOS framing allowance:** llama-server 8f114a9 counts the stop token in
  `usage.completion_tokens` but emits no content delta for it, so the Scenario A integrity
  rule (`usage.completion_tokens == client content chunks`) needed one real-engine-specific
  allowance (chunks == usage−1 for EOS-stopped streams, chunks == usage for cap-stopped
  ones). Both populations are counted per run in `logs/checks.log`; no violations observed
  across 121 total pooled events.
- **Cancellation log-census discrepancy (not reproduced on retry):** the first cancellation
  run (06:19–06:22 UTC) had an unattributed extra `stop: cancel task` log line
  (`id_task=4134`, no matching `launch_slot_` entry). A same-configuration recheck this
  session (07:46–07:48 UTC, fresh `llama-server`, idle host) produced a clean 20-for-20
  match and all checks PASS. Both runs' engine-release timing was within the declared 2.5 s
  bound. Full details and both runs' evidence: `checklist.md` item 5,
  `raw/runs/cancel-mid-stream-cpu/` (final) vs.
  `raw/runs/cancel-mid-stream-cpu-attempt1/` + `logs/attempt1-cancel/` (original, preserved).
- **Failover in-flight-request boundary:** of 28 failover-workload requests, exactly 1
  errors — the request already accepted by llama.cpp at the instant of the SIGKILL. This is
  the expected, documented boundary of client-visible failover (a request already dispatched
  upstream cannot be transparently retried after acceptance); conservation is exact
  (6 pre-kill + 12 downtime + 9 post-restart + 1 in-flight-at-kill = 28).
- **Gateway-overhead diagnostic ran negative:** the via-gateway arm measured a *lower*
  pooled TTFT p50 than the engine-direct arm (−172.9 ms). Both arms ran minutes apart
  against their own fresh `llama-server` process on a shared 4-core host with llama-server
  alone observed up to ~398% of one core; the reports' threats-to-validity sections
  attribute the sign flip to CPU-contention noise between arms, not a real gateway
  speed-up, and explicitly state the run pair cannot resolve overhead below ~100 ms. The
  `<100 ms added` hypothesis is technically met (a negative delta is less than the bound)
  but this is not read as validating low overhead — see `checklist.md` item 4.
- **Cross-reference correction:** `scenarios/b/README.md` and a `pins/pins.yaml` note both
  cited the host-process-not-containers decision as "A-007"; the actual entry recording
  that decision in `docs/implementation-notes.md` is **D-004** (A-007 is the unrelated
  cancellation release-bound assumption). Corrected both references in this pass; no
  evidence artifact depended on the mislabeled cross-reference.
- **Schedule health:** max send slip across all timed runs stayed under 77 ms (well inside
  the watchdog); no run was invalidated on that basis.

## Deviations affecting this evidence

- **D-004 — Scenario B runs host processes, not containers** (registry/CDN egress still
  blocked, per D-002's precedent; a bridged container hop around a host-pinned engine buys
  no isolation on a 4-core measurement host). Binaries built read-only via `git archive
  <pinned commit>`; llama.cpp consumed prebuilt with commit + binary sha256 verified at
  build time; model pinned by file sha256.
- **A-007 / A-008 — reversible measurement-bound assumptions**, not external targets
  (cancellation release bound; calibration-derived SLO thresholds).
- Session interruptions (bug in original `run.sh` pid capture; a mid-run container freeze)
  produced two aborted attempts, both preserved under `aborted/` and excluded from every
  acceptance number.

Full deviation records: `docs/implementation-notes.md`.

## Defects filed upstream

None. The cancellation log-census discrepancy (above) is recorded as an open, unreproduced
observation, not a filed defect — a same-configuration recheck did not reproduce it.
