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
  gateway + mock backend + PostgreSQL + OTel stack (Scenario A);
- **Five end-to-end scenarios** ([`scenarios/`](scenarios/README.md)) — from the GPU-free
  correctness spine (A) to the capacity-feedback loop (E), the central integration story;
- **Milestone evidence I1–I8** ([`evidence/`](evidence/README.md)), archived reports
  ([`reports/`](reports/README.md)), and postmortems
  ([`postmortems/`](postmortems/README.md));
- **The portfolio narrative** ([`portfolio/`](portfolio/README.md)), study tracker
  ([`study/tracker.md`](study/tracker.md)), and OSS activity log
  ([`oss/log.md`](oss/log.md)).

> **Status (2026-07-10):** skeleton (task IL-T001 / milestone M1). Structure, formats, and
> scenario definitions are in place; **everything is unpinned and no evidence exists yet** —
> no sibling repo has published a release. The quickstart becomes runnable at IL-T002.

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
