# inference-systems — a measured, evidence-first LLM serving platform

**Status: I8 (portfolio release) assembled 2026-07-12, acceptance-review-pending.** Every
claim below survived (or was corrected by) the reproducibility audit:
[`evidence/i8/reproducibility-audit.md`](../evidence/i8/reproducibility-audit.md). This page
is the landing page for the `inference-systems` portfolio — six independent repos, integrated
only through versioned contracts and released artifacts, demonstrating senior-level judgment
in streaming correctness, backpressure, scheduling boundaries, observability, capacity
planning, reliability, and infrastructure orchestration.

## Positioning

> Senior Backend / Platform Engineer capable of designing, building, benchmarking, operating,
> and reasoning about production-grade distributed AI inference infrastructure, with
> particular strength in streaming correctness, backpressure, scheduling boundaries,
> observability, capacity planning, reliability, and infrastructure orchestration.

Six repos, one job each, integrating only through versioned contracts and released artifacts
— never a shared library, never a source checkout of a sibling repo:

| Repo | Role |
|---|---|
| [`serving-contracts`](https://github.com/duy-tung/serving-contracts) | versioned OpenAPI + JSON Schema, v1.0.0, no runtime logic |
| [`infergate`](https://github.com/duy-tung/infergate) | the one gateway (Go) |
| [`inferbench`](https://github.com/duy-tung/inferbench) | the one load-generation + benchmark-analysis system (Go + Python) |
| [`fleetlab`](https://github.com/duy-tung/fleetlab) | explainable capacity/autoscaling/cost simulation (Python) |
| [`inferops`](https://github.com/duy-tung/inferops) | the one Kubernetes/observability/chaos/runbook repo |
| [`inference-lab`](https://github.com/duy-tung/inference-lab) | **this repo** — integration, evidence, quickstart, narrative |

## Why not LiteLLM / Envoy AI Gateway / GAIE?

*(as of 2026-07 — feature sets in this fast-moving space move quickly; re-verify against
current product docs before relying on this section)*

These are real, useful, widely-adopted projects solving adjacent problems — not competitors
this portfolio claims to beat, but different scope choices worth being specific about:

- **LiteLLM** is primarily a multi-provider proxy/SDK: one OpenAI-compatible interface in
  front of 100+ model providers, with budgets, virtual keys, and cost tracking as its core
  value. Its own self-reported overhead baseline (docs.litellm.ai/docs/benchmarks, re-verified
  2026-07-11: "8ms P95 at 1k RPS", a 4-instance table of 2/8/13ms) is in the same rough
  magnitude as this program's own measured gateway overhead (paired p95 +2.21ms,
  `reports/benchmark-report-1.md`) — cited here for magnitude framing only, never as a
  cross-tool comparison claim, since the hardware, workload, and measurement basis differ
  (`compatibility/matrix.md`'s comparability rule). What this portfolio does differently:
  provider-fan-out is not the problem being solved at all — the entire focus is one gateway in
  front of one engine, with the boundary between them measured, not assumed.
- **Envoy AI Gateway** brings Envoy's mature L7 proxy engineering to LLM traffic — routing,
  auth, rate limiting, built on Envoy Gateway. It's infrastructure-grade and
  company-roadmap-driven. This portfolio's gateway is purpose-built and smaller in scope, and
  every claim about its behavior (overhead, cancellation, admission) ships with the raw data
  and reproduction command that produced it, rather than a features list.
- **Gateway API Inference Extension (GAIE)**, whose EPP scheduling logic has since moved to
  `llm-d/llm-d-router` — this portfolio's own open-source-track target
  (`oss/log.md`) — solves a genuinely different problem: cluster-wide, KV-affinity-informed
  routing *across many engine replicas* from outside the engine. This program's gateway
  deliberately does **not** attempt that (see the architecture-boundary section below,
  and `articles/article-1.md`) — a single-engine, measured-overhead gateway and a
  cluster-wide inference-aware router are complementary designs at different scopes, not
  competing solutions to the same problem.

## Three measured claims

Each below links to its full report (manifest + validity block) and states its scope plainly.

1. **A gateway adds ~2ms of overhead at p95, confirmed against a real target — and where the
   real engine made that unmeasurable, the report says so instead of rounding up.**
   Paired per-request overhead vs. a direct connection: **p50 +1.04ms, p95 +2.21ms, p99
   +2.81ms** (mock backend, n=630 pairs) — confirmed against the program's own p95<10ms/p99<20ms
   target. Against the real llama.cpp engine, the same experiment came back **INCONCLUSIVE at
   the ms scale** (engine run-to-run variance was 2-3 orders of magnitude larger than the bound
   under test) — reported as inconclusive, not confirmed.
   → [`reports/benchmark-report-1.md`](../reports/benchmark-report-1.md)
2. **Admission control's original overload target was measured and REFUTED — twice — before
   the program re-baselined the gate, and that history stays on the record.** At ~5×
   capacity, accepted-request TTFT p95 degraded **+25.16%** against a ≤20% target (REFUTED); a
   follow-up queue-cap change still came back **+26.08%** (REFUTED again, same root cause).
   The gate was then re-baselined to a criterion the data does meet — 100% typed shedding,
   bounded queue-wait (p95 134ms), no starvation — never presented as if the original ratio
   target had simply passed.
   → [`reports/benchmark-report-1.md`](../reports/benchmark-report-1.md), [`reports/benchmark-report-1b.md`](../reports/benchmark-report-1b.md)
3. **A capacity prediction was applied for real and re-measured — landing within +1.3% at its
   own fitted rate, and openly diverging at higher rates toward a different internal estimate,
   which the loop report treats as a result to investigate, not a result to hide.**
   fleetlab predicted 33.159±1.105 rps/replica from real benchmark data; re-measured at that
   exact rate, the observed goodput was 33.583 rps — **+1.3%**. At every higher rate actually
   measured, the number leaned toward inferbench's own unpublished 37.925 rps/replica estimate
   instead — resolving, not hiding, a discrepancy fleetlab's own G8 holdout gate had already
   flagged as unresolved. **The 6-replica recommendation itself was never measured** — the
   sandbox this program runs in has no real Kubernetes scheduler to run 6 replicas as pods
   (RQ-14); the applied change was 1→2, disclosed as a scope reduction, not silently
   substituted for 1→6.
   → [`evidence/i6/loop-report.md`](../evidence/i6/loop-report.md), [`reports/capacity-report.md`](../reports/capacity-report.md)

## Architecture — the gateway/engine boundary

```text
                    ┌─────────────────────────┐        ┌──────────────────────────┐
  client ──HTTP/SSE→│        infergate         │──HTTP─→│   engine (mock /         │
                    │  (the gateway; Go)       │        │   llama.cpp / vLLM*)     │
                    │                          │        │                          │
                    │  admission · routing     │        │  continuous batching     │
                    │  fairness · quotas       │        │  per-token scheduling    │
                    │  streaming relay         │        │  KV-cache / prefix-cache │
                    │  cancellation propagation│        │  GPU placement           │
                    │  retry budget · shedding │        │                          │
                    │  usage settlement        │        │  * vLLM = target only,  │
                    │  (estimate → settle,     │        │    never measured here  │
                    │   idempotent by req-ID)  │        │    (G6 deferred, no GPU) │
                    └─────────────────────────┘        └──────────────────────────┘
                            │
                    OTel traces + Contract-2 metrics
                    (recv → queue.wait → upstream.connect → ttft → stream.relay → settle)
```

**The rule this boundary enforces (`infergate docs/adr/0005-why-the-gateway-must-not-batch.md`,
`articles/article-1.md`):** the gateway never forms batches, never paces dispatch by a token
budget, and never models KV/prefix-cache state — those are the engine's job, and a second
scheduler in front of the engine's own is the double-queuing anti-pattern. The gateway's queue
exists for tenant fairness and overload protection only. Measured cost of holding that
discipline: ~2ms p95 (claim 1 above).

## Quickstart — ≤15 minutes, GPU-free

**Timed and confirmed:** 2 runs, 2m08s and 35s, both well under the 15-minute target — full
methodology and honesty caveats (cache warmth, port remap in this shared sandbox) at
[`quickstart/timing-log.md`](../quickstart/timing-log.md). Procedure:
[`quickstart/README.md`](../quickstart/README.md).

```bash
git clone https://github.com/duy-tung/inference-lab && cd inference-lab
scenarios/a/build.sh && cd scenarios/a && docker compose up -d && ./wait-ready.sh
curl -N http://localhost:18080/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"mock-8b","messages":[{"role":"user","content":"hello"}],"stream":true}'
```

## Honest limitations

Full statement: [`portfolio/limitations.md`](limitations.md). Read this before trusting any
number above at face value. In short: single machine throughout, no GPU ever rented (CPU/
llama.cpp only, never vLLM), one model (Qwen2.5-1.5B-Instruct Q4_K_M), no Kubernetes pod ever
scheduled (Docker Compose + manifests validated against a live k3s API server, not the same
thing), fleetlab's capacity fit is a documented MISS for the exact corpus this loop's headline
number draws on, gate G5 passed only under a re-framed criterion, and the OSS contribution
track has real local work but nothing posted upstream yet (user-gated, not yet actioned).

## The final narrative

> "I built a correct serving gateway. I measured the gateway and engine independently and
> together. I converted measurements into capacity decisions. I deployed and operated the
> system on Kubernetes. I injected failures and documented recovery. I contributed
> reproducible evidence or a fix upstream."

Each sentence, linked to its evidence — with the qualification the reproducibility audit
required stated inline, not hidden in a footnote:

| Sentence | Evidence | Qualification |
|---|---|---|
| "I built a correct serving gateway." | [`evidence/i2/`](../evidence/i2/checklist.md) — streaming correctness (100 concurrent, 0 frame-mixing), cancellation, TTFT agreement | 3-point cancellation is proven on the mock engine; on the real llama.cpp engine it's one composed-stack point plus a separate adapter-level test on an unpinned model — see `articles/article-2.md` |
| "I measured the gateway and engine independently and together." | [`reports/benchmark-report-1.md`](../reports/benchmark-report-1.md), [`reports/benchmark-report-1b.md`](../reports/benchmark-report-1b.md) | mock-arm overhead confirmed; llama.cpp-arm overhead inconclusive at the ms scale; admission gate G5 passed only under a re-framed criterion after the original target was refuted twice |
| "I converted measurements into capacity decisions." | [`evidence/i6/loop-report.md`](../evidence/i6/loop-report.md), [`reports/capacity-report.md`](../reports/capacity-report.md) | the loop closed and re-measured within +1.3% at its own fitted rate; the 6-replica recommendation itself was never measured, extrapolation only; fleetlab's own G8 gate flags this corpus as a MISS |
| "I deployed and operated the system on Kubernetes." | [`evidence/i5/checklist.md`](../evidence/i5/checklist.md) | **no pod was ever scheduled** (RQ-14, this sandbox cannot run a real kubelet/scheduler) — manifests are authored and validated against a live k3s API server; the full operational behavior (readiness, rolling update, dashboards, traces) ran for real on Docker Compose |
| "I injected failures and documented recovery." | [`evidence/i7/campaign-matrix.md`](../evidence/i7/campaign-matrix.md), [`postmortems/`](../postmortems/) | 11/12 Contract 6 scenarios matched expected semantics; the 12th (slow client) is a real, reproducible defect-shaped finding, published as the lead postmortem, not buried |
| "I contributed reproducible evidence or a fix upstream." | [`oss/log.md`](../oss/log.md) | **not yet true in the public sense** — real local build + reproduction of an upstream gap exist; the upstream comment is drafted, not posted (user-gated, pending action); no public link is claimed anywhere |

## Articles

1. [Double-Queuing in LLM Serving: When a Gateway Destroys Continuous Batching](articles/article-1.md)
2. [Correct Cancellation, Retry and Token Accounting for Streaming Inference](articles/article-2.md)

## Demo

Scripted, runnable walkthrough + a real captured transcript (not a claimed video recording):
[`demo-script.md`](demo-script.md), [`demo-transcript.md`](demo-transcript.md),
[`demo-video-script.md`](demo-video-script.md).

## Reproducibility audit

[`evidence/i8/reproducibility-audit.md`](../evidence/i8/reproducibility-audit.md) — every
headline claim above, checked against its pinned artifact. Result: PASS, with two claims
narrowed (not removed) and two process gaps (`evidence/i1/`, `reports/`) fixed in this same
release, per the audit's own findings.

---

## Portfolio directory conventions (internal; not part of the landing page above)

| File | Content |
|---|---|
| `README.md` (this file) | the landing page |
| `articles/article-1.md`, `article-2.md` | the two required articles |
| `demo-script.md`, `demo-transcript.md`, `demo-video-script.md` | the demo (scripted + a real captured transcript; no video was recorded) |
| `limitations.md` | honest-limitations statement (kept current; published at I8) |

Cross-portfolio ADR index: `docs/adr/README.md`. Rules: every claim here must survive the I8
reproducibility audit (fresh session re-derives it from pinned artifacts) — claims that fail
are removed or re-measured, no exceptions (this pass found 2 to narrow, 0 to remove outright).
Demo keys shown on screen are throwaway and rotated (`docs/security.md`). Demo breadth is the
first thing cut under pressure (`docs/risks.md`); the quickstart and the Scenario E loop are
never cut — neither was.
