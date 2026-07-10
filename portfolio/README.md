# Portfolio — narrative artifacts (assembled at IL-T009 / I8)

**Status (2026-07-10): conventions only.** Content is written at IL-T009, when the evidence
it must link to exists. Nothing narrative is drafted before its evidence — the landing page
claims must be traceable, so the artifacts here are evidence-last by design.

## Deliverables (expected files)

| File | Content |
|---|---|
| `landing.md` | the landing page, in the exact order below |
| `articles/article-1.md` | "Double-Queuing in LLM Serving: When a Gateway Destroys Continuous Batching" |
| `articles/article-2.md` | "Correct Cancellation, Retry and Token Accounting for Streaming Inference" |
| `articles/article-3.md` | (optional) "How to Benchmark TTFT, ITL and Goodput Without Lying to Yourself" — first to cut under schedule pressure |
| `demo-script.md` | live demo script — walks the narrative sentence-by-sentence over real evidence |
| `demo-video-script.md` | 5-minute-class video script |
| `limitations.md` | honest-limitations statement (kept current; published at I8) |
| diagrams | architecture diagrams incl. the explicit gateway/engine boundary |

Cross-portfolio ADR index: `docs/adr/README.md`.

## Landing page — this exact order (normative)

1. Positioning statement (the target positioning, `docs/charter.md`).
2. **"Why not LiteLLM / Envoy AI Gateway / GAIE?"** related-work section — accurate, sourced
   from product docs (LiteLLM entry produced via the study track), respectful, and specific
   about what this portfolio does differently (measured gateway/engine boundary,
   evidence-first).
3. Three measured claims, each linked to its report (with manifest + validity block).
4. Architecture diagram with the **explicit gateway/engine boundary** drawn (gateway:
   admission, routing, streaming relay, cancellation, quotas, retry budget; engine:
   continuous batching, per-token scheduling, KV/prefix cache, GPU placement).
5. Quickstart (the ≤15-minute Scenario A path).
6. Honest limitations.
7. The final narrative (verbatim, `docs/charter.md`), each sentence hyperlinked to its
   evidence.

## Honest-limitations statement (baseline content; kept current until I8)

Single-node Kubernetes scale (one GPU node); 1–2 rented GPUs, not fleet-scale production;
simulation ≠ production (fleetlab predictions carry stated uncertainty);
SGLang/PD-disaggregation at study/benchmark level (if at all); no CUDA/kernel work;
multi-region and multi-replica-gateway as design notes only; benchmark numbers valid only
for the pinned hardware/model/engine configurations.

## Rules

- Every claim on the landing page must survive the I8 reproducibility audit (fresh session
  re-derives it from pinned artifacts) — claims that fail are removed or re-measured, no
  exceptions.
- Demo keys shown on screen are throwaway and rotated (`docs/security.md`).
- Demo breadth is the first thing cut under pressure (`docs/risks.md`); the quickstart and
  the Scenario E loop are never cut.
