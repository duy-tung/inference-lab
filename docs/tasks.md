# Tasks — inference-lab

Stable IDs — never renumbered. Kept current with status + evidence links. IL-T010–T012 are
the OSS-track execution tasks (externally paced, never on the critical path).

| ID | Title | Complexity | Critical path | Parallel-safe | Required | Status | Evidence |
|---|---|---|---|---|---|---|---|
| IL-T001 | Skeleton: pins, quickstart, scenarios, logs | M | yes | no | Required | **In review** (skeleton committed 2026-07-10; awaiting user plan review) | this commit; `pins/` validator output in `docs/implementation-notes.md` |
| IL-T002 | Scenario A + milestone I2 | M | yes | no | Required | Not started | — |
| IL-T003 | Scenario B + milestone I3 | M | yes | no | Required | Not started | — |
| IL-T004 | Scenario C + milestone I4 (GPU) | M | yes | no | Required | Not started | — |
| IL-T005 | Scenario D + milestone I5 | M | yes | no | Required | Not started | — |
| IL-T006 | Scenario E + milestone I6 (the central story) | L | yes | no | Required | Not started | — |
| IL-T007 | Failure campaign evidence + milestone I7 | M | yes | no | Required | Not started | — |
| IL-T008 | Compatibility matrix upkeep | S | no | yes | Required | Ongoing (starts with first consumed release) | — |
| IL-T009 | Portfolio release + milestone I8 | L | yes | no | Required | Not started | — |
| IL-T010 | OSS: score, build, first reproduction | M | no | yes | Required | Not started (gated on program wave ≥3 equivalent) | — |
| IL-T011 | OSS: minimal reproducer + upstream communication | M | no | yes | Required | Not started | — |
| IL-T012 | OSS: contribution + review follow-through | M | no | yes | Required | Not started | — |

Execution order: IL-T001 → IL-T002 → IL-T003 → IL-T004 → IL-T005 → IL-T006 → IL-T007 →
IL-T009, with IL-T008 ongoing per consumed release and IL-T010–T012 in parallel once the
program's gateway + bench core exist.

---

## IL-T001 — Skeleton: pins, quickstart, scenarios, logs

- **Goal:** bootstrap inference-lab structure + full `docs/` set.
- **Requirement:** machine-readable version-pin matrix (format + validator script); quickstart
  doc structure; scenario A–E definitions (purpose, components, pinned inputs, acceptance
  checklist each); OSS log skeleton; study-progress tracker.
- **Dependencies:** plan approval.
- **Expected files:** `docs/*` (15 files + `adr/`), `pins/pins.yaml` (+ validator),
  `scenarios/{a..e}/README.md`, `quickstart/README.md`, `oss/log.md`, `study/tracker.md`,
  `compatibility/README.md`.
- **Review focus:** pins format (machine-readable, provenance + date fields, digest support);
  no-runtime-logic scope honored.
- **Verification:** docs checklist complete; pins validator runs green on a seed entry.
- **Stop condition:** structure reviewed and approved.

## IL-T002 — Scenario A + milestone I2

- **Goal:** orchestrate `inferbench → infergate → mock → PostgreSQL → OTel` locally via
  compose; record I2 evidence.
- **Requirement:** compose file pinned to released images; seeded workload run; evidence per
  the full I2 acceptance list (`docs/integration.md`).
- **Dependencies:** IG-T003 (gateway streaming+cancellation), IB-T004 (bench client
  correctness), SC-T009 (contracts v0.1.0), IL-T001.
- **Expected files:** `scenarios/a/compose.yaml`, run scripts, `evidence/i2/*` (run logs,
  raw-event files, trace export, acceptance checklist).
- **Review focus:** evidence completeness against the I2 checklist; measurement-tolerance
  statement present.
- **Verification:** I2 checklist executed item-by-item. Indicative: `docker compose up` in
  `scenarios/a`; `inferbench run --workload chat-short --seed 42 --target http://infergate...`.
- **Stop condition:** I2 accepted (demonstrated + reviewed).

## IL-T003 — Scenario B + milestone I3

- **Goal:** orchestrate `inferbench → infergate → llama.cpp` on CPU; record I3 evidence.
- **Requirement:** scenario B compose/scripts; `chat-short` + `shared-prefix` workloads
  complete; first schema-valid benchmark report (report #0, methodology shakedown) archived;
  cancellation verified against llama.cpp; mock↔llama.cpp failover demonstrated.
- **Dependencies:** I2; IG-T005 (llama.cpp adapter), IB-T006 (report generator).
- **Expected files:** `scenarios/b/*`, `evidence/i3/*` (benchmark report #0, campaign logs),
  pins update (llama.cpp commit + GGUF model revision).
- **Review focus:** report #0 validity block; failover evidence.
- **Stop condition:** I3 accepted.

## IL-T004 — Scenario C + milestone I4 (GPU)

- **Goal:** orchestrate `inferbench → infergate → vLLM → observability` on a rented GPU;
  record I4 evidence.
- **Requirement/hypothesis:** GPU path works within the pinned config; streaming +
  cancellation verified via engine metrics; gateway-overhead comparison (direct vs
  via-gateway) measured with ≥3 runs/point. GPU session requires written hypothesis + full
  manifest + auto-stop + budget alert (gate G6).
- **Dependencies:** I3; IG-T014 (vLLM adapter), IB-T011 first session, G6.
- **Expected files:** `scenarios/c/*`, `evidence/i4/*` (session log, benchmark report,
  cancellation-verification metrics export, full GPU session manifest), pins update (vLLM
  version/commit, model checkpoint + quantization, driver/CUDA, instance type).
- **Review focus:** GPU session plan pre-approved; manifest completeness; fallback honesty.
- **Stop condition:** I4 accepted, **or** CPU-fallback deviation recorded (llama.cpp becomes
  the measured baseline).

## IL-T005 — Scenario D + milestone I5

- **Goal:** archive evidence for the operated stack
  `inferops → infergate → vLLM → OTel/Prometheus/Grafana/Tempo`; verify Scenario D from the
  consumer side. (I5 is owned by inferops.)
- **Requirement:** scenario D definition points at inferops runbooks + released manifests (no
  source checkouts); this repo captures and archives the I5 evidence set.
- **Dependencies:** IO-T005 (in-cluster vLLM via gateway).
- **Expected files:** `scenarios/d/README.md` (+ invocation pointers), `evidence/i5/*`
  (manifests, smoke outputs, dashboard exports, rolling-update test log), pins update
  (inferops release, dashboard/config bundle versions).
- **Review focus:** deployment-from-released-images-only confirmed; evidence completeness.
- **Stop condition:** I5 accepted (by its owner) and archived here.

## IL-T006 — Scenario E + milestone I6 (the central story)

- **Goal:** close and publish the capacity-feedback loop. inference-lab is the loop owner;
  fleetlab owns the recommendation.
- **Requirement:** benchmark results → fleetlab produces a schema-valid capacity
  recommendation (Contract 7, with stated uncertainty) → inferops applies the recommended
  change (replica count / config) → repeated benchmark measures the outcome → predicted vs
  measured compared and **published, including where the prediction was wrong**. Prediction
  error is a result, not a failure.
- **Dependencies:** I5 archived; FL-T009 (recommendation emitter), IO-T009 (autoscaling
  experiments), SC-T010 (contracts v1.0.0).
- **Expected files:** `scenarios/e/*` (loop orchestration script + README), `evidence/i6/*`
  (recommendation file, applied manifests, before/after benchmark results, error analysis =
  the loop report), pins update (fleetlab release, contracts v1.0.0).
- **Review focus:** loop honesty — prediction vs outcome stated plainly; uncertainty carried
  through; no cherry-picking.
- **Stop condition:** I6 accepted. (Never-cut: the loop may shrink to mock/llama.cpp scale but
  must close.)

## IL-T007 — Failure campaign evidence + milestone I7

- **Goal:** turn the inferops fault campaign into archived evidence + postmortems (inferops
  executes; this repo archives).
- **Requirement:** for selected scenarios: inject (inferops), observe gateway semantics,
  measure client impact (inferbench); publish ≥2 postmortems in the standard format; archive
  the 12-row campaign matrix (injected / observed / verdict), with client impact measured for
  at least the streaming-critical scenarios (1, 2, 5, 6, 12).
- **Dependencies:** IO-T006/T007.
- **Expected files:** `evidence/i7/*` (campaign matrix, client-impact measurements),
  `postmortems/pm-001.md`, `postmortems/pm-002.md` (+ format template).
- **Review focus:** postmortems built from real metrics, not narrative; deviations
  (GPU-dependent scenarios run on llama.cpp/mock path) recorded.
- **Stop condition:** I7 accepted.

## IL-T008 — Compatibility matrix upkeep

- **Goal:** keep the compatibility matrices and pins current across every release and
  milestone.
- **Requirement:** on every consumed release: pin bump entry (tag/digest/date/provenance);
  matrix row per integration milestone stating which released versions are proven together;
  the benchmark comparability rule printed in the matrix; re-run trigger notes (e.g. contract
  MAJOR ⇒ I1 re-run before any scenario is re-claimed).
- **Dependencies:** IL-T001; ongoing per release.
- **Expected files:** `pins/pins.yaml` (living), `compatibility/matrix.md`.
- **Review focus:** no unproven "compatible" claims; every row cites milestone evidence.
- **Stop condition:** matrix current at I8.

## IL-T009 — Portfolio release + milestone I8

- **Goal:** ship the portfolio release and pass the reproducibility audit.
- **Requirement:** quickstart ≤15 min from fresh clone (GPU-free, Scenario A); demo script +
  recorded demo; benchmark + capacity reports linked; failure evidence linked; OSS evidence
  (public links) recorded; landing page + articles; honest-limitations statement;
  compatibility matrix current; **reproducibility audit**: a fresh session re-derives every
  headline claim from pinned artifacts; claims that fail are removed or re-measured — no
  exceptions.
- **Dependencies:** I2–I7 evidence archived; IL-T008 current; IL-T010–T012 state known.
- **Expected files:** `portfolio/landing.md`, `portfolio/articles/{article-1,article-2}.md`
  (+ optional third), `portfolio/demo-script.md`, `portfolio/demo-video-script.md`,
  `portfolio/limitations.md`, `quickstart/*` finalized, release tag + audit checklist.
- **Review focus:** stranger-test dry run; audit rigor; limitations honesty.
- **Stop condition:** I8 accepted.

## IL-T010 — OSS: score, build, first reproduction

- **Goal:** refresh OSS candidate scoring with live checks, build the primary target locally,
  reproduce one existing issue. (Log here; work happens upstream.)
- **Requirement:** re-verify volatile facts live before committing — especially the Gateway
  API Inference Extension → llm-d migration (`InferenceModel`→`InferenceObjective` rename; as
  of 2026-07 — re-verify): if EPP work has moved, follow it into llm-d (same score profile).
  Build + test the chosen primary locally (kind-based for GAIE; record versions). Reproduce an
  existing open issue (prefer `good-first-issue`/`help-wanted` with testable behavior).
- **Dependencies:** program wave ≥3 equivalent (gateway + bench core exist).
- **Expected files:** `oss/scoring-refresh.md`, `oss/log.md` entries (build log, reproduction
  log, environment versions).
- **Review focus:** target choice sign-off by the user before proceeding to upstream contact.
- **Stop condition:** reproduction acknowledged upstream, or fallback triggered per
  contingency (`docs/oss-opportunities.md`).

## IL-T011 — OSS: minimal reproducer + upstream communication

- **Goal:** reduce the reproduction to the smallest config/cluster/test that shows it;
  communicate evidence upstream.
- **Requirement:** minimal reproducer + environment manifest posted as an issue/comment
  upstream. Public links recorded (created at execution time, not before). **User reviews
  every submission before posting.**
- **Dependencies:** IL-T010.
- **Expected files:** `oss/log.md` entries with public issue/comment links + the reproducer
  reference.
- **Stop condition:** maintainer response, or 2-week silence → contingency path.

## IL-T012 — OSS: contribution + review follow-through

- **Goal:** land a small upstream contribution and follow review through.
- **Requirement:** small test / fix / benchmark / validation / Kubernetes example / docs PR
  (avoid-list applies); address review promptly, keep scope fixed; record lessons.
- **Dependencies:** IL-T011.
- **Expected files:** `oss/log.md` entries (PR links, review threads, lessons note).
- **Review focus:** user reviews the PR before posting; review responses stay in scope.
- **Stop condition:** merged, **or** under substantive review at I8 with the contingency
  documented.
