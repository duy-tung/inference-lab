# I4 — GPU inference: CPU-fallback acceptance checklist (Scenario C, IL-T004)

Recorded 2026-07-12. This is an **evidence-assembly** record, not a new measurement session:
per the resource constraint in effect this session (other compute-heavy jobs running on this
host) and per the GPU-deferral decision below, nothing in this document was newly measured.
Every number is a reference to evidence already published in this repo (`evidence/i3/`) or in
sibling repos (`infergate`, `inferbench`), cited by path and commit. Nothing is copied or
re-derived; see §2 for the pointers and §4 for path-existence spot checks.

**Overall: I4's normative (GPU) acceptance is NOT claimed. This is the documented
CPU-fallback deviation the scenario's own README and `docs/tasks.md` IL-T004 anticipate
("I4 accepted, **or** CPU-fallback deviation recorded"). The llama.cpp variant proven at I3,
plus two pieces of additional real-engine evidence from sibling repos (infergate IG-T005,
inferbench IB-T010 E1), stands in as the measured baseline. §3 lists exactly what remains
deferred and unclaimed.**

## 0. Why this is a CPU-fallback record, not a GPU acceptance

- Gate **G6** (GPU session discipline) requires, before any GPU spend: a written hypothesis,
  full config manifest, auto-stop script, and budget alert — none of which exist here because
  no GPU session was run.
- **User decision (2026-07-11):** defer G6 / no GPU rental for I4. This task executes the
  scenario C README's own contingency ("Failure handling & CPU fallback": "if GPU access is
  blocked, the llama.cpp variant (Scenario B) becomes the measured baseline; the deviation,
  its consequences for portfolio claims, and the repositioning are recorded — never silently
  substituted").
- Verified live this session that the GPU-path prerequisites genuinely do not exist yet (not
  just "not chosen"):
  - `infergate` `docs/tasks.md`: `IG-T014 | vLLM adapter (GPU gate G6) | M9 | ... | not started`
    (infergate repo at commit `f362ceb7835c91182f19645a705de66af3017c82`).
  - `inferbench` `docs/tasks.md` §`IB-T011 — Experiment set 2 (GPU): vLLM behavior`: not
    executed (inferbench repo at commit `62c2704997e6c8a2966307ee3d8dbfd16747b631`).
  - `pins/pins.yaml`'s header comment still lists `engine-vllm` under "Entries still expected
    ... (needed for I4)" — unpinned.
- Full repositioning rationale: §5 below (program charter §7).

## 1. Acceptance checklist (executed copy of `scenarios/c/README.md`'s checklist)

| # | Criterion (verbatim from `scenarios/c/README.md`) | Outcome | Evidence reference |
|---|---|---|---|
| 1 | G6 satisfied **before** the session: written hypothesis + full config manifest + auto-stop script + budget alert; session plan pre-approved by the user | **DEFERRED** — no GPU session was attempted, so there is nothing to satisfy G6 against; G6 remains the gate for any future GPU session | user decision 2026-07-11 (this task's mandate); `scenarios/c/README.md` §"GPU session discipline" |
| 2 | Stack deployed from pinned artifacts: vLLM version/commit, model checkpoint + quantization + tokenizer, driver/CUDA, instance type all recorded in pins | **DEFERRED** — none of these pins exist | `pins/pins.yaml` header comment ("Entries still expected ... engine-vllm ... needed for I4"); infergate `IG-T014` not started; inferbench `IB-T011` not executed |
| 3 | Streaming verified end-to-end via gateway against vLLM on GPU | **CPU-FALLBACK-DEVIATION** — streaming verified end-to-end via gateway against **llama.cpp (CPU)** instead, at I3 | §2.1 below |
| 4 | **Cancellation verified via engine metrics**: KV usage / running-count drop within the declared bound after client disconnect; metrics export archived | **CPU-FALLBACK-DEVIATION** — verified via **llama.cpp** engine-side observables (`/slots` polling + `cancel task` server log), not vLLM KV-cache-usage/running-count | §2.2 below |
| 5 | **Gateway-overhead comparison** (direct vs via-gateway) measured with **≥3 runs per point**; comparability rule respected | **CPU-FALLBACK-DEVIATION, mixed verdict, reported honestly** — mock arm **CONFIRMED**, llama.cpp arm **INCONCLUSIVE at the ms scale** (engine-noise floor 2–3 orders of magnitude above the bound under test) | §2.3 below |
| 6 | Session **auto-stop confirmed in the session log**; spend within budget alert | **DEFERRED** — no GPU session ran; no spend to confirm | — |
| 7 | All artifacts carry the full manifest | **PARTIAL, honestly** — every cited CPU-path report/result carries its full manifest (engine commit+flags, model+tokenizer, hardware, gateway+config version, warm-up policy, repetition count, hypothesis); the GPU-specific manifest fields (driver/CUDA, instance type, vLLM version/commit) do not exist because no GPU session ran | `evidence/i3/reports/*.report.md`; inferbench `docs/evidence/ib-t010/*.report.md` (commit `6a3fb5347b9e0d21fa56c63836bc242a7d7d51e2`) |
| 8 | Evidence archived: session log, GPU benchmark report, cancellation-verification metrics export, GPU session manifest, this checklist → `evidence/i4/` | **CPU-FALLBACK-DEVIATION** — no GPU session log / GPU benchmark report / GPU session manifest exist (none ran); this checklist + its references stand in, per the documented fallback | this file; `evidence/i4/notes.md`; `evidence/i4/pins-snapshot.yaml` |
| 9 | Reviewed (user acceptance) — or the CPU fallback deviation recorded (below) | **CPU-FALLBACK-DEVIATION RECORDED** | this document; `docs/implementation-notes.md` D-005; user decision 2026-07-11 deferring G6/GPU rental |

## 2. Evidence assembled (the four pillars)

### 2.1 llama.cpp inference through the gateway (already proven at I3)

`inferbench → infergate → llama.cpp`, real Qwen2.5-1.5B-Instruct GGUF Q4_K_M, composed and
measured at IL-T003:

- `chat-short-cpu`, v1.0.0, seed 1003001: via-gateway arm 40/40 ok, 0 errors, 0 shed, wall
  10m6.6s; paired engine-direct arm (same workload/seed, fresh engine) 40/40 ok, wall
  10m15.1s.
- `shared-prefix-cpu`, v1.0.0: via-gateway arm 25/25 ok, 0 errors, 0 shed, wall 10m36.1s.
- Three schema-valid benchmark reports generated (report #0, methodology shakedown), each
  carrying the mandatory manifest + validity block + threats-to-validity block.

Source (reference only): `evidence/i3/checklist.md` items 2–4; `evidence/i3/raw/runs/`
{`chat-short-cpu-gw`, `chat-short-cpu-direct`, `shared-prefix-cpu`}; `evidence/i3/reports/`
{`i3-chat-short-cpu-direct`, `i3-chat-short-cpu-gw`, `i3-shared-prefix-cpu`}`.report.md`;
inference-lab commit `61132b2` (I3 accepted).

### 2.2 Cancellation verified against the real engine

Two independent, complementary sources, both against the **same pinned llama.cpp commit**
(`8f114a9b573b69035299f9b924047f53c1e22c7e`, pins.yaml `engine-llamacpp`):

**(a) infergate IG-T005 — adapter/unit level, gateway in front of a real `llama-server`.**
3-point cancellation measured over 6 recorded race-enabled runs:

- **queued:** client vanishes during body read → gateway accounts `queued` in
  **2.6 µs–645 µs**; engine provably untouched (0 busy slots) — never dispatched.
- **pre-first-token:** ~3600-token nonce-fresh prompt holds the engine in prefill; cancel →
  slot freed in **0.77 s–2.19 s** (load-dependent) — the spread is the engine's own
  abort-detection granularity (disconnects noticed at the next decode-batch boundary, so an
  early-batch cancel waits out that batch); the discriminating evidence is the engine's
  `cancel task` log line plus gateway `pre_first_token` accounting.
- **mid-stream:** 3 chunks read, cancel during ~3500-token generation → slot freed in
  **1.25 ms–5.24 ms** (probe's raw-socket baseline ≈ 53 ms), `cancel task` logged.

Source (reference only): infergate `docs/implementation-notes.md`, log entry
"2026-07-10 — IG-T005: llama.cpp adapter (M4)" and its row in the "Evidence links (per task)"
table; `internal/backend/llamacpp/llamaserver_test.go`; infergate commit
`74f2372acea62645fa3c1d91689574ea9de7c589` (repo currently at
`f362ceb7835c91182f19645a705de66af3017c82`).

**Caveat (honesty):** IG-T005's cancellation measurement used an **8.9 MB locally authored
random-weight llama-architecture GGUF** (infergate deviation D2, `docs/implementation-notes.md`
there), **not** the pinned `model-gguf` (Qwen2.5-1.5B-Instruct) artifact — the network
allowlist at the time blocked model downloads. D2's own rationale (engine wire protocol, SSE
framing, slot semantics, and cancellation-release observability are engine code, independent
of weight quality) is why this is still valid *engine-level* cancellation evidence, but it is
**not** evidence about the specific pinned model file. (b) below is, and uses the real model.

**(b) I3's own cancellation arm — composed-stack level, real Qwen2.5-1.5B-Instruct model,
full `inferbench → infergate → llama.cpp` chain.** Engine slot-release verified within the
declared 2.5 s bound on **two independent runs**: the original run (20/20 client-canceled
requests, deltas −32.2 ms to +83.9 ms vs. bound) and a same-session recheck (20/20, deltas
−29.4 ms to +79.3 ms). One run's automated log-census invariant (`cancel task` log-line count
vs. client-canceled count) showed a 21-vs-20 mismatch that did **not** reproduce on retry —
recorded as an open, unreproduced observation, not a resolved defect.

Source (reference only): `evidence/i3/checklist.md` item 5; `evidence/i3/raw/runs/`
{`cancel-mid-stream-cpu` (final), `cancel-mid-stream-cpu-attempt1` (preserved original)};
`evidence/i3/logs/llama-server-cancel.log`; inference-lab commit `61132b2`.

Both are cited together because they show the **same pinned engine commit's** cancellation
behavior at two levels of granularity (adapter unit test vs. full composed-stack workload),
which is stronger than either alone — but neither is vLLM/GPU evidence (§3).

### 2.3 Gateway-overhead comparison (direct vs via-gateway)

Source: inferbench `docs/evidence/ib-t010/benchmark-report-1.md` ("Benchmark report #1 —
IB-T010, Experiment set 1 (CPU): gateway overhead + admission value"), commit
`6a3fb5347b9e0d21fa56c63836bc242a7d7d51e2` (inferbench repo currently at
`62c2704997e6c8a2966307ee3d8dbfd16747b631`). Both arms below ran **3 repetitions per point**
with a paired same-workload/same-seed design (direct vs via-gateway is the single declared
variable), satisfying the "≥3 runs/point" requirement.

**Honesty note on pins:** this experiment's own manifest header records `infergate pin
6827d8c3d177464c17fae3b4dc6c2c475323333b` — a **later** infergate commit than the one pinned
in this repo's Scenario B / I3 pin set (`infergate-binary` @ `74f2372`). It shares the same
llama.cpp commit (`8f114a9`) and the same pinned model file (sha256 `6a1a2eb6…`) as I3, but
ran its own (single-slot, `-np 1 -c 4096`) engine flags for the llama.cpp arm, distinct from
Scenario B's `-np 2 -c 8192` configuration. It is cited here as sibling-repo evidence (the
same archiving pattern this repo uses for I1/I5/I7) — **not** as proof about the specific
`infergate-binary` pin `pins/pins.yaml` records for I3/I4 (see §4).

- **Mock arm — CONFIRMED.** Paired per-request TTFT overhead (gateway − direct, n=630 pairs):
  p50 **+1.04 ms**, p90 +1.96 ms, p95 **+2.21 ms**, p99 **+2.81 ms**, max +28.8 ms (10.3% of
  pairs negative — run noise). Pooled-delta basis: Δp95 **+1.15 ms**, Δp99 −13.5 ms (a
  direct-arm tail anomaly, not a gateway effect). Gateway-side queue wait p95 <1 ms. **Verdict
  vs. the <10 ms p95 / <20 ms p99 target: CONFIRMED on both the paired and pooled bases.**
  Source: `docs/evidence/ib-t010/benchmark-report-1.md` §1, §2.1; `e1-mock-overhead.json`;
  `ib-t010-e1-mock-{direct,gateway}.report.md`.

- **llama.cpp arm — INCONCLUSIVE at the ms scale (reported honestly, not forced to a
  verdict).** 45 requests/rep at 0.4 rps, single slot, 111 pooled events/arm, 0 errors.
  Run-to-run engine variance (per-rep direct-arm p95: 3.70 s → 2.32 s → 1.74 s) is 2–3 orders
  of magnitude larger than the 10 ms bound under test; the gateway arm measured *lower* at
  every percentile (paired median delta **−8.5 ms**, paired p95 **+0.45 s**, 57.7% of pairs
  negative) — attributed to the arms running sequentially against one warming server
  instance, not a genuine gateway speed-up (the same single-host-contention artifact family as
  I3's own chat-short overhead diagnostic, `evidence/i3/checklist.md` item 4). The report's own
  words: "the honest positive statement this arm supports: routing llama.cpp traffic through
  infergate produced no detectable added latency at the engine's own variance scale — and the
  mock arm ... is the resolving instrument for the ms-scale claim."
  Source: `docs/evidence/ib-t010/benchmark-report-1.md` §1, §2.2; `e1-llamacpp-overhead.json`;
  `ib-t010-e1-llamacpp-{direct,gateway}.report.md`.

### 2.4 Failover mock↔llama.cpp (already proven at I3)

`chat-short-failover` (28 sent, 27 ok / 1 error): pre-kill segment 6/6 served by llama.cpp
(TTFT p50 1.917 s); `llama-server` SIGKILLed mid-stream; downtime segment 12/12 served by mock
(TTFT p50 0.306 s) with **zero client-visible failures** during the ~142 s outage;
post-restart segment 9/9 back on llama.cpp (TTFT p50 1.870 s). The 1 error is the single
request already accepted upstream by llama.cpp at the instant of the kill (the documented,
expected boundary of client-visible failover — conservation 6+12+9+1=28, not a leak).

Source (reference only): `evidence/i3/checklist.md` item 6; `evidence/i3/raw/runs/`
`chat-short-failover/`; `evidence/i3/raw/failover-timeline.json`;
`evidence/i3/raw/mock-debug-state-failover.json`; inference-lab commit `61132b2`.

## 3. Deferred GPU evidence — explicitly NOT claimed

None of the following exist, and none are asserted by this document or by `pins/pins.yaml`'s
`proven_at` entries:

- **Engine-metrics-verified cancellation via vLLM** — KV-cache-usage-ratio / running-request
  -count drop observed on `/metrics` within a declared bound after client disconnect. §2.2's
  evidence is llama.cpp-engine-observable (`/slots`, server log), not vLLM metrics.
- **GPU-scale gateway-overhead comparison** — direct-vs-via-gateway measured against vLLM on
  a rented GPU at production-representative rates/concurrency (continuous-batching regime).
  §2.3 is CPU-only, and even there the real-engine arm is explicitly inconclusive at the
  declared ms-scale bound.
- **vLLM-specific behavioral surprises / capability descriptor** — probed continuous-batching
  behavior, prefix-cache observability, and metric names at vLLM v0.24.x baseline (infergate
  `IG-T014`, not started).
- **GPU session artifacts (gate G6)** — written hypothesis, full config manifest, auto-stop
  script, budget alert, session log with confirmed auto-stop, spend-vs-budget accounting. None
  ran; none exist.
- **GPU-specific pins** — vLLM version/commit, model checkpoint + quantization + tokenizer for
  a GPU-class model, driver/CUDA versions, instance type. `pins/pins.yaml`'s `engine-vllm`
  entry remains a comment ("needed for I4"), not an artifact.

## 4. Pins used (the CPU-fallback baseline) — updated in `pins/pins.yaml`

`proven_at` extended to include `I4` (alongside the existing `I3`) for the six pin entries
that back the evidence in §2, with the precision noted per entry:

| Pin id | Backs (§2 pillars) | Note |
|---|---|---|
| `contracts-bundle-v0-2-0` | 2.1, 2.2, 2.3, 2.4 | same bundle (v0.2.0/`484b449`) validated by both I3 and the IB-T010 evidence |
| `infergate-binary` (`74f2372`) | 2.1, 2.2(b), 2.4 | **not** used by 2.3 (that ran infergate@`6827d8c` — see §2.3 honesty note) |
| `infergate-mock-binary` (`74f2372`) | 2.4 | failover fallback engine |
| `inferbench-binary-69a5abc` | 2.1, 2.2(b), 2.4 | **not** used by 2.3 (that ran inferbench@`6a3fb53`, cited but not pinned here — see §2.3) |
| `engine-llamacpp` (`8f114a9`) | 2.1, 2.2(a) engine-commit-only, 2.2(b), 2.3, 2.4 | same llama.cpp commit across every pillar; 2.2(a) and 2.3's llama.cpp arm used non-Scenario-B flags (their own configs), 2.2(b)/2.1/2.4 used Scenario B's `-np 2 -c 8192` |
| `model-gguf` (Qwen2.5-1.5B-Instruct Q4_K_M) | 2.1, 2.2(b), 2.3, 2.4 | **not** used by 2.2(a), which ran an unpinned tiny random-weight test GGUF (D2) |

No new `pins/pins.yaml` artifact entry was created for infergate@`6827d8c` or
inferbench@`6a3fb53` (the commits behind §2.3): they were produced entirely inside their own
repos' task execution, not via this repo's own scenario/build tooling, and are cited here
under this repo's evidence-archivist role — the same pattern already used for the I1/I5/I7
archiving duties (`docs/integration.md`) — rather than pinned as an inference-lab-composed
artifact.

## 5. Repositioning note (program charter §7)

From `portfolio-planning/00-program-charter.md` §7 "Budget and hardware assumptions"
(the program-level charter, not this repo's `docs/charter.md`):

> Contingency: if GPU access fails, llama.cpp becomes the primary measured engine and the
> portfolio is repositioned around CPU/edge inference plus the mock-backend evidence; GPU
> experiments compress into one scripted final session.

I4 is the milestone at which this contingency is exercised. Consequence for portfolio claims:
this repo's own narrative sentence "I measured the gateway and engine independently and
together" (`docs/charter.md` § Final narrative) is, for now, demonstrated at **CPU scale**
(llama.cpp) rather than GPU scale. The honest-limitations statement due at I8 must carry this
forward explicitly, and any future GPU session that executes `IG-T014` + `IB-T011` + a real
run of this scenario's checklist items 1/2/4/6 supersedes this record with a **new dated
entry** (this one stays archived per evidence immutability, ADR-0002) — it does not overwrite
it.

## 6. Uncertainties / open follow-ups

- I3's cancellation log-census discrepancy (21-vs-20 `cancel task` log lines on the original
  run, not reproduced on retry) remains an open, unreproduced observation — see
  `evidence/i3/checklist.md` item 5. Not resolved by this evidence-assembly task.
- IG-T005's cancellation numbers (§2.2a) were measured against an unpinned tiny random-weight
  GGUF, not the pinned model — a caveat on that source, not on the composed-stack evidence
  (§2.2b), which used the real model.
- The gateway-overhead comparison's llama.cpp arm (§2.3) is explicitly inconclusive at the
  declared ms-scale bound; only the mock arm resolves the hypothesis. A GPU-class engine (or
  a lower-variance CPU setup) would be needed to resolve the llama.cpp-arm question for real.
- §2.3's infergate/inferbench commits differ from this repo's own Scenario B/I3 pins (see §2.3
  and §4) — cited as sibling-repo evidence, not re-pinned here.
- If/when GPU budget is later approved: re-run Scenario C for real against vLLM per
  `scenarios/c/README.md`; that run supersedes this CPU-fallback record with a new dated
  evidence entry, per ADR-0002 (this one is not deleted or rewritten).
