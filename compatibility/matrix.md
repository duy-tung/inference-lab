# Compatibility matrix — proven-together sets per integration milestone

Rules and format: [README.md](README.md). Ledger: `pins/pins.yaml`. Every row must cite
archived evidence; rows without evidence do not get written.

> Results are comparable only when model revision, quantization, tokenizer, engine
> version+flags, hardware, driver/CUDA, workload version+seed, and warm-up policy all match,
> or the difference is the single declared experimental variable.

**Status (2026-07-12):** I2 (Scenario A) row **ACCEPTED** (user review 2026-07-11, deviation
D-001 recorded). I3 (Scenario B) row **ACCEPTED** (user review 2026-07-11; open observation
on the cancellation-check item recorded, not blocking — see `evidence/i3/checklist.md`).
I4 (Scenario C) row recorded 2026-07-12 as a **CPU-FALLBACK DEVIATION**, not a GPU
acceptance: gate G6 (GPU session) was deferred by user decision 2026-07-11 (no GPU rental),
so the Scenario B pin set stands in as the measured baseline, supplemented by two sibling-repo
evidence sources (infergate IG-T005 cancellation evidence; inferbench IB-T010 E1
gateway-overhead comparison) cited by path+commit, not re-pinned — see
`evidence/i4/checklist.md` for the full item-by-item mapping and the explicit
deferred-GPU-evidence list (vLLM engine-metrics cancellation, GPU-scale overhead comparison,
vLLM-specific behaviors, GPU session manifest — none exist, none claimed). Full digests:
`pins/pins.yaml` + `evidence/i2/pins-snapshot.yaml` + `evidence/i3/pins-snapshot.yaml` +
`evidence/i4/pins-snapshot.yaml`.

| Milestone | Contracts | infergate image/binary | mock image/binary | inferbench | Engine | Model | inferops | fleetlab | Proven (date) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| I2 — Scenario A (local request path) | 8d81492 (v0.2.0 tag pending; v0.1.0 released) | infergate@5d69aeb, local build `sha256:a38a0aa6…` | infergate-mock@5d69aeb, local build `sha256:b74d4502…` | caa5074 (binary `sha256:b9f1a39c…`) | mock (deterministic; seed 42, ttft 300ms, itl 30ms) | mock-8b (mockengine@5d69aeb) | — | — | *ACCEPTED 2026-07-11 (user review; deviation D-001 recorded)* (evidence recorded 2026-07-10; D-001: no PostgreSQL usage write) | [`evidence/i2/`](../evidence/i2/checklist.md) |
| I3 — Scenario B (local inference, first real engine) | v0.2.0 (tag 484b449) | infergate@74f2372, **host binary** `sha256:ba79b99f…` (decision D-004: host processes, not containers) | infergate-mock@74f2372, host binary `sha256:aa262948…` | 69a5abc (binary `sha256:82e8abf6…`; same commit's analysis/report package via PYTHONPATH) | llama.cpp@8f114a9 (prebuilt, binary `sha256:af4e0118…`; `-np 2 -c 8192 -t 4 --metrics --slots`) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6…` | — | — | *ACCEPTED 2026-07-11 (user review; open observation on checklist item 5's cancellation log-census, not reproduced on retry)* | [`evidence/i3/`](../evidence/i3/checklist.md) |
| I4 — Scenario C (GPU inference) — **CPU-FALLBACK DEVIATION, GPU acceptance NOT claimed** | v0.2.0 (tag 484b449) — same bundle as I3 | infergate@74f2372, host binary `sha256:ba79b99f…` (same pin as I3; the IB-T010 overhead comparison below ran a later infergate@6827d8c, cited not pinned) | infergate-mock@74f2372, host binary `sha256:aa262948…` (same pin as I3) | 69a5abc (binary `sha256:82e8abf6…`; same pin as I3; the IB-T010 overhead comparison ran inferbench@6a3fb53, cited not pinned) | llama.cpp@8f114a9 (same pin as I3; **no vLLM pin exists**) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6…` (same pin as I3; **no GPU-class model pin exists**) | — | — | *CPU-FALLBACK DEVIATION recorded 2026-07-12 (G6 deferred by user decision 2026-07-11; no GPU rental). Streaming, cancellation (composed-stack arm), and failover = I3's own evidence; cancellation additionally corroborated by infergate IG-T005 (adapter-level, real llama-server, unpinned test model); gateway-overhead comparison = inferbench IB-T010 E1 — mock arm CONFIRMED (paired p95 +2.21 ms), llama.cpp arm INCONCLUSIVE at the ms scale (engine noise 2–3 orders of magnitude above the 10 ms bound). Deferred, not claimed: vLLM engine-metrics-verified cancellation, GPU-scale overhead comparison, vLLM-specific behaviors, GPU session manifest/auto-stop/budget.* | [`evidence/i4/`](../evidence/i4/checklist.md) |

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
- 2026-07-12 — Scenario C / I4: when GPU budget is approved and infergate `IG-T014` (vLLM
  adapter) + inferbench `IB-T011` (GPU experiment set) land, re-run Scenario C for real
  against vLLM per `scenarios/c/README.md`; that run supersedes this CPU-fallback row with a
  new dated evidence entry (ADR-0002 evidence immutability — this row is not deleted or
  rewritten, only superseded).
