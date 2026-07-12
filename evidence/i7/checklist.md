# I7 — Failure campaign: acceptance checklist (Scenario — none owned here; IL-T007)

Assembled 2026-07-12. **This is primarily an evidence-assembly record**, per this task's own
brief and `docs/integration.md`: I7 is owned and executed by `inferops` (fault injection),
this repo's role is consumer-side evidence archiving + writing the postmortems
(`docs/tasks.md` IL-T007). Nearly every number below is a reference to evidence already
published in the `inferops` repository (`/home/user/inferops`, campaign commits `bfca054`
(IO-T006, scenarios 1-6), `a1e0af5` (IO-T007, scenarios 7-12 + noisy-neighbor), `a07fd2f`
(HEAD, evidence note fixes)), cited by path and commit — nothing is copied or re-derived.
The three postmortems (`postmortems/pm-001.md`..`pm-003.md`) are new writing produced by this
session, built entirely from the cited raw artifacts (transcripts, metric dumps,
`events.jsonl`, `requests.csv`) — no timeline entry in them is invented.

**Overall: I7's normative acceptance criteria (07 §I7) are demonstrated by the inferops
campaign, with two things surfaced prominently rather than buried: (a) scenario 4 is a real,
reproducible defect-shaped finding (not just a topology limitation), and (b) four scenarios
(1, 3, 7, 10) carry a structural, non-defect single-backend-topology deviation. I7 acceptance
review by the user is pending — recorded here per the I2/I3/I5 precedent (`proven_at: [I7]`
is set on the backing pins below, but "accepted" status is a separate, pending user-review
step; see `docs/implementation-notes.md`).**

## 0. Headline deviations (read first)

### 0.1 Scenario 4 (slow client) — a real, reproducible defect-shaped finding, not a topology artifact

Unlike every other deviation in this campaign, scenario 4 is **not** a consequence of the
reduced (single-backend, no-GPU) topology — it is a genuine gap between the *deployed*
gateway's behavior and Contract 6's expected semantics, reproduced twice (a deterministic
raw-socket stall test and a population-level `inferbench` run), and only partially
self-disclosed in advance by infergate's own source comment. **Verdict: deviation-documented
(not expected-semantics-matched)** — the only one of the 12 scenarios with that verdict. Full
detail in `postmortems/pm-001.md` and `faults/scenario-04/verdict.md` (inferops, commit
`a1e0af5`). This is surfaced here at the top of the checklist, in the campaign matrix
(§2), and as the lead postmortem — never folded silently into the matched-scenario tally.

### 0.2 Structural single-backend-topology deviations (scenarios 1, 3, 7, 10)

This release's gateway CLI (`cmd/gateway/main.go:145-152`, infergate) wires exactly one
backend into `route.Router` — IG-T012 N-backend routing exists internally but "is not yet
flag-driven for N>1" (infergate's own recorded scope reduction, not an inferops or
inference-lab decision). Four scenarios whose expected semantics include a
multi-backend routing-shift clause (1: retry onto another healthy backend; 3: traffic shifts
away from the slow backend; 7: non-injected backends stay healthy; 10: routing shifts to
healthy backends) cannot demonstrate that specific clause on this release — every other
clause in each of those four scenarios matched cleanly. Verdict for all four:
**expected-semantics-matched, with one documented structural deviation**. Not filed as a
defect (a consumer repo cannot add CLI surface to another repo); surfaced as a concrete,
campaign-backed consumer case for IG-T012 landing. Scenario 1 additionally carries a small,
separately-diagnosed metrics-instrumentation nuance (`inference_retries_total` does not
increment when a retry's own `Select()` call also fails) — not a functional defect, recorded
for a future infergate doc-comment.

### 0.3 Scenario 6 admission-path discrepancy (no-auth topology)

Every ad hoc fault-campaign gateway instance runs `-auth-mode=none` (required so `inferbench`,
which sends no `Authorization` header, can drive it — `faults/lib.sh` header comment). Under
`-auth-mode=none` there is no tenant identity for the per-tenant quota gate to key on, so
scenario 6's shed path is the queue/global-budget one (`overloaded`/503,
`reason=queue_full`) rather than the per-tenant `rate_limited`/429 path the contract fixture's
literal wording names — both are real, contract-named admission-shed paths; this deployment
can only reach one of them. Flagged in `hypothesis.md` *before* running, confirmed as
predicted — **documented as an expected discrepancy of the reduced topology, not a defect.**

### 0.4 Scenario 10 pause-vs-fail-fast injector nuance

`docker pause` (chosen so `/healthz` itself also fails, unlike the `-error-rate` mechanism
used elsewhere) makes the backend **hang** rather than **fail fast** for the handful of
requests already in flight at the exact injection instant (3/30) — a property of the chosen
injection method, not the gateway; each was correctly accounted for as `canceled` once the
*client's own* timeout gave up. Once health flipped, subsequent requests correctly failed fast
(17× typed 503 in ~11ms). Verdict: **expected-semantics-matched, with two documented
deviations** (this one + the single-backend routing-shift limitation from §0.2).

### 0.5 CPU-fallback continuation (D-005/D-006) — no GPU anywhere in this campaign

Every scenario in this campaign ran against the same CPU-only stack this repo's I4/I5 records
already carry forward (D-005, D-006): the mock backend for scenarios 1-4/6/7/9/10, and the
real llama.cpp CPU engine (same pinned commit `8f114a9b573b69035299f9b924047f53c1e22c7e` and
model file as I3/I4/I5) for scenario 8's config-reload test. No vLLM, no GPU node, no GPU
claim anywhere in the campaign. Per 07 §I7's own acceptance text ("GPU-dependent ones may run
on the llama.cpp/mock path with a recorded deviation"), this single, already-established
deviation covers the whole campaign — there was no scenario-by-scenario GPU/CPU split to
record, because the entire program has no GPU access this wave (I4/D-005).

## 1. I7 acceptance criteria (verbatim from `portfolio-planning/07-integration-milestones.md`
§I7) mapped to evidence

| # | Criterion (verbatim) | Verdict | Evidence (path + commit) |
|---|---|---|---|
| 1 | "All 12 contract fault scenarios injected (GPU-dependent ones may run on the llama.cpp/mock path with a recorded deviation)" | **PASS, with the CPU-fallback caveat above (§0.5)** | `inferops/faults/scenario-{01..12}/inject.sh` + `evidence/<timestamp>/` (commits `bfca054`, `a1e0af5`, `a07fd2f`); `inferops/faults/campaign-matrix.md`: "All 12/12 scenarios executed. Kill-criteria set (1, 2, 5, 6, 11, 12) fully run; no scope reduction was needed." |
| 2 | "For each: expected gateway semantics observed or deviation documented" | **PASS** — 11/12 matched expected semantics: 6 fully clean (2, 5, 8, 9, 11, 12) + 5 matched with a documented deviation (1, 3, 6, 7, 10 — of which 1/3/7/10 are the single-backend structural limitation §0.2 and 6 is an expected no-auth shed-path discrepancy); 1/12 deviation-documented, not-matched (4 — §0.1). Sum: 6+5+1=12. (Corrected at I7 verification from an earlier "8/12"/"9/12" roll-up that understated the match rate and mis-summed; per-row verdicts unchanged.) Every scenario has a recorded verdict; none silently passed. | `inferops/faults/scenario-{01..12}/verdict.md`; summarized in `evidence/i7/campaign-matrix.md` (this repo, archived transcription) |
| 3 | "Client impact measured by inferbench for at least the streaming-critical scenarios (1, 2, 5, 6, 12)" | **PASS** — all five measured with a real `inferbench` build (commit `62c2704997e6c8a2966307ee3d8dbfd16747b631`), no scope reduction | `inferops/faults/scenario-{01,02,05,06,12}/evidence/*/inferbench-run/`; summarized in `evidence/i7/client-impact.md` (this repo) |
| 4 | "≥2 postmortems published in the standard format (timeline from real metrics, detection gap, root cause, mitigation, action items)" | **PASS — 3 published** (exceeds the minimum of 2) | `postmortems/pm-001.md` (scenario 4, slow client — the campaign's one real defect-shaped finding), `postmortems/pm-002.md` (scenario 2, backend killed after first token — clean textbook semantics), `postmortems/pm-003.md` (scenario 9, usage database failure — cleanest "nothing went wrong, exactly as designed" result in the campaign) |

## 2. Per-scenario summary (12 rows: injected / observed / verdict)

Full table archived at [`evidence/i7/campaign-matrix.md`](campaign-matrix.md) — a dated,
cited transcription of `inferops/faults/campaign-matrix.md` at commit `a07fd2f` (not vendored
source; this is evidence archival, the same duty this repo already exercises for I1/I5). Do
not edit that file independently of a fresh citation — if the inferops matrix changes, a new
dated archival entry supersedes this one (ADR-0002).

## 3. Client impact — streaming-critical scenarios (1, 2, 5, 6, 12)

Summarized at [`evidence/i7/client-impact.md`](client-impact.md), with per-scenario numbers,
the `inferbench` run directories cited, and the one honest caveat recorded in scenario 6
(small admitted-population sample, n=3).

## 4. Postmortems

Three published, all built from the cited raw evidence (never narrated from memory):

| Postmortem | Scenario | Headline finding |
|---|---|---|
| `postmortems/pm-001.md` | 4 — slow client | The gateway's write-deadline mechanism did not observably close a genuinely stalled stream across an 8s stall (2.6x the configured 3s deadline) — a real, reproducible gap infergate's own source already partially discloses as incomplete. |
| `postmortems/pm-002.md` | 2 — backend killed after first token | Byte-level captured SSE stream shows a textbook-clean mid-stream error event, structurally-guaranteed zero post-first-token retries, and correctly-settled partial usage (1796 tokens billed). |
| `postmortems/pm-003.md` | 9 — usage database failure | 35/35 requests succeeded at identical latency through a real ~3s PostgreSQL outage; the async-settlement design fully decoupled serving from accounting, with a zero-loss, zero-duplicate backlog drain. |

## 5. Pins used / added (`pins/pins.yaml`)

New entries, `proven_at: [I7]`:

| Pin id | What it records | Verified how |
|---|---|---|
| `inferops-fault-campaign` | inferops repo state through commit `a07fd2f` (IO-T006 `bfca054` + IO-T007 `a1e0af5` + the evidence-note fix `a07fd2f`) — the whole 12-scenario Contract 6 fault campaign + the noisy-neighbor observation run | inferops `docs/tasks.md`/`docs/implementation-notes.md` IO-T006/T007 log entries + `git log` on `/home/user/inferops` |
| `inferops-fault-campaign-inferbench` | the `inferbench` binary used to measure client impact, built fresh from `/home/user/inferbench` commit `62c2704997e6c8a2966307ee3d8dbfd16747b631` | `inferops/faults/campaign-matrix.md` header note + `inferops/docs/implementation-notes.md` IO-T006/T007 entry; commit confirmed live against `/home/user/inferbench` (`git rev-parse HEAD` = same hash). **No digest recorded**: this was a host build to a scratch path (`faults/lib.sh`'s `INFERBENCH_BIN` default) not independently re-verified by this session — recorded honestly as commit-pinned only, the same "no tagged release yet" pattern already used for `inferbench-binary`/`inferbench-binary-69a5abc` above. |

**Extended (already-existing entries), `proven_at` gains `I7`:**

| Pin id | Why extended |
|---|---|
| `inferops-infergate-image` (v0.1.0, commit `49236a3`, digest `sha256:1971426b393b3e00b30cac0690d38b31667b5e34ebbeb6e111a54c369fb54c7e`) | Every ad hoc fault-campaign gateway instance (`gateway-faults`, `gateway-faults-a/-b`) is started from this exact digest — `inferops/faults/lib.sh`'s `GATEWAY_IMAGE` constant is byte-identical to the already-pinned I5 entry; confirmed by direct comparison, not re-inspected live (the running containers from I5's `docker inspect` are the same image referenced here). Scenario 9 also uses this image via the main compose gateway. |
| `inferops-mock-backend-image` (v0.1.0, commit `49236a3`, digest `sha256:d7df3d5609daa85adef6a07e4471c8bb90f5e2472f0bf3b32deb2fa9efb547e2`) | Same reasoning: `inferops/faults/lib.sh`'s `MOCK_IMAGE` constant is byte-identical to the already-pinned I5 entry; backs `mock-faults`/`mock-faults-a/-b` for 10 of the 12 scenarios. |
| `engine-llamacpp` (`8f114a9b573b69035299f9b924047f53c1e22c7e`) | Scenario 8 (config reload under traffic) ran against the real `gateway-llamacpp` instance, the same pinned llama.cpp commit already proven at I3/I4/I5 — `inferops/faults/scenario-08/verdict.md` cites `scripts/config-rollout.sh` (IO-T010) runs against this exact engine. |
| `model-gguf` (Qwen2.5-1.5B-Instruct GGUF Q4_K_M, `sha256:6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e`) | Same reasoning as `engine-llamacpp`: scenario 8 served real inference through this exact pinned model file. |
| `inferops-llamacpp-engine-image` (`infergate-llamacpp-engine:8f114a9`, digest `sha256:43af71918dda78a1daaf19849e1c3cccfd7bad7c432b6c1420a45a62e99410be`) | Scenario 8 (config reload under traffic) ran through the `gateway-llamacpp` instance backed by this engine image — the same digest proven at I5; `proven_at` gains I7. |

`milestone_evidence.I7` now points at `evidence/i7/`. Validator: `python3 pins/validate_pins.py`
→ green (see commit for exact entry count).

## 6. Deferred — explicitly NOT claimed

- **GPU inference of any kind.** No GPU node, no vLLM, no CUDA execution anywhere in this
  campaign (§0.5) — a direct continuation of I4/I5's CPU-fallback deviation (D-005, D-006),
  not a new one.
- **Multi-backend routing-shift, for real.** Scenarios 1, 3, 7, 10's routing-shift clauses are
  not demonstrated on this release (§0.2) — this is not claimed as passed anywhere, including
  in the campaign matrix (§2) or the compatibility matrix row this checklist feeds.
- **A production incident this postmortem set describes.** All three postmortems (§4) describe
  *injected* faults in a fault-injection campaign, not real production incidents — each
  postmortem states this plainly in its own header.
- **Memory-growth measurement for scenario 4's abort condition.** Out of this campaign's
  instrumentation scope (`postmortems/pm-001.md`, `inferops/faults/scenario-04/verdict.md`) —
  recorded as a coverage gap, not silently assumed passing.
- **A fix for the scenario 4 finding.** This repo does not patch infergate (program rule);
  the finding is routed as observations for infergate (§0.1, `postmortems/pm-001.md` §5).

## 7. Uncertainties / open follow-ups

- **I7 acceptance is subject to user review**, same as I2/I3/I5 before it. `proven_at: [I7]`
  is recorded on the pins above because the evidence genuinely exists and supports it; this
  does not substitute for the review step.
- Scenario 4's root-cause hypothesis (`http.ResponseController.SetWriteDeadline` possibly
  returning `http.ErrNotSupported` silently) is **not proven** — confirming it requires adding
  instrumentation to infergate itself, out of this repo's and inferops's scope (routed as an
  action item to infergate, `postmortems/pm-001.md` §5).
- IG-T012 (N-backend routing CLI/config exposure) landing would let scenarios 1, 3, 7, 10 be
  re-run for a fully faithful reproduction of their routing-shift clauses — noted as a re-run
  trigger, not scheduled here.
- The noisy-neighbor observation run (`inferops/faults/noisy-neighbor/`) is not one of the 12
  numbered Contract 6 scenarios and is not counted toward the 12-row matrix or this
  checklist's acceptance criteria; it is cited in `evidence/i7/campaign-matrix.md` as
  supplementary evidence only, consistent with inferops's own scope note.
- Scenario 6's admitted-population client-impact number is a small sample (n=3 `ok` out of
  399 sent) — the p95 latency claim it supports is directionally correct but statistically
  weak; recorded honestly in `evidence/i7/client-impact.md`, not inflated.
