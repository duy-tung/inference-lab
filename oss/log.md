# OSS Activity Log

Execution log for IL-T010–T012 (track definition: `docs/oss-opportunities.md`). OSS work is
externally paced and never on the critical path.

## Honesty rules (normative for this log)

- This log records **real interactions only**. Planned-but-not-sent communications are
  marked **[DRAFT]** and carry no links.
- **No upstream issues or PRs existed at planning time** — all public links are created at
  execution time, never before.
- Every entry is dated; environment versions are recorded with build/reproduction entries.
- The user reviews every upstream submission before posting; each posted entry notes that
  review.

## Minimum completion target (mandatory for I8)

| # | Item | Status | Public link |
|---|---|---|---|
| 1 | One acknowledged issue reproduction | **local reproduction complete, not yet communicated upstream** — draft comment prepared for user review, gated on IL-T011 (see 2026-07-11 reproduction entry below); "acknowledged" requires posting + a maintainer response, which is user-gated and has not happened | — |
| 2 | One PR merged or under substantive review | not started | — |
| 3 | One public benchmark or design artifact | not started | — |
| 4 | Documented maintainer interaction | not started (interaction is drafted, not sent — see IL-T011) | — |

## Targets (selection: `docs/oss-opportunities.md`; re-scored live at IL-T010, 2026-07-11)

| Role | Target | Status as of 2026-07-11 |
|---|---|---|
| Primary | **llm-d/llm-d-router** (EPP's new home — formerly targeted as GAIE) | Migration **confirmed live**: GAIE's README states EPP/`InferenceObjective`/Body-Based Router migrated to the llm-d org, concretely to `llm-d/llm-d-router`. User approved llm-d-router as primary 2026-07-11. See `oss/scoring-refresh.md`. |
| Secondary surface | Gateway API Inference Extension (GAIE), kubernetes-sigs | Kept for conformance/docs items; its newcomer issue pool was effectively empty (0 open `good first issue`) as of 2026-07-11. |
| Secondary track | OpenTelemetry GenAI semantic conventions | **Re-pointed** to `open-telemetry/semantic-conventions-genai` — `gen_ai.*` moved out of the core `semantic-conventions` repo at v1.42.0 (2026-06-12); new repo is pre-1.0 (Development, no releases, 123 open issues). |
| Fallback | vLLM | docs/metrics/tests scope only; unchanged. |

Live re-scoring at IL-T010 is recorded in `oss/scoring-refresh.md` (maintainer responsiveness
and issue availability were expectations at planning time; both are now live-verified, and the
issue-shortlist volatility observed even *within* IL-T010's own execution window is documented
there in §9).

## Entry format

```markdown
### YYYY-MM-DD — <target> — <type: build | reproduction | issue-comment | PR | ping | lesson> [DRAFT?]
- What:            (one line)
- Environment:     (versions/commits — for build & reproduction entries)
- Public link:     (real links only; omit for drafts)
- User review:     (date reviewed pre-post — for submissions)
- Outcome/status:  (acknowledged / silent since <date> / merged / in review / ...)
- Next step:       (incl. contingency clock if silent: ping at +2w, fallback at +4w)
```

## Contingency clocks (from `docs/oss-opportunities.md`)

- Issue silent 2 weeks → one polite ping + start a parallel second item.
- PR silent 4 weeks → shift effort to fallback, leave PR open.
- Both stalled at I8 → documented graceful degradation in this log, never a silent cut.

---

## Entries

### 2026-07-11 — llm-d/llm-d-router — lesson (scoring refresh + target decision)
- What:            Live re-verification of `docs/oss-opportunities.md` candidate scoring before
  any upstream commitment (IL-T010 requirement). Confirmed the GAIE→llm-d migration has
  happened: GAIE's EPP, `InferenceObjective`, and Body-Based Router have moved to
  `llm-d/llm-d-router`. Full detail, updated 0–3×8 scoring table, and process/CLA notes in
  `oss/scoring-refresh.md`. User reviewed the refresh and approved **llm-d/llm-d-router as
  primary target** on 2026-07-11 (GAIE kept as a secondary surface for conformance/docs; OTel
  GenAI semconv track re-pointed to the new `semantic-conventions-genai` repo, which absorbed
  `gen_ai.*` at v1.42.0/2026-06-12; vLLM fallback unchanged).
- Environment:     n/a (research only; no code built in this entry).
- Public link:     — (read-only research; nothing posted upstream).
- User review:     2026-07-11 — target choice approved (llm-d-router primary; GAIE secondary
  surface; OTel track re-pointed to semantic-conventions-genai).
- Outcome/status:  decision recorded; superseded the planning-time GAIE-primary pre-commitment
  per its own documented contingency ("if EPP work has moved, follow it into llm-d").
- Next step:       proceed to build + reproduction (this same day; see entries below).

### 2026-07-11 — llm-d/llm-d-router — build
- What:            Shallow-cloned `llm-d/llm-d-router` to `/home/user/tools/oss/llm-d-router`
  (outside `inference-lab`, per task rules) and built + tested it from source. `go build ./...`
  succeeds cleanly (exit 0). `go test ./...`: **116 packages pass** (`ok`); 65 packages have no
  test files; **5 packages fail, all for external-environment reasons, not logic**:
  `test/e2e` (needs a running envoy/EPP stack + kind-style cluster — panics reaching for a
  cluster that doesn't exist), `test/integration/epp` (needs `envtest`'s `etcd`/`kube-apiserver`
  binaries under `/usr/local/kubebuilder/bin`, not installed), `test/coordinator/e2e/coordinator`
  (requires `COORDINATOR_IMAGE` env var + a cluster), `test/sidecar/e2e` (requires a `kubectl`
  binary and a live cluster with a deployed pod), `test/profiling/tokenizerbench` (requires an
  EPP already reachable at `localhost:30080`). The `Makefile`'s `make build`/`make test` targets
  wrap everything in a Docker "builder" image (`Dockerfile.builder`, `FROM golang:1.25.12`) whose
  base image would need a registry pull; bypassed that and used the host Go toolchain directly
  instead — `go.mod` requires `go 1.25.12` and `GOTOOLCHAIN=auto` transparently fetched it via
  `proxy.golang.org` (reachable, per task constraints; no registry blob CDN or GitHub release
  asset needed for a from-source build).
- Environment:     commit `30385f8e17f7400dec99542fc4148988b33c295f` (2026-07-10 17:38:51
  -0700), `main`. Host: go1.24.7 base toolchain, auto-upgraded to go1.25.12 per `go.mod`; Linux
  amd64, 4 cores. Docker 29.3.1 present but not used for the build (see above).
- Public link:     — (local build only; repo is public upstream but nothing was pushed).
- User review:     n/a (build/test only, no upstream interaction).
- Outcome/status:  build clean; unit test suite green; e2e/integration/coordinator/sidecar
  suites correctly require infra this environment doesn't have (documented above) rather than
  failing on logic.
- Next step:       reproduction (below); no further build work needed for IL-T010.

### 2026-07-11 — llm-d-inference-sim — build + router-sim smoke
- What:            Checked whether `llm-d-inference-sim` (the CPU-only vLLM stand-in used to
  exercise the router without a GPU) was worth building for a local smoke test. It was cheap:
  shallow-cloned to `/home/user/tools/oss/llm-d-inference-sim`, `go build ./cmd/llm-d-inference-sim`
  succeeded directly (same `GOTOOLCHAIN=auto` mechanism, no Docker), and it ran standalone —
  served an OpenAI-compatible `/v1/chat/completions` (echo mode) and a vLLM-shaped `/metrics`
  endpoint immediately. Went further and ran a genuine **local router+sim smoke**: the repo
  documents a no-Kubernetes "file discovery" EPP mode
  (`docs/discovery.md#running-epp-with-file-discovery-no-kubernetes`); built the `epp` binary
  from the router repo, pointed a `file-discovery` plugin config at an `endpoints.yaml` listing
  the running sim's `127.0.0.1:18099`, and started `epp` with `--secure-serving=false`. EPP's
  own `/metrics` then showed `inference_pool_ready_pods{name="epp-smoke"} 1` and
  `llm_d_epp_per_endpoint_queue_size{model_server_endpoint="sim-0",name="epp-smoke"} 0` —
  i.e. the router discovered the CPU-only simulator, treated it as one ready pool member, and
  began polling its metrics, with zero Kubernetes, zero GPU, and zero Docker. Did **not** wire
  up Envoy for a full HTTP ext_proc round trip (that needs an Envoy binary/image and is
  materially more setup than "reasonably cheap" for this step) — the EPP↔discovery↔sim
  integration itself is the useful signal and is confirmed working.
- Environment:     `llm-d-inference-sim` commit `1d5ad9678a2fc7fcaece5b9af64b593465e97868`
  (2026-07-06), `main`. `llm-d-router` `epp` binary built at the same commit as the build entry
  above. Sim on `127.0.0.1:18099` (echo mode, dummy tokenizer, `--model my-model`). EPP on
  gRPC `19002`/health `19003`/metrics `19090`, `--pool-name epp-smoke`, file-discovery config at
  a scratch path with `watchFile: true`.
- Public link:     — (local smoke only).
- User review:     n/a.
- Outcome/status:  sim builds and runs standalone; router+sim discovery/health-tracking smoke
  passes (`inference_pool_ready_pods` == 1, per-endpoint metrics keyed by the sim's discovered
  name). Full HTTP ext_proc path through Envoy explicitly out of scope for this smoke (would
  require Envoy setup beyond "reasonably cheap"); noted as a gap, not attempted.
- Next step:       none required for IL-T010; could be extended with an Envoy hop in a later
  task if a fuller end-to-end demo becomes useful for the portfolio artifact.

### 2026-07-11 — llm-d/llm-d-router — reproduction (#1625, fairness_id cardinality subset)
- What:            Before investing in any one candidate issue, re-verified all five
  shortlisted issues (#1798, #1803, #1625, #1693, #1694) live, per the IL-T010 requirement to
  confirm a pick is "still unassigned with no linked PR before investing." **All five had
  already gained an assignee and/or a linked PR** in the hours between scoring and execution
  (same day) — detail and a table in `oss/scoring-refresh.md` §9. Rather than claim a
  nominally-available issue that was stale by the time of checking, reproduced the **residual,
  unaddressed half of #1625**: its own open fix, PR #1909, bounds cardinality for the
  `model_name` label only (verified from the PR's file diff — `pkg/epp/datastore/*.go` +
  new `pkg/epp/metrics/cardinality.go`); it does not touch `fairness_id`, which is still passed
  unbounded, unsanitized, straight from a client-controlled request header
  (`agentidentity` PreAdmitter plugin → `SchedulingRequest.FairnessID` →
  `metrics.RecordRequestCounter` et al.) into `prometheus.CounterVec.WithLabelValues`. Added a
  local-only Go test (`pkg/epp/metrics/cardinality_repro_test.go`, never committed/pushed
  anywhere) that calls the real, unmodified `RecordRequestCounter`/`RecordRequestErrCounter`
  with 5000 distinct client-controlled `fairness_id` values and confirms via
  `prometheus/client_golang/testutil.CollectAndCount` that all 5000 produce permanent, distinct
  Prometheus series on two metric families (`llm_d_epp_request_total`,
  `llm_d_epp_request_err_total`) in 0.06s wall-clock, no cap, no rejection. Full write-up
  (code paths, command, exact output, observed-vs-expected, scope caveats) at
  `oss/reproductions/2026-07-11-llm-d-router-1625-fairness-id-cardinality.md`.
- Environment:     commit `30385f8e17f7400dec99542fc4148988b33c295f` (same as the build entry).
  `go test ./pkg/epp/metrics/... -run TestFairnessIDCardinalityExplosion_Repro1625 -v` on
  go1.25.12 (via `GOTOOLCHAIN=auto`). Full `pkg/epp/metrics` + `pkg/epp/metrics/collectors`
  suites re-run with the repro test present: all pass, no regressions.
- Public link:     — (nothing posted upstream; draft only).
- User review:     draft comment prepared at `oss/drafts/2026-07-11-llm-d-router-1625-comment.md`,
  clearly marked DRAFT / NOT POSTED, pending user review at IL-T011.
- Outcome/status:  reproduction complete and evidence captured locally; **not** "acknowledged"
  (that requires posting + a maintainer response, which is user-gated per
  `docs/oss-opportunities.md` and did not happen in this task). This is the honest IL-T010 end
  state per its stop condition: "reproduction ready for upstream communication, draft prepared."
- Next step:       IL-T011 — user reviews the draft comment, re-verifies #1625/#1909's live
  status immediately before posting (repo turns over on an hours-to-a-day cadence, see
  `oss/scoring-refresh.md` §9), and if approved, posts the comment. Contingency clock (per
  `docs/oss-opportunities.md`) starts from the post date, not from today.
