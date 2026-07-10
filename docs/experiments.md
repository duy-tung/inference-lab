# Experiments — inference-lab

This repo runs only three classes of experiment of its own. All other performance numbers in
this repo are archived copies with provenance; this repo never generates new performance
claims.

## This repo's own performance hypotheses

- **H1 — Quickstart time.** Scenario A quickstart completes in **≤15 minutes from fresh clone
  on a GPU-free machine**. Verified by timed runs (protocol in `docs/testing.md` §c); the
  number is measured, never assumed. ≥2 timed runs before I8, recorded in
  `quickstart/timing-log.md`.
- **H2 — Reproducibility.** Every headline portfolio claim is re-derivable from pinned
  artifacts by a fresh session. The I8 reproducibility audit is the test (procedure in
  `docs/testing.md` §d).

## 1. Loop (I6) prediction-vs-measured protocol

The Scenario E experiment. Roles: fleetlab predicts; inferops applies; inferbench measures;
this repo orchestrates and publishes.

1. **Inputs frozen:** benchmark-result IDs, workload version + seed, SLO, cost profile,
   hardware profiles — all recorded in the recommendation file (Contract 7) and pinned.
2. **Prediction recorded first:** fleetlab's recommendation (topology, engine config,
   predicted goodput/latency/cost **with stated uncertainty**, autoscaling signal +
   thresholds, assumptions) is archived under `evidence/i6/` *before* any change is applied.
3. **Change applied:** inferops applies exactly the recommended change (replica count /
   config); applied manifests archived.
4. **Outcome measured:** inferbench re-runs the same workload (same version + seed, warm-up
   policy, repetition count) against the changed deployment; before/after results archived.
5. **Comparison published:** predicted vs measured, per metric, with the prediction's stated
   uncertainty band — **including where the prediction was wrong**. Prediction error is a
   result, not a failure; the error analysis feeds fleetlab profile refinement.
6. **Comparability guard:** before publishing, verify the comparability rule (single declared
   experimental variable = the applied change; everything else pinned and matching).

Honesty rules: no cherry-picking runs; invalid runs invalidated with reasons, never silently
dropped; uncertainty carried through to the published comparison.

## 2. Quickstart timing runs

Per the timing protocol (`docs/testing.md` §c): fresh clone, cache state noted, wall-clock
measured, machine spec recorded. Each run appends an entry to `quickstart/timing-log.md`:

```text
date | machine (CPU/RAM/OS) | docker cache | duration | pass(≤15m)? | notes
```

A failed run (>15 min) triggers analysis of the slowest step (recorded in the log) and a fix
in the quickstart flow or an upstream image-size defect report — never a relaxed target.

## 3. Demo dry runs

Before recording the demo (IL-T009): full dry run of the demo script against pinned artifacts,
timed against the 5-minute class; every claim spoken in the demo checked against its evidence
link; failures fixed in the script or the claim dropped. Dry-run outcomes recorded in
`portfolio/` alongside the script.

## Experiment hygiene (applies to all of the above)

- Protocol written before the run; deviations from protocol recorded with the results.
- Every artifact carries date + provenance.
- A GPU is never required; any experiment touching GPU-backed components runs at whatever
  scale the pinned evidence already provides.
