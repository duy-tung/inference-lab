# Study Progress Tracker

Curriculum tracker for the study-to-artifact track. This repo enforces the governing rule:

> **No resource is consumed for its own sake.** Every selected resource has a consuming
> project, an exact artifact, a relevance threshold, a stop condition, and a duplication
> check. **A resource that produces no artifact after two sessions is dropped.** There is no
> generic Raft project and no full-course completion anywhere in this track.

Status values: `not started` / `in progress (session N)` / `artifact done` / `dropped
(reason)`. Every status change is dated in the session log at the bottom. Artifacts live in
their consuming repo; this tracker links to them.

## 1. MIT 6.5840 (selected topics only — no full course, no Raft lab in baseline)

Topics: RPC semantics, at-most-once, linearizability, fault tolerance, cache consistency,
task scheduling, invariant reasoning.

| Artifact | Consumer | Relevance threshold | Stop condition | Status | Link |
|---|---|---|---|---|---|
| API-key revocation consistency ADR (staleness bounds; at-most-once admin semantics) | infergate / IG-T015 | must change the revocation design or its tests | ADR approved | not started | — |
| Tenant-config consistency ADR (snapshot propagation vs read-your-writes) | infergate / IG-T015 | testable consistency statement | ADR approved | not started | — |
| Usage-settlement invariants (exactly-once effect via idempotent settle) | infergate / IG-T008 | each invariant maps to a test | invariants tested | not started | — |
| Multi-gateway scaling design note (state partitioning, quota semantics at N>1) | infergate / IG-T015 | states what breaks at N>1 + trade-offs | note reviewed | not started | — |
| Stale-health-snapshot experiment (quantified routing impact) | infergate / IG-T017 | hypothesis + controlled experiment | report published | not started | — |
| Fault-state machine (request lifecycle incl. failure/cancel edges) | infergate / IG-T017 | covers the full error taxonomy | diagram + tests aligned | not started | — |

Optional micro-lab (MapReduce or KV) only if a demonstrated gap appears above.

## 2. CMU 15-445 (selected topics only)

Topics: concurrency control, MVCC, logging, crash recovery, distributed databases.

| Artifact | Consumer | Relevance threshold | Stop condition | Status | Link |
|---|---|---|---|---|---|
| Versioned configuration-snapshot model (MVCC-flavored semantics doc) | infergate / IG-T004 | informs snapshot/versioning implementation | doc merged with ADR | not started | — |
| Append-only usage ledger design | infergate / IG-T008 | write-path + compaction/retention stated | design implemented | not started | — |
| Idempotent recovery design | infergate / IG-T018 | recovery cases enumerated | design tested | not started | — |
| Crash-recovery integration test | infergate / IG-T018 | test kills the gateway mid-traffic | test green in CI | not started | — |
| Transaction-boundary ADR (snapshot store / ledger / quota state) | infergate / IG-T018 | boundaries explicit | ADR approved | not started | — |

## 3. Papers

| Paper | Depth | Artifact | Consumer | Stop condition | Status | Link |
|---|---|---|---|---|---|---|
| PagedAttention (SOSP'23) | deep (§1–4, §6.1–6.2; skip kernels) | KV-cache memory worksheet + overload-signal notes | fleetlab FL-T003; infergate routing | worksheet cross-checked vs measured memory | not started | — |
| Orca (OSDI'22) | deep (§1–3) | "Why the gateway must not batch" ADR basis | infergate ADR; article #1 | ADR approved | not started | — |
| Sarathi-Serve (OSDI'24) | medium | `max_num_batched_tokens` TTFT/ITL trade-off hypothesis | inferbench IB-T011 | experiment run | not started | — |
| DistServe (OSDI'24) | medium | goodput@SLO definition + when-to-disaggregate decision tree | contracts; fleetlab | definition encoded in schemas | not started | — |
| SGLang/RadixAttention (NeurIPS'24) | medium | shared-prefix workload design + hash-block vs radix note | inferbench workloads | workload designed | not started | — |
| Mooncake (FAST'25) | medium | early-rejection lineage note for admission control | infergate IG-T010 | note done | not started | — |
| FlashAttention (2022) | skim | HBM/SRAM IO-aware note | study notes; interview depth | note done | not started | — |
| Pope et al., Efficiently Scaling Transformer Inference | skim | capacity-math worksheet backbone | fleetlab FL-T003 | worksheet used | not started | — |
| Goodput-critique (arXiv 2410.14257) | skim | stall-rate-beside-goodput reporting rule | inferbench report template | rule encoded | not started | — |
| Speculative decoding (Leviathan et al.) | skim (stretch) | one-page mechanism note | inferbench stretch | note done | not started | — |

## 4. Engine source reading (artifact-first, path-pinned; commits re-verified at execution)

Reading rule: follow one HTTP request's execution path; pin the commit; `git log -- <path>`
before reading (paths drift). **Do-not-read-deeply:** Triton/TensorRT-LLM, TGI
(source-reported as archived 2026-03; as of 2026-07), Ray Serve/KServe controllers,
Kubernetes scheduler internals, CUDA kernels.

| Target | Artifact | Consumer | Stop condition | Status | Link |
|---|---|---|---|---|---|
| vLLM V1 (`vllm/v1/engine/async_llm.py`, `core.py`, `vllm/v1/core/sched/scheduler.py`, `kv_cache_manager.py`, entrypoints) | "Life of a streaming request in vLLM V1" sequence diagram + 2-page `Scheduler.schedule()` annotation + 3 gateway-batching boundary tests | infergate adapter + boundary tests | diagram + tests exist | not started | — |
| llama.cpp `tools/server/` | slot-model vs token-budget note + `-np` parallelism experiment | infergate adapter; I3 | note + experiment done | not started | — |
| Gateway API Inference Extension + llm-d (EPP scorers) | "infergate router vs EPP" comparison + routing-signal design review | infergate routing ADR; OSS track | comparison published | not started | — |
| SGLang scheduler + radix cache (read-only) | vLLM-vs-SGLang caching comparison 1-pager | stretch experiment design | 1-pager done | not started | — |
| LiteLLM (product docs only) | accurate "Why not LiteLLM?" related-work section | **inference-lab portfolio (landing page §2)** | section written | **done** (2026-07-12, IL-T009: `portfolio/README.md` "Why not LiteLLM / Envoy AI Gateway / GAIE?" section; LiteLLM's self-reported overhead baseline re-verified 2026-07-11 by inferbench, docs.litellm.ai/docs/benchmarks, cited for magnitude framing only) | `portfolio/README.md` |

## 5. Books (chapter-selective; never standalone summaries — only inputs to registered artifacts)

| Book | Selected material | Artifact | Consumer | Stop condition | Status |
|---|---|---|---|---|---|
| Designing Data-Intensive Applications | consistency, replication, transactions | inputs to IG-T015/T018 ADRs (cited) | infergate | ADRs approved | not started |
| Systems Performance (Gregg) | methodology + latency analysis | benchmark-methodology checklist addition; USE-method pass over gateway under load | inferbench G4; infergate | checklist merged | not started |
| Google SRE | "Handling Overload", cascading failures, retry budgets | admission/retry-budget ADR + runbook review lens | infergate IG-T010/T013; inferops | ADR approved | not started |
| Database Internals | storage/recovery chapters | ledger + recovery design inputs | infergate IG-T018 | design tested | not started |
| AI Engineering (Huyen) | serving/inference chapters | capacity-report structure review; gap check vs fleetlab reports | fleetlab | review note done | not started |
| Computer Architecture: A Quantitative Approach | memory-hierarchy + accelerator chapters (skim) | GPU-literacy note (bandwidth vs FLOPs) | fleetlab | note done | not started |

## 6. AI Engineering from Scratch (conditional)

Named as a companion by the program brief, but **no copy exists in the workspace**. Entries
are conditional on the user providing it; until then, no entries claim it.

## 7. Agent-runtime design note (optional stretch, design-only)

One short design note (durable tool execution, idempotency keys, approval signals, sandbox
boundary, prompt-injection boundary) — consumed by inference-lab as related-work/interview
depth. Threshold: must sharpen the "what I deliberately did not build" narrative. Stop:
note reviewed. Not a milestone; not implemented. Status: not started.

## 8. Point resources

| Resource | Consumer | Status |
|---|---|---|
| OTel GenAI semantic conventions (pin version; status "Development" as of 2026-07 — re-verify) | contracts trace-attribute section (SC-T005) | not started |
| Kubernetes "Schedule GPUs" docs | inferops GPU-node profile (IO-T005) | not started |
| Modal GPU Glossary / vLLM docs (V1 guide, metrics design, optimization) | capability mapping (IG-T014) + fleetlab profiles | not started |
| Engineering postmortems and provider incident reports | postmortem format for I7 (with the "quality regressions can pass latency SLOs" caveat) | not started |

---

## Session log (artifact-or-drop enforcement: 2 artifact-less sessions ⇒ drop, dated here)

| Date | Resource | Session # | Outcome (artifact progress / drop decision) |
|---|---|---|---|
| *(no study sessions yet)* | | | |
