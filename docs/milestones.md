# Repository Milestones — inference-lab

Dependency-ordered; no calendar durations. A milestone is done only when its acceptance
criteria are demonstrated and reviewed. Integration milestones (I1–I8) are defined in
`docs/integration.md`; repo milestones below track this repo's own deliverables.

| # | Milestone | Acceptance criteria | Status |
|---|---|---|---|
| M1 | Skeleton + docs | All 15 docs exist with content; pins file format defined + validated by a script; scenario A–E definitions written; OSS log + study tracker initialized. | **In progress** (IL-T001; awaiting user plan review) |
| M2 | Scenario A / I2 accepted | I2 acceptance (see `docs/integration.md`) demonstrated and reviewed; evidence archived under `evidence/i2`; pins record contracts v0.1.x + infergate/mock images + inferbench version. | **In review** (executed 2026-07-10; evidence + pins recorded; D-001 usage-write deviation; awaiting user acceptance) |
| M3 | Scenario B / I3 accepted | I3 acceptance demonstrated; benchmark report #0 archived; llama.cpp commit + GGUF revision pinned. | **Done** (ACCEPTED 2026-07-11, user review; open observation on the cancellation log-census, not blocking; `evidence/i3/`) |
| M4 | Scenario C / I4 accepted | I4 acceptance demonstrated (or CPU-fallback deviation recorded); GPU session manifest archived; vLLM/model/driver/CUDA pins recorded. | **Done as CPU-fallback deviation** (recorded 2026-07-12; G6/GPU deferred by user decision 2026-07-11 — no GPU rental, no GPU acceptance claimed; llama.cpp baseline (I3) + infergate IG-T005 + inferbench IB-T010 E1 assembled as evidence; `evidence/i4/`) |
| M5 | Scenario D / I5 evidence archived | I5 (owned by inferops) accepted; this repo archives manifests, smoke outputs, dashboard exports, rolling-update log; compatibility matrix updated. | **Evidence archived, acceptance review pending** (assembled 2026-07-12 from inferops commit `db30279`; headline deviation RQ-14 compose-pivot — no pod scheduling claimed; CPU-fallback llama.cpp continues I4/D-005, no vLLM/GPU; `evidence/i5/`) |
| M6 | Scenario E / I6 accepted | The loop closes: recommendation → applied change → re-benchmark → predicted-vs-measured comparison published **including where the prediction was wrong**. Contracts v1.0.0 pinned. | **Evidence archived, acceptance review pending** (assembled 2026-07-12 from fleetlab FL-T009 `dd05e7d` + inferops IO-T009 `89871a6`; recommendation archived + independently re-validated against Contract 7 in both v0.2.0 and the newly-frozen v1.0.0 bundles; applied change was 1→2 replicas, **not** the recommended 1→6 — disclosed scope reduction; 33.159 rps/replica confirmed within +1.3% at its own fitted rate, leaning toward inferbench's unpublished 37.925 rps/replica estimate at higher rates; 6-replica figure never measured; `in_flight` beat the recommended `queue_depth` signal; contracts v1.0.0 pinned, I1 re-run GREEN; `evidence/i6/`) |
| M7 | Failure campaign / I7 evidence | Campaign matrix (12 rows or documented reduced set) archived; ≥2 postmortems in standard format published. | **Evidence archived, acceptance review pending** (assembled 2026-07-12 from inferops commits `bfca054`/`a1e0af5`/`a07fd2f`; 12/12 scenarios injected, 0 scope reduction; client impact measured by inferbench for scenarios 1, 2, 5, 6, 12; 3 postmortems published, exceeding the ≥2 minimum; headline finding — scenario 4, slow client, a real deviation-documented defect — surfaced prominently, not buried; no vLLM/GPU claim, continues I4/D-005 and I5/D-006; `evidence/i7/`. Executed ahead of M6/I6 in dependency order — I6 is blocked on IO-T009 autoscaling, which itself follows the fault campaign per the 2026-07-12 resequencing decision recorded in `docs/implementation-notes.md`.) |
| M8 | Portfolio release / I8 accepted | Quickstart ≤15 min fresh-clone verified; landing page + 2 articles + demo script + honest limitations published; OSS evidence recorded; reproducibility audit passed. | **Assembled 2026-07-12, acceptance-review-pending** (quickstart timed 2m08s + 35s, both PASS; landing page `portfolio/README.md` + 2 articles + demo script/transcript/video-script + `portfolio/limitations.md` published; OSS evidence recorded per the documented contingency — local build + reproduction done, upstream comment drafted not posted, user-gated (`oss/log.md`); reproducibility audit `evidence/i8/reproducibility-audit.md` PASS with 2 claims narrowed and 2 process gaps fixed, 0 removed outright) |

## OSS milestones (externally paced; run parallel from any wave ≥3 equivalent)

| # | Milestone | Acceptance | Status |
|---|---|---|---|
| MO1 | Target re-verified + built + issue reproduced | IL-T010 done: live re-verification of volatile facts (esp. GAIE → llm-d migration), local build with recorded versions, one existing issue reproduced | **Done** (2026-07-11: llm-d-router confirmed as EPP's new home, built + tested (116/121 testable packages green), issue #1625's `fairness_id` cardinality subset reproduced locally; see `oss/log.md`) |
| MO2 | Reproducer communicated upstream | IL-T011 done: minimal reproducer + environment manifest posted upstream; public links recorded; user reviewed the submission pre-post | **Not met — documented contingency** (comment drafted at `oss/drafts/2026-07-11-llm-d-router-1625-comment.md`, explicitly not posted; posting requires user review/action per this milestone's own gate, which has not happened as of I8; `oss/log.md`'s 2026-07-12 framing note and `portfolio/limitations.md` §6 state this plainly) |
| MO3 | Contribution merged or under substantive review | IL-T012 done: small PR landed or under substantive review at I8; lessons recorded | Not started (blocked on MO2) |

## Gate discipline

- Each milestone acceptance is a **mandatory user-review point**.
- At each milestone gate, a fresh-context verifier checks the work against the acceptance
  criteria — self-review alone is not acceptance evidence.
- Never-cut core (see `docs/risks.md`): the Scenario A quickstart and the Scenario E loop.
