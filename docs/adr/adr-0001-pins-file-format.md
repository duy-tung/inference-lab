# ADR-0001 — Pins file format: YAML ledger with per-artifact entries

- **Status:** accepted
- **Date:** 2026-07-10
- **Deciders:** inference-lab (IL-T001); user review pending as part of the M1 plan review

## Context

inference-lab owns the version-pin matrix: the single authoritative record of which contract
bundle, image digests, engine versions, model revisions, and config bundles are proven
together per integration milestone. Requirements: machine-readable; per-entry provenance and
date fields; digest support for container images; validatable by a script; reviewable in
diffs; append-mostly ledger semantics (history matters as much as current state).

Options considered: (a) YAML file + schema validator; (b) JSON file + JSON Schema;
(c) one file per artifact in a directory tree; (d) a small SQLite database.

## Decision

One YAML file, `pins/pins.yaml`, with top-level `schema_version`, `updated`,
`comparability_rule`, `milestone_evidence`, and an `artifacts` list of flat entries
(`id`, `component`, `kind`, `version`, `digest`, `provenance`, `date`, `proven_at`,
`source`, `reverify`, `notes`), validated by `pins/validate_pins.py` (Python 3 + PyYAML).
Full field rules: `docs/interfaces.md` §3.

Rationale:

- YAML over JSON: comments (needed for "as of / re-verify" annotations) and readable review
  diffs; the schema stays 1:1 convertible to JSON if tooling ever requires it (reversible).
- Single file over a directory tree: the matrix is small (tens of entries), and a single file
  gives an at-a-glance "what is proven together" view plus trivially diffable pin bumps.
- Script validation over JSON Schema tooling: one dependency-light script this repo fully
  controls; it can enforce cross-field rules JSON Schema states awkwardly (digest required
  iff `kind: container-image`, `proven_at` ⊆ I1..I8, id uniqueness).
- No database: this repo holds no runtime state; git history + dated entries are the ledger.

## Consequences

- Every pin bump is a reviewed diff; provenance and date are mandatory, so unproven or
  undated pins fail validation before they can be recorded.
- The compatibility matrices (`compatibility/matrix.md`) are derived views over this file and
  must cite evidence; the pins file itself never claims "proven" without a `proven_at`
  milestone whose evidence exists.
- Breaking format changes require a `schema_version` bump + validator update in the same
  commit.
- PyYAML becomes a (dev-time-only) dependency of validation; acceptable per assumption A-002.
