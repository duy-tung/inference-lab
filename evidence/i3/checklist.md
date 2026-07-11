# I3 — Local inference: executed acceptance checklist (Scenario B, IL-T003)

Executed 2026-07-11 against the composed Scenario B stack
(`inferbench → infergate → llama.cpp`, host processes per decision D-004). All numbers
**measured** (provenance: this run; raw artifacts referenced per item, all under
`evidence/i3/`). Orchestration: `scenarios/b/{build.sh,run.sh}`; every automated criterion
below is recomputable from the raw artifacts via `scenarios/b/checks.py` (outputs archived
in `logs/checks.log`).

**Overall: all executed criteria PASS; one criterion (cancellation) is a documented
DEVIATION — the underlying engine behavior is verified within bound on two independent
runs, but the first run tripped an unexplained log-census invariant that a same-config
recheck did not reproduce. I3 acceptance review by the user is pending. `proven_at` stays
`[]` in `pins/pins.yaml` until then (I2 precedent).**

## Session history (honest accounting)

This evidence set was produced across three separate work sessions, all preserved:

1. **Attempt 1 (2026-07-11 00:44–00:53 UTC) — INVALID, kept as defect evidence.** A bug in
   the original `run.sh` (`start_llama` captured a wrapper-subshell pid, not the
   `llama-server` pid) let a stale engine process hold port 18082 through preflight
   testing; every per-phase engine in this attempt failed to bind. Aborted by the operator
   ~9 minutes in. Fixed in the committed `run.sh` (`exec` inside the backgrounded subshell +
   `port_must_be_free` guard + post-start pid/port verification). Partial artifacts
   preserved unmodified at `evidence/i3/aborted/attempt-1-2026-07-11/`.
2. **Attempt 2 (2026-07-11 01:08–01:19 UTC, resumed 06:05–06:28 UTC) — the run that
   produced this evidence set.** Interrupted mid-`shared-prefix-cpu` phase at ~01:19 UTC by
   a container/session freeze; the partial run (no completion summary, manifest without a
   completed schedule) is preserved at
   `evidence/i3/aborted/attempt-2-interrupted-2026-07-11/` and was **not** used for any
   acceptance claim. Resumed at 06:05 UTC using `run.sh`'s `PHASES` resume gating
   (`sharedprefix cancel failover validate analysis checks`), which re-ran
   `shared-prefix-cpu` cleanly and completed every remaining phase through `checks` at
   06:28:22 UTC. That run finished with **one failing check**: `cancel-llama` (see item 4
   below) — `run.sh` fails loudly and preserves all evidence when a check fails (`set -e`
   plus explicit check collection), so nothing was silently retried at the time.
3. **This session (2026-07-11 07:43–07:48 UTC) — reproducibility recheck.** The prior
   agent's process was dead but the evidence was complete and schema-valid; the machine was
   otherwise idle (load average ~0.06/0.34/0.20, 4 cores free, no other listeners on the
   scenario ports). Rather than accept a single ambiguous FAIL as-is, `PHASES="cancel
   checks"` was re-run once against the same pinned binaries/model with a fresh
   `llama-server` process: **the recheck passed cleanly** (see item 4). `PHASES="validate"`
   was then re-run to refresh `logs/kit-validate.log` against the current
   `cancel-mid-stream-cpu` artifacts. The original (failing) attempt's cancellation data is
   preserved, not overwritten in place, at
   `evidence/i3/raw/runs/cancel-mid-stream-cpu-attempt1/` and
   `evidence/i3/logs/attempt1-cancel/` (includes the full `checks.log` from that run). No
   other phase was re-run in this session — every other artifact in `evidence/i3/` (raw
   runs, reports, results) is the original 06:xx-06:28 output, untouched.

## Acceptance checklist

| # | Criterion | Outcome | Evidence |
|---|---|---|---|
| 1 | Stack composed from pinned artifacts only: llama.cpp commit pinned, GGUF model revision + quantization + tokenizer hash pinned; pins validator green | **PASS** | `pins/pins.yaml` (Scenario B pin set: `contracts-bundle-v0-2-0`, `infergate-binary`, `infergate-mock-binary`, `inferbench-binary-69a5abc`, `engine-llamacpp`, `model-gguf`); `evidence/i3/pins-snapshot.yaml`; `evidence/i3/logs/build-info.txt` (all pins re-verified at build: llama.cpp commit match, model sha256 match, binary sha256s recorded); `python3 pins/validate_pins.py` → `OK (13 artifact entries)` |
| 2 | `chat-short` workload completes on CPU through the gateway (seeded, versioned) | **PASS** — `chat-short-cpu` v1.0.0, seed 1003001, via-gateway arm: 40 sent / 40 ok / 0 errors / 0 shed, wall 10m6.6s; paired engine-direct arm (same workload/seed, fresh engine): 40/40 ok, wall 10m15.1s | `raw/runs/chat-short-cpu-gw/`, `raw/runs/chat-short-cpu-direct/`; `logs/run.log` |
| 3 | `shared-prefix` workload completes on CPU through the gateway (seeded, versioned) | **PASS** — `shared-prefix-cpu` v1.0.0, via-gateway: 25 sent / 25 ok / 0 errors / 0 shed, wall 10m36.1s (resumed cleanly after the attempt-2 interruption; see session history) | `raw/runs/shared-prefix-cpu/`; `logs/run.log` |
| 4 | **Benchmark report #0** generated and schema-valid: full run manifest (engine commit + flags, model revision + tokenizer, hardware, gateway + config version, warm-up policy, repetition count, hypothesis) + validity block; pooled percentiles, never averaged across runs; goodput@SLO with shed rate adjacent; labeled a methodology shakedown | **PASS** — three reports generated (`chat-short-cpu-direct`, `chat-short-cpu-gw`, `shared-prefix-cpu`), all schema-valid against `benchmark-result` (Contract 3) and all carrying the mandatory Validity block, Threats-to-validity block, and Unexplained-anomalies block; every report states "methodology shakedown, not a performance claim". Headline numbers (pooled, single repetition — see caveats): via-gateway chat-short TTFT p50 **2.313 s** / e2e p50 **9.346 s** / goodput@SLO **1.0000 (36/36)**; engine-direct chat-short TTFT p50 **2.486 s** / e2e p50 **10.364 s** / goodput@SLO **1.0000 (36/36)**; shared-prefix TTFT p50 **13.193 s** / e2e p50 **24.742 s** / goodput@SLO **0.9524 (20/21)**. Gateway-overhead diagnostic (`ttft-compare` check): via-gateway pooled p50 **172.9 ms lower** than engine-direct pooled p50 — within the declared <100 ms-added hypothesis bound only because it is negative; the reports' own threats-to-validity section attributes this to single-host CPU contention (client + gateway + engine share 4 cores; llama-server alone measured up to 398% of one core), not a genuine gateway speed-up, and the run pair explicitly disclaims resolving overhead below ~100 ms | `evidence/i3/reports/i3-{chat-short-cpu-direct,chat-short-cpu-gw,shared-prefix-cpu}.report.md`; `raw/results/*.benchmark-result.json`; `logs/kit-validate.log` (`benchmark-result` schema PASS ×3); `logs/checks.log` (`ttft-compare` section) |
| 5 | **Cancellation verified against llama.cpp**: client disconnect propagates; engine release observable within bound | **DEVIATION** — engine release IS verified within the declared 2.5 s bound on **both** independent runs: attempt run (20/20 client-canceled requests, engine slot-release deltas -32.2 ms to +83.9 ms vs. bound) and this session's recheck (20/20, deltas -29.4 ms to +79.3 ms). The recheck's automated log-census invariant (`llama-server 'cancel task' log lines == client canceled count`) also passed cleanly (20==20). The **first** run's invariant did not (21 lines vs. 20 canceled): one extra `stop: cancel task, id_task=4134` log line has no matching `launch_slot_` entry anywhere in that run's log, so it cannot be tied to any of the 20 client-visible requests — evidence is consistent with (but does not prove) a request that was queued behind the 2 slots and canceled before ever being dispatched (workload is Poisson-arrival at 0.2 rps against `-np 2`, so brief 3-deep queueing bursts are possible), which `checks.py`'s log-census check does not currently account for. Root cause is **not conclusively established** — recorded honestly as unreproduced-on-retry rather than asserted as either a confirmed defect or dismissed as noise. Filed as a follow-up: either loosen the `cancel-llama` check to count launched-and-canceled tasks specifically, or determine why llama-server logged a phantom cancel for an unlaunched task id. Every `output_tokens_at_cancel == 8` (cancel trigger fired correctly) on both runs; no slot left processing at the end of either poll | `raw/runs/cancel-mid-stream-cpu/` (final, passing recheck); `raw/runs/cancel-mid-stream-cpu-attempt1/` + `logs/attempt1-cancel/` (original, preserved); `logs/llama-server-cancel.log`, `raw/slots-poll-cancel.jsonl`; `logs/checks.log` `cancel-llama` section (PASS, from the recheck); `logs/attempt1-cancel/checks-full.log` (original FAIL, preserved) |
| 6 | **Failover mock↔llama.cpp demonstrated** through the gateway, with client-visible behavior recorded | **PASS** — `chat-short-failover` (28 sent, 27 ok / 1 error): pre-kill segment 6/6 served by llama.cpp (TTFT p50 1.917 s); llama-server SIGKILLed mid-stream at 06:23:50.653Z; downtime segment 12/12 served by mock (TTFT p50 0.306 s) with **zero client-visible failures** during the ~142 s outage; llama-server restarted, post-restart segment 9/9 back on llama.cpp (TTFT p50 1.870 s). The 1 error is the single request already accepted upstream by llama.cpp at the instant of the kill — it cannot transparently fail over after acceptance, which is the documented, expected boundary of client-visible failover, not a leak (conservation: 6+12+9+1=28). Attribution is by measured timing signature (mock: constant ~300 ms TTFT / ~30 ms ITL; llama.cpp: ≥0.2 s prefill / ≥40 ms ITL), cross-checked against the mock's own `/debug/state` stream counters (12 requests / 12 completed / 0 aborts, exact match) | `raw/runs/chat-short-failover/`; `raw/failover-timeline.json`; `raw/mock-debug-state-failover.json`; `logs/checks.log` `failover` section (PASS) |
| 7 | Raw-event JSONL / manifests / workloads / SLO / backend-capability / smoke SSE schema-valid against the pinned contracts bundle (v0.2.0) | **PASS** — all 7 run sets' `events.jsonl` valid against `raw-event`, all 7 `manifest.json` valid against `benchmark-run`; all 6 workload files valid against `workload`; derived SLO valid against `slo`; llama.cpp capability descriptor valid against `backend-capability`; smoke SSE transcript valid against `api.stream-event`; all 3 analysis result files valid against `benchmark-result` (kit @ serving-contracts v0.2.0, tag 484b449; content identical to the 8d81492 prerelease pin used to build inferbench@69a5abc — see the cosmetic-mismatch note on the `contracts-bundle-v0-2-0` pin entry) | `logs/kit-validate.log` (refreshed this session against the final `cancel-mid-stream-cpu` artifacts) |
| 8 | Evidence archived: benchmark report #0, campaign logs, this checklist → `evidence/i3/`; pins updated with `proven_at: [I3]` rows | **PARTIAL BY DESIGN** — evidence fully archived (this directory); `pins/pins.yaml` carries the full Scenario B pin set with `proven_at: []` **intentionally**, filled only at user acceptance (I2 precedent, `docs/implementation-notes.md`) | `evidence/i3/`; `pins/pins.yaml` |
| 9 | Reviewed (user acceptance) | **PENDING** — I3 is claimed (and `proven_at`/`milestone_evidence` in `pins/pins.yaml` filled) only after user review of this evidence, including the cancellation-invariant deviation (item 5) | — |

## Other deviations affecting this evidence

- **D-004** (`docs/implementation-notes.md`): Scenario B runs host processes, not
  containers — approximates the "released images by digest" ideal with commit-pinned
  binaries + recorded content digests, same spirit as I2's D-002. (The scenario README and
  a pins.yaml note previously mis-cited this as "decision A-007" — a cross-reference typo
  from the earlier session, corrected in this pass; A-007 is the unrelated cancellation
  release-bound assumption.)
- **A-007 / A-008** (`docs/implementation-notes.md`): the 2.5 s cancellation release bound
  and the calibration-derived SLO thresholds are both recorded as reversible assumptions,
  not external targets.
- Single-host client+server co-location and single-repetition sampling apply to every
  reported number in this evidence set (see each report's Threats-to-validity block); no
  number here is a performance claim.

## Defects filed upstream

None conclusively. The item-5 log-census discrepancy is recorded as an open, unreproduced
observation (see above) rather than a filed defect, since a same-configuration recheck did
not reproduce it and the root cause is not established.
