# Tasks — inference-lab

Stable IDs — never renumbered. Kept current with status + evidence links. IL-T010–T012 are
the OSS-track execution tasks (externally paced, never on the critical path).

| ID | Title | Complexity | Critical path | Parallel-safe | Required | Status | Evidence |
|---|---|---|---|---|---|---|---|
| IL-T001 | Skeleton: pins, quickstart, scenarios, logs | M | yes | no | Required | **In review** (skeleton committed 2026-07-10; awaiting user plan review) | this commit; `pins/` validator output in `docs/implementation-notes.md` |
| IL-T002 | Scenario A + milestone I2 | M | yes | no | Required | **Done** (executed 2026-07-10; I2 ACCEPTED by user 2026-07-11 with recorded deviation D-001 — PostgreSQL usage write re-runs at IG-T008) | `scenarios/a/`, `evidence/i2/checklist.md` |
| IL-T003 | Scenario B + milestone I3 | M | yes | no | Required | **Done** (executed 2026-07-11; I3 ACCEPTED by user 2026-07-11; open observation on the cancellation log-census, not blocking) | `scenarios/b/`, `evidence/i3/checklist.md`, `evidence/i3/reports/` |
| IL-T004 | Scenario C + milestone I4 (GPU) | M | yes | no | Required | **Done as CPU-fallback deviation** (assembled 2026-07-12; G6/GPU deferred by user decision 2026-07-11 — no GPU rental; I4 recorded via the llama.cpp baseline (I3) + infergate IG-T005 + inferbench IB-T010 E1, not GPU acceptance) | `evidence/i4/checklist.md`, `evidence/i4/pins-snapshot.yaml` |
| IL-T005 | Scenario D + milestone I5 | M | yes | no | Required | **Done, evidence archived** (assembled 2026-07-12 from the inferops operational stack, commit `db30279`; headline deviation RQ-14 compose-pivot — no pod scheduling claimed, manifests validated against a live k3s API server instead; CPU-fallback llama.cpp continues I4/D-005, no vLLM/GPU; **acceptance review pending**, I2/I3 precedent) | `scenarios/d/README.md`, `evidence/i5/checklist.md`, `evidence/i5/pins-snapshot.yaml`, `evidence/i5/raw/demo-20260712T005146Z/` |
| IL-T006 | Scenario E + milestone I6 (the central story) | L | yes | no | Required | Not started | — |
| IL-T007 | Failure campaign evidence + milestone I7 | M | yes | no | Required | **Done, evidence archived** (assembled 2026-07-12 from the inferops 12-scenario Contract 6 fault campaign, commits `bfca054`/`a1e0af5`/`a07fd2f`; headline finding surfaced not buried — scenario 4 (slow client) is a real, reproducible deviation-documented finding; scenarios 1, 3, 7, 10 carry a documented structural single-backend-topology deviation; client impact measured by inferbench for scenarios 1, 2, 5, 6, 12; 3 postmortems published, exceeding the ≥2 minimum; no GPU/vLLM claim, continues I4/D-005 and I5/D-006; **acceptance review pending**, I2/I3/I5 precedent) | `evidence/i7/checklist.md`, `evidence/i7/campaign-matrix.md`, `evidence/i7/client-impact.md`, `evidence/i7/pins-snapshot.yaml`, `postmortems/pm-001.md`, `pm-002.md`, `pm-003.md` |
| IL-T008 | Compatibility matrix upkeep | S | no | yes | Required | Ongoing (starts with first consumed release) | — |
| IL-T009 | Portfolio release + milestone I8 | L | yes | no | Required | Not started | — |
| IL-T010 | OSS: score, build, first reproduction | M | no | yes | Required | **In review** (executed 2026-07-11: live scoring refresh done, user approved llm-d/llm-d-router primary; built + tested from source; local-only reproduction of issue #1625's unaddressed `fairness_id` cardinality subset complete; upstream communication drafted but **not posted** — user review pending at IL-T011, so the task's own "acknowledged upstream" stop condition is not yet met) | `oss/scoring-refresh.md`, `oss/log.md` (2026-07-11 entries), `oss/reproductions/2026-07-11-llm-d-router-1625-fairness-id-cardinality.md`, `oss/drafts/2026-07-11-llm-d-router-1625-comment.md` |
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
- **Status (2026-07-10):** executed — `scenarios/a/{build.sh,compose.yaml,run.sh,checks.py}`
  + evidence under `evidence/i2/` (checklist, raw events, metrics scrapes, trace export, kit
  validation). Deviations recorded: D-001 (no PostgreSQL — IG-T007/T008 are Wave 3; usage
  criterion not claimable, scenario re-runs when IG-T008 lands), D-002/D-003 (registry
  egress blocked — local FROM-scratch images, ocb-built collector). Awaiting I2 acceptance
  review.

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
- **Status (2026-07-12):** **CPU-fallback deviation recorded, GPU acceptance NOT claimed.**
  Gate G6 (GPU session) deferred by user decision 2026-07-11 (no GPU rental this program
  wave); `IG-T014` (vLLM adapter, infergate) and `IB-T011` (GPU experiment set, inferbench)
  remain not started/not executed as of this date — verified live against both sibling repos
  before writing this record. Per `scenarios/c/README.md`'s own contingency clause, the
  llama.cpp variant proven at I3 stands in as the measured baseline, assembled (not
  re-measured) from three already-published evidence sources: `evidence/i3/` (streaming,
  composed-stack cancellation, failover), infergate `docs/implementation-notes.md`
  (`IG-T005` log entry — adapter-level 3-point cancellation vs. real `llama-server`, mid-stream
  slot release 1.25–5.24 ms), and inferbench `docs/evidence/ib-t010/` (`IB-T010` E1 —
  gateway-overhead comparison: mock arm CONFIRMED paired p95 +2.21 ms, llama.cpp arm
  INCONCLUSIVE at the ms scale, reported honestly). Full item-by-item mapping, the
  deferred-GPU-evidence list, and the pins used: `evidence/i4/checklist.md`. `pins/pins.yaml`
  `proven_at` extended to `[I3, I4]` for the six Scenario B pin-set entries this evidence
  draws on; no vLLM/GPU-specific pin exists or is claimed.

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
- **Status (2026-07-12):** executed — evidence assembled from the already-completed inferops
  fault campaign (`/home/user/inferops`, commits `bfca054` IO-T006 scenarios 1-6, `a1e0af5`
  IO-T007 scenarios 7-12 + noisy-neighbor, `a07fd2f` evidence-note fixes). All 12/12 scenarios
  injected; client impact measured by inferbench for the 5 mandated streaming-critical
  scenarios (1, 2, 5, 6, 12); 3 postmortems published (pm-001..pm-003), exceeding the ≥2
  minimum. Headline findings surfaced prominently, not buried: scenario 4 (slow client) is a
  real, reproducible **deviation-documented** finding (the write-deadline did not close an
  8-second-stalled stream, 2.6x the configured 3s deadline) — the campaign's one result that
  reads as a defect rather than a topology limitation, corroborating infergate's own
  `internal/stream/relay.go` comment marking full slow-client handling as "later work";
  scenarios 1, 3, 7, 10 carry a documented structural single-backend-topology deviation
  (infergate `cmd/gateway/main.go` wires exactly one backend, IG-T012 not yet flag-driven for
  N>1 — infergate's own recorded scope reduction); scenario 6 carries one expected,
  non-defect admission-path discrepancy (no-auth topology). No GPU/vLLM claim anywhere —
  continuation of I4/D-005 and I5/D-006's CPU-fallback. Full item-by-item mapping:
  `evidence/i7/checklist.md`. **I7 acceptance review by the user is pending**, I2/I3/I5
  precedent.

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
