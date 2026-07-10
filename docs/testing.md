# Testing — inference-lab

This repo tests **orchestration, not runtime**. Runtime behavior is tested in the owning
repos; here we verify that pins are well-formed, scenarios meet their acceptance checklists,
the quickstart meets its time budget, and every published claim is re-derivable.

## a. Pins validator

`pins/validate_pins.py` schema-checks every entry in `pins/pins.yaml`:

- required fields present (`id`, `component`, `kind`, `version`, `provenance`, `date`,
  `proven_at`, `source`);
- `id` unique; `component`/`kind`/`provenance` values from the allowed enums;
- `digest` present and `sha256:<64 hex>`-shaped for every `container-image` entry;
- `date` is a real ISO date; `proven_at` values drawn from `I1..I8`;
- top-level `schema_version`, `updated`, and the comparability rule present.

Run: `python3 pins/validate_pins.py` (validates `pins/pins.yaml` and the seed fixture
`pins/examples/seed-entry.yaml`). Exit code 0 = green. The validator must be green before any
milestone is recorded and at every review gate.

## b. Scenario acceptance checklists

Each scenario directory (`scenarios/a` … `scenarios/e`) contains an acceptance checklist
mirroring its owning milestone's criteria (I2, I3, I4, I5, I6 respectively — see
`docs/integration.md`). A scenario is claimed only when its checklist is executed
item-by-item with recorded outcomes, and the executed copy is archived under
`evidence/i<N>/checklist.md`.

Scenario scripts are structured as four separately runnable, idempotent steps with recorded
output: **bring-up → smoke → evidence capture → teardown**. Scripts fail loudly (non-zero
exit, captured logs) and never mask a component failure.

## c. Quickstart timing protocol

- Fresh clone into a clean directory; Docker cache state noted (cold vs warm — both recorded,
  the published number is the documented one).
- Wall-clock measured from `git clone` start to Scenario A smoke success (stopwatch or
  scripted timestamps).
- Target: **≤15 minutes on a GPU-free machine**.
- **≥2 timed runs before I8**; every run recorded in `quickstart/timing-log.md` with date,
  machine spec, cache state, and measured duration. The number is measured, never assumed
  (hypothesis H1 in `docs/experiments.md`).

## d. Reproducibility-audit procedure (executed at I8, in a fresh session)

For each headline claim on the landing page:

1. Locate the pinned artifacts (pins entry + evidence directory) the claim cites.
2. Re-derive the number/statement from those artifacts alone, in a fresh session with no
   context from the original run.
3. Record pass/fail in the audit checklist.
4. **Any claim that fails is removed or re-measured — no exceptions.**

## e. Link-integrity check

Before each milestone acceptance and at I8: verify that every link in `compatibility/`,
`reports/`, `portfolio/`, and the ADR index resolves (relative paths exist; external links
recorded with an access date). A broken evidence link blocks acceptance.

## What is deliberately NOT tested here

- Component correctness (gateway streaming, bench measurement, simulation math) — owned by
  the respective repos; a failure observed here becomes a defect report upstream.
- Performance — this repo archives measured reports; it never generates new performance
  claims.
