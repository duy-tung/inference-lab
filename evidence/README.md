# Evidence — milestone evidence archive (I1–I8)

One directory per integration milestone: `evidence/i1` … `evidence/i8` (created when the
first evidence for that milestone lands — no empty placeholders). This repo is the evidence
archivist for **all** of I1–I8; roles per milestone: `docs/integration.md`.

**Status (2026-07-10):** first evidence set landed — `evidence/i2/` (Scenario A, IL-T002):
executed checklist, pins snapshot, run logs, raw events, metrics scrapes, trace export.
I2 acceptance review pending (documented deviation D-001: no PostgreSQL usage write yet).

## Layout per milestone (convention from `docs/interfaces.md` §4)

```text
evidence/i<N>/
├── checklist.md          # the executed acceptance checklist (item-by-item outcomes)
├── pins-snapshot.yaml    # the pins entries the run used (or a pinned git ref)
├── logs/                 # bring-up / smoke / teardown logs, redacted per docs/security.md
├── raw/                  # raw-event JSONL, metrics exports, trace exports
├── reports/              # generated reports (manifest + validity block) or links
└── notes.md              # dated observations, defects filed upstream, deviations
```

## Rules (normative; ADR-0002)

1. **Immutable once accepted.** After a milestone is accepted, its evidence is append-only:
   corrections/supersessions are new dated entries; nothing is edited, renamed, or deleted.
2. Every number carries **provenance** (measured / source-reported / assumed) and a **date**.
3. **Failed runs are evidence too** — archived and labelled invalid, never deleted, never
   published as results.
4. No secrets: logs redacted before commit (`docs/security.md`).
5. Every compatibility-matrix row and landing-page claim must resolve to a directory here.
