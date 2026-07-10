# Scenario E — Capacity feedback loop (THE central integration story)

```text
inferbench results → fleetlab → deployment recommendation → inferops → repeated benchmark
```

- **Owning milestone:** I6 (owner: inference-lab for the loop; fleetlab for the
  recommendation). Task: IL-T006.
- **Status:** defined (2026-07-10). Loop orchestration script arrives with IL-T006; inputs
  unpinned.
- **Depends on:** I5 archived; fleetlab recommendation emitter (FL-T009); inferops
  autoscaling experiments (IO-T009); **contracts v1.0.0** (SC-T010) with its I1 re-run;
  benchmark corpus (IB-T010/T011).
- **Never-cut:** the loop may shrink to mock/llama.cpp scale, **but it must close.**

## Purpose

Close the loop that makes the sentence *"I converted measurements into capacity decisions"*
demonstrable: real benchmark results go into fleetlab; fleetlab emits a schema-valid capacity
recommendation with stated uncertainty; inferops applies exactly that change; a repeated
benchmark measures the outcome; predicted vs measured is published — **including where the
prediction was wrong**. Prediction error is a result, not a failure.

## Components (all released artifacts / files, pinned in `pins/pins.yaml`)

| Component | Artifact | Pin entry (expected id) |
|---|---|---|
| Measurements | inferbench benchmark-result files (Contract 3), by result ID | `inferbench-binary` + result IDs in the loop report |
| Recommender | fleetlab release; recommendation file per **Contract 7** | `fleetlab-release` |
| Applier | inferops release (applies replica/config change) | `inferops-bundle` |
| Contracts | serving-contracts **v1.0.0** | `contracts-bundle` |
| Operated stack | everything pinned at Scenario D | (carried over) |

**Pinned inputs: currently none — everything unpinned as of 2026-07-10.**

## Expected outcome

A published loop report under `evidence/i6/` containing: the recommendation file (with
uncertainty), the applied manifests, before/after benchmark results (same workload
version + seed, warm-up policy, repetition count), and the predicted-vs-measured error
analysis — honest about where the prediction missed.

## Indicative invocation (executed at IL-T006, not before)

```bash
fleetlab recommend --results <benchmark-result-ids> --slo <slo> --cost <profile>
# inferops applies the recommended replica/config change per runbook
inferbench run --workload <same version+seed> --target <operated stack>   # re-benchmark
# loop orchestration script assembles the loop report from the four artifacts
```

## Acceptance checklist (mirrors I6 — executed copy goes to `evidence/i6/checklist.md`)

- [ ] Contracts **v1.0.0** pinned; its **I1 re-run** green (prerequisite) and linked in pins.
- [ ] Input benchmark results referenced by ID; workload version + seed, SLO, cost profile,
      hardware profiles frozen and recorded.
- [ ] fleetlab recommendation file archived **before any change is applied**; it is
      **schema-valid against Contract 7** and carries: recommended topology (replica counts,
      engine config), predicted goodput/latency/cost **with stated uncertainty**, autoscaling
      signal + thresholds, assumptions + sensitivity notes.
- [ ] inferops applied **exactly the recommended change**; applied manifests archived.
- [ ] Repeated benchmark run under the comparability rule (single declared variable = the
      applied change; same workload version + seed, warm-up policy, repetition count).
- [ ] **Predicted vs measured comparison published**, per metric, against the stated
      uncertainty band — **including where the prediction was wrong**; no cherry-picking;
      invalid runs invalidated with reasons, never dropped silently.
- [ ] Error analysis feeds back: fleetlab profile-refinement notes recorded (or filed
      upstream to fleetlab).
- [ ] Evidence archived: recommendation file, applied manifests, before/after results, error
      analysis (= the loop report), this checklist → `evidence/i6/`.
- [ ] Pins updated (fleetlab release, contracts v1.0.0, `proven_at: [I6]`); compatibility
      matrix row added.
- [ ] Reviewed (user acceptance).

## Failure handling

- Prediction badly off → **publish the error analysis** and refine profiles (fleetlab). That
  is the experiment working, not failing.
- Loop mechanics broken (schema mismatch, plumbing) → fix Contract 7 plumbing in the owning
  repo(s); this repo archives the failure and re-runs after the pin bump.
- Scale pressure → shrink the loop to mock/llama.cpp scale with a recorded deviation; never
  skip closing it.
