# ADRs — inference-lab + cross-portfolio index

This directory holds (1) this repo's own architecture decision records and (2) the
**cross-portfolio ADR index** — links to every ADR across the six repos (an IL-owned
portfolio artifact, kept current as sibling repos publish ADRs).

ADR format: status, context, decision, consequences. Statuses: `proposed`, `accepted`,
`superseded-by-NNNN`.

## This repo's ADRs

| ID | Title | Status | Date |
|---|---|---|---|
| [ADR-0001](adr-0001-pins-file-format.md) | Pins file format: YAML ledger with per-artifact entries | accepted | 2026-07-10 |
| [ADR-0002](adr-0002-evidence-immutability.md) | Evidence immutability: accepted evidence is append-only | accepted | 2026-07-10 |

## Cross-portfolio ADR index

One row per ADR anywhere in the portfolio. Populated as sibling repos publish ADRs; link
integrity checked per `docs/testing.md` §e. *(Empty as of 2026-07-10 — no sibling repo has
published ADRs yet.)*

| Repo | ADR | Title | Status | Link | Indexed |
|---|---|---|---|---|---|
| — | — | *(none indexed yet)* | — | — | — |

Known upcoming ADRs to watch for (from the program plan; indexed when they exist, not
before): infergate "Why the gateway must not batch" (Orca-based, feeds article #1); infergate
API-key revocation consistency; infergate tenant-config consistency; infergate
transaction-boundary; infergate admission/retry-budget.
