# Scope — inference-lab

## This repo owns

- The **machine-readable version-pin matrix** (`pins/pins.yaml` + validator) — the
  authoritative record of which contract bundle, image digests, engine versions, model
  revisions, and config bundles are proven together per milestone.
- The **local quickstart**: fresh clone → running Scenario A in ≤15 minutes on a GPU-free
  machine (`quickstart/`).
- **End-to-end orchestration of scenarios A–E** (`scenarios/`).
- **Demo scenarios and scripts**; the demo video script (5-minute class).
- **Reports** — archived benchmark, capacity, autoscaling, loop (I6), and calibration reports.
- **Diagrams** — architecture diagrams including the explicit gateway/engine boundary.
- The **ADR index across the portfolio** (links to every ADR across the six repos), plus this
  repo's own ADRs.
- The **postmortems archive** (standard format).
- **Compatibility matrices** — which released versions are proven together, per integration
  milestone, including the benchmark comparability rule.
- The **portfolio landing page** and **technical articles**.
- The **curriculum/study progress tracker** (`study/tracker.md`).
- The **OSS activity log** (`oss/log.md`).
- **Milestone evidence archive** for all of I1–I8 (`evidence/`).

## The five scenarios (owned here; definitions in `scenarios/*/README.md`)

| Scenario | Path | Milestone | Notes |
|---|---|---|---|
| A | infergate → mock backend → PostgreSQL → OTel | I2 | correctness spine, GPU-free; the quickstart scenario |
| B | infergate → llama.cpp → inferbench | I3 | first real engine, CPU |
| C | infergate → vLLM → inferbench → observability | I4 | GPU path (CPU fallback is a recorded deviation) |
| D | inferops → infergate → vLLM → OTel/Prometheus/Grafana/Tempo | I5 | operated on K8s; I5 owned by inferops, archived here |
| E | inferbench results → fleetlab → recommendation → inferops → repeated benchmark | I6 | THE central integration story; never-cut |

## Portfolio artifacts (assembled at IL-T009)

- Landing page in this exact order: positioning statement; "Why not LiteLLM / Envoy AI
  Gateway / GAIE?" related-work section; three measured claims each linked to its report;
  architecture diagram with the explicit gateway/engine boundary; quickstart; honest
  limitations; the final narrative verbatim with each sentence hyperlinked to evidence.
- Articles: (1) "Double-Queuing in LLM Serving: When a Gateway Destroys Continuous Batching";
  (2) "Correct Cancellation, Retry and Token Accounting for Streaming Inference";
  (3, optional) "How to Benchmark TTFT, ITL and Goodput Without Lying to Yourself".
- Demo script + demo video script; honest-limitations statement.

## This repo does NOT own

- Any core runtime logic.
- Any duplicated capability: there is exactly one gateway (infergate), one load-generation
  system (inferbench), one deployment stack (inferops) in the whole program.
- Gateway/bench/simulation/ops source. This repo composes released artifacts only.
- Fixes: runtime defects discovered here are routed to the owning repo, never fixed here.

See `docs/non-goals.md` for the enforced exclusion list.
