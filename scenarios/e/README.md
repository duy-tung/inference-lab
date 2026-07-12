# Scenario E — Capacity feedback loop (THE central integration story)

```text
inferbench results → fleetlab → deployment recommendation → inferops → repeated benchmark
```

**As actually executed (2026-07-12, mock scale, applied 1→2 not the recommended 1→6):**
`inferbench (IB-T010, ib-t010-e2-{baseline,overload}-sane) → fleetlab (FL-T009, dd05e7d,
6-replica recommendation) → inferops (IO-T009, 89871a6, applied 1→2 replicas — a disclosed
compose-substrate scope reduction) → inferops's own re-measurement (not a fresh inferbench
run)`. See the Status line and `evidence/i6/checklist.md` §0 for the full, honest deviation
text — including the divergence at higher rates and the never-measured 6-replica figure.

- **Owning milestone:** I6 (owner: inference-lab for the loop; fleetlab for the
  recommendation). Task: IL-T006.
- **Status:** executed (2026-07-12) — evidence archived in
  [`evidence/i6/`](../../evidence/i6/checklist.md); **I6 acceptance review by the user is
  pending** (I2/I3/I5/I7 precedent). Inputs pinned in `pins/pins.yaml` (I6 pin set:
  `contracts-bundle-v1-0-0`, `fleetlab-bundle`,
  `fleetlab-recommendation-e2-admission-sane-v1-5x-scaleout`,
  `inferops-autoscaling-experiments`). **Headline honesty items:** (1) the applied change was
  **1→2** replicas, not the recommended 1→6 — a disclosed compose-substrate resource/time
  scope reduction (RQ-14 continuation); the 6-replica prediction itself was never measured,
  only extrapolated. (2) fleetlab's fitted 33.159 rps/replica figure is confirmed within +1.3%
  at its own fitted rate, but diverges at higher rates — leaning toward inferbench's own
  unpublished 37.925 rps/replica "overload-empirical" estimate, not the published fit. (3) the
  re-measurement is an independent replication, not a byte-identical comparability-rule-strict
  re-run of fleetlab's own training data (different gateway build, host, warm-up policy,
  repetition count, workload seed). (4) `inference_requests_in_flight` measured to beat
  fleetlab's recommended `inference_queue_depth` signal for this shallow-queue config — a real
  refinement, fed back but not yet filed upstream. Full detail: `evidence/i6/loop-report.md`.
- **Depends on:** I5 archived; fleetlab recommendation emitter (FL-T009, satisfied —
  commit `dd05e7d`); inferops autoscaling experiments (IO-T009, satisfied — commit `89871a6`);
  **contracts v1.0.0** (SC-T010, satisfied — tag `v1.0.0`, I1 re-run GREEN across all four
  consumers 2026-07-12); benchmark corpus (IB-T010/T011, satisfied — `ib-t010-e2-baseline-1x-sane`
  / `ib-t010-e2-overload-5x-sane`).
- **Never-cut:** the loop may shrink to mock/llama.cpp scale, **but it must close.** It shrank
  (mock scale, 1→2 instead of 1→6) and it closed.

## Purpose

Close the loop that makes the sentence *"I converted measurements into capacity decisions"*
demonstrable: real benchmark results go into fleetlab; fleetlab emits a schema-valid capacity
recommendation with stated uncertainty; inferops applies exactly that change; a repeated
benchmark measures the outcome; predicted vs measured is published — **including where the
prediction was wrong**. Prediction error is a result, not a failure.

## Components (all released artifacts / files, pinned in `pins/pins.yaml`)

| Component | Artifact | Pin entry (actual id) |
|---|---|---|
| Measurements | inferbench benchmark-result IDs `ib-t010-e2-baseline-1x-sane` / `ib-t010-e2-overload-5x-sane` (cited by fleetlab's own recommendation, not re-pinned here — same archiving pattern as I1/I5/I7) | `fleetlab-recommendation-e2-admission-sane-v1-5x-scaleout` |
| Recommender | fleetlab @ `dd05e7d` (FL-T009); recommendation file per **Contract 7** | `fleetlab-bundle`, `fleetlab-recommendation-e2-admission-sane-v1-5x-scaleout` |
| Applier | inferops @ `89871a6` (IO-T009 `f5fdd86`; applied 1→2, **not** the recommended 1→6) | `inferops-autoscaling-experiments` |
| Contracts | serving-contracts **v1.0.0** (tag `507208b`) | `contracts-bundle-v1-0-0` |
| Operated stack | infergate v0.1.0 release image (same digest as Scenario D/I5/I7) | `inferops-infergate-image`, `inferops-mock-backend-image` |

**Pinned 2026-07-12** (I6 pin set, `pins/pins.yaml`). No compose file or orchestration script
lives here: per the program's no-runtime-logic rule, the loop is assembled by citation — the
recommendation, the applied change, and the re-measurement are each produced in their owning
repo and archived here by path+commit+hash, never vendored or re-executed by this repo's own
tooling.

## Expected outcome — and what was actually produced

A published loop report under `evidence/i6/` containing: the recommendation file (with
uncertainty), the applied manifests, before/after benchmark results (same workload
version + seed, warm-up policy, repetition count), and the predicted-vs-measured error
analysis — honest about where the prediction missed. **Produced:**
[`evidence/i6/loop-report.md`](../../evidence/i6/loop-report.md) — with two disclosed
deviations from this exact expectation, stated plainly rather than elided: the applied change
was 1→2 replicas (not the recommended 1→6), and the "before/after benchmark results" are
inferops's own re-measurement (not a fresh `inferbench`-binary run against the same seed
fleetlab's `re_measurement` plan specified) — see `evidence/i6/loop-report.md` §3.1 for the
full comparability-rule audit.

## Actual invocation (as executed 2026-07-11/12)

```bash
# fleetlab (2026-07-11, commit dd05e7d):
fleetlab recommend --results ib-t010-e2-baseline-1x-sane,ib-t010-e2-overload-5x-sane \
  --slo ib-t010-e2-baseline --cost cost-g5-xlarge-ondemand
#   -> examples/recommendations/e2-admission-sane-v1-5x-scaleout.capacity-recommendation.json

# inferops (2026-07-12, commit 89871a6/f5fdd86) — applied 1->2, not the recommended 1->6:
bash experiments/autoscaling/run-scaling-demo.sh                       # 1->2 replica scale-out demo
bash experiments/autoscaling/run-scaling-demo-2replica-capacity.sh     # genuine saturating 2-replica capacity check
bash experiments/autoscaling/run-signal-comparison.sh                  # autoscaling-signal comparison (in_flight vs queue_depth)

# this repo (2026-07-12) — independent Contract 7 re-validation of the recommendation file:
python3 kit/contracts-validate.py validate --schema capacity-recommendation \
  /home/user/fleetlab/examples/recommendations/e2-admission-sane-v1-5x-scaleout.capacity-recommendation.json
  # run against BOTH the v0.2.0 vendored bundle and a live v1.0.0-tagged checkout -> PASS, PASS
```

## Acceptance checklist (mirrors I6 — executed copy: `evidence/i6/checklist.md`)

- [x] Contracts **v1.0.0** pinned; its **I1 re-run** green (prerequisite) and linked in pins.
- [x] Input benchmark results referenced by ID; workload version + seed, SLO, cost profile,
      hardware profiles frozen and recorded.
- [x] fleetlab recommendation file archived **before any change is applied**; it is
      **schema-valid against Contract 7** and carries: recommended topology (replica counts,
      engine config), predicted goodput/latency/cost **with stated uncertainty**, autoscaling
      signal + thresholds, assumptions + sensitivity notes.
- [~] inferops applied **exactly the recommended change** — **DEVIATION, disclosed**: applied
      1→2 replicas, not the recommended 1→6 (compose-substrate scope reduction); applied
      manifests/scripts cited by path+commit.
- [~] Repeated benchmark run under the comparability rule — **PARTIAL, disclosed**: admission
      and mock-timing flags matched exactly; gateway build, host, warm-up policy, repetition
      count, and workload seed identity did not match fleetlab's own `re_measurement` plan
      (independent replication, not an exact re-run).
- [x] **Predicted vs measured comparison published**, per metric, against the stated
      uncertainty band — **including where the prediction was wrong**; no cherry-picking;
      invalid runs invalidated with reasons, never dropped silently.
- [~] Error analysis feeds back: fleetlab profile-refinement notes recorded — **not yet filed
      upstream to fleetlab** (recorded as an open follow-up).
- [x] Evidence archived: recommendation file, applied manifests (cited), before/after results,
      error analysis (= the loop report), this checklist → `evidence/i6/`.
- [x] Pins updated (fleetlab bundle + recommendation, contracts v1.0.0, `proven_at: [I6]`);
      compatibility matrix row added.
- [ ] Reviewed (user acceptance) — **pending**, I2/I3/I5/I7 precedent.

## Failure handling

- Prediction badly off → **publish the error analysis** and refine profiles (fleetlab). That
  is the experiment working, not failing. **Exercised**: the fitted 33.159 rps/replica figure
  diverges at higher rates (§4.1 of the loop report) — published, not hidden, with refinement
  notes recorded (§5).
- Loop mechanics broken (schema mismatch, plumbing) → fix Contract 7 plumbing in the owning
  repo(s); this repo archives the failure and re-runs after the pin bump. **Exercised**: the
  recommendation's `engine_config.flags` empty-object gap (loop-report.md §2) is recorded as
  loop-mechanics feedback, not filed as a defect.
- Scale pressure → shrink the loop to mock/llama.cpp scale with a recorded deviation; never
  skip closing it. **Exercised**: applied 1→2 instead of 1→6, disclosed throughout, loop still
  closed.
