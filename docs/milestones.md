# Repository Milestones — inference-lab

Dependency-ordered; no calendar durations. A milestone is done only when its acceptance
criteria are demonstrated and reviewed. Integration milestones (I1–I8) are defined in
`docs/integration.md`; repo milestones below track this repo's own deliverables.

| # | Milestone | Acceptance criteria | Status |
|---|---|---|---|
| M1 | Skeleton + docs | All 15 docs exist with content; pins file format defined + validated by a script; scenario A–E definitions written; OSS log + study tracker initialized. | **In progress** (IL-T001; awaiting user plan review) |
| M2 | Scenario A / I2 accepted | I2 acceptance (see `docs/integration.md`) demonstrated and reviewed; evidence archived under `evidence/i2`; pins record contracts v0.1.x + infergate/mock images + inferbench version. | Not started |
| M3 | Scenario B / I3 accepted | I3 acceptance demonstrated; benchmark report #0 archived; llama.cpp commit + GGUF revision pinned. | Not started |
| M4 | Scenario C / I4 accepted | I4 acceptance demonstrated (or CPU-fallback deviation recorded); GPU session manifest archived; vLLM/model/driver/CUDA pins recorded. | Not started |
| M5 | Scenario D / I5 evidence archived | I5 (owned by inferops) accepted; this repo archives manifests, smoke outputs, dashboard exports, rolling-update log; compatibility matrix updated. | Not started |
| M6 | Scenario E / I6 accepted | The loop closes: recommendation → applied change → re-benchmark → predicted-vs-measured comparison published **including where the prediction was wrong**. Contracts v1.0.0 pinned. | Not started |
| M7 | Failure campaign / I7 evidence | Campaign matrix (12 rows or documented reduced set) archived; ≥2 postmortems in standard format published. | Not started |
| M8 | Portfolio release / I8 accepted | Quickstart ≤15 min fresh-clone verified; landing page + 2 articles + demo script + honest limitations published; OSS evidence recorded; reproducibility audit passed. | Not started |

## OSS milestones (externally paced; run parallel from any wave ≥3 equivalent)

| # | Milestone | Acceptance | Status |
|---|---|---|---|
| MO1 | Target re-verified + built + issue reproduced | IL-T010 done: live re-verification of volatile facts (esp. GAIE → llm-d migration), local build with recorded versions, one existing issue reproduced | Not started |
| MO2 | Reproducer communicated upstream | IL-T011 done: minimal reproducer + environment manifest posted upstream; public links recorded; user reviewed the submission pre-post | Not started |
| MO3 | Contribution merged or under substantive review | IL-T012 done: small PR landed or under substantive review at I8; lessons recorded | Not started |

## Gate discipline

- Each milestone acceptance is a **mandatory user-review point**.
- At each milestone gate, a fresh-context verifier checks the work against the acceptance
  criteria — self-review alone is not acceptance evidence.
- Never-cut core (see `docs/risks.md`): the Scenario A quickstart and the Scenario E loop.
