# Implementation Notes — inference-lab

Running log of decisions, surprises, re-verification results of volatile facts, and
deviations. Newest entries first within each section.

## Log

### 2026-07-10 — IL-T001 bootstrap

- Repository skeleton created: full `docs/` set (15 docs + `adr/`), `pins/pins.yaml` +
  validator, scenario A–E definitions, quickstart structure, compatibility conventions +
  empty matrix, OSS log skeleton, study tracker, evidence/reports/postmortems/portfolio
  directory conventions.
- Pins file format defined per ADR-0001; evidence immutability per ADR-0002. Validator
  (`pins/validate_pins.py`, PyYAML-based) runs green on the empty `pins.yaml` and on the seed
  fixture `pins/examples/seed-entry.yaml`.
- Everything is **unpinned as of 2026-07-10**: `artifacts: []` — no sibling repo has a
  release yet. The seed fixture is a format demonstration only and is clearly marked
  non-normative; it makes no "proven together" claim.
- Reversible assumptions recorded (below). No compose files yet — those are IL-T002 scope.
- Volatile facts carried forward with `reverify` flags (all "as of 2026-07 — re-verify at use
  time"): OTel GenAI semconv status "Development"; vLLM v0.24.x baseline; GAIE → llm-d
  migration (`InferenceModel`→`InferenceObjective` rename); GPU budget envelope $150–250.
  None were re-verified live in this session — they enter the docs flagged, not asserted.

## Assumptions (reversible; recorded per working-style rule)

- **A-001 (2026-07-10):** Pins format is YAML (`pins.yaml`) with a Python/PyYAML validator,
  chosen over JSON for comment support and human-readable diffs in review. Reversible: the
  schema is representable 1:1 in JSON if tooling later requires it. See ADR-0001.
- **A-002 (2026-07-10):** Validator dependency is Python 3 + PyYAML (available in the dev
  environment). If a future CI environment lacks PyYAML, the fallback is vendoring a
  requirements note, not vendoring code.
- **A-003 (2026-07-10):** Scenario/quickstart docs assume Docker Compose as the local
  orchestrator for scenarios A–C (the program's GPU-free local path); the compose files
  themselves are IL-T002+ scope and their format may still be adjusted then.
- **A-004 (2026-07-10):** Milestone-evidence links inside `pins.yaml` use the
  `milestone_evidence` map (milestone → relative path) rather than per-entry links, keeping
  entries artifact-shaped. Reversible without schema break (additive field).

## Deviations

*(none yet)*

<!--
Deviation policy: when repository evidence forces a deviation from the approved plan, choose
the conservative reversible option, record the evidence, decision, consequences, and
follow-up here, and continue. Pause for user input only when the deviation changes public
contracts, repository ownership, security posture, or milestone scope.

Entry format:

### D-NNN (YYYY-MM-DD) — short title
- Evidence:
- Decision:
- Consequences:
- Follow-up:
-->
