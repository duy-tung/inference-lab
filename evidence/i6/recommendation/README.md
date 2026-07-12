# Archived copy — fleetlab FL-T009 capacity recommendation

This is a byte-identical archived copy of a released evidence artifact from a sibling repo,
kept here because Scenario E's own checklist (`scenarios/e/README.md`) requires the
recommendation file to be "archived **before any change is applied**" as a first-class
loop-evidence artifact (`portfolio-planning/prompts/05-inference-lab-plan.md` §3: "the
recommendation file is a first-class evidence artifact"). This is the one exception to this
repo's usual cite-don't-copy convention for sibling-repo evidence (used for inferops manifests
at I5/I7): the file is small, self-contained data (not code), and the acceptance criterion
names it explicitly.

- **Origin:** `/home/user/fleetlab`, file
  `examples/recommendations/e2-admission-sane-v1-5x-scaleout.capacity-recommendation.json`,
  commit `dd05e7decca5a998afdf496d1c439141caba5a29` (FL-T009), created
  `2026-07-11T00:00:00Z` (per the file's own `created_at` field) — i.e. **before** any applied
  change (IO-T009 ran 2026-07-12).
- **sha256 (this copy):** `85e5d9727775d89f96437daf8a3087690d45ec3f0500850adbd660e595c1ec9f`
  — identical to the source file at the cited commit (verified by direct `sha256sum` this
  session; no edits made in transit).
- **Independently re-validated this session** (not just fleetlab's own claim) against **two**
  contract bundles:
  1. `python3 vendor/serving-contracts-v0.2.0/kit/contracts-validate.py --bundle
     vendor/serving-contracts-v0.2.0 validate --schema capacity-recommendation
     examples/recommendations/e2-admission-sane-v1-5x-scaleout.capacity-recommendation.json`
     (run inside `/home/user/fleetlab`) → `PASS ... [capacity-recommendation]`.
  2. `python3 kit/contracts-validate.py validate --schema capacity-recommendation
     /home/user/fleetlab/examples/recommendations/e2-admission-sane-v1-5x-scaleout.capacity-recommendation.json`
     run against a live checkout of `/home/user/serving-contracts` at tag **`v1.0.0`**
     (commit `507208b25737470b9eb2f9553a5c55f8f535f1d5`) → `PASS ... [capacity-recommendation]`.
     `schemas/capacity-recommendation.schema.json` is byte-identical between the v0.2.0 and
     v1.0.0 tags (`git diff v0.2.0 v1.0.0 -- schemas/capacity-recommendation.schema.json`
     produced no output) — Contract 7 is not one of the three contracts v1.0.0 freezes, so this
     is expected, not a coincidence. The serving-contracts working tree was restored to `main`
     immediately after (`git checkout main -- .`; `git status` clean) — no edits made there.
- **Full narrative + predicted-vs-measured comparison:** `evidence/i6/loop-report.md`.
- **Acceptance mapping:** `evidence/i6/checklist.md`.

See `evidence/i6/loop-report.md` §6 for the one plumbing-precision gap found while reading this
file closely: `recommended_topology.replica_groups[0].engine_config.flags` is an empty object
— the admission-sane-v1 flags (`-admission-tenant-queue-cap=3` etc.) that actually define the
recommended configuration are carried only in the prose `baseline`/`change_summary` fields
("gateway-mock-admission-sane-v1"), not structurally in `engine_config`. inferops's own
reproduction of the admission flags for IO-T009 was inferred from context (matching
`ib-t010-e2-baseline-1x-sane`'s own manifest), not machine-applied from this field.
