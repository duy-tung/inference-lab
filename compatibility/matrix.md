# Compatibility matrix — proven-together sets per integration milestone

Rules and format: [README.md](README.md). Ledger: `pins/pins.yaml`. Every row must cite
archived evidence; rows without evidence do not get written.

> Results are comparable only when model revision, quantization, tokenizer, engine
> version+flags, hardware, driver/CUDA, workload version+seed, and warm-up policy all match,
> or the difference is the single declared experimental variable.

**Status (2026-07-11):** I2 (Scenario A) row **ACCEPTED** (user review 2026-07-11, deviation
D-001 recorded). I3 (Scenario B) row recorded from the executed run — **evidence archived,
acceptance review pending** (deviation on the cancellation-check item; see
`evidence/i3/checklist.md`); "Proven" is claimed only after review. Full digests:
`pins/pins.yaml` + `evidence/i2/pins-snapshot.yaml` + `evidence/i3/pins-snapshot.yaml`.

| Milestone | Contracts | infergate image/binary | mock image/binary | inferbench | Engine | Model | inferops | fleetlab | Proven (date) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| I2 — Scenario A (local request path) | 8d81492 (v0.2.0 tag pending; v0.1.0 released) | infergate@5d69aeb, local build `sha256:a38a0aa6…` | infergate-mock@5d69aeb, local build `sha256:b74d4502…` | caa5074 (binary `sha256:b9f1a39c…`) | mock (deterministic; seed 42, ttft 300ms, itl 30ms) | mock-8b (mockengine@5d69aeb) | — | — | *ACCEPTED 2026-07-11 (user review; deviation D-001 recorded)* (evidence recorded 2026-07-10; D-001: no PostgreSQL usage write) | [`evidence/i2/`](../evidence/i2/checklist.md) |
| I3 — Scenario B (local inference, first real engine) | v0.2.0 (tag 484b449) | infergate@74f2372, **host binary** `sha256:ba79b99f…` (decision D-004: host processes, not containers) | infergate-mock@74f2372, host binary `sha256:aa262948…` | 69a5abc (binary `sha256:82e8abf6…`; same commit's analysis/report package via PYTHONPATH) | llama.cpp@8f114a9 (prebuilt, binary `sha256:af4e0118…`; `-np 2 -c 8192 -t 4 --metrics --slots`) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6…` | — | — | *executed 2026-07-11; user acceptance review pending* (checklist item 5: cancellation release verified within bound on both runs, but a log-census invariant failed once and did not reproduce on retry — recorded as an open, unreproduced observation) | [`evidence/i3/`](../evidence/i3/checklist.md) |

## Re-run trigger notes

- 2026-07-10 — Scenario A re-runs (and the I2 usage-write criterion executes for real) when
  infergate IG-T008 lands PostgreSQL usage accounting and a new gateway release is pinned
  (deviation D-001, `docs/implementation-notes.md`).
- 2026-07-10 — serving-contracts v0.2.0 tag pending: when tagged, re-validate the archived
  I2 artifacts against the released bundle and supersede the `contracts-bundle-prerelease`
  pin (expected no-op: 8d81492 is the tag candidate).
- 2026-07-11 — Scenario B / I3: if the `cancel-llama` log-census discrepancy (checklist item
  5) recurs on a future run, escalate from "open observation" to a filed defect against
  either `scenarios/b/checks.py`'s counting assumption or llama-server's queued-cancel
  logging, and re-run the cancellation phase for confirmation.
