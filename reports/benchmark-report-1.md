# Benchmark report #1 (archived copy) — IB-T010 E1/E2: gateway overhead + admission value (CPU)

**Origin (not generated here):** `inferbench` repo, `docs/evidence/ib-t010/benchmark-report-1.md`
(303 lines), commit `cc404a6160921be2a7be18dc663be1601a40726a`. This file is an archived,
condensed index — inference-lab never generates new performance claims (`reports/README.md`
rule; `docs/experiments.md`). Read the origin for the full per-point tables, anomaly
discussion, and every reproduction command.

| | |
|---|---|
| Date | 2026-07-11 |
| infergate pin | `6827d8c3d177464c17fae3b4dc6c2c475323333b` (a later commit than this repo's own I3/I4 pin `74f2372` — cited by inferbench, not re-pinned here) |
| serving-contracts pin | v0.2.0 = `484b449` (kit-validated, 60/60 PASS across the six per-point results) |
| llama.cpp pin | `8f114a9b573b69035299f9b924047f53c1e22c7e` (same commit as this repo's `engine-llamacpp` pin) |
| model | `qwen2.5-1.5b-instruct-q4_k_m.gguf`, sha256 `6a1a2eb6…` (same file as this repo's `model-gguf` pin) |
| hardware | 4 vCPU / 15 GB RAM, no GPU, client+gateway+engine co-located (loopback) |
| Supports | `evidence/i4/checklist.md` §2.3 (cited, not re-measured, for the I4 CPU-fallback gateway-overhead pillar) |

## Headline verdicts (verbatim from the origin's §1)

| # | Hypothesis | Verdict | Key numbers |
|---|---|---|---|
| E1-mock | gateway adds non-queue overhead p95 <10 ms / p99 <20 ms vs direct | **CONFIRMED** (mock arm) | paired per-request overhead p50 **+1.04 ms**, p95 **+2.21 ms**, p99 **+2.81 ms** (n=630 pairs); pooled Δp95 **+1.15 ms**; gateway-side queue wait p95 **<1 ms** |
| E1-llama.cpp | same hypothesis, real engine | **INCONCLUSIVE at the ms scale** | run-to-run engine variance (direct p95 ranged 3.70s→1.74s across reps) is 2-3 orders of magnitude larger than the 10ms bound; paired median delta −8.5ms is an order/warming artifact, not a speed-up claim |
| E2 (gate G5) | admission ON at ~5× capacity keeps accepted-request TTFT p95 degradation ≤20% vs ~1× baseline; sheds typed; no starvation | **REFUTED on the strict ≤20% criterion** — degradation **+25.16%** (95% CI [+19.4%, +31.1%]) | companion criteria held: sheds 100% typed `503 overloaded` + `Retry-After` (2067/2067); no starvation (single-tenant scope) |

**The E2 refutation is reported as measured — no re-tuning to pass.** See
`reports/benchmark-report-1b.md` for the follow-up experiment and the program's gate-G5
re-baseline decision.

## Validity block (excerpted from the origin's §4.1 "Threats to validity")

1. Single-host co-location: client, gateway, and engine share one 4-vCPU container over
   loopback — a visible tail-cluster anomaly in the E1-mock direct arm is attributed to this
   (§4.2 of the origin), not to gateway/engine behavior.
2. Mock backend cannot degrade organically (no concurrency limiter) — E2 isolates admission
   mechanics, it does not simulate engine saturation.
3. E1-llama.cpp ran sequential arms against one server instance (order/warming effect) — this
   is exactly why that sub-result is INCONCLUSIVE, not CONFIRMED or REFUTED.
4. No rate sweep in this report (`knee_estimate: null` everywhere) — no saturation claim beyond
   the E2 capacity-probe's declared purpose.
5. One discarded run (E1-llama.cpp attempt 1, gateway process torn down before scrape) — full
   re-run, no per-run cherry-picking; discarded log retained at the origin.

## Reproduction

One command per point, given the pinned binaries built via `git archive` (exact commands,
hypothesis files, and per-point result/report paths: origin §5). Coordinated-omission-safe
basis throughout (`scheduled_send_ts`, serving-contracts `8d81492`/v0.2.0).
