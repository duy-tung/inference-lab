# Implementation Notes — inference-lab

Running log of decisions, surprises, re-verification results of volatile facts, and
deviations. Newest entries first within each section.

## Log

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
