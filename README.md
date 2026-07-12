# inference-lab

Integration, evidence, demonstration, and portfolio-narrative repository of the
**inference-systems** portfolio — six composable repos that together form one
production-grade LLM inference-serving platform (`serving-contracts`, `infergate`,
`inferbench`, `fleetlab`, `inferops`, and this repo).

This repo contains **no runtime logic**. It orchestrates released artifacts only, and it is
the single source of:

- **What is proven together** — the machine-readable version-pin matrix
  ([`pins/pins.yaml`](pins/pins.yaml)) and per-milestone compatibility matrices
  ([`compatibility/`](compatibility/matrix.md));
- **The ≤15-minute, GPU-free quickstart** ([`quickstart/`](quickstart/README.md)) — a real
  gateway + mock backend + OTel stack (Scenario A; PostgreSQL usage accounting is a documented
  deviation, D-001, not yet composed here — see the quickstart doc), **timed and confirmed:
  2m08s and 35s** across 2 runs;
- **Five end-to-end scenarios** ([`scenarios/`](scenarios/README.md)) — from the GPU-free
  correctness spine (A) to the capacity-feedback loop (E), the central integration story;
- **Milestone evidence I1–I8** ([`evidence/`](evidence/README.md)), archived reports
  ([`reports/`](reports/README.md)), and postmortems
  ([`postmortems/`](postmortems/README.md));
- **The portfolio narrative** ([`portfolio/`](portfolio/README.md)), study tracker
  ([`study/tracker.md`](study/tracker.md)), and OSS activity log
  ([`oss/log.md`](oss/log.md)).

> **Status (2026-07-12):** portfolio release assembled (task IL-T009 / milestone I8,
> **acceptance-review-pending**). I2 and I3 are user-accepted; I4–I7 and I6 are recorded with
> acceptance review pending; I1 and I8 were archived/assembled this same release. Read the
> story: [`portfolio/README.md`](portfolio/README.md) (the landing page). Read the honest
> caveats before trusting any number: [`portfolio/limitations.md`](portfolio/limitations.md).
> Read the audit that checked every headline claim against its pinned artifact:
> [`evidence/i8/reproducibility-audit.md`](evidence/i8/reproducibility-audit.md).

## Start here

| To understand… | Read |
|---|---|
| what this repo is and the narrative it must prove | [`docs/charter.md`](docs/charter.md) |
| the layout and the pins-as-ledger design | [`docs/architecture.md`](docs/architecture.md) |
| what this repo deliberately does not do | [`docs/non-goals.md`](docs/non-goals.md) |
| contracts consumed, pins format, evidence conventions | [`docs/interfaces.md`](docs/interfaces.md) |
| the integration milestones and this repo's roles | [`docs/integration.md`](docs/integration.md) |
| the task plan and current status | [`docs/tasks.md`](docs/tasks.md) |

Validate the pin matrix: `python3 pins/validate_pins.py`
