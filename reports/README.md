# Reports — archived copies, linked by pin

Archived copies of the owning repos' published reports: benchmark (inferbench), capacity /
autoscaling / calibration (fleetlab), and the I6 loop report. **This repo never generates
new performance claims** — every report here is an archived copy with a link to its origin
and to the pins entries it ran against.

**Status (2026-07-12, IL-T009): four reports archived.** This directory sat empty from
2026-07-10 through I3-I7 despite those milestones' checklists citing several of these reports
extensively by path+commit — a gap in the evidence-archivist duty for this specific
directory, corrected now (found during the I8 reproducibility-audit data-gathering pass).

| Report | Origin | Supports |
|---|---|---|
| [`benchmark-report-1.md`](benchmark-report-1.md) | inferbench `docs/evidence/ib-t010/benchmark-report-1.md` @ `cc404a6` | I4 CPU-fallback gateway-overhead pillar; landing-page claim "gateway overhead p95" |
| [`benchmark-report-1b.md`](benchmark-report-1b.md) | inferbench `docs/evidence/ib-t010/benchmark-report-1b.md` @ `62c2704` | admission/G5 story, including the honest re-baseline (REFUTED twice on the strict criterion, PASS on the re-framed one) |
| [`capacity-report.md`](capacity-report.md) | fleetlab `reports/holdout-validation.md` @ `dd05e7d` (G8 gate) | I6 loop report; the "simulation ≠ production" limitation |
| [`../evidence/i6/loop-report.md`](../evidence/i6/loop-report.md) | this repo (I6 loop owner) | the "+1.3%" capacity-feedback-loop headline claim |

Benchmark report #0 (methodology shakedown, Scenario B / I3) is `evidence/i3/reports/` —
archived under its owning milestone's evidence directory rather than here, since it predates
this directory's own upkeep; not duplicated.

## Rules

1. Every report carries its **full run manifest** and **validity block** (Contract 3);
   reports without them are not archived as reports.
2. Percentiles are pooled, never averaged across runs; goodput@SLO is always shown with the
   shed rate adjacent (and the stall-rate caveat where applicable).
3. Every archived report links: origin (owning repo release/artifact), pins entries used,
   and the evidence directory of the milestone it supports.
4. Invalid runs are invalidated, never published; superseded reports stay, annotated
   (ADR-0002).
5. Comparisons must satisfy the comparability rule printed in `compatibility/matrix.md`.
