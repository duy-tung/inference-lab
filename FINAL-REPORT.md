# Final Program Report — composable AI inference systems portfolio

**Status: portfolio tagged `v1.0.0` (this repo, commit `b940f5c`), 2026-07-12. I1–I3 are
user-accepted; I4–I8 are fresh-context verified and recorded as
acceptance-review-pending — this report does not claim user sign-off that has not
happened.** Every number below is cited to a file that exists on disk in this repo (or, where
explicitly marked, to a sibling repo's own archived evidence); none is invented for this
document, per the I8 reproducibility audit's own rule
([`evidence/i8/reproducibility-audit.md`](evidence/i8/reproducibility-audit.md)).

---

## 1. What was built

Six independent repositories, each with exactly one job, integrating only through versioned
contracts and released artifacts — never a shared library, never a source checkout of a
sibling repo. Together they implement, measure, operate, and honestly report on a streaming
LLM-inference serving path: a Go gateway in front of a real CPU inference engine
(llama.cpp + Qwen2.5-1.5B), a coordinated-omission-safe Go/Python load-generation and analysis
system, a Python capacity simulator whose recommendation was applied for real and
re-measured, and a Docker-Compose-based operational stack with a 12-scenario fault campaign —
closing with a portfolio release that survived its own adversarial reproducibility audit.

| Repo | Release / pin | Role |
|---|---|---|
| [`serving-contracts`](https://github.com/duy-tung/serving-contracts) | **v1.0.0** frozen (tag `507208b`) | Versioned OpenAPI + JSON Schema contract bundle; no runtime logic. Freeze is prose-only over v0.2.0 (zero shape/validation-outcome changes); I1 re-run GREEN across all four consumers on the frozen bundle. |
| [`infergate`](https://github.com/duy-tung/infergate) | **v0.1.0** released image (commit `49236a3`) | The one gateway (Go): streaming/SSE relay, cancellation propagation, tenancy + usage settlement, admission control, P2C routing, retry budget + circuit breaker, config snapshots + drain. |
| [`inferbench`](https://github.com/duy-tung/inferbench) | no tagged release yet; pinned by commit (e.g. `62c2704` for the fault-campaign client) | The one load-generation + benchmark-analysis system (Go client + Python analysis): coordinated-omission-safe open-loop scheduler, pooled-percentile reporting, methodology gate G4. |
| [`fleetlab`](https://github.com/duy-tung/fleetlab) | no tagged release yet; pinned at commit `dd05e7d` (FL-T009) | Explainable capacity/autoscaling/cost simulator (Python); G8 holdout-validated fitted profiles; emits the Contract-7 capacity recommendation the I6 loop closes on. |
| [`inferops`](https://github.com/duy-tung/inferops) | no tagged release yet; pinned at commit `a07fd2f`/`89871a6` | The one deploy/observability/chaos/runbook repo: Docker Compose operational stack + Kustomize k8s manifests (k3s-API-validated), 12-scenario fault campaign, 10 runbooks. |
| [`inference-lab`](https://github.com/duy-tung/inference-lab) | **v1.0.0** (this repo, tag on commit `b940f5c`) | Integration hub: I1–I8 evidence archive, pins/compatibility matrices, quickstart, portfolio narrative — this report. |

---

## 2. Headline measured claims

| # | Claim | Measured number | Evidence path + commit | Milestone |
|---|---|---|---|---|
| 1 | 100-concurrent-stream integrity | **154 concurrent** in-flight streams (≥100 required), **0 frame-mixing violations**, 2736/2736 events ok | [`evidence/i2/checklist.md`](evidence/i2/checklist.md) item 3; raw `evidence/i2/raw/runs/concurrency-100/`; `evidence/i2/logs/checks.log` line 25 (`inference-lab@d0a858c`) | I2 |
| 2 | 3-point cancellation, mock backend, composed stack | pre-first-token deltas 0.247–0.573 ms; mid-stream 0.310–0.724 ms; near-completion 0.318–0.638 ms — all sub-millisecond against a 100 ms bound | [`evidence/i2/checklist.md`](evidence/i2/checklist.md) item 4; `evidence/i2/raw/runs/cancel-*/` (`inference-lab@d0a858c`) | I2 |
| 3 | 3-point cancellation, **real llama.cpp, narrowed scope (honest)** | Composed-stack + pinned model: **1 point** (mid-stream) verified within the 2.5 s bound on two independent runs (deltas −32.2 ms…+83.9 ms and −29.4 ms…+79.3 ms). A separate adapter-level test covers all 3 points (queued 2.6–645 µs; pre-first-token 0.77–2.19 s; mid-stream 1.25–5.24 ms) but against an **unpinned random-weight test GGUF**, not the pinned model. No 3-point/pinned-model/composed-stack result exists in one place — stated plainly rather than rounded up. | [`evidence/i3/checklist.md`](evidence/i3/checklist.md) item 5; [`evidence/i4/checklist.md`](evidence/i4/checklist.md) §2.2; [`portfolio/limitations.md`](portfolio/limitations.md) §2 | I3/I4/I7 |
| 4 | CO-safe benchmark methodology | `scheduled_send_ts`-basis raw events (coordinated-omission-safe), enforced by schema + client + tests; G4 methodology gate **passed an adversarial audit** (5 bypass attacks all correctly refused) | [`evidence/i8/reproducibility-audit.md`](evidence/i8/reproducibility-audit.md) claim #4; `serving-contracts@8d81492` `schemas/raw-event.schema.json` (cited, not re-derived) | I2/I3 (G4, program-state) |
| 5 | Gateway overhead, mock arm | Paired per-request TTFT overhead p50 **+1.04 ms**, p95 **+2.21 ms**, p99 **+2.81 ms** (n=630 pairs) — **CONFIRMED** vs the p95<10ms/p99<20ms SLO | [`reports/benchmark-report-1.md`](reports/benchmark-report-1.md) (origin: `inferbench@cc404a6`) | I2/I4 (IB-T010) |
| 6 | Gateway overhead, real llama.cpp arm | **INCONCLUSIVE at the ms scale** — engine run-to-run variance (3.70s→1.74s across reps) is 2–3 orders of magnitude larger than the 10 ms bound under test; reported as a non-result, not rounded to a pass | [`reports/benchmark-report-1.md`](reports/benchmark-report-1.md) §"E1-llama.cpp" | I4 (IB-T010) |
| 7 | Admission control / gate G5 at ~5× capacity | Original ≤20% accepted-TTFT-degradation-ratio target **REFUTED twice**: **+25.16%** (CI [+19.4,+31.1]%) on the first run, **+26.08%** (CI [+16.3,+35.2]%) on a prescribed queue-cap follow-up, same root cause (queue-transit scales uniformly with load). Gate then **re-baselined to PASS** under a different, still-rigorous criterion: 100% typed shedding + `Retry-After` (2067/2067 then 2259/2259), bounded queue-wait (p95 **134 ms**), no starvation. The original ratio target is disclosed as REFUTED, not deleted. | [`reports/benchmark-report-1.md`](reports/benchmark-report-1.md), [`reports/benchmark-report-1b.md`](reports/benchmark-report-1b.md) | I4 (IB-T010, G5) |
| 8 | Noisy-neighbor multi-tenant fairness | p95 shift **0.0–4.6%** vs a <15% target (weighted-round-robin 30:10 + aging) | [`reports/benchmark-report-1b.md`](reports/benchmark-report-1b.md) (cites IG-T011); [`evidence/i7/campaign-matrix.md`](evidence/i7/campaign-matrix.md) noisy-neighbor observation run (tenant B held p50 122ms/p95 126ms throughout tenant A's flood) | I4/I7 |
| 9 | Crash recovery | **10/10 SIGKILL** runs identical: 36/36 ledger rows, **0 lost, 0 duplicated**, in-flight failures observed within ≤4.4 ms, no hangs. **This is infergate's own evidence, cited not archived in this repo** — no inference-lab evidence/i*/ directory reproduces this test. | infergate `docs/evidence/ig-t018/` (commit `f511d89`, sibling repo — see [`docs/adr/README.md`](docs/adr/README.md) ADR-0003 for the accompanying design record) | infergate-internal (IG-T018), not a numbered inference-lab milestone |
| 10 | Config reload / rolling update under traffic | **0 dropped streams** every time it was tested: rolling update 27 short + 3 streaming requests, 0 client-visible errors; config-rollout 0/24 short + 0/4 streaming dropped across rollout+rollback; fault-campaign scenario 8, 3 independent runs, 0/71 short + 0/12 stream dropped cumulative, `config_version` v1→v7 monotonic | [`evidence/i5/checklist.md`](evidence/i5/checklist.md) item 3; [`evidence/i7/campaign-matrix.md`](evidence/i7/campaign-matrix.md) row 8 | I5/I7 |
| 11 | I6 capacity-feedback loop (**the headline**) | fleetlab predicted **33.159±1.105 rps/replica**; re-measured at the identical fitted rate (37.8072 rps offered): **33.583 rps achieved = +1.3%**. Divergences published, not hidden: at every higher rate measured, the number leans toward inferbench's own **unpublished 37.925 rps/replica** estimate (1–5% off) over the published fit (9–13% off); the **6-replica recommendation itself was never measured** — only 1→2 was applied (extrapolation only for 6, both land inside/above the stated interval but are not a measurement); `inference_requests_in_flight` beat the recommended `inference_queue_depth` signal (+6.1s lag vs +64.4s) for this shallow-queue config | [`evidence/i6/loop-report.md`](evidence/i6/loop-report.md) (fleetlab@`dd05e7d`, inferops@`f5fdd86`/`89871a6`) | I6 |
| 12 | 12-scenario fault campaign | **12/12 scenarios executed**; **11/12 matched expected semantics** (6 fully clean + 5 matched-with-documented-deviation); **1/12 (scenario 4, slow client) is a real, reproducible defect**: an 8 s full stall was not closed by the gateway despite a configured 3 s write-deadline (2.6× the deadline) — surfaced as the lead postmortem, not buried | [`evidence/i7/campaign-matrix.md`](evidence/i7/campaign-matrix.md); [`postmortems/pm-001.md`](postmortems/pm-001.md) | I7 |
| 13 | Quickstart | **2m 08s** warm-cache run, **35s** forced-Docker-rebuild run — both against a ≤15-minute, GPU-free target (7×–25× headroom); Go module/build cache warm-cache caveat disclosed | [`quickstart/timing-log.md`](quickstart/timing-log.md) | I8 |

---

## 3. Milestone status

| Milestone | Scope | Status | Verifier |
|---|---|---|---|
| I1 | Contract compatibility, all 4 consumers vs frozen bundle | **GREEN**, archived (re-entrant; re-runs every contract release) | orchestrator archival pass (IL-T008), 2026-07-12 |
| I2 | Scenario A — local request path (mock engine) | **ACCEPTED** (user review 2026-07-11; deviation D-001, no PostgreSQL usage write, recorded) | fresh-context verifier (task `a9929d1`) + user |
| I3 | Scenario B — local inference, first real engine (llama.cpp) | **ACCEPTED** (user review 2026-07-11; one open, unreproduced cancellation-log-census observation recorded) | fresh-context verifier (task `a150717`) + user |
| I4 | Scenario C — GPU inference | **CPU-fallback deviation recorded** (D-005) — GPU acceptance explicitly NOT claimed; llama.cpp variant + sibling-repo evidence stand in | orchestrator evidence-assembly pass, 2026-07-12 |
| I5 | Scenario D — operational stack | **VERIFIED, acceptance-review-pending** — every number re-derived exactly; RQ-14 compose-pivot deviation honestly stated | fresh-context verifier (task `a36091f`), Opus |
| I6 | Scenario E — capacity-feedback loop (central story) | **ACCEPTED, acceptance-review-pending** — loop causality confirmed from raw events; all 4 divergences headline-published | fresh-context verifier (task `aabbbf4`), Opus |
| I7 | Failure campaign (12 scenarios) | **ACCEPTED, acceptance-review-pending** — postmortems traced to raw evidence; a roll-up-count bug both verifiers caught was fixed (`inference-lab@e347e92`) | fresh-context verifier (task `ad86b7c`), Opus |
| I8 | Portfolio release | **Reproducibility audit PASS** (2 claims narrowed, 2 process gaps fixed, 0 removed); acceptance-review-pending | Opus fresh-context (audit-of-the-audit) |

---

## 4. Honest limitations

Full statement: [`portfolio/limitations.md`](portfolio/limitations.md). Summary:

- **Compose, not Kubernetes.** No pod was ever scheduled anywhere in this program — this
  sandbox cannot run a CRI-based container runtime under a real kubelet/scheduler (RQ-14,
  proven at the runc/nsexec level). What is real: Kustomize manifests authored and validated
  against a live k3s API server (schema validation, defaulting, controller reconciliation to
  etcd), plus the full operational behavior (readiness, rolling update, dashboards, traces)
  demonstrated on Docker Compose. "Deployed and operated on Kubernetes" is true only in this
  qualified sense.
- **CPU/llama.cpp, never GPU/vLLM (gate G6).** No GPU was rented; `infergate`'s vLLM adapter
  and `inferbench`'s GPU experiment set were never built or run. Every engine number in this
  portfolio characterizes llama.cpp CPU inference under `-np 2 -c 8192 -t 4`. No vLLM number
  exists anywhere in `pins/pins.yaml` or any evidence file.
- **One model throughout:** Qwen2.5-1.5B-Instruct GGUF Q4_K_M (`sha256:6a1a2eb6…`). Every
  benchmark number is conditioned on this exact file.
- **Simulation ≠ production.** fleetlab's G8 holdout gate is a documented **MISS** (12.6–20.4%
  error) for the exact `ib-t010` corpus the I6 loop's 6-replica recommendation was fitted from;
  the loop's +1.3% re-measurement is real but does not retroactively validate the
  never-measured 6-replica extrapolation.
- **v1.0.0 was tagged under standing pre-authorization**, surfaced to the user for retroactive
  objection rather than pre-approved tag-by-tag (same pattern as `infergate`'s v0.1.0 image
  releases consumed by `inferops` without source checkout).
- **Benchmark numbers are valid only for the pinned hardware/model/engine/workload
  configuration** they were measured under (`compatibility/matrix.md`'s comparability rule) —
  a config differing in any of model revision, quantization, engine flags, hardware, or
  workload seed is not comparable to any number in this portfolio.

---

## 5. OSS evidence

- **Built and tested `llm-d-router`** (commit `30385f8e`) from source: clean build, 116/121
  testable packages green (5 correctly require infra not present in this sandbox — e2e/kind
  cluster, envtest binaries, a coordinator image, a live kubectl target).
- **Reproduced upstream issue #1625** locally: the `fairness_id` unbounded-cardinality gap, not
  covered by the issue's own linked PR #1909, with a runnable Go test as evidence.
- **Upstream comment DRAFTED, not posted** — `oss/drafts/2026-07-11-llm-d-router-1625-comment.md`.
  Posting requires user review and action per the program's own standing gate ("the user
  reviews every submission before posting"); this has not happened. **No public interaction is
  claimed anywhere.** This is the documented contingency degradation per
  `portfolio-planning/09-open-source-track.md` §4, exercised honestly rather than
  overclaimed. Full accounting: [`oss/log.md`](oss/log.md).

---

## 6. Study-track artifacts

Cross-portfolio ADR index: [`docs/adr/README.md`](docs/adr/README.md). The 6.5840/15-445-flavored
consistency and recovery work lives in `infergate`'s own ADR set (accepted, user-reviewed
2026-07-11 for three of them under RQ-13):

- `infergate/docs/adr/0001-api-key-revocation-consistency.md` — bounded-staleness revocation
  consistency (measured 1.011s/74ms vs a 5s bound).
- `infergate/docs/adr/0003-transaction-boundaries.md` — transaction boundaries across the
  snapshot store, usage ledger, and quota state.
- `infergate/docs/adr/0004-retry-budget.md` — retry budget and the pre-first-token-only retry
  invariant.
- `infergate/docs/adr/0006-tenant-config-consistency.md` — tenant-config consistency.
- `infergate/docs/adr/0007-multi-gateway-design.md` — multi-gateway (N-replica) design note.
- The **stale-health-snapshot experiment** (`IG-T017`): a monotonic staleness→impact curve
  (20ms→15 misrouted requests/0.59% error, up to 3s→4162 misrouted/24.4% error), showing the
  shipped 200ms default carries roughly 2× headroom against a 5% error threshold.

**Note on this repo's own tracker:** [`study/tracker.md`](study/tracker.md) still shows most
6.5840/15-445 rows as "not started" — this is a stale status column in inference-lab's own
tracking file; the underlying artifacts were in fact delivered in `infergate`, confirmed
directly against `docs/adr/README.md`'s cross-portfolio index above. Flagged here rather than
silently left inconsistent.

---

## 7. Reproducibility

- **Quickstart ≤15 minutes, GPU-free:** 2 timed runs, 2m08s (warm cache) and 35s
  (forced Docker rebuild, Go cache still warm), both well under target — full methodology and
  honesty caveats (cache warmth, one Go-module-download risk factor for a genuinely cold
  machine) in [`quickstart/timing-log.md`](quickstart/timing-log.md).
- **Reproducibility audit passed:** [`evidence/i8/reproducibility-audit.md`](evidence/i8/reproducibility-audit.md)
  independently re-read (not merely cited) the raw artifact behind every headline claim above.
  Result: **PASS**, with 2 claims narrowed (cancellation scope on the real engine; gate-G5
  "pass" restated as a re-framed-criterion pass) and 2 process gaps fixed in the same release
  (`evidence/i1/` and `reports/` had been empty/missing through I2–I7) — **0 claims removed
  outright**. One disclosed audit-scope limitation: the OSS build/reproduction claims (#14–15
  in that audit) were not independently re-run this pass (re-cloning and re-building an
  external ~2-year-old Go repo was judged out of scope for a reproducibility audit of this
  portfolio's own artifacts).
- Every headline number in §2 above traces to a pinned artifact under `evidence/i<N>/` or
  `reports/`, cross-referenced against `pins/pins.yaml` (validator green, 28+ entries) and
  `compatibility/matrix.md`'s comparability rule.

---

*Report assembled 2026-07-12 from this repository's own evidence tree at commit `b940f5c`
(tag `v1.0.0`). No number in this document was generated by this report — every figure above
is a citation into an existing, dated file.*
