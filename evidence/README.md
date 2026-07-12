# Evidence — milestone evidence archive (I1–I8)

One directory per integration milestone: `evidence/i1` … `evidence/i8` (created when the
first evidence for that milestone lands — no empty placeholders). This repo is the evidence
archivist for **all** of I1–I8; roles per milestone: `docs/integration.md`.

**Status (2026-07-10):** first evidence set landed — `evidence/i2/` (Scenario A, IL-T002):
executed checklist, pins snapshot, run logs, raw events, metrics scrapes, trace export.
I2 acceptance review pending (documented deviation D-001: no PostgreSQL usage write yet).

**Status (2026-07-12):** `evidence/i7/` landed (failure campaign, IL-T007): checklist,
campaign matrix (12-row, archived from inferops by path+commit), client-impact summary, pins
snapshot. 3 postmortems published under `postmortems/`. I7 acceptance review pending, same
precedent as I2/I3/I5.

**Status (2026-07-12):** `evidence/i6/` landed (capacity feedback loop, IL-T006 — the central
integration story): checklist, loop report (predicted-vs-measured, honest divergences
surfaced), an archived copy of fleetlab's recommendation file (independently re-validated
against Contract 7 in both the v0.2.0 and newly-frozen v1.0.0 bundles), pins snapshot. The
fitted 33.159 rps/replica capacity figure is confirmed within +1.3% at its own fitted rate but
diverges — leaning toward inferbench's own unpublished 37.925 rps/replica estimate — at higher
rates; the recommended 1→6 replica scale-out was applied and re-measured only as far as 1→2
(disclosed scope reduction); the 6-replica prediction itself was never measured. I6 acceptance
review pending, same precedent as I2/I3/I5/I7.

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
