# Compatibility matrix — proven-together sets per integration milestone

Rules and format: [README.md](README.md). Ledger: `pins/pins.yaml`. Every row must cite
archived evidence; rows without evidence do not get written.

> Results are comparable only when model revision, quantization, tokenizer, engine
> version+flags, hardware, driver/CUDA, workload version+seed, and warm-up policy all match,
> or the difference is the single declared experimental variable.

## Current component state (as of 2026-07-12, IL-T008 consistency pass / I8 audit)

Distinct from the per-milestone "proven together" rows below (which are, correctly, historical
and never rewritten — ADR-0002), this table answers "what does each component look like right
now": its latest tagged release (if any) vs. its latest commit (HEAD), so a reader can see how
far current `main` in each sibling repo has drifted from what was actually proven together. A
newer HEAD does **not** invalidate a milestone row's claim — the row's own pinned commit is what
was proven, and it stays proven at that commit forever.

| Component | Latest tagged release | Latest commit (HEAD, this repo's clone) | Milestones proven at |
|---|---|---|---|
| serving-contracts | `v1.0.0` (`507208b`) | `507208b` (release commit is HEAD) | I1, I6 (contracts-bundle-v1-0-0); I2 (contracts-bundle-prerelease); I3/I4 (contracts-bundle-v0-2-0) |
| infergate | `v0.1.0` (`49236a3`) | `f362ceb` (ADR-0001/0006/0007 finalization, 2026-07-11 — newer than the tagged release; no v0.2.0 tag yet) | I2 (`5d69aeb` local build); I3/I4 (`74f2372` host binary); I5/I7 (`49236a3`, the v0.1.0 release image) |
| inferbench | *(no tagged release yet — pinned by commit, same pattern as fleetlab/inferops)* | `62c2704` (G5 re-baseline decision recorded in benchmark report 1b) | I2 (`caa5074`); I3/I4 (`69a5abc`); I7 (`62c2704`, fault-campaign client) |
| fleetlab | *(no tagged release yet)* | `dd05e7d` (FL-T009 recommendation emitter + limitations report — this is also the I6 pin, i.e. HEAD = the proven commit) | I6 (`dd05e7d`) |
| inferops | *(no tagged release yet)* | `c695425` (IO-T008 runbooks — newer than the I5/I6/I7 pins) | I5 (`db30279`); I6 (`89871a6`); I7 (`a07fd2f`) |

No component pin recorded above is stale relative to a claim being made: every "proven
together" row cites the exact commit/digest used for that milestone's evidence, and none of
the newer HEADs shown here have been re-run through any scenario. Re-run triggers for when a
newer HEAD *should* supersede a row are listed under "Re-run trigger notes" below.

**Status (2026-07-12):** I1 (Contract compatibility) row **ARCHIVED** (evidence-archivist duty;
first independently cross-checked I1 snapshot in this repo — see `evidence/i1/checklist.md`).
I2 (Scenario A) row **ACCEPTED** (user review 2026-07-11, deviation
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
I7 (failure campaign) row recorded 2026-07-12, owner **inferops** (execution) / **inference-lab**
(evidence, `docs/integration.md`): all 12 Contract 6 fault scenarios injected against the
same I5 CPU-fallback stack (no new pins — same released infergate/mock images, same llama.cpp
engine/model). 11/12 verdicts matched expected semantics (6 fully clean; 5 matched-with-documented-deviation,
of which scenario 6 is an expected non-defect discrepancy and 1/3/7/10 carry the documented structural
single-backend-topology deviation, and **1/12 (scenario 4, slow client) is a real,
reproducible deviation-documented finding** — surfaced prominently in the checklist and as the
lead postmortem, never folded silently into the "mostly clean" summary. Client impact measured
by inferbench for all 5 mandated streaming-critical scenarios (1, 2, 5, 6, 12); 3 postmortems
published. **I7 acceptance review by the user is pending**, same as I2/I3/I5 before it.
I6 (capacity feedback loop, the central story) row recorded 2026-07-12, owner
**inference-lab** (loop) / **fleetlab** (recommendation), applied+re-measured by **inferops**:
fleetlab's FL-T009 recommendation (6 replicas, fitted 33.159±1.105 rps/replica, predicted
goodput `[165.279, 189.036]` rps) archived before any change, schema-valid against Contract 7
(independently re-validated this session against both v0.2.0 and the newly-frozen v1.0.0
bundle — PASS both). inferops's IO-T009 applied a **1→2** replica change, **not** the
recommended 1→6 (a disclosed compose-substrate scope reduction) and re-measured. Predicted vs
measured published honestly: the fitted 33.159 rps/replica figure **confirmed within +1.3%**
at its own fitted rate; at every higher rate measured, the result leans toward inferbench's own
unpublished "overload-empirical" 37.925 rps/replica estimate (1–5% off) over the published fit
(9–13% off) — resolving, not contradicting, the open question fleetlab's own G8 holdout report
already flagged unresolved. **The 6-replica recommendation itself was never measured**
(extrapolation only, stated as such throughout). A measured refinement:
`inference_requests_in_flight` beat fleetlab's recommended `inference_queue_depth` signal for
this shallow-queue config. Contracts **v1.0.0** (SC-T010) pinned as the I6 prerequisite, I1
re-run GREEN across all four consumers 2026-07-12. **I6 acceptance review by the user is
pending**, same as I2/I3/I5/I7 before it.
I8 (portfolio release) row assembled 2026-07-12: the full frozen release set as of this
release, summarizing every row above — no new component pin. Reproducibility audit PASS
(`evidence/i8/reproducibility-audit.md`): 2 headline claims narrowed (cancellation scope on
the real llama.cpp engine; gate-G5 "pass" restated as a re-framed-criterion pass after the
original ≤20% ratio target was REFUTED twice), 2 process gaps fixed in this same release
(`evidence/i1/` and `reports/` were both empty/missing before I8), 0 claims removed outright.
**I8 acceptance review by the user is pending**, same as I1/I2/I3/I5/I6/I7 before it.
Full digests: `pins/pins.yaml` + `evidence/i1/checklist.md` + `evidence/i2/pins-snapshot.yaml` +
`evidence/i3/pins-snapshot.yaml` + `evidence/i4/pins-snapshot.yaml` +
`evidence/i5/pins-snapshot.yaml` + `evidence/i6/pins-snapshot.yaml` +
`evidence/i7/pins-snapshot.yaml` + `evidence/i8/reproducibility-audit.md` (I8 introduces no
new component pin — it is the release checkpoint over the set already recorded above).

| Milestone | Contracts | infergate image/binary | mock image/binary | inferbench | Engine | Model | inferops | fleetlab | Proven (date) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| I1 — Contract compatibility (owner: serving-contracts; archived here per evidence-archivist duty) — **no scenario runs; consumer-CI cross-check only** | **v1.0.0** (tag `507208b`) | pinned `v0.2.0`/`484b449` at time of re-check (consumer's own recorded pin string) | pinned `v0.2.0`/`484b449` at time of re-check | pinned `v0.2.0`/`484b449` at time of re-check | — | — | pinned `v0.2.0` at time of re-check | pinned `v0.2.0`/`484b449` (vendored) at time of re-check | *ARCHIVED 2026-07-12 (IL-T008 — first independently cross-checked I1 snapshot in this repo; re-entrant, re-runs every release). All four consumers GREEN validating their own emitted artifacts (not only fixtures) against the frozen v1.0.0 bundle: infergate 2/2 deployment-contract + 2/2 backend-capability; inferbench 29/29 benchmark-run + 29/29 raw-event + 6/6 workload + 3/3 slo + 9/9 benchmark-result; fleetlab 1/1 capacity-recommendation + 1/1 slo; inferops 6/6 live-gateway-smoke fixtures. Kit selftest 52/52 positives, 29/29 negatives, GREEN. No consumer needed a change to stay green.* | [`evidence/i1/`](../evidence/i1/checklist.md) |
| I2 — Scenario A (local request path) | 8d81492 (v0.2.0 tag pending; v0.1.0 released) | infergate@5d69aeb, local build `sha256:a38a0aa6…` | infergate-mock@5d69aeb, local build `sha256:b74d4502…` | caa5074 (binary `sha256:b9f1a39c…`) | mock (deterministic; seed 42, ttft 300ms, itl 30ms) | mock-8b (mockengine@5d69aeb) | — | — | *ACCEPTED 2026-07-11 (user review; deviation D-001 recorded)* (evidence recorded 2026-07-10; D-001: no PostgreSQL usage write) | [`evidence/i2/`](../evidence/i2/checklist.md) |
| I3 — Scenario B (local inference, first real engine) | v0.2.0 (tag 484b449) | infergate@74f2372, **host binary** `sha256:ba79b99f…` (decision D-004: host processes, not containers) | infergate-mock@74f2372, host binary `sha256:aa262948…` | 69a5abc (binary `sha256:82e8abf6…`; same commit's analysis/report package via PYTHONPATH) | llama.cpp@8f114a9 (prebuilt, binary `sha256:af4e0118…`; `-np 2 -c 8192 -t 4 --metrics --slots`) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6…` | — | — | *ACCEPTED 2026-07-11 (user review; open observation on checklist item 5's cancellation log-census, not reproduced on retry)* | [`evidence/i3/`](../evidence/i3/checklist.md) |
| I4 — Scenario C (GPU inference) — **CPU-FALLBACK DEVIATION, GPU acceptance NOT claimed** | v0.2.0 (tag 484b449) — same bundle as I3 | infergate@74f2372, host binary `sha256:ba79b99f…` (same pin as I3; the IB-T010 overhead comparison below ran a later infergate@6827d8c, cited not pinned) | infergate-mock@74f2372, host binary `sha256:aa262948…` (same pin as I3) | 69a5abc (binary `sha256:82e8abf6…`; same pin as I3; the IB-T010 overhead comparison ran inferbench@6a3fb53, cited not pinned) | llama.cpp@8f114a9 (same pin as I3; **no vLLM pin exists**) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6…` (same pin as I3; **no GPU-class model pin exists**) | — | — | *CPU-FALLBACK DEVIATION recorded 2026-07-12 (G6 deferred by user decision 2026-07-11; no GPU rental). Streaming, cancellation (composed-stack arm), and failover = I3's own evidence; cancellation additionally corroborated by infergate IG-T005 (adapter-level, real llama-server, unpinned test model); gateway-overhead comparison = inferbench IB-T010 E1 — mock arm CONFIRMED (paired p95 +2.21 ms), llama.cpp arm INCONCLUSIVE at the ms scale (engine noise 2–3 orders of magnitude above the 10 ms bound). Deferred, not claimed: vLLM engine-metrics-verified cancellation, GPU-scale overhead comparison, vLLM-specific behaviors, GPU session manifest/auto-stop/budget.* | [`evidence/i4/`](../evidence/i4/checklist.md) |
| I5 — Scenario D (operational stack) — **RQ-14 COMPOSE-PIVOT, no pod scheduling claimed; CPU-fallback continues I4/D-005, no vLLM/GPU** | v0.2.0 (tag 484b449, contracts referenced but not re-validated by this row — inferops runs infergate's own release, not this repo's scenario tooling) | infergate **v0.1.0 release** (commit 49236a3), `sha256:1971426b393b3e00b30cac0690d38b31667b5e34ebbeb6e111a54c369fb54c7e` — first genuine tagged-release image pin in the program | infergate-mock v0.1.0 (commit 49236a3), `sha256:d7df3d5609daa85adef6a07e4471c8bb90f5e2472f0bf3b32deb2fa9efb547e2` | — (no inferbench-driven load run this milestone; rolling-update/config-rollout load generated by inferops's own scripted clients) | llama.cpp@8f114a9 (same commit as I3/I4's engine-llamacpp, packaged as `infergate-llamacpp-engine:8f114a9` `sha256:43af71918dda78a1daaf19849e1c3cccfd7bad7c432b6c1420a45a62e99410be`; **no vLLM pin exists**) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6…` (same file as I3/I4, re-verified live this session) | inferops @ `db30279` (IO-T002…IO-T010); OTel Collector `0.112.0`, Prometheus `v2.55.1`, Grafana `11.3.1`, Tempo `2.6.1` (upstream digests); golden dashboard `inferops-golden` (11/11 Contract-2 names) | — | *RECORDED 2026-07-12 — **acceptance review pending** (I2/I3 precedent). Deployment-from-released-images: PASS (RQ-14 caveat on runtime substrate). Warm-up-aware readiness: PASS (5/5). Rolling update under load, zero client-visible errors: PASS (27 short + 3 stream requests, 0 errors; corroborated by drain-test 3/3 and config-rollout 0/24+0/4 dropped). Golden dashboards live: PASS (Grafana API + live panel query; extended this session to the llama.cpp backend). Traces end-to-end: PASS (mock-backed, IO-T003; extended this session with a fresh llama.cpp-backed trace, full span sequence, `evidence/i5/raw/demo-20260712T005146Z/`). No pod ever scheduled anywhere in this evidence (RQ-14); no GPU/vLLM claim (I4/D-005 continuation).* | [`evidence/i5/`](../evidence/i5/checklist.md) |
| I7 — Failure campaign (12 Contract 6 fault scenarios) — **no new pins; same I5 CPU-fallback stack, no vLLM/GPU** | v0.2.0 (tag 484b449, referenced by the fixed fault-scenario fixtures, not re-validated by this row) | infergate **v0.1.0 release** (commit 49236a3), same digest as I5 — every ad hoc fault-campaign instance (`gateway-faults`, `gateway-faults-a/-b`) plus the main compose gateway (scenario 9) | infergate-mock v0.1.0 (commit 49236a3), same digest as I5 — backs 10 of the 12 scenarios | `inferbench` commit `62c2704997e6c8a2966307ee3d8dbfd16747b631` (host build; no digest recorded — see `evidence/i7/pins-snapshot.yaml`) | mock (10/12 scenarios) + llama.cpp@8f114a9 (scenario 8, config reload — same commit as I3/I4/I5; **no vLLM pin exists**) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6…` (scenario 8 only, same file as I3/I4/I5) | inferops @ `a07fd2f` (IO-T006 `bfca054` + IO-T007 `a1e0af5`, the 12-scenario fault campaign) | — | *RECORDED 2026-07-12 — **acceptance review pending** (I2/I3/I5 precedent). All 12/12 scenarios injected: PASS. Expected semantics observed or deviation documented, per scenario: PASS — 11/12 matched (6 fully clean + 5 matched-with-documented-deviation: 1/3/7/10 single-backend structural, 6 expected non-defect discrepancy), **1/12 (scenario 4) deviation-documented as a real, reproducible finding — surfaced, not buried**. Client impact measured by inferbench for scenarios 1, 2, 5, 6, 12: PASS (0 scope reduction). ≥2 postmortems published: PASS, 3 published (pm-001 scenario 4, pm-002 scenario 2, pm-003 scenario 9). No GPU/vLLM claim (I4/D-005, I5/D-006 continuation).* | [`evidence/i7/`](../evidence/i7/checklist.md) |
| I6 — Capacity feedback loop (Scenario E, the central story) — **applied 1→2, NOT the recommended 1→6; entirely mock-backend scale** | **v1.0.0** (tag `507208b`, the I6 prerequisite — SC-T010 freeze; I1 re-run GREEN across all 4 consumers 2026-07-12; Contract 7 unchanged by the freeze, independently re-validated this session) | infergate **v0.1.0 release** (commit 49236a3), same digest as I5/I7 — runs the IO-T009 gateway instances (`gateway-signals`, `gateway-signals-2`) | infergate-mock v0.1.0 (commit 49236a3), same digest as I5/I7 | `fleetlab-recommendation-e2-admission-sane-v1-5x-scaleout` fit from `ib-t010-e2-baseline-1x-sane`/`ib-t010-e2-overload-5x-sane` (inferbench IB-T010, cited not re-pinned here); re-measured by inferops's own IO-T009 client, not a fresh `inferbench` run | mock (`gateway-mock-admission-sane-v1`) — **no llama.cpp/vLLM/GPU involvement in this loop** (fleetlab's own FL-T004 loop-mechanics scope decision) | mock-8b | inferops @ `89871a6` (IO-T009 `f5fdd86` — signal-comparison, scaling-demo, 2-replica-capacity-check) | fleetlab @ `dd05e7d` (FL-T009 — recommendation emitter) | *RECORDED 2026-07-12 — **acceptance review pending** (I2/I3/I5/I7 precedent). Recommendation archived before any change, schema-valid against Contract 7: PASS (independently re-validated against v0.2.0 AND v1.0.0). Applied change: **DEVIATION** — 1→2 replicas applied, not the recommended 1→6 (disclosed compose-substrate scope reduction, RQ-14 continuation). Repeated benchmark under the comparability rule: **PARTIAL** — admission/mock flags matched exactly; gateway build, host, warm-up policy, repetition count, and workload seed identity did not match fleetlab's own `re_measurement` plan (independent replication, not an exact re-run — see `evidence/i6/loop-report.md` §3.1). Predicted vs measured published including where wrong: PASS — 33.159 rps/replica confirmed within +1.3% at its own fitted rate; at higher rates the measurement leans toward inferbench's own unpublished 37.925 rps/replica estimate, not the published fit; **the 6-replica prediction itself was never measured** (extrapolation only). Refinement: `in_flight` beat the recommended `queue_depth` signal for this config. No GPU/vLLM claim anywhere in this loop.* | [`evidence/i6/`](../evidence/i6/checklist.md) |
| I8 — Portfolio release — **the full frozen release set; no new component pin, this row summarizes what's already proven above** | **v1.0.0** (tag `507208b`, same as I6) | infergate **v0.1.0 release** (commit 49236a3, same as I5/I6/I7) | infergate-mock v0.1.0 (commit 49236a3, same as I5/I6/I7) | commit-pinned, no tagged release yet (same as I3/I4/I7 rows above) | llama.cpp@8f114a9 (I3/I4/I5/I7 baseline; **no vLLM/GPU pin exists anywhere in this file**) | Qwen2.5-1.5B-Instruct GGUF Q4_K_M (same file, all rows) | inferops @ `89871a6`/`a07fd2f` (I6/I7) | fleetlab @ `dd05e7d` (I6) | *ASSEMBLED 2026-07-12 — **acceptance review pending** (I2/I3/I5/I6/I7 precedent). Quickstart timed 2m08s + 35s, both PASS (`quickstart/timing-log.md`). Demo script + real captured transcript (no video recorded). Benchmark + capacity reports linked with validity blocks (`reports/`). Failure-campaign evidence linked (`evidence/i7/`). OSS evidence recorded per the documented contingency — local build + reproduction real, upstream comment drafted not posted, user-gated (`oss/log.md`). Compatibility matrix current (this row + the I1 row above, both new this release). Reproducibility audit PASS: 2 claims narrowed (cancellation scope on the real engine; gate-G5 pass restated as re-framed-criterion pass), 2 process gaps fixed (`evidence/i1/`, `reports/`), 0 claims removed outright — `evidence/i8/reproducibility-audit.md`. Honest-limitations statement published (`portfolio/limitations.md`).* | [`evidence/i8/`](../evidence/i8/reproducibility-audit.md) |

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
- 2026-07-12 — Failure campaign / I7: when infergate ships a fix for the scenario 4
  (slow-client write-deadline) finding (`postmortems/pm-001.md` §5), re-run Contract 6
  scenario 4 to confirm the deadline now observably fires; that run supersedes only scenario
  4's row-cell content with a new dated evidence entry (ADR-0002 — this row is not deleted or
  rewritten). Likewise, when infergate `IG-T012` (N-backend routing) lands CLI/config exposure
  for N>1 backends, re-run scenarios 1, 3, 7, 10 for a fully faithful reproduction of their
  routing-shift clauses. When a real GPU/vLLM session supersedes I4/I5 (above), a
  corresponding I7 re-run against that stack supersedes this row's CPU-fallback claim too.
- 2026-07-12 — Capacity feedback loop / I6: **the 6-replica recommendation itself remains
  untested — the highest-priority re-run trigger in this matrix.** When a real Kubernetes
  scheduler becomes available in this environment (RQ-14 resolution) or a larger
  compose-substrate budget is approved, re-run inferops's IO-T009 at the full 1→6 replica scale
  fleetlab actually recommended, using fleetlab's own `re_measurement` plan (workload
  `ib-t010-e2-overload@1.0.0`, seed `10010201`) for a strict comparability-rule-compliant
  re-run rather than this row's independent replication; that run supersedes this row with a
  new dated evidence entry (ADR-0002 — this row is not deleted or rewritten). Separately, when
  fleetlab acts on the profile-refinement notes filed at `evidence/i6/loop-report.md` §5 (the
  capacity-estimate preference at higher rates, the `in_flight`-over-`queue_depth` signal
  preference, the `engine_config.flags` Contract 7 plumbing gap), a new FL-T009 recommendation
  supersedes the one this row cites. When any consumer re-pins to `serving-contracts@v1.0.0`
  for real (all four still record `v0.2.0`/`484b449` as of this row), update this row's
  Contracts cell accordingly — no re-run is required since Contract 7 content is unchanged.
