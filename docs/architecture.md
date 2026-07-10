# Architecture — inference-lab

## Position in the dependency graph: pure sink

inference-lab consumes released artifacts from all five sibling repos and provides nothing at
build time to any of them. No other repo may depend on inference-lab artifacts at build time.
All integration is via versioned contracts, released artifacts (images by digest, binaries,
tagged bundles), result files, and documented network protocols — **never source imports**.

```text
serving-contracts ──┐
infergate ──────────┤
inferbench ─────────┼──▶ inference-lab   (released artifacts, result files, reports only)
fleetlab ───────────┤
inferops ───────────┘
```

Consequences enforced in review:

- Never check out another repo's source to build it; never vendor another repo's code;
  never patch a component here.
- Runtime defects discovered here are routed to the owning repo as evidence-backed defect
  reports; this repo waits for the next release and bumps its pin.
- This repo contains no services and no daemons — everything is declarative/orchestration.

## Repository layout

```text
pins/            machine-readable pin matrix (pins.yaml) + validator script
scenarios/a..e   one directory per scenario: compose/invocation scripts referencing pinned
                 images/versions only, a README (purpose + expected outcome), and an
                 acceptance checklist mirroring the owning milestone's criteria
quickstart/      the ≤15-minute GPU-free path (Scenario A), with a timed dry-run procedure
evidence/i1..i8  archived milestone evidence: run logs, raw-event files, trace exports,
                 dashboards, manifests, checklists
compatibility/   compatibility matrices per integration milestone + the comparability rule
reports/         archived copies of the owning repos' published reports, linked by pin
postmortems/     standard-format postmortems (timeline from real metrics, detection gap,
                 root cause, mitigation, action items)
portfolio/       landing page, articles, demo script + demo video script, limitations,
                 diagrams, cross-portfolio ADR index
study/           curriculum/study progress tracker (artifact-or-drop rule enforced here)
oss/             OSS activity log (real interactions only; drafts marked as drafts)
docs/            this documentation set + this repo's own ADRs
```

## Pins-as-ledger design

`pins/pins.yaml` is the authoritative, machine-readable record of which contract bundle,
image digests, engine versions, model revisions, and config bundles are **proven together**,
per integration milestone. Design properties:

- **One entry per artifact**, carrying: stable `id`, `component`, `kind`, `version` (tag),
  `digest` (mandatory for container images), `provenance` (`measured` / `source-reported` /
  `assumed`), `date` (ISO), `proven_at` (list of integration milestones), `source`, and
  optional `reverify` flag for volatile facts ("as of 2026-07 — re-verify at use time").
- **Append-mostly ledger semantics**: a pin bump is a new dated entry (or a dated update with
  the old value recorded in the entry history); the file plus git history together form the
  ledger of what was proven when.
- **Validated by a script** (`pins/validate_pins.py`) that schema-checks every entry; the
  validator must be green before any milestone is recorded.
- The compatibility matrices in `compatibility/` are per-milestone *views* over the pins file;
  every "proven together" row cites archived evidence under `evidence/`.

Format specification: see `docs/interfaces.md` and ADR-0001 (`docs/adr/adr-0001-pins-file-format.md`).

## Evidence architecture

- Evidence is **immutable once a milestone is accepted**; corrections are new dated entries
  (ADR-0002).
- Every archived number carries provenance (measured / source-reported / assumed) and a date.
- Evidence directories mirror the integration milestones (`evidence/i1` … `evidence/i8`);
  each accepted milestone directory contains the executed acceptance checklist.
- Reports in `reports/` are archived copies with a link to their origin and the pins entry
  they ran against; this repo never generates new performance claims of its own.

## Concurrency and failure model

- **Concurrency: none.** Scripts are sequential and idempotent. Scenario scripts are
  re-runnable, split into separate steps with recorded output: bring-up, smoke, evidence
  capture, teardown.
- **Failure behavior:** scenario scripts fail loudly (non-zero exit, captured logs) and never
  mask a component failure. A failed scenario run is evidence of a defect in the owning repo —
  record it, file it upstream (in-program), pin-bump when fixed, re-run. Never "fix it locally
  to make the demo work."

## State ownership

This repo owns: the pin matrix, scenario evidence, compatibility matrices, OSS log, and the
study tracker. Everything else is an archived copy with a link to its origin and pin.
No databases, no runtime state.
