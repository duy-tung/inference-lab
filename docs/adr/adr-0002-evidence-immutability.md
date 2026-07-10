# ADR-0002 — Evidence immutability: accepted evidence is append-only

- **Status:** accepted
- **Date:** 2026-07-10
- **Deciders:** inference-lab (IL-T001); user review pending as part of the M1 plan review

## Context

This repo archives the evidence behind every portfolio claim (milestone evidence, reports,
postmortems). The portfolio's value rests on the I8 reproducibility audit: a fresh session
must be able to re-derive every headline claim from pinned artifacts. That is only credible if
evidence cannot be quietly rewritten after acceptance — including "harmless" cleanups.
Program evidence rules already require provenance + date on every number and forbid
publishing invalidated runs.

## Decision

Evidence under `evidence/i*/`, `reports/`, and `postmortems/` is **immutable once its
milestone is accepted**:

1. No edits, renames, or deletions of accepted evidence files. Corrections, invalidations,
   and supersessions are **new dated entries** that reference what they correct
   (e.g. `notes.md` entry + a new file suffixed with its date).
2. A superseded artifact stays in place, annotated as superseded by the new entry — never
   removed.
3. Failed/invalid runs are archived and labelled invalid; they are defect evidence, not
   publishable results, and they are never deleted to tidy the record.
4. Before acceptance, an evidence directory is work-in-progress and may be freely edited;
   acceptance (the reviewed milestone gate) is the freeze point.
5. Redaction is the single exception: if unpublishable data (secrets, private data — see
   `docs/security.md`) is discovered in accepted evidence, the redacted replacement is made
   as a new dated entry, and the incident is recorded in `docs/implementation-notes.md`.

## Consequences

- The audit trail is trustworthy: git history plus dated correction entries reconstruct
  exactly what was claimed when, and on what basis.
- Evidence directories grow monotonically; readers follow `notes.md` / supersession notes to
  the current-best entry. Slight redundancy is the accepted cost of auditability.
- Review gates must check for accidental edits to accepted evidence (a diff touching
  `evidence/i<N>` of an accepted milestone is a review flag).
