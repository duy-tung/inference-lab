# Double-Queuing in LLM Serving: When a Gateway Destroys Continuous Batching

*Part of the inference-systems portfolio. Evidence: `infergate docs/adr/0005-why-the-gateway-must-not-batch.md`, `reports/benchmark-report-1.md`, `evidence/i2/checklist.md`. As of 2026-07 — engine internals referenced here (vLLM V1's scheduler) are source-verified at a pinned commit; re-verify before relying on them for a different engine version.*

## The anti-pattern

A modern inference engine — vLLM V1 is the reference point this program built against
(source-verified, pinned commit, `IG-T014` re-verification pending since the GPU path was
never opened here) — already runs a scheduler. Continuous batching admits new requests into
the running batch every decode step, using per-step token budgets and live KV-cache occupancy
that only the engine can see. There is no separate "prefill phase" waiting for a batch to
fill; work streams in continuously.

The tempting mistake is to put a *second* scheduler in front of it: hold requests briefly at
the gateway to batch them, pace dispatch by an estimated token budget, or route by guessing at
KV-cache state from the outside. Every one of these decisions adds delay in front of an engine
that is already deciding, every step, exactly how much work it can absorb — with strictly more
information than the gateway will ever have. The result is not throughput help; it's
double-queuing, and it shows up as pure added latency with none of the batching benefit,
because the engine's own scheduler still has to re-derive the same decision the gateway just
delayed making.

## The rule this portfolio built to

`infergate` (this program's one gateway) encodes the boundary as a hard architectural rule,
enforced by three CI tests (`ADR-0005`):

1. **No batch formation.** A dispatched request is forwarded immediately whenever the target
   backend has in-flight headroom. The gateway's queue is non-empty *only* when every eligible
   backend is already at its per-backend in-flight limit — i.e., the gateway queues for
   admission control and fairness, never to accumulate a batch.
2. **No token budgets in the gateway.** Admission and quota arithmetic use request-level
   estimate-and-settle accounting (see article #2); nothing paces dispatch by a per-step token
   count, because that is the engine's own scheduling variable.
3. **No KV/prefix-cache modeling in the gateway.** Backend pressure is read from engine-published,
   capability-mapped metrics and normalized to a scalar signal — never inferred by simulating
   what the engine's cache must look like.

The gateway's queue exists for one job only: tenant fairness and overload protection ("full
but not choking"), not throughput optimization. That's a real trade-off, stated plainly: a
KV-aware placement scorer (the kind Kubernetes' Gateway API Inference Extension / `llm-d-router`
EPP attempts — this portfolio's own OSS-track target, `oss/log.md`) is deliberately left on the
table, because it needs engine-internal state that belongs on the engine side of the boundary,
not bolted onto a general-purpose gateway.

## What "no double-queuing" looks like, measured

A design principle is a claim until it's measured. `inferbench`'s IB-T010 E1 experiment put a
number on it: with the gateway sitting directly in front of a deterministic mock engine at a
realistic ~300ms TTFT / 30ms ITL operating point, the **paired per-request overhead the
gateway adds is p50 +1.04 ms, p95 +2.21 ms, p99 +2.81 ms** (n=630 pairs, 3 repetitions) —
comfortably inside the program's own p95<10ms/p99<20ms non-queue-overhead target. Gateway-side
queue wait stayed under 1ms throughout. That is what "the gateway forwards immediately when
there is headroom" looks like from the outside: a couple of milliseconds of pure plumbing
overhead, not a second scheduling delay stacked in front of the engine's own.

The same experiment run against the real, CPU-only llama.cpp engine came back
**INCONCLUSIVE at the millisecond scale** — not because the boundary broke, but because
llama.cpp's own run-to-run variance on a shared, contended 4-vCPU host (direct-arm p95 ranged
3.70s → 2.32s → 1.74s across repetitions) is two to three orders of magnitude larger than the
10ms bound being tested. This is reported honestly as inconclusive, not rounded up to
"confirmed" — full detail and the anomaly discussion: `reports/benchmark-report-1.md` §2.2,
§4.2.

## Why this matters for the "why not X" question

Kubernetes' Gateway API Inference Extension (and its EPP successor, now living at
`llm-d/llm-d-router`) takes the opposite trade-off deliberately: it *does* attempt
inference-aware, KV-affinity-informed routing decisions from outside the engine, accepting the
staleness of an external view in exchange for cluster-wide load balancing across many engine
replicas — a different problem than the one a single gateway in front of one engine instance
is solving here. Neither choice is wrong in isolation; they optimize for different scopes
(single-engine correctness and measured overhead vs. cluster-wide placement). This portfolio's
contribution is the measured, disciplined version of the narrower scope: a gateway that
provably does not become a second scheduler, with a number attached to exactly how little
overhead that discipline costs.

## Honest caveat

This article's engine-side reasoning (vLLM V1's scheduler design) is source-verified but was
never load-tested in this program — gate G6 (GPU session) was deferred, so every number cited
above is CPU/llama.cpp or mock-engine, never vLLM. See `portfolio/limitations.md` §1-2.
