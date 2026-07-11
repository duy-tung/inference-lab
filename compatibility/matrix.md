# Compatibility matrix — proven-together sets per integration milestone

Rules and format: [README.md](README.md). Ledger: `pins/pins.yaml`. Every row must cite
archived evidence; rows without evidence do not get written.

> Results are comparable only when model revision, quantization, tokenizer, engine
> version+flags, hardware, driver/CUDA, workload version+seed, and warm-up policy all match,
> or the difference is the single declared experimental variable.

**Status (2026-07-10):** first row recorded from the Scenario A / I2 run — **evidence
archived, acceptance review pending** (with the PostgreSQL usage-write deviation D-001);
"Proven" is claimed only after review. Full digests: `pins/pins.yaml` +
`evidence/i2/pins-snapshot.yaml`.

| Milestone | Contracts | infergate image | mock image | inferbench | Engine | Model | inferops | fleetlab | Proven (date) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| I2 — Scenario A (local request path) | 8d81492 (v0.2.0 tag pending; v0.1.0 released) | infergate@5d69aeb, local build `sha256:a38a0aa6…` | infergate-mock@5d69aeb, local build `sha256:b74d4502…` | caa5074 (binary `sha256:b9f1a39c…`) | mock (deterministic; seed 42, ttft 300ms, itl 30ms) | mock-8b (mockengine@5d69aeb) | — | — | *ACCEPTED 2026-07-11 (user review; deviation D-001 recorded)* (evidence recorded 2026-07-10; D-001: no PostgreSQL usage write) | [`evidence/i2/`](../evidence/i2/checklist.md) |

## Re-run trigger notes

- 2026-07-10 — Scenario A re-runs (and the I2 usage-write criterion executes for real) when
  infergate IG-T008 lands PostgreSQL usage accounting and a new gateway release is pinned
  (deviation D-001, `docs/implementation-notes.md`).
- 2026-07-10 — serving-contracts v0.2.0 tag pending: when tagged, re-validate the archived
  I2 artifacts against the released bundle and supersede the `contracts-bundle-prerelease`
  pin (expected no-op: 8d81492 is the tag candidate).
