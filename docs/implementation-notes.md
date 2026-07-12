# Implementation Notes — inference-lab

Running log of decisions, surprises, re-verification results of volatile facts, and
deviations. Newest entries first within each section.

## Log

### 2026-07-12 — IL-T008 + IL-T009: compatibility matrix consistency pass, portfolio release, I8 assembled

- **IL-T008 (matrix consistency pass).** Found two process gaps while sweeping the matrix for
  "every milestone row present + evidence-linked": (1) `evidence/i1/` (contract compatibility,
  archived per this repo's evidence-archivist duty) had never actually been created, despite
  I2-I7 evidence citing I1 status throughout — fixed by archiving the serving-contracts@507208b
  v1.0.0-freeze I1 re-run (GREEN across all four consumers against real emitted artifacts) as
  `evidence/i1/checklist.md`, adding an I1 row to `compatibility/matrix.md` and
  `milestone_evidence.I1` to `pins/pins.yaml`. (2) added a "current component state" table to
  the matrix distinguishing each component's latest tagged release/HEAD from the commit
  actually proven at each milestone (no row's claim is invalidated by a newer HEAD; that's what
  the re-run-trigger notes already govern). Validator stayed green throughout, 28 artifact
  entries (no new pin needed for I1; `contracts-bundle-v1-0-0` already covered the tag).
- **IL-T009 (portfolio release + I8), in the order executed:**
  1. Finalized `quickstart/README.md` into an actually-followable procedure (the build.sh step
     was previously undocumented in the quickstart flow; added `scenarios/a/wait-ready.sh` as
     a real script instead of a referenced-but-missing one) and then **actually timed it**
     twice from a fresh clone: 2m08s (warm Docker+Go caches) and 35s (`docker rmi` + `docker
     builder prune -a -f` forced a real image rebuild; Go module/build caches left warm — the
     single biggest, disclosed source of divergence from a genuinely cold machine, since a
     first-time `go mod download` over this sandbox's proxied network was never exercised).
     Both PASS the 15-minute target by a wide margin. A pre-existing, unrelated container in
     this shared sandbox (`inferops-haproxy`, from earlier already-archived milestone evidence
     work) held host port 18080; rather than stop a workload this session didn't create, both
     timed runs used a local port remap (compose `!override` merge key / a sed-edited copy of
     `compose.yaml` in the cloned directory) — the committed `scenarios/a/compose.yaml` is
     unchanged. Full methodology + honesty caveats: `quickstart/timing-log.md`.
  2. Found `reports/` had sat empty (only its own README) since 2026-07-10 despite I3/I4/I6
     evidence citing inferbench's and fleetlab's reports extensively by path — archived
     condensed copies of `benchmark-report-1.md`, `benchmark-report-1b.md` (inferbench), and
     `capacity-report.md` (fleetlab holdout validation), each with a validity-block excerpt and
     a link to the full origin.
  3. Captured a real demo: `portfolio/demo-script.md` (runnable, walks contracts → gateway
     streaming+cancellation → benchmark → capacity loop) plus a genuine terminal capture
     (`portfolio/demo-transcript.md`) from a live Scenario A stack. The cancellation capture
     landed on the **pre-first-token** point, not the mid-stream point the script's prose
     narrates (a timing race between the demo's own client timeout and the mock's configured
     TTFT) — recorded as observed, not smoothed over to match the script.
  4. OSS evidence framed per the documented contingency (`09-open-source-track.md` §4): added
     an explicit 2026-07-12 note to `oss/log.md` stating plainly that the minimum completion
     target is not met, local build+reproduction are real, the upstream comment is drafted and
     **not posted** (posting requires user review/action, which has not happened), and no
     public link is claimed anywhere. Nothing was posted upstream in this session.
  5. Landing page (`portfolio/README.md`, chosen over a separate `landing.md` — see the
     `docs/tasks.md` IL-T009 note) + two articles (`articles/article-1.md` double-queuing,
     `articles/article-2.md` cancellation/accounting) + `portfolio/limitations.md`, all written
     from real evidence gathered this session (ADRs, benchmark reports, usage-invariants docs)
     with dates/commits cited throughout.
  6. **The reproducibility audit** (`evidence/i8/reproducibility-audit.md`), the critical I8
     gate: audited every headline claim (100-concurrent-stream integrity, 3-point
     cancellation, CO-safe methodology/G5, gateway-overhead p95, the I6 +1.3% loop, the fault
     campaign, OSS evidence) against its pinned artifact, re-reading raw files directly (not
     trusting prose summaries) and independently recomputing at least one number per claim
     class where practical (e.g. the I6 +1.3% figure was recomputed from
     `inferops/experiments/autoscaling/evidence/.../summary.json` directly: (33.583-33.159)/33.159
     = +1.278%, matching). **Result: PASS, with 2 claims narrowed (not removed)** — the
     3-point-cancellation claim on the real llama.cpp engine was too broad (the pinned-model
     composed-stack test only covers one point; a separate 3-point test exists but ran against
     an unpinned test model — both facts are now stated together, not conflated) and the gate-G5
     "admission control passes" claim needed the re-framing context (the original ≤20% ratio
     target was REFUTED twice before the gate was re-baselined) attached everywhere it appears.
     **0 claims were removed outright** — in every case a true, reproducible, better-qualified
     version of the claim existed and now replaces the overclaiming short form. The two process
     gaps from IL-T008/step-2 above are also logged as audit findings, since they were
     discovered during this same audit pass.
- **Follow-up:** I8 acceptance review by the user is pending, same precedent as I2 (accepted),
  I3 (accepted), and I4/I5/I6/I7 (recorded, review pending). `pins/pins.yaml` updated
  (`milestone_evidence.I8`), `compatibility/matrix.md` gained an I8 row, validator green
  throughout (28 artifact entries — I8 introduces no new component pin).

### 2026-07-12 — IL-T006: Scenario E + milestone I6 (the central story) — capacity feedback loop closed

- **The headline deliverable of the program.** Assembled from three already-existing evidence
  sources, each cited by path+commit, per this repo's evidence-archivist/loop-owner role: the
  fleetlab FL-T009 recommendation (`/home/user/fleetlab`, commit
  `dd05e7decca5a998afdf496d1c439141caba5a29`), the inferops IO-T009 applied-change +
  re-measurement (`/home/user/inferops`, commit
  `89871a64d35bab9450481ff1afdd19ad8310a9d9`, IO-T009 itself at
  `f5fdd86ae670b1a1b0d6412f3c530f6e939ebd74`), and the inferbench IB-T010 benchmark corpus the
  recommendation was fitted from (`ib-t010-e2-baseline-1x-sane` /
  `ib-t010-e2-overload-5x-sane`, already cited by I4's own evidence). Nothing in any sibling
  repo's source was read or modified; the recommendation file itself was archived as a byte-
  identical copy (the one deliberate exception to the cite-don't-copy convention used for
  inferops manifests at I5/I7 — a small, self-contained data artifact the acceptance criterion
  names explicitly).
- **Independent Contract 7 re-validation performed this session** (not just relying on
  fleetlab's own claim): ran `kit/contracts-validate.py validate --schema
  capacity-recommendation` against the FL-T009 recommendation file twice — once against
  fleetlab's own vendored v0.2.0 bundle, once against a live checkout of serving-contracts at
  the newly-frozen **v1.0.0** tag (commit `507208b25737470b9eb2f9553a5c55f8f535f1d5`) — **PASS
  both**. Also independently confirmed `schemas/capacity-recommendation.schema.json` is
  byte-identical between the v0.2.0 and v1.0.0 tags (`git diff`, no output) — Contract 7 is
  not one of the three contracts (1-3) the v1.0.0 freeze touches, so this was expected, not
  luck. The serving-contracts working tree was restored to `main` immediately after (`git
  checkout main -- .`; verified clean).
- **Headline honesty item 1 — the applied change was 1→2 replicas, not the recommended 1→6.**
  fleetlab recommended scaling `gateway-mock-admission-sane-v1` from 1 to 6 replicas to serve
  a 189.0362 rps demand. inferops's IO-T009 applied and re-measured only a 1→2 scale-out — a
  disclosed compose-substrate resource/time-budget scope reduction, compounded by the
  already-established RQ-14 deviation (no Kubernetes pod scheduling exists in this environment
  at all, so there is no real scheduler to enact 6 replicas as pods regardless). **The
  6-replica prediction itself was never tested** — only extrapolated from 1- and 2-replica
  data, and every appearance of that extrapolated number in this evidence set says so
  explicitly (`evidence/i6/loop-report.md` §4.3). This is the single most important item this
  task's brief asked to be surfaced plainly, and it is surfaced first, in the checklist's own
  §0, not buried in a caveats section.
- **Headline honesty item 2 — predicted vs measured, including where the prediction
  diverged.** fleetlab's fitted per-replica capacity (33.159 rps, from
  `ib-t010-e2-baseline-1x-sane`) is confirmed within **+1.3%** when re-measured at the exact
  rate it was fitted from — a strong independent, cross-environment replication. At every
  higher offered rate this evidence covers (50 rps, 189 rps, and a genuine 2-replica-scale
  80 rps saturation check), the measurement instead tracks 1–5% from inferbench's own
  **unpublished** "overload-empirical" alternative estimate (37.925 rps) and 9–13% from the
  published fit — leaning toward 37.925, not 33.159. This resolves (does not contradict) the
  open question fleetlab's own G8 holdout report already flagged as unresolved
  (`fleetlab/reports/holdout-validation.md` §2a/§3, a documented MISS at 12.6% error) — three
  new independent points all point the same direction. Published in full in
  `evidence/i6/loop-report.md` §4.1/§4.2, not cherry-picked to the favorable fitted-point number
  alone.
- **Headline honesty item 3 — a comparability-rule audit this session performed, not just
  cited.** Directly diff'd fleetlab's own training-data run manifests
  (`inferbench/docs/evidence/ib-t010/e2-baseline/rep-1/manifest.json`) against IO-T009's
  re-measurement manifests. The admission and mock-timing flags match byte-for-byte; the
  gateway build (a dev commit vs. a later v0.1.0 tagged release), host, warm-up policy
  (50-request discard vs. none), repetition count (3 vs. 1), and workload seed identity
  (fleetlab's own `re_measurement` plan named seed `10010201`; IO-T009 used freshly authored
  workloads with different seeds embedding the same declared rates) all differ. Recorded as an
  explicit finding (`evidence/i6/loop-report.md` §3.1, checklist §0.4): this evidence is best
  read as an **independent replication**, not a byte-identical single-variable re-run — a
  distinction IO-T009's own report did not spell out in this much detail (it disclosed "a
  different host" but not the build/warm-up/repetition/seed differences).
- **A measured autoscaling-signal refinement, fed back but not yet filed upstream.**
  `inference_requests_in_flight` fired 6.1s after the workload's true capacity knee with zero
  false triggers; fleetlab's recommended `inference_queue_depth` signal fired 64.4s late for
  this shallow-queue (cap 3) admission config — sharpening FL-T009's own disclosed caveat from
  a magnitude problem into a stability problem. Recorded as profile-refinement feedback
  (`evidence/i6/loop-report.md` §5) per the acceptance criterion's own wording ("recorded, or
  filed upstream to fleetlab") — not yet filed as an actual fleetlab commit/issue (fleetlab's
  repo state is unchanged since before IO-T009 ran); this is stated as an open follow-up, not
  silently treated as already actioned.
- **A Contract 7 plumbing-precision gap found while applying the recommendation.**
  `recommended_topology.replica_groups[0].engine_config.flags` in the FL-T009 recommendation
  file is an empty object — the admission-sane-v1 flags that define "the recommended
  configuration" live only in the file's prose `baseline`/`change_summary` fields, not
  structurally in `engine_config`. inferops reproduced the flags correctly by reading
  fleetlab's evidence directly, not by mechanically applying a structured field. Recorded as
  loop-mechanics feedback (`scenarios/e/README.md`'s own failure-handling clause), not filed as
  a defect.
- **Not attempted, recorded as an open gap rather than a silent omission:** running fleetlab's
  own `fleetlab/emit/dry_run_validate.py` (the Contract-7 consumption-side checker) against
  real IO-T009 data. It exists and is tested against a synthetic fixture, but constructing a
  real Contract-3 `benchmark-result.json` from IO-T009's raw events to feed it was judged out
  of this task's loop-assembly scope — recorded as a genuine follow-up in
  `evidence/i6/loop-report.md` §6, not attempted and then hidden if it didn't work.
- **Pins added** (`pins/pins.yaml`, all `proven_at: [I6]`): `contracts-bundle-v1-0-0`,
  `fleetlab-bundle`, `fleetlab-recommendation-e2-admission-sane-v1-5x-scaleout`,
  `inferops-autoscaling-experiments`. No existing pin's `proven_at` was extended to I6 (the
  loop runs entirely on the mock backend, a different pin family from the llama.cpp/model pins
  I3-I5/I7 carry forward; `inferops-infergate-image`/`inferops-mock-backend-image` were not
  independently re-verified against the I6 containers specifically this session, so their
  `proven_at` was deliberately left unextended rather than claimed without a matching
  verification step — `evidence/i6/pins-snapshot.yaml`). `python3 pins/validate_pins.py` →
  green, 28 artifact entries.
- **I6 acceptance review by the user is pending**, same as I2/I3/I5/I7 before it.

### 2026-07-12 — IL-T007: Failure campaign evidence + milestone I7 archived

- **Executed ahead of IL-T006/I6 in the nominal dependency order.** The program's stated
  execution order is IL-T005 → IL-T006 → IL-T007, but I6 (the capacity-feedback loop) is
  blocked on IO-T009 (inferops autoscaling experiments), which was itself sequenced by
  inferops to run *after* the fault campaign (IO-T006/T007). Since the fault campaign
  completed first and its evidence has genuine standalone value, this task ran now rather than
  waiting on an I6 that cannot start yet. This is a scheduling reorder, not a dependency
  violation: I7 has no prerequisite on I6 in `docs/integration.md`/`07-integration-milestones.md`
  §I7 (its prerequisites are I5 + IO-T006/T007, both satisfied). Recorded here so the ordering
  is traceable, not silently reshuffled.
- **This session assembled evidence from the inferops fault-injection campaign**
  (`/home/user/inferops`, commits `bfca054f76d9ddd4728777ab56b0d3c23535d2d8` (IO-T006,
  scenarios 1-6), `a1e0af58bad7fbe52d5790c8560729aea2f77e49` (IO-T007, scenarios 7-12 +
  noisy-neighbor), `a07fd2ff35a1c6a7d26a596fd95365bf884595bd` (evidence-note fixes for
  scenario 7)), which was already complete and running. Nothing in inferops's own source was
  read or modified; every artifact cited by path and commit, per the I1/I5/I7 archiving duty.
- **All 12/12 Contract 6 fault scenarios injected, no scope reduction.** Per-scenario detail:
  `inferops/faults/scenario-{01..12}/{hypothesis,checklist,inject.sh,verdict}.md` + dated
  `evidence/` directories; the 12-row summary: `inferops/faults/campaign-matrix.md`. Archived
  (transcribed, cited, not vendored) at `evidence/i7/campaign-matrix.md`.
- **Headline finding surfaced prominently, not buried:** scenario 4 (slow client) is the
  campaign's one **deviation-documented** verdict — a real, reproducible gap, not a topology
  artifact. A raw TCP client held a stream open through an 8-second full stall (2.6x the
  configured 3-second `-stream-write-timeout`) and the gateway never closed it; the stream
  simply resumed once reads resumed. This corroborates rather than contradicts infergate's own
  `internal/stream/relay.go` comment ("Full slow-client fault handling — scenario 4 — is later
  work; the bound exists now"). Written up as `postmortems/pm-001.md`, the lead postmortem —
  deliberately placed first, not last, among the three.
- **Structural, non-defect deviation (scenarios 1, 3, 7, 10):** infergate's released gateway
  CLI (`cmd/gateway/main.go:145-152`) wires exactly one backend into `route.Router` — IG-T012
  N-backend routing exists internally but "is not yet flag-driven for N>1" (infergate's own
  recorded scope reduction). Four scenarios whose expected semantics include a multi-backend
  routing-shift clause cannot demonstrate that one clause; every other clause in each matched
  cleanly. Not filed as a defect (a consumer repo cannot add CLI surface to another repo);
  surfaced as a concrete, campaign-backed case for IG-T012 landing. Scenario 6 additionally
  carries one expected, non-defect admission-path discrepancy (the no-auth topology required
  so `inferbench` can drive load reaches the queue/global-budget 503 shed path, not the
  per-tenant `rate_limited`/429 path — both real, contract-named paths).
- **Client impact measured by `inferbench` for all 5 mandated streaming-critical scenarios**
  (1, 2, 5, 6, 12) — `inferbench` commit `62c2704997e6c8a2966307ee3d8dbfd16747b631` (host
  build, no tagged release exists yet upstream, recorded honestly as commit-pinned only).
  Summarized with per-scenario numbers at `evidence/i7/client-impact.md`.
- **3 postmortems published** (`postmortems/pm-001.md` scenario 4, `pm-002.md` scenario 2,
  `pm-003.md` scenario 9), exceeding the ≥2 minimum — each built entirely from the cited raw
  evidence (`transcript.log`, `events.jsonl`, `requests.csv`, metric dumps), with no invented
  timeline entries; every timeline row cites its source artifact. Scenario selection rationale
  (`evidence/i7/checklist.md` §4): scenario 4 for the one real defect-shaped finding; scenario
  2 for the richest byte-level SSE evidence in the campaign (a captured raw stream showing the
  exact standardized mid-stream error event); scenario 9 for the cleanest "nothing went wrong,
  exactly as designed" resilience result (35/35 requests unaffected by a real ~3s PostgreSQL
  outage).
- **No GPU/vLLM claim anywhere** — the whole campaign ran on the same CPU-fallback stack this
  repo's I4/D-005 and I5/D-006 already carry forward (mock backend for 10/12 scenarios; real
  llama.cpp, same pinned commit and model as I3/I4/I5, for scenario 8's config-reload test via
  `gateway-llamacpp`). Per 07 §I7's own acceptance text, this single already-established
  deviation covers the whole campaign — there is no new scenario-by-scenario GPU/CPU split to
  record.
- **Pins:** 2 new `pins/pins.yaml` entries (`inferops-fault-campaign`,
  `inferops-fault-campaign-inferbench`, both `proven_at: [I7]`); `engine-llamacpp`,
  `model-gguf`, `inferops-infergate-image`, `inferops-mock-backend-image`,
  `inferops-llamacpp-engine-image` gained `I7` in their existing `proven_at` lists (same
  commits/digests, confirmed by direct comparison against `inferops/faults/lib.sh`'s
  `GATEWAY_IMAGE`/`MOCK_IMAGE` constants and scenario 8's `gateway-llamacpp` citation).
  Validator green: 24 artifact entries (`python3 pins/validate_pins.py`).
  `milestone_evidence.I7` now points at `evidence/i7/`.
- `compatibility/matrix.md` gained an I7 row (headline finding stated in the row itself, not
  just in a footnote) and a re-run trigger note (scenario 4 re-run when infergate ships a fix;
  scenarios 1/3/7/10 re-run when IG-T012 lands N-backend CLI exposure).
- **Honesty:** I7 acceptance review by the user is pending, exactly like I2/I3/I5 before it —
  `proven_at: [I7]` reflects that the evidence exists and supports the claim, not that the
  milestone has been accepted. See `evidence/i7/checklist.md` §7 for the full uncertainties
  list. The two headline findings (scenario 4's defect, scenarios 1/3/7/10's structural
  deviation) are stated at the top of the checklist (§0), in the compatibility matrix row, in
  this log entry, and as postmortem content — deliberately repeated rather than mentioned once
  and left to be missed.

### 2026-07-12 — IL-T005: Scenario D / I5 evidence archived (D-006, RQ-14 compose-pivot)

- **This session assembled evidence from the inferops operational stack** (`/home/user/inferops`,
  commit `db30279760dacc3f5af25595551365530f60bdac`), which was already built and running:
  IO-T002 (compose cluster baseline, `135dd34`), IO-T003 (observability stack, `816c469`),
  IO-T004 (lifecycle semantics, `326e7bf`), IO-T005 (llama.cpp CPU-fallback engine, `17aee67`),
  IO-T010 (config rollout + upgrade/rollback, `db30279`). Nothing in inferops's own source was
  read or modified; the stack was cited by path+commit exactly as I1/I5/I7 archiving duty
  requires (`docs/integration.md`).
- **Headline deviation, carried through every claim in this record (D-006 below):** inferops's
  own RQ-14 compose-pivot — this sandbox cannot schedule any Kubernetes pod on any CRI-based
  distribution (proven at the runc/nsexec level: containerd's CRI plugin sets
  `oomScoreAdj: -998` on every pod sandbox; this environment's own container lacks
  `CAP_SYS_RESOURCE`). The *runtime* stack runs on Docker Compose; Kubernetes manifests are
  fully authored (Kustomize) and validated against a **live k3s API server** (real
  `kubectl apply` to etcd, server-side dry-run) — everything except the final
  kubelet→CRI→runc pod-start step. **No pod scheduling is claimed anywhere.**
- **GPU node continues I4's CPU-fallback (D-005), not a new deviation:** gate G6 was never
  opened for inferops either (no GPU rented, no budget session). The engine actually serving
  traffic is real llama.cpp — the **same pinned commit** (`8f114a9b573b69035299f9b924047f53c1e22c7e`)
  and, re-verified live this session by `sha256sum`, the **same pinned model file**
  (`6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e`) as this repo's own I3/I4
  Scenario B baseline. No vLLM, no GPU claim anywhere.
- **I5's five acceptance criteria (`portfolio-planning/07-integration-milestones.md` §I5),
  mapped item-by-item in `evidence/i5/checklist.md` §1:**
  1. Deployment from released images only — **PASS** (RQ-14 caveat): infergate **v0.1.0**
     (the program's first genuine tagged-release image, not a git-archive local build) at
     digest `sha256:1971426b393b3e00b30cac0690d38b31667b5e34ebbeb6e111a54c369fb54c7e`,
     confirmed running via live `docker inspect` this session; the observability stack
     (OTel/Prometheus/Grafana/Tempo) are genuine upstream Docker Hub/quay.io digests; the
     llama.cpp engine image is a pinned-upstream-commit build (same pattern as Scenario B).
  2. Warm-up-aware readiness — **PASS** (`inferops/scripts/evidence/warmup-readiness-20260711T235223Z/`,
     5/5: `/healthz` genuinely false during simulated warm-up, typed 503 mid-warm-up, 0
     restarts).
  3. Rolling update under load, zero client-visible errors — **PASS**
     (`inferops/scripts/evidence/rolling-update-20260711T234628Z/`: 27 short + 3 stream
     requests, 0 client-visible errors; corroborated by `drain-test-20260711T234926Z/` 3/3 and
     the PDB `deploy/infergate/base/pdb.yaml`; further corroborated by IO-T010's
     config-rollout-under-load, 0/24 + 0/4 dropped).
  4. Golden dashboards live — **PASS** (`inferops/dashboards/golden-dashboard.json`, 11/11
     Contract-2 names, Grafana-API-confirmed provisioning + live panel-query render).
  5. Traces end-to-end — **PASS** (exemplar → Tempo, full span sequence
     `recv → queue.wait → upstream.connect → ttft → stream.relay → settle`, proven at
     IO-T003 against the mock backend).
- **New evidence generated this session (not pure citation), kept light per instruction:** the
  cited inferops evidence proved the observability pipeline end-to-end only against the
  mock-backed main gateway (IO-T003); IO-T005's own smoke test verified real llama.cpp
  inference + cancellation but not Prometheus/Tempo. This session sent 5 non-stream + 2
  streaming real completions through `gateway-llamacpp` (port 8082), confirmed
  `inference_requests_total{backend="llamacpp"}` advanced by exactly 7, pulled a fresh
  Prometheus exemplar, and resolved it in Tempo with the full expected span sequence — closing
  that gap. Archived at `evidence/i5/raw/demo-20260712T005146Z/` (`transcript.log` is the
  master record).
- **Pins:** 9 new `pins/pins.yaml` entries added (`inferops-bundle`, `inferops-infergate-image`,
  `inferops-mock-backend-image`, `inferops-llamacpp-engine-image`,
  `inferops-otel-collector-image`, `inferops-prometheus-image`, `inferops-grafana-image`,
  `inferops-tempo-image`, `inferops-dashboards`), all `proven_at: [I5]`; `engine-llamacpp` and
  `model-gguf` gained `I5` in their existing `proven_at` lists (same commit / same file,
  re-verified live). Validator green: 22 artifact entries (`python3 pins/validate_pins.py`).
  `milestone_evidence.I5` now points at `evidence/i5/`.
- `compatibility/matrix.md` gained an I5 row (RQ-14 compose-pivot + CPU-fallback both stated in
  the row itself, not just in a footnote).
- **Honesty:** I5 acceptance review by the user is pending, exactly like I2/I3 before it —
  `proven_at: [I5]` reflects that the evidence exists and supports the claim, not that the
  milestone has been accepted. See `evidence/i5/checklist.md` §6 for the full uncertainties
  list (missing dashboard screenshot, fault campaign not yet run, etc.).

### 2026-07-12 — IL-T004: Scenario C / I4 recorded as a CPU-fallback deviation (D-005)

- **Not a GPU run.** Gate G6 (written hypothesis + full config manifest + auto-stop script +
  budget alert, pre-approved by the user, mandatory before any GPU spend) was **deferred by
  user decision on 2026-07-11** — no GPU rental this program wave. Verified live before
  writing this entry that the GPU-path prerequisites genuinely do not exist yet: infergate
  `IG-T014` (vLLM adapter) is **not started** (infergate `docs/tasks.md`, repo at commit
  `f362ceb7835c91182f19645a705de66af3017c82`); inferbench `IB-T011` (GPU experiment set 2)
  has **not been executed** (inferbench `docs/tasks.md`, repo at commit
  `62c2704997e6c8a2966307ee3d8dbfd16747b631`); `pins/pins.yaml`'s header still lists
  `engine-vllm` as an unpinned "entry still expected."
- **This session assembled evidence; it did not measure anything new**, per the scenario C
  README's own contingency clause ("if GPU access is blocked, the llama.cpp variant (Scenario
  B) becomes the measured baseline") and program charter §7
  (`portfolio-planning/00-program-charter.md`, "Budget and hardware assumptions": "if GPU
  access fails, llama.cpp becomes the primary measured engine ... GPU experiments compress
  into one scripted final session"). Three already-published sources were cited by path and
  commit (never copied):
  1. `evidence/i3/` (this repo, I3 accepted 2026-07-11, commit `61132b2`) — llama.cpp
     streaming (`chat-short`/`shared-prefix` via gateway), the composed-stack cancellation
     arm, and mock↔llama.cpp failover.
  2. infergate `docs/implementation-notes.md`, log entry "2026-07-10 — IG-T005: llama.cpp
     adapter (M4)" (commit `74f2372acea62645fa3c1d91689574ea9de7c589`, same commit as this
     repo's pinned `engine-llamacpp`) — adapter-level 3-point cancellation against a real
     `llama-server`: queued 2.6 µs–645 µs, pre-first-token 0.77 s–2.19 s (decode-batch
     abort-detection granularity), mid-stream **1.25 ms–5.24 ms**. Caveat carried forward
     honestly: this measurement used an unpinned tiny random-weight test GGUF (infergate
     deviation D2), not the pinned Qwen2.5-1.5B-Instruct model.
  3. inferbench `docs/evidence/ib-t010/benchmark-report-1.md` (`IB-T010` E1, commit
     `6a3fb5347b9e0d21fa56c63836bc242a7d7d51e2`) — gateway-overhead comparison (direct vs
     via-gateway, ≥3 runs/point): mock arm **CONFIRMED** (paired p95 +2.21 ms, p99 +2.81 ms,
     both under the <10 ms/<20 ms target); llama.cpp arm **INCONCLUSIVE at the ms scale**,
     reported honestly (engine run-to-run variance 2–3 orders of magnitude above the bound
     under test). Noted that this experiment's own infergate pin (`6827d8c`) and llama.cpp
     flags (`-np 1 -c 4096`, single slot) differ from this repo's Scenario B pins — cited as
     sibling-repo evidence, not re-pinned here (see the deviation entry below).
- Full item-by-item mapping against `scenarios/c/README.md`'s acceptance checklist, the
  explicit deferred-GPU-evidence list, and the pins rationale: `evidence/i4/checklist.md`
  (+ `evidence/i4/pins-snapshot.yaml`, `evidence/i4/notes.md`).
- `pins/pins.yaml`: `proven_at` extended to `[I3, I4]` for the six Scenario B pin-set entries
  this evidence draws on (`contracts-bundle-v0-2-0`, `infergate-binary`,
  `infergate-mock-binary`, `inferbench-binary-69a5abc`, `engine-llamacpp`, `model-gguf`);
  `milestone_evidence.I4` now points at `evidence/i4/`. Validator green (still 13 artifact
  entries — no new pins.yaml artifacts were added; see the deviation entry for why). No
  vLLM/GPU-specific `proven_at` claim was made anywhere.
- `compatibility/matrix.md` gained an I4 row (CPU-fallback, explicitly marked as such) and its
  stale "I3 acceptance review pending" status line was corrected to "ACCEPTED" (I3 was in fact
  accepted 2026-07-11; the matrix file had not been updated to say so until now).

### 2026-07-11 — IL-T003: Scenario B executed, I3 evidence recorded

- Composed stack: `inferbench (host) → infergate gateway → llama.cpp` (real engine, CPU),
  host processes not containers (deviation D-004, below). Build/run/check scripts under
  `scenarios/b/`; evidence under `evidence/i3/` (checklist executed item-by-item,
  `evidence/i3/notes.md` for dated observations).
- Pins used and recorded (validator green, 6 new entries + 7 carried from I2 = 13 total):
  serving-contracts v0.2.0 (tag 484b449), infergate@74f2372 + infergate-mock@74f2372 host
  binaries (sha256 recorded), inferbench@69a5abc binary (same commit's analysis/report
  package used via `PYTHONPATH`), llama.cpp@8f114a9 prebuilt (commit + binary sha256
  verified at build), Qwen2.5-1.5B-Instruct GGUF Q4_K_M (file sha256 = pinned revision).
  `proven_at` stays `[]` everywhere until I3 passes user acceptance review.
- Session had two aborted attempts before the evidence-producing run (a `run.sh` pid-capture
  bug; a mid-run container freeze) — both preserved under `evidence/i3/aborted/`, excluded
  from every acceptance number. Full accounting: `evidence/i3/checklist.md` "Session
  history".
- All acceptance numbers live in `evidence/i3/checklist.md` + `logs/checks.log`; every
  check computed from raw artifacts by `scenarios/b/checks.py` (evidence tooling only).
  Benchmark report #0 (three arms: engine-direct, via-gateway, shared-prefix) generated by
  the pinned `inferbench-analysis` package, schema-valid against `benchmark-result`, each
  carrying the mandatory validity block.
- One follow-up-agent recheck (2026-07-11, later same day): the evidence-producing run's
  single failing check (`cancel-llama`: a llama-server log-census off-by-one, 21 "cancel
  task" lines vs 20 client cancels) was re-tested once against the same pins on an
  otherwise-idle host; the recheck passed cleanly (20/20) and did not reproduce the
  discrepancy. Recorded as an open, unreproduced observation rather than a resolved defect
  — see `evidence/i3/checklist.md` item 5. The original run's data is preserved (not
  overwritten) for defect-evidence purposes.
- Cross-reference correction: `scenarios/b/README.md` and a `pins/pins.yaml` note both
  mis-cited the host-process decision as "A-007"; corrected to **D-004** (its actual entry
  below) in this pass.

### 2026-07-10 — IL-T002: Scenario A executed, I2 evidence recorded

- Composed stack: `inferbench (host) → infergate gateway → mock backend`, gateway exporting
  OTLP/HTTP traces to an OTel Collector (file + debug exporters). PostgreSQL absent by
  deviation D-001 (below). Compose + Dockerfiles + build/run/check scripts under
  `scenarios/a/`; evidence under `evidence/i2/` (checklist executed item-by-item).
- Pins used and recorded (validator green, 7 entries): infergate@5d69aeb gateway + mock
  images (local builds from `git archive`, image IDs recorded as digests),
  inferbench@caa5074 binary (sha256 recorded), serving-contracts@8d81492 pre-release bundle
  (kit used for all validation), OTel Collector v0.156.0 (ocb build), GenAI semconv v1.34.0
  (`reverify: true` — status "Development" as of 2026-07, observed live on gateway spans).
  `proven_at` stays `[]` everywhere until I2 passes user acceptance review.
- All acceptance numbers live in `evidence/i2/checklist.md` + `logs/checks.log`; every
  check computed from raw artifacts by `scenarios/a/checks.py` (evidence tooling only).
- Volatile-fact re-verification done live this session: OTel GenAI semconv still a
  "Development"-status attribute set at v1.34.0 (observed `gen_ai.*` attributes on real
  spans); OTel Collector current release v0.156.0 (2026-07-06, Go module proxy).

### 2026-07-10 — IL-T001 bootstrap

- Repository skeleton created: full `docs/` set (15 docs + `adr/`), `pins/pins.yaml` +
  validator, scenario A–E definitions, quickstart structure, compatibility conventions +
  empty matrix, OSS log skeleton, study tracker, evidence/reports/postmortems/portfolio
  directory conventions.
- Pins file format defined per ADR-0001; evidence immutability per ADR-0002. Validator
  (`pins/validate_pins.py`, PyYAML-based) runs green on the empty `pins.yaml` and on the seed
  fixture `pins/examples/seed-entry.yaml`.
- Everything is **unpinned as of 2026-07-10**: `artifacts: []` — no sibling repo has a
  release yet. The seed fixture is a format demonstration only and is clearly marked
  non-normative; it makes no "proven together" claim.
- Reversible assumptions recorded (below). No compose files yet — those are IL-T002 scope.
- Volatile facts carried forward with `reverify` flags (all "as of 2026-07 — re-verify at use
  time"): OTel GenAI semconv status "Development"; vLLM v0.24.x baseline; GAIE → llm-d
  migration (`InferenceModel`→`InferenceObjective` rename); GPU budget envelope $150–250.
  None were re-verified live in this session — they enter the docs flagged, not asserted.

## Assumptions (reversible; recorded per working-style rule)

- **A-001 (2026-07-10):** Pins format is YAML (`pins.yaml`) with a Python/PyYAML validator,
  chosen over JSON for comment support and human-readable diffs in review. Reversible: the
  schema is representable 1:1 in JSON if tooling later requires it. See ADR-0001.
- **A-002 (2026-07-10):** Validator dependency is Python 3 + PyYAML (available in the dev
  environment). If a future CI environment lacks PyYAML, the fallback is vendoring a
  requirements note, not vendoring code.
- **A-003 (2026-07-10):** Scenario/quickstart docs assume Docker Compose as the local
  orchestrator for scenarios A–C (the program's GPU-free local path); the compose files
  themselves are IL-T002+ scope and their format may still be adjusted then.
- **A-004 (2026-07-10):** Milestone-evidence links inside `pins.yaml` use the
  `milestone_evidence` map (milestone → relative path) rather than per-entry links, keeping
  entries artifact-shaped. Reversible without schema break (additive field).
- **A-005 (2026-07-10):** Container-image pins for locally built images record the local
  content-addressed image ID as `digest` (matches the pins schema's `sha256:<64 hex>`),
  because no registry hosting exists yet (RQ-4) and unpushed images have no RepoDigest.
  Reversible: re-record the registry digest in a new dated entry when images are pushed.
- **A-006 (2026-07-10):** The cancellation release bound for the composed Scenario A stack
  is declared at 100 ms (the same bound infergate declared and met for IG-T003/G2),
  measured as mock-observed abort timestamp (`/debug/state` `at_unix_nano`) vs client-side
  cancel completion (raw-event `end_ts`) on a shared host clock. Reversible: tighten after
  more runs.
- **A-007 (2026-07-11):** The cancellation release bound for the composed Scenario B stack
  (real engine) is declared at **2.5 s**, measured as the `/slots` `is_processing`
  true→false transition (25 ms polling) vs client-side cancel completion. The bound is the
  ENGINE's release granularity, not gateway latency: llama-server notices an abort at the
  next decode-batch boundary, which can be one concurrent prefill ubatch away (infergate
  IG-T005 measured the gateway-propagation component directly at 1.25–5.24 ms mid-stream,
  and pre-first-token release up to 2.19 s at prefill-batch boundaries). Reversible:
  tighten per-regime (decode-only vs mixed prefill) after more runs.
- **A-008 (2026-07-11):** Scenario B SLO thresholds are derived from same-day calibration
  probe maxima through the composed path (×1.5 headroom, rounded up to 2 significant
  digits; seeds distinct from the measured runs), keeping `slo.schema.json`'s
  measurement-only rule for model-serving SLOs honest. The SLO exists to exercise
  goodput@SLO end-to-end; it is not an external target. Reversible: re-derive whenever
  host, engine build, model, flags, or rates change (stated in the SLO file itself).

## Deviations

### D-001 (2026-07-10) — Scenario A v1 runs without PostgreSQL (no usage write yet)

- **Evidence:** infergate@5d69aeb (the pinned gateway) has no tenancy/usage accounting —
  IG-T007 (tenant/config registry) and IG-T008 (usage accounting + PostgreSQL write) are
  Wave-3 tasks in infergate; the pinned gateway's settle path is annotated "trivial settle:
  accounting (IG-T008) not built yet".
- **Decision:** compose Scenario A v1 **without** a PostgreSQL service; record the I2
  acceptance item "PostgreSQL usage write observed and consistent with raw events" as
  **DEVIATION (not claimable)** in `evidence/i2/checklist.md`. Nothing is faked: no
  placeholder database, no synthetic usage rows.
- **Consequences:** I2 evidence is complete for every other criterion; the usage-write
  criterion remains open, so I2 acceptance is requested *with* this recorded deviation.
- **Follow-up:** when IG-T008 lands and a new infergate release is pinned, re-run Scenario A
  with PostgreSQL composed and execute the usage-write criterion for real (new dated
  evidence entry under `evidence/i2/`).

### D-002 (2026-07-10) — Local FROM-scratch images instead of registry-pulled multi-stage builds

- **Evidence:** this environment's egress proxy answers 403 to CONNECT for every container
  registry blob CDN tried (docker.io via `production.cloudfront.docker.com`, ghcr.io via
  `pkg-containers.githubusercontent.com`) — recorded from the proxy status output during
  this session. No base image (golang/alpine/distroless) can be pulled, so an in-Docker
  multi-stage Go build is impossible here.
- **Decision:** `scenarios/a/build.sh` compiles the pinned sources on the host
  (CGO_ENABLED=0, toolchain recorded in `.build/build-info.txt`), strictly from
  `git archive <pinned commit>` — never a working tree — and the committed Dockerfiles
  assemble minimal `FROM scratch` images. Local image IDs recorded as digests (A-005).
- **Consequences:** images are reproducible from pins + scripts but not registry-hosted;
  the "released images by digest" ideal is approximated by commit-pinned local builds with
  recorded content digests.
- **Follow-up:** when registry access/hosting exists (RQ-4), switch to pushed multi-stage
  images and re-record RepoDigests in new dated pin entries.

### D-003 (2026-07-10) — OTel Collector built with ocb instead of the upstream contrib image

- **Evidence:** the proxy denial in D-002 also blocks
  `docker.io/otel/opentelemetry-collector-contrib` AND GitHub release assets (the
  `otelcol-contrib` tarball got 403). The Go module proxy IS allowlisted.
- **Decision:** build a minimal collector (otlp receiver, batch processor, contrib file
  exporter, debug exporter) with the official OpenTelemetry Collector Builder
  (ocb v0.156.0) from the pinned manifest `scenarios/a/otelcol-builder-manifest.yaml`;
  package it `FROM scratch`. All component versions are pinned released modules (v0.156.0).
- **Consequences:** functionally equivalent for Scenario A's needs (OTLP/HTTP in, file
  export out); not byte-identical to the upstream contrib distribution image.
- **Follow-up:** re-pin to the upstream contrib image digest when a registry is reachable
  (`otel-collector-image` carries `reverify: true`).

### D-004 (2026-07-11) — Scenario B runs host processes, not containers

- **Evidence:** the Scenario B definition (IL-T001) listed digest-pinned images
  (`infergate-image`, `infergate-mock-image`). The real engine, however, is a **prebuilt
  host llama-server** (shared-library build at /home/user/tools/llama.cpp) serving a 1.1 GiB
  host model file, and the registry constraints of D-002 still hold (no base images
  pullable). Containerizing only the gateway/mock around a host engine buys no isolation
  and adds a bridge hop to a measurement path already fighting for 4 CPU cores.
- **Decision:** Scenario B composes **host processes**: gateway + mock-backend compiled
  read-only from `git archive <pinned commit>` (sha256s recorded in
  `evidence/i3/logs/build-info.txt`, pinned as `kind: binary` entries), llama-server used
  prebuilt with its commit AND binary sha256 verified at build time, the model pinned by
  file sha256. Port/PID lifecycle is managed by `scenarios/b/run.sh` with stale-port guards.
- **Consequences:** the "released images by digest" ideal is approximated by commit-pinned
  binaries with recorded content digests (same spirit as D-002); container/registry rigor
  remains proven at I2, and full operational rigor (released images, k8s) is I5's job.
- **Follow-up:** when registry hosting exists (RQ-4), Scenario B can be re-composed from
  pushed images; the pins gain image entries in a new dated set.

### D-005 (2026-07-12) — I4 recorded as a CPU-fallback deviation; GPU acceptance not claimed

- **Evidence:** gate G6 (GPU session discipline: written hypothesis, full config manifest,
  auto-stop script, budget alert, pre-approved by the user) requires a GPU rental that the
  user decided against on 2026-07-11 for this program wave. Independently confirmed this
  session that the GPU-path prerequisites do not yet exist: infergate `IG-T014` (vLLM
  adapter) is not started; inferbench `IB-T011` (GPU experiment set) has not run;
  `pins/pins.yaml` carries no `engine-vllm`/model-checkpoint/driver-CUDA/instance-type pins.
- **Decision (conservative, reversible, per `scenarios/c/README.md`'s own contingency clause
  and program charter §7):** I4 is recorded via the llama.cpp CPU-fallback baseline already
  proven at I3, supplemented by two sibling-repo evidence sources cited by path+commit —
  infergate IG-T005 (adapter-level cancellation vs. a real `llama-server`) and inferbench
  IB-T010 E1 (gateway-overhead comparison, direct vs via-gateway) — assembled, not
  re-measured, this session. No new `pins/pins.yaml` artifact entries were created for the
  two sibling-repo commits behind the IB-T010 comparison (infergate@`6827d8c`,
  inferbench@`6a3fb53`) or for IG-T005's commit (same commit as the already-pinned
  `engine-llamacpp`, so nothing new to add there either): those commits were built and
  verified by their own repos' tooling, not this repo's `scenarios/*/build.sh`, so they are
  cited under this repo's evidence-archivist role (the same pattern as the I1/I5/I7 archiving
  duties) rather than pinned as inference-lab-composed artifacts. `proven_at` was extended to
  include `I4` only for the six Scenario B pin-set entries that genuinely back this evidence
  (`contracts-bundle-v0-2-0`, `infergate-binary`, `infergate-mock-binary`,
  `inferbench-binary-69a5abc`, `engine-llamacpp`, `model-gguf`) — see each entry's notes in
  `pins/pins.yaml` for exactly which §2 evidence pillar(s) each one backs (not all six back
  all four pillars; the gateway-overhead comparison in particular used different
  infergate/inferbench commits than this repo's own I3 pins).
- **Consequences:** I4's normative acceptance criteria (streaming + cancellation verified via
  **vLLM engine metrics** on a **rented GPU**; gateway-overhead comparison **at GPU scale**;
  GPU session auto-stop/budget) are **not demonstrated and not claimed**. The portfolio's
  final-narrative sentence "I measured the gateway and engine independently and together"
  (`docs/charter.md`) is, for now, evidenced at CPU scale only. The I8 honest-limitations
  statement must carry this forward. Full acceptance-item mapping and the explicit
  deferred-GPU-evidence list: `evidence/i4/checklist.md`.
- **Follow-up:** when GPU budget is approved and `IG-T014` + `IB-T011` land, re-run Scenario C
  for real against vLLM per `scenarios/c/README.md` and its full G6 discipline; that run
  supersedes this record with a **new dated evidence entry** under `evidence/i4/` (this one
  stays archived unmodified, per evidence immutability, ADR-0002) and the corresponding
  `compatibility/matrix.md` row is superseded, not rewritten.

### D-006 (2026-07-12) — I5 recorded on inferops's RQ-14 compose-pivot stack; no pod scheduling claimed

- **Evidence:** `inferops`'s own environment cannot schedule any Kubernetes pod, on any
  CRI-based distribution, in this sandbox — proven at the runc/nsexec level
  (`/home/user/tools/k8s-env-probe-report.md`, cited by `inferops/docs/implementation-notes.md`
  Deviation D-1, user-approved as RQ-14 on 2026-07-11, *before* this repo's own IL-T005 task
  began): containerd's CRI plugin unconditionally sets `oomScoreAdj: -998` on every pod
  sandbox, and the sandbox's container lacks `CAP_SYS_RESOURCE`, so pod-sandbox creation fails
  identically under kind and k3s, under both runc and crun. This is an environment limitation
  external to both repos, not a defect in any manifest inferops authored.
- **Decision (conservative, reversible; not this repo's decision to make or unmake — it
  belongs to inferops, whose evidence this repo only archives per its evidence-archivist
  role):** I5 is recorded on inferops's actual operational stack: the *runtime* substrate is
  Docker Compose; Kubernetes manifests are fully authored (Kustomize, ADR-0001) and validated
  against a live k3s API server (real `kubectl apply` to etcd, server-side dry-run) —
  everything except the final kubelet→CRI→runc pod-start step. This repo's own role (IL-T005:
  consumer-side verification + evidence archiving) is unaffected in kind — the acceptance
  criteria (deployment from released images, warm-up-aware readiness, zero-error rolling
  update, golden dashboards, end-to-end traces) are all still demonstrated, just against a
  compose stack instead of a scheduled cluster, and this record says so on every claim (never
  silently implying pod scheduling). GPU node continues I4's own D-005 CPU-fallback (no GPU
  rented, no vLLM) — not a new deviation, the same one, carried forward.
- **Consequences:** every "deployed"/"running"/"serving traffic" claim in `evidence/i5/`
  refers to the compose stack, not a scheduled Kubernetes Pod; every "manifest correctness"
  claim refers to k3s API-server validation. I5's normative language ("on the local cluster +
  GPU node") is satisfied in spirit (deployment-contract conformance, lifecycle semantics,
  observability, released-image discipline) but not literally (no pod, no GPU) — carried
  forward to the I8 honest-limitations statement alongside I4's GPU deferral.
- **Follow-up:** if this sandbox's `CAP_SYS_RESOURCE` restriction is ever lifted, inferops
  re-runs its k3s validation scripts with a full agent (kubelet) as a strictly additive
  confirmation — no manifest changes expected. If/when a real GPU session runs (superseding
  I4), a corresponding I5 re-run against a real vLLM-on-GPU deployment supersedes this record
  too, per ADR-0002 evidence immutability (this record stays archived, not deleted).

<!--
Deviation policy: when repository evidence forces a deviation from the approved plan, choose
the conservative reversible option, record the evidence, decision, consequences, and
follow-up here, and continue. Pause for user input only when the deviation changes public
contracts, repository ownership, security posture, or milestone scope.

Entry format:

### D-NNN (YYYY-MM-DD) — short title
- Evidence:
- Decision:
- Consequences:
- Follow-up:
-->
