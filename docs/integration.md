# Integration Milestones — inference-lab's roles (I1–I8)

This repo **owns I2, I3, I4, I6, and I8**, and is the **evidence archivist for all of
I1–I8**. Common rules: every milestone runs against pinned released artifacts recorded in
`pins/pins.yaml`; evidence is archived under `evidence/i<N>/`; a milestone is "accepted" only
when its acceptance criteria are demonstrated **and reviewed**.

| Milestone | Owner | This repo's role | Scenario |
|---|---|---|---|
| I1 — Contract compatibility | serving-contracts | archive the four green consumer-CI links per bundle tag | — |
| I2 — Local request path | **inference-lab** | owner + evidence | A |
| I3 — Local inference | **inference-lab** | owner + evidence | B |
| I4 — GPU inference | **inference-lab** | owner + evidence | C |
| I5 — Operational stack | inferops | archive manifests, smoke outputs, dashboards, rolling-update log | D |
| I6 — Capacity feedback (central story) | **inference-lab** (loop) / fleetlab (recommendation) | loop owner + evidence | E |
| I7 — Failure campaign | inferops (execution) / inference-lab (evidence) | campaign matrix, postmortems, client-impact measurements | — |
| I8 — Portfolio release | **inference-lab** | owner: release, audit, narrative | — |

## I2 — Local request path (owner: inference-lab)

**Prereqs:** IG-T003, IB-T004, IL-T001; contracts v0.1.x.
**Pins:** contracts, infergate image, mock image, inferbench version.
**Acceptance:** `inferbench → infergate → mock backend` runs a seeded workload: 100 concurrent
streams, zero frame mixing; 3-point cancellation verified (mock abort observed within bound);
raw events schema-valid; client-vs-gateway TTFT agreement within declared tolerance;
traces/metrics visible (Scenario A includes PostgreSQL usage write + OTel).
**Failure handling:** frame mixing or cancellation leak → stop, fix in infergate, re-run;
measurement disagreement → check measurement-point definitions before touching code.
**Evidence:** run logs, raw-event files, trace export, acceptance checklist → `evidence/i2/`.

## I3 — Local inference (owner: inference-lab)

**Prereqs:** I2; IG-T005; IB-T006. **Pins:** + llama.cpp commit + GGUF model revision.
**Acceptance:** `inferbench → infergate → llama.cpp` completes `chat-short` and
`shared-prefix` workloads on CPU; first schema-valid benchmark report generated (manifest +
validity block); cancellation verified against llama.cpp; failover mock↔llama.cpp
demonstrated.
**Failure handling:** llama.cpp behavioral surprises → capability descriptor updated, adapter
fixed (in infergate); invalid report → G4 review before proceeding.
**Evidence:** benchmark report #0 (methodology shakedown), campaign logs → `evidence/i3/`.

## I4 — GPU inference (owner: inference-lab)

**Prereqs:** I3; IG-T014; G6 (hypothesis + manifest + auto-stop + budget alert); IB-T011
first session. **Pins:** + vLLM version/commit, model checkpoint + quantization, driver/CUDA,
instance type.
**Acceptance:** `inferbench → infergate → vLLM` on a rented GPU: streaming + cancellation
verified via engine metrics (KV usage / running-count drop within bound); gateway-overhead
comparison (direct vs via-gateway) measured with ≥3 runs/point; session auto-stopped; all
artifacts carry the full manifest.
**Failure handling:** engine metric-name drift → update capability mapping, re-verify; budget
trip → stop, record, fall back.
**CPU fallback:** documented deviation; the llama.cpp variant becomes the measured baseline.
**Evidence:** session log, GPU benchmark report, cancellation-verification metrics export →
`evidence/i4/`.

## I6 — Capacity feedback, the central story (owner: inference-lab for the loop; fleetlab for the recommendation)

**Prereqs:** I5; FL-T009; IO-T009; contracts v1.0.0 (SC-T010); benchmark corpus from
IB-T010/T011. **Pins:** everything above + fleetlab release.
**Acceptance:** benchmark results → fleetlab produces a schema-valid capacity recommendation
(with stated uncertainty) → inferops applies the recommended change (replica count / config)
→ repeated benchmark measures the outcome → predicted vs measured compared and published,
**including where the prediction was wrong**.
**Failure handling:** prediction badly off → that is a *result*, not a failure — publish the
error analysis and refine profiles; loop mechanics broken → fix Contract 7 plumbing.
**Evidence:** the loop report (recommendation file, applied manifests, before/after benchmark
results, error analysis) → `evidence/i6/`.

## I8 — Portfolio release (owner: inference-lab)

**Prereqs:** I1–I7 accepted; OSS minimum target met or contingency documented; IL-T009.
**Acceptance:** fresh-clone quickstart reproduces Scenario A in ≤15 minutes on a GPU-free
machine; demo script + recorded demo; benchmark report(s) and capacity report published with
validity blocks; failure-campaign evidence linked; OSS evidence (public links) recorded;
compatibility matrix current; reproducibility audit passed (a fresh session can re-derive
every headline claim from pinned artifacts); honest-limitations section published.
**Failure handling:** any headline claim that cannot be reproduced is removed or re-measured —
no exceptions.
**Evidence:** release tag of inference-lab + the audit checklist → `evidence/i8/`.

## Archiving duty for milestones owned elsewhere

| Milestone | Owner | This repo archives |
|---|---|---|
| I1 — Contract compatibility (all four consumers validate golden fixtures against the same bundle in CI; unsupported-field rejection covered; re-entrant per contract release; v1.0.0 re-run is an I6 prerequisite) | serving-contracts | the four green CI run links referencing the same bundle tag, linked in the pins file → `evidence/i1/` |
| I5 — Operational stack (deployment from released images only; warm-up-aware readiness; rolling update under load with zero client-visible errors; golden dashboards live; traces end-to-end) | inferops | manifests, smoke outputs, dashboard exports, rolling-update test log (IL-T005) → `evidence/i5/` |
| I7 — Failure campaign (all 12 fault scenarios injected — GPU-dependent ones may run on llama.cpp/mock with recorded deviation; expected semantics observed or deviation documented; client impact measured for scenarios 1, 2, 5, 6, 12; ≥2 postmortems) | inferops (execution), inference-lab (evidence) | campaign matrix, postmortems, client-impact measurements (IL-T007) → `evidence/i7/` + `postmortems/` |

## Re-run triggers

- **Every contract release re-runs I1** (I1 is re-entrant). Contract **MAJOR** release ⇒ I1
  must be re-run **before any scenario is re-claimed** at the new bundle version.
- A pin bump of any component invalidates the "proven together" claim of the affected matrix
  rows until the owning scenario is re-run (or the row is annotated as superseded).
- Contracts **v1.0.0 I1 re-run is a prerequisite for I6**.
- Fault-scenario contract changes ⇒ affected I7 campaign rows re-run before re-claiming.
- Re-run outcomes are new dated evidence entries; superseded evidence stays archived.
