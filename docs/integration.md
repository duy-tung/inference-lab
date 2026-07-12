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
**Status (2026-07-10):** executed (IL-T002) — evidence archived (`evidence/i2/checklist.md`:
all executed criteria PASS); the PostgreSQL usage-write criterion is a documented deviation
(D-001, re-run when IG-T008 lands); **acceptance review pending**.

## I3 — Local inference (owner: inference-lab)

**Prereqs:** I2; IG-T005; IB-T006. **Pins:** + llama.cpp commit + GGUF model revision.
**Acceptance:** `inferbench → infergate → llama.cpp` completes `chat-short` and
`shared-prefix` workloads on CPU; first schema-valid benchmark report generated (manifest +
validity block); cancellation verified against llama.cpp; failover mock↔llama.cpp
demonstrated.
**Failure handling:** llama.cpp behavioral surprises → capability descriptor updated, adapter
fixed (in infergate); invalid report → G4 review before proceeding.
**Evidence:** benchmark report #0 (methodology shakedown), campaign logs → `evidence/i3/`.
**Status (2026-07-11):** **ACCEPTED** by user review; `evidence/i3/checklist.md` all
executed criteria PASS, one open (unreproduced) observation on the cancellation log-census
check, not blocking acceptance.

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
**Status (2026-07-12):** **CPU-fallback deviation recorded (D-005); GPU acceptance NOT
claimed.** Gate G6 deferred by user decision 2026-07-11 (no GPU rental); infergate `IG-T014`
and inferbench `IB-T011` remain not started/not executed as verified this session. The
llama.cpp baseline proven at I3 stands in, supplemented by infergate IG-T005 (adapter-level
cancellation vs. a real `llama-server`) and inferbench IB-T010 E1 (gateway-overhead
comparison — mock arm CONFIRMED, llama.cpp arm INCONCLUSIVE at the ms scale, reported
honestly) — assembled from already-published evidence, not newly measured. Deferred and NOT
claimed: vLLM engine-metrics-verified cancellation, GPU-scale overhead comparison,
vLLM-specific behaviors, GPU session manifest/auto-stop/budget. Full mapping:
`evidence/i4/checklist.md`.

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

**Status (2026-07-12):** I6 evidence archived (`evidence/i6/checklist.md`): the loop closes.
fleetlab's FL-T009 recommendation (commit `dd05e7d`) archived before any change and
independently re-validated this session against Contract 7 in both the v0.2.0 bundle and the
newly-frozen **v1.0.0** bundle (PASS both — Contract 7 is unchanged by the freeze). inferops's
IO-T009 (commit `89871a6`) applied a **1→2** replica change — **not** the recommended 1→6, a
disclosed compose-substrate scope reduction (RQ-14 continuation) — and re-measured.
Predicted-vs-measured published honestly: the fitted 33.159 rps/replica figure confirmed
within +1.3% at its own fitted rate; at higher rates the measurement leans toward inferbench's
own unpublished 37.925 rps/replica estimate over the published fit, resolving the open question
fleetlab's own G8 holdout report already flagged unresolved; **the 6-replica recommendation
itself was never measured** (extrapolation only, stated as such); a measured refinement
(`in_flight` beats the recommended `queue_depth` signal for this config) recorded and fed back.
Contracts v1.0.0 (SC-T010) pinned as the I6 prerequisite, I1 re-run GREEN across all four
consumers. **I6 acceptance review by the user is pending**, same as I2/I3/I5/I7 before it.

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

**Status (2026-07-12):** I8 assembled — quickstart timed twice (2m08s, 35s), both PASS against
the 15-minute target (`quickstart/timing-log.md`); demo script + a real captured transcript
(`portfolio/demo-script.md`, `portfolio/demo-transcript.md`) — no video recording exists, and
the video *script* is labeled as a script, not a claimed recording; `reports/benchmark-report-1.md`,
`reports/benchmark-report-1b.md`, `reports/capacity-report.md`, and `evidence/i6/loop-report.md`
linked from the landing page with validity blocks; `evidence/i7/campaign-matrix.md` +
`postmortems/` linked; OSS evidence recorded per the documented contingency (local build +
reproduction real; upstream comment drafted, not posted, user-gated — `oss/log.md`); compatibility
matrix current (IL-T008 consistency pass, `evidence/i1/` archived for the first time);
reproducibility audit **PASS** (`evidence/i8/reproducibility-audit.md`) — 2 claims narrowed
(cancellation scope, gate-G5 framing), 2 process gaps fixed (`evidence/i1/`, `reports/`), 0
claims removed outright; honest-limitations section published (`portfolio/limitations.md`).
**I8 acceptance review by the user is pending**, same precedent as every prior milestone in
this program.

## Archiving duty for milestones owned elsewhere

| Milestone | Owner | This repo archives |
|---|---|---|
| I1 — Contract compatibility (all four consumers validate golden fixtures against the same bundle in CI; unsupported-field rejection covered; re-entrant per contract release; v1.0.0 re-run is an I6 prerequisite) | serving-contracts | the four green CI run links referencing the same bundle tag, linked in the pins file → `evidence/i1/` |
| I5 — Operational stack (deployment from released images only; warm-up-aware readiness; rolling update under load with zero client-visible errors; golden dashboards live; traces end-to-end) | inferops | manifests, smoke outputs, dashboard exports, rolling-update test log (IL-T005) → `evidence/i5/` |
| I7 — Failure campaign (all 12 fault scenarios injected — GPU-dependent ones may run on llama.cpp/mock with recorded deviation; expected semantics observed or deviation documented; client impact measured for scenarios 1, 2, 5, 6, 12; ≥2 postmortems) | inferops (execution), inference-lab (evidence) | campaign matrix, postmortems, client-impact measurements (IL-T007) → `evidence/i7/` + `postmortems/` |

**Status (2026-07-12):** I5 evidence archived (`evidence/i5/checklist.md`): all five acceptance
criteria demonstrated on the inferops operational stack (commit `db30279`) — deployment from
released images only, warm-up-aware readiness, zero-error rolling update, golden dashboards
live, traces end-to-end (mock-backed, plus a fresh llama.cpp-backed trace generated this
session). Headline deviation: RQ-14 compose-pivot (inferops cannot schedule any Kubernetes pod
in this sandbox; runtime is Docker Compose, manifests validated against a live k3s API server —
no pod scheduling claimed); GPU node continues I4's CPU-fallback (D-005: no vLLM, no GPU).
**I5 acceptance review by the user is pending**, same as I2/I3 before it.

**Status (2026-07-12):** I7 evidence archived (`evidence/i7/checklist.md`): all 12 Contract 6
fault scenarios injected against the inferops 12-scenario campaign (commits `bfca054`/`a1e0af5`/
`a07fd2f`) — 11/12 verdicts matched expected semantics (6 fully clean + 5 matched-with-documented-deviation: scenarios 1, 3, 7, 10
overlap) matched with a documented structural single-backend-topology deviation, and **1/12
(scenario 4, slow client) is a real, reproducible deviation-documented finding, surfaced
prominently rather than buried** in the checklist and as the lead postmortem. Client impact
measured by inferbench for all 5 mandated streaming-critical scenarios (1, 2, 5, 6, 12); 3
postmortems published (`postmortems/pm-001..pm-003.md`), exceeding the ≥2 minimum. No GPU/vLLM
claim anywhere — continuation of I4/D-005 and I5/D-006. **I7 acceptance review by the user is
pending**, same as I2/I3/I5 before it.

## Re-run triggers

- **Every contract release re-runs I1** (I1 is re-entrant). Contract **MAJOR** release ⇒ I1
  must be re-run **before any scenario is re-claimed** at the new bundle version.
- A pin bump of any component invalidates the "proven together" claim of the affected matrix
  rows until the owning scenario is re-run (or the row is annotated as superseded).
- Contracts **v1.0.0 I1 re-run is a prerequisite for I6**.
- Fault-scenario contract changes ⇒ affected I7 campaign rows re-run before re-claiming.
- Re-run outcomes are new dated evidence entries; superseded evidence stays archived.
