# Risks — inference-lab

Localized from the program risk register. Each risk has a concrete trigger and a mitigation
that this repo can execute; program-wide risks are noted where they land here.

| Risk | Trigger | Mitigation |
|---|---|---|
| This repo absorbs runtime fixes / becomes a monolith | any component patch, vendored code, or source checkout appears here | hard rule: route defects to the owning repo with evidence; pin-bump on release; reject the change in review |
| Pin/release churn eats building time (program risk R1) | pin bookkeeping dominates; lockstep changes across repos twice in a row | contract-first discipline; automate pins validation (`pins/validate_pins.py`); consolidation is a user-review decision only |
| OSS latency or rejection (program risk R6) | contingency thresholds in `docs/oss-opportunities.md` hit (2-week issue silence; 4-week PR silence) | parallel secondary target; graceful degradation; OSS is never on the critical path |
| Fabrication/overclaiming (program risk R12) | any claim lacking a manifest/log | evidence rules (`docs/non-goals.md` §6); the I8 reproducibility audit removes unreproducible claims — no exceptions |
| GPU-dependent scenarios blocked (program risk R2) | budget alert fires; no GPU access | scenario variants fall back to llama.cpp/mock with **recorded deviations**; portfolio repositioned around CPU/edge evidence if needed |
| Demo breadth balloons | scenario/demo work blocks a milestone without new evidence | demo breadth is reducible; cut per the reduction order below |

## Reduction/kill order (when a milestone exit is threatened)

1. Cut demo breadth and optional article #3 first.
2. Reduce chaos-evidence breadth to the streaming-critical fault scenarios (1, 2, 5, 6, 12),
   with documented deviation.
3. Reduce GPU scenario variants to CPU fallbacks with recorded deviations.

## Never-cut core

- The **Scenario A quickstart** and the **Scenario E loop** (the loop may shrink to
  mock/llama.cpp scale but must close).
- Program-wide never-cut items that surface here as evidence: cancellation correctness, some
  fault-injection evidence, methodologically valid benchmarking, contract validation.

## Generic drop rule

Drop or postpone any work item that blocks the critical path without producing new evidence,
duplicates an existing capability, lacks a measurable artifact, exceeds GPU budget, or can't
be explained and reviewed by the user.
