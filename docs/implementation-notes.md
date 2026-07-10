# Implementation Notes — inference-lab

Running log of decisions, surprises, re-verification results of volatile facts, and
deviations. Newest entries first within each section.

## Log

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
