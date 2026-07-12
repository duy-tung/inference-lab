# Benchmark report #1b (archived copy) — IB-T010 E2b: queue-cap follow-up + gate G5 re-baseline

**Origin (not generated here):** `inferbench` repo, `docs/evidence/ib-t010/benchmark-report-1b.md`
(243 lines), commit `62c2704997e6c8a2966307ee3d8dbfd16747b631`. Archived, condensed index only
— see the origin for full tables and reproduction commands.

| | |
|---|---|
| Date | 2026-07-11 |
| infergate pin | `6827d8c3d177464c17fae3b4dc6c2c475323333b` (same as report #1) |
| serving-contracts pin | v0.2.0 = `484b449` (9/9 kit-validated, including the 7 report-#1 results carried forward) |
| Provenance | the pre-declared follow-up prescribed by a fresh-context G5 gate verifier after report #1's honest REFUTED verdict |
| Supports | `evidence/i4/checklist.md` §2.3 (cited context for the I4 CPU-fallback admission story); the honest-limitations "benchmark numbers valid only for the pinned config" statement |

## Headline verdict (verbatim from the origin's §1)

| Hypothesis | Verdict | Key numbers |
|---|---|---|
| shrinking the admission queue cap 3→1 (tenant+global, paired; budget/deadline held fixed) pulls the 5×-vs-1× accepted-TTFT p95 degradation under the G5 ≤20% criterion | **REFUTED on the strict ≤20% criterion, again** — degradation **+26.08%** (95% CI [+16.3%, +35.2%]) | companion criteria held: sheds 100% typed (2259/2259); no starvation (single-tenant scope) |

**Second REFUTED result, same root cause** (queue-transit scales with the depth parameter
roughly uniformly across load levels, so no single-knob queue-cap change shrinks the *ratio*).
Per the G5-verifier's explicit prescription, this task did **not** iterate to a third
queue-cap value — the result stops here and gate review paused to the user.

## Program decision on gate G5 (verbatim from the origin, recorded 2026-07-11, post-review)

> After E2 (+25.16%) and E2b (+26.08%) both REFUTED the ≤20% accepted-TTFT-degradation
> target, and a fresh-context gate verifier confirmed every number and the mechanism, the
> program owner re-baselined gate **G5 to PASS** under assumption A9 (source-derived targets
> may be re-baselined after first measurement if infeasible-in-principle)... The **re-framed
> G5 criterion is MET**: at ~5× capacity, load shedding is 100% typed (`503 overloaded` +
> `Retry-After`, verified at three layers), accepted-request queue-wait is **bounded**
> (gateway-side p95 = 134 ms), and there is **no starvation** (single-tenant here;
> multi-tenant fairness p95 shift 0.0–4.6% < 15% at IG-T011). This negative result and its
> mechanism analysis are retained, in full, as the published finding — not superseded or
> hidden.

**Honesty note for this repo's own claims (I8):** any headline portfolio statement that says
"admission control passes G5" must carry this context — G5 passed under a **re-framed**
criterion (bounded queue-wait + typed shedding + no starvation), not the original ≤20%
degradation ratio, which was REFUTED twice and never met. The original ≤20% figure is not
quietly dropped; it stays on record as the target measurement showed to be
architecture-inappropriate for an admission-by-queueing gateway.

## Reproduction

`scripts/ib-t010-e2b-queue-cap.sh` (origin); regenerate any per-point report or the bootstrap
degradation stat with the one-liners in the origin's closing section.
