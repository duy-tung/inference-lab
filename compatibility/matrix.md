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
vLLM-specific behaviors, GPU session manifest — none exist, none claimed). I5 (Scenario D) row
recorded 2026-07-12, owner **inferops** (this repo archives per its evidence-archivist duty,
`docs/integration.md`): deployment from released images, warm-up-aware readiness, zero-error
rolling update, golden dashboards, and end-to-end traces all demonstrated on the inferops
compose stack — headline deviation **RQ-14 compose-pivot** (inferops cannot schedule any
Kubernetes pod in this sandbox; runtime is Docker Compose, manifests validated against a live
k3s API server, no pod scheduling claimed) plus the carried-forward I4/D-005 CPU-fallback (no
GPU node, no vLLM). **I5 acceptance review by the user is pending**, same as I2/I3 before it.
Full digests: `pins/pins.yaml` + `evidence/i2/pins-snapshot.yaml` +
`evidence/i3/pins-snapshot.yaml` + `evidence/i4/pins-snapshot.yaml` +
`evidence/i5/pins-snapshot.yaml`.

| Milestone | Contracts | infergate image/binary | mock image/binary | inferbench | Engine | Model | inferops | fleetlab | Proven (date) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| I2 — Scenario A (local request path) | 8d81492 (v0.2.0 tag pending; v0.1.0 released) | infergate@5d69aeb, local build `sha256:a38a0aa6…` | infergate-mock@5d69aeb, local build `sha256:b74d4502…` | caa5074 (binary `sha256:b9f1a39c…`) | mock (deterministic; seed 42, ttft 300ms, itl 30ms) | mock-8b (mockengine@5d69aeb) | — | — | *ACCEPTED 2026-07-11 (user review; deviation D-001 recorded)* (evidence recorded 2026-07-10; D-001: no PostgreSQL usage write) | [`evidence/i2/`](../evidence/i2/checklist.md) |
| I3 — Scenario B (local inference, first real engine) | v0.2.0 (tag 484b449) | infergate@74f2372, **host binary** `sha256:ba79b99f…` (decision D-004: host processes, not containers) | infergate-mock@74f2372, host binary `sha256:aa262948…` | 69a5abc (binary `sha256:82e8abf6…`; same commit's analysis/report package via PYTHONPATH) | llama.cpp@8f114a9 (prebuilt, binary `sha256:af4e0118…`; `-np 2 -c 8192 -t 4 --metrics --slots`) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6…` | — | — | *ACCEPTED 2026-07-11 (user review; open observation on checklist item 5's cancellation log-census, not reproduced on retry)* | [`evidence/i3/`](../evidence/i3/checklist.md) |
| I4 — Scenario C (GPU inference) — **CPU-FALLBACK DEVIATION, GPU acceptance NOT claimed** | v0.2.0 (tag 484b449) — same bundle as I3 | infergate@74f2372, host binary `sha256:ba79b99f…` (same pin as I3; the IB-T010 overhead comparison below ran a later infergate@6827d8c, cited not pinned) | infergate-mock@74f2372, host binary `sha256:aa262948…` (same pin as I3) | 69a5abc (binary `sha256:82e8abf6…`; same pin as I3; the IB-T010 overhead comparison ran inferbench@6a3fb53, cited not pinned) | llama.cpp@8f114a9 (same pin as I3; **no vLLM pin exists**) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6…` (same pin as I3; **no GPU-class model pin exists**) | — | — | *CPU-FALLBACK DEVIATION recorded 2026-07-12 (G6 deferred by user decision 2026-07-11; no GPU rental). Streaming, cancellation (composed-stack arm), and failover = I3's own evidence; cancellation additionally corroborated by infergate IG-T005 (adapter-level, real llama-server, unpinned test model); gateway-overhead comparison = inferbench IB-T010 E1 — mock arm CONFIRMED (paired p95 +2.21 ms), llama.cpp arm INCONCLUSIVE at the ms scale (engine noise 2–3 orders of magnitude above the 10 ms bound). Deferred, not claimed: vLLM engine-metrics-verified cancellation, GPU-scale overhead comparison, vLLM-specific behaviors, GPU session manifest/auto-stop/budget.* | [`evidence/i4/`](../evidence/i4/checklist.md) |
| I5 — Scenario D (operational stack) — **RQ-14 COMPOSE-PIVOT, no pod scheduling claimed; CPU-fallback continues I4/D-005, no vLLM/GPU** | v0.2.0 (tag 484b449, contracts referenced but not re-validated by this row — inferops runs infergate's own release, not this repo's scenario tooling) | infergate **v0.1.0 release** (commit 49236a3), `sha256:1971426b393b3e00b30cac0690d38b31667b5e34ebbeb6e111a54c369fb54c7e` — first genuine tagged-release image pin in the program | infergate-mock v0.1.0 (commit 49236a3), `sha256:d7df3d5609daa85adef6a07e4471c8bb90f5e2472f0bf3b32deb2fa9efb547e2` | — (no inferbench-driven load run this milestone; rolling-update/config-rollout load generated by inferops's own scripted clients) | llama.cpp@8f114a9 (same commit as I3/I4's engine-llamacpp, packaged as `infergate-llamacpp-engine:8f114a9` `sha256:43af71918dda78a1daaf19849e1c3cccfd7bad7c432b6c1420a45a62e99410be`; **no vLLM pin exists**) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6…` (same file as I3/I4, re-verified live this session) | inferops @ `db30279` (IO-T002…IO-T010); OTel Collector `0.112.0`, Prometheus `v2.55.1`, Grafana `11.3.1`, Tempo `2.6.1` (upstream digests); golden dashboard `inferops-golden` (11/11 Contract-2 names) | — | *RECORDED 2026-07-12 — **acceptance review pending** (I2/I3 precedent). Deployment-from-released-images: PASS (RQ-14 caveat on runtime substrate). Warm-up-aware readiness: PASS (5/5). Rolling update under load, zero client-visible errors: PASS (27 short + 3 stream requests, 0 errors; corroborated by drain-test 3/3 and config-rollout 0/24+0/4 dropped). Golden dashboards live: PASS (Grafana API + live panel query; extended this session to the llama.cpp backend). Traces end-to-end: PASS (mock-backed, IO-T003; extended this session with a fresh llama.cpp-backed trace, full span sequence, `evidence/i5/raw/demo-20260712T005146Z/`). No pod ever scheduled anywhere in this evidence (RQ-14); no GPU/vLLM claim (I4/D-005 continuation).* | [`evidence/i5/`](../evidence/i5/checklist.md) |

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
- 2026-07-12 — Scenario D / I5: if this sandbox's `CAP_SYS_RESOURCE` restriction is ever
  lifted, inferops re-runs `clusters/{local,gpu-node}/validate-k3s.sh` with a full k3s agent
  (strictly additive — no manifest changes expected) and this row is superseded with a new
  dated entry recording actual pod scheduling. Likewise, when GPU budget is approved and a
  real vLLM/GPU session runs on inferops's GPU-node profile, that run supersedes this row's
  CPU-fallback engine (same event that would supersede I4's row). Neither supersession deletes
  or rewrites this row (ADR-0002).
