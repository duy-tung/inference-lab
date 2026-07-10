# Reports — archived copies, linked by pin

Archived copies of the owning repos' published reports: benchmark (inferbench), capacity /
autoscaling / calibration (fleetlab), and the I6 loop report. **This repo never generates
new performance claims** — every report here is an archived copy with a link to its origin
and to the pins entries it ran against.

**Status (2026-07-10): empty.** First expected content: benchmark report #0 (methodology
shakedown, Scenario B / I3).

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
