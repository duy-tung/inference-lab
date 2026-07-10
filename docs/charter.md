# Charter — inference-lab

## Mission

inference-lab is the integration, research, evidence, demonstration, and portfolio-narrative
repository of the **inference-systems** portfolio. It contains **no core runtime logic**; it
orchestrates released artifacts only (compose files, scripts, pinned versions). It must never
become a monolith and must never duplicate any capability owned elsewhere.

The portfolio consists of six independent, composable repositories that together form one
production-grade LLM inference-serving platform:

| Repo | Role |
|---|---|
| `serving-contracts` | versioned specs/schemas, no runtime logic |
| `infergate` | the only gateway (Go) |
| `inferbench` | the only load-generation + benchmark-analysis system (Go + Python) |
| `fleetlab` | explainable capacity/autoscaling/cost/placement simulation (Python) |
| `inferops` | the only Kubernetes/observability/chaos/runbook repo |
| `inference-lab` | **this repo** — integration, evidence, demonstration, narrative |

Repos integrate only via versioned contracts, released artifacts, files, or documented
network protocols. The dependency graph is acyclic; inference-lab is its **pure sink**.

## Target positioning (verbatim program goal)

> Senior Backend / Platform Engineer capable of designing, building, benchmarking, operating,
> and reasoning about production-grade distributed AI inference infrastructure, with particular
> strength in streaming correctness, backpressure, scheduling boundaries, observability,
> capacity planning, reliability, and infrastructure orchestration.

## Independent value

A stranger can clone this repo alone and get:

- a working **≤15-minute, GPU-free quickstart** of a real gateway + mock + PostgreSQL + OTel stack;
- honest benchmark and capacity reports;
- postmortems;
- a compatibility matrix stating exactly which versions are proven together;
- a readable portfolio narrative.

Quickstart + evidence + narrative has standalone reader value.

## Integration value

inference-lab is the pure sink of the dependency graph:

- it **archives evidence for all eight integration milestones (I1–I8)**;
- it **owns the version-pin matrix and compatibility matrices** — the single source of
  "what is proven together";
- it **orchestrates the five end-to-end scenarios** — including Scenario E, the central
  integration story of the whole program.

The five integration scenarios (owned here):

```text
A. infergate → mock backend → PostgreSQL → OTel                        (correctness spine, GPU-free)
B. infergate → llama.cpp → inferbench                                  (first real engine, CPU)
C. infergate → vLLM → inferbench → observability                       (GPU path)
D. inferops → infergate → vLLM → OTel/Prometheus/Grafana/Tempo         (operated on K8s)
E. inferbench results → fleetlab → deployment recommendation → inferops → repeated benchmark
                                                                       (THE central integration story)
```

## Final narrative (verbatim — the landing page must make every sentence demonstrable, with evidence)

> "I built a correct serving gateway. I measured the gateway and engine independently and
> together. I converted measurements into capacity decisions. I deployed and operated the
> system on Kubernetes. I injected failures and documented recovery. I contributed
> reproducible evidence or a fix upstream."

Each sentence maps to evidence archived in this repository:

| Sentence | Primary evidence |
|---|---|
| "I built a correct serving gateway." | `evidence/i2/` (Scenario A: streaming correctness, cancellation, TTFT agreement) |
| "I measured the gateway and engine independently and together." | `evidence/i3/`, `evidence/i4/` (benchmark reports #0 and #1, gateway-overhead comparison) |
| "I converted measurements into capacity decisions." | `evidence/i6/` (the Scenario E loop report, predicted vs measured) |
| "I deployed and operated the system on Kubernetes." | `evidence/i5/` (manifests, rolling update under load, dashboards) |
| "I injected failures and documented recovery." | `evidence/i7/` + `postmortems/` (campaign matrix, ≥2 postmortems) |
| "I contributed reproducible evidence or a fix upstream." | `oss/log.md` (public links, or documented contingency) |

## Definition of Done (repo-level)

inference-lab is accepted when: I2–I8 evidence is archived (I2/I3/I4/I6/I8 accepted as owner;
I1/I5/I7 archived per duty); pins and compatibility matrices are current (verified at I8); and
the portfolio release is shipped — quickstart (≤15 min, GPU-free, stranger-tested), recorded
demo, benchmark + capacity reports linked, failure-campaign evidence and ≥2 postmortems linked,
OSS evidence recorded or contingency documented, two articles + landing page +
honest-limitations statement published, and the reproducibility audit passed (every headline
claim re-derivable from pinned artifacts by a fresh session; failing claims removed or
re-measured — no exceptions).
