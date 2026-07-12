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

One row per ADR anywhere in the portfolio. Populated 2026-07-12 (IL-T009 / I8) by reading each
sibling repo's `docs/adr/` directly (path + status line quoted, not re-derived) — link
integrity is "path exists in the cited sibling repo as of the commit that repo was pinned at
in this release," not a live URL check (no repo has remote-hosted ADR pages; all links below
are relative filesystem citations, matching this program's own "released artifacts/files, not
a source import" integration rule). Superseded here if a sibling repo's own ADR count changes
at a future pin bump.

| Repo | ADR | Title | Status |
|---|---|---|---|
| serving-contracts | `docs/adr/0001-bundle-versioning.md` | Bundle versioning, not per-schema versioning | Accepted |
| serving-contracts | `docs/adr/0002-json-schema-draft.md` | JSON Schema draft pinned to 2020-12 | Accepted |
| serving-contracts | `docs/adr/0003-openapi-version.md` | OpenAPI 3.1.x for the inference API spec | Accepted |
| serving-contracts | `docs/adr/0004-fixture-layout.md` | Fixture layout under `examples/` | Accepted |
| infergate | `docs/adr/0001-api-key-revocation-consistency.md` | API-key revocation consistency | Accepted (user-reviewed 2026-07-11, RQ-13) |
| infergate | `docs/adr/0002-config-snapshot-model.md` | Versioned configuration-snapshot model | Accepted (2026-07-10) |
| infergate | `docs/adr/0003-transaction-boundaries.md` | Transaction boundaries: snapshot store, ledger, quota state | Accepted (2026-07-10) |
| infergate | `docs/adr/0004-retry-budget.md` | Retry budget and pre-first-token-only retries | Accepted (2026-07-10) |
| infergate | `docs/adr/0005-why-the-gateway-must-not-batch.md` | Why the gateway must not batch | Accepted (2026-07-10) — **feeds `portfolio/articles/article-1.md`** |
| infergate | `docs/adr/0006-tenant-config-consistency.md` | Tenant-config consistency | Accepted (user-reviewed 2026-07-11, RQ-13) |
| infergate | `docs/adr/0007-multi-gateway-design.md` | Multi-gateway (N-replica) design note | Accepted (user-reviewed 2026-07-11, RQ-13) |
| inferbench | `docs/adr/ADR-0001-open-loop-scheduler.md` | Open-loop seeded arrival scheduler | Accepted (2026-07-10) |
| inferbench | `docs/adr/ADR-0002-statistics-choices.md` | Statistics choices: pooled percentiles, bootstrap CIs, warm-up exclusion, knee detection | Accepted (2026-07-10) |
| inferbench | `docs/adr/ADR-0003-closed-loop-flagging.md` | Closed-loop mode exists but is flagged everywhere | Accepted (2026-07-10) |
| inferbench | `docs/adr/ADR-0004-tool-calibration-protocol.md` | Calibration protocol vs reference tooling | Accepted (2026-07-10) |
| fleetlab | `docs/adr/0001-stack-and-simulator-style.md` | Python stack and simulator style | Accepted (2026-07-10) |
| fleetlab | `docs/adr/0002-fitting-method.md` | Fitting method (FL-T004) | **Proposed** — pending G8 human review (see `reports/holdout-validation.md`; the gate itself has run, human sign-off on this specific ADR not yet exercised) |
| fleetlab | `docs/adr/0003-signal-comparison-design.md` | Signal-comparison design (FL-T006) | Accepted |
| inferops | `docs/adr/0001-deployment-tooling.md` | Deployment tooling: Kustomize + raw manifests | Accepted (2026-07-10) |
| inferops | `docs/adr/0003-keda-not-adopted.md` | KEDA not adopted for IO-T009 autoscaling experiments | Accepted (2026-07-12) |
| inference-lab | `adr-0001-pins-file-format.md` | Pins file format: YAML ledger with per-artifact entries | Accepted (2026-07-10) |
| inference-lab | `adr-0002-evidence-immutability.md` | Evidence immutability: accepted evidence is append-only | Accepted (2026-07-10) |

**Note:** `inferops/docs/adr/` has no `0002-*.md` file (numbering is not contiguous in that
repo — not a broken link here, the gap is upstream and not this index's error). fleetlab's
`vendor/serving-contracts-v0.2.0/docs/adr/` is a vendored copy of serving-contracts' own ADRs
at the pin fleetlab vendors — not indexed separately here to avoid double-counting the same
four ADRs already listed above.
