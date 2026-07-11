# Reproduction — llm-d/llm-d-router #1625 (fairness_id cardinality subset)

- **Upstream issue:** https://github.com/llm-d/llm-d-router/issues/1625 —
  "[Observability] epp/metrics: unbounded label cardinality from user-controlled inputs
  (metrics cardinality DoS)"
- **Status of this note:** local reproduction only. **Nothing was posted upstream.** The
  draft comment for user review is at `oss/drafts/2026-07-11-llm-d-router-1625-comment.md`.
- **Why this issue, and why this scope:** see `oss/scoring-refresh.md` §9. All five shortlisted
  candidates (#1798, #1803, #1625, #1693, #1694) had gained an assignee and/or a linked PR by
  the time of live re-verification at execution (same day as scoring). Of those, #1625 is the
  strongest portfolio fit (directly the metrics-contract / SC-T005 territory) and its open fix,
  PR #1909, is **scoped to the `model_name` label only** — confirmed from the PR's file diff,
  which touches `pkg/epp/datastore/{datastore,modelrewritestore}.go` and adds
  `pkg/epp/metrics/cardinality.go` (`boundModel()`/`boundModels()`, cap 1000 + "other" overflow),
  with no changes to `fairness_id`, pod, namespace, or port labels. This reproduction targets
  the **residual, unaddressed subset**: `fairness_id`, which flows into Prometheus labels with
  zero bounding, on the current `main` branch.

## Environment

- Repo: `llm-d/llm-d-router`, cloned shallow (depth 50) to `/home/user/tools/oss/llm-d-router`
  (outside `inference-lab`, per task instructions).
- Commit: `30385f8e17f7400dec99542fc4148988b33c295f` (2026-07-10 17:38:51 -0700), `main`.
- Go toolchain: host had go1.24.7; `go.mod` requires `go 1.25.12`; `GOTOOLCHAIN=auto` transparently
  downloaded and used `go1.25.12` via `proxy.golang.org` (reachable; registry blob CDNs and
  GitHub release assets are not needed for a from-source Go build).
- No Kubernetes cluster, no Docker-based builder image, no GPU used for this reproduction — it
  is a plain `go test` against the `pkg/epp/metrics` package.

## The code path (read, not modified upstream)

- `pkg/epp/metrics/metrics.go:547` — `RecordRequestCounter(modelName, targetModelName,
  fairnessID string, priority int)` calls
  `llmdRequestCounter.WithLabelValues(modelName, targetModelName, fairnessID, prioStr).Inc()`
  with **no validation, bounding, or sanitization** of `fairnessID`. The same pattern repeats in
  `RecordRequestErrCounter`, `RecordRequestSizes`, `RecordRequestLatencies`,
  `RecordNormalizedTimePerOutputToken`, `RecordRequestTTFT`, and the flow-control queue/dispatch
  histograms (`pkg/epp/metrics/llm_d_router_metrics.go` — `modelLabelsWithFairnessPriority`
  includes `fairness_id` on 6+ metric families).
- `pkg/epp/handlers/server.go:224-231` (`extractFairnessAndPriority`) —
  `fairnessID := reqCtx.SchedulingRequest.FairnessID` if non-empty, else the constant
  `metadata.DefaultFairnessID` ("default-flow"). Called at `server.go:458` immediately before
  `metrics.RecordRequestCounter`.
- `pkg/epp/framework/plugins/requestcontrol/preadmitter/agentidentity/agent_identity.go` — the
  in-tree `agent-identity` PreAdmitter plugin resolves `FairnessID` **directly from a
  client-supplied request header** (`x-claude-code-session-id`, `x-session-affinity`,
  `session-id`/`session_id`, plus any operator-configured `AdditionalSessionHeaders`), with no
  closed-set validation before the value reaches `WithLabelValues`.
- Net effect: any client that varies one of those headers per request (a fresh UUID, a random
  token) causes the EPP to mint and permanently retain a new Prometheus time series per value,
  across at least 6 metric families. Prometheus itself never evicts label combinations, so
  memory grows without bound — the DoS vector the issue describes.

## Reproduction

A test file was added to the local clone only (not committed to any repo, not pushed anywhere):
`pkg/epp/metrics/cardinality_repro_test.go` (package `metrics`, so it can call the unexported
`llmdRequestCounter`/`llmdRequestErrCounter` vars directly, following the existing pattern in
`pkg/epp/metrics/metrics_test.go`, which already uses
`github.com/prometheus/client_golang/prometheus/testutil`).

The test calls the real, unmodified production functions `RecordRequestCounter` and
`RecordRequestErrCounter` — the exact call path reached from `handlers/server.go:458` — with
5000 distinct, client-controlled `fairness_id` values simulating 5000 requests from a client
that varies its session header per request, then asserts (via `promtestutil.CollectAndCount`)
how many distinct Prometheus series exist afterward.

Command:

```
cd /home/user/tools/oss/llm-d-router
go test ./pkg/epp/metrics/... -run TestFairnessIDCardinalityExplosion_Repro1625 -v
```

Output (full log captured; excerpt below):

```
=== RUN   TestFairnessIDCardinalityExplosion_Repro1625
    cardinality_repro_test.go:80: REPRODUCED #1625: 5000 requests with 5000 distinct
    client-controlled fairness_id values produced 5000 permanent series on
    llm_d_epp_request_total and 5000 permanent series on llm_d_epp_request_err_total --
    no bound, no allowlist, no overflow bucket (contrast with cardinality.go's boundModel(),
    which caps model_name at 1000 + 'other').
--- PASS: TestFairnessIDCardinalityExplosion_Repro1625 (0.06s)
PASS
ok  	github.com/llm-d/llm-d-router/pkg/epp/metrics	0.098s
```

The full package test suite (`go test ./pkg/epp/metrics/... -v`) still passes with the repro
test added — no regression, no interference with existing tests (108 other subtests pass;
`0.159s` for `pkg/epp/metrics`, `1.118s` for `pkg/epp/metrics/collectors`).

## Observed vs. expected

- **Observed (current `main`, commit `30385f8e17f7400dec99542fc4148988b33c295f`):** 5000
  distinct, single-use `fairness_id` values produce 5000 permanent Prometheus time series on
  `llm_d_epp_request_total` alone, and another 5000 on `llm_d_epp_request_err_total`, in 60ms of
  wall-clock CPU time locally — with zero API errors, zero rejections, and no warning logged.
  Growth is linear and unbounded in the number of distinct values a client chooses to send; the
  only "cap" is memory. This reproduces the issue's core claim exactly, and additionally shows
  it is not an isolated metric: the same `fairness_id` label appears on 6+ metric families
  (confirmed by `grep` over `pkg/epp/metrics/*.go`), so the blast radius of one unbounded label
  is larger than a single counter.
- **Expected (per the issue, and consistent with the precedent PR #1909 already set for
  `model_name`):** `fairness_id` cardinality from user/header-controlled input should be bounded
  — e.g. capped with an "other" overflow bucket the way `boundModel()` now does for
  `model_name`, or restricted to an operator-configured allowlist of fairness classes. PR #1909
  does not do this; it explicitly scopes to `model_name` (confirmed from its file diff: it
  touches `pkg/epp/datastore/datastore.go`, `pkg/epp/datastore/modelrewritestore.go`, and adds
  `pkg/epp/metrics/cardinality.go`/`cardinality_test.go` — nothing under
  `pkg/epp/handlers/server.go` or the `agentidentity` plugin).

## What this reproduction does and does not establish

- It establishes, with real production code and a passing/failing assertion, that the
  `fairness_id` vector is real, present on `main` today, and untouched by the in-flight fix for
  the sibling `model_name` vector.
- It does **not** attempt to demonstrate actual process memory exhaustion (that would need a
  much larger N and a running EPP process instrumented for RSS, which is a heavier
  reproduction than "CPU-only, minutes" — left for IL-T011 if the user wants a stronger
  reproducer before communicating upstream) — the local test instead uses the standard,
  reviewer-legible signal (`CollectAndCount` on the actual `CounterVec`), which is the same
  technique the repo's own `cardinality_test.go` (in PR #1909) uses to prove the bound works in
  the other direction.
- It does not include a fix or PR — per the hard rule for this task, nothing was posted
  upstream and no code changes were made to the actual llm-d-router working tree beyond the
  local-only, never-pushed test file.

## Build + test context this reproduction sits inside

Full build/test results for the llm-d-router repo at the same commit are recorded in
`oss/log.md` under the 2026-07-11 build entry. Summary: `go build ./...` succeeds cleanly;
116 of 121 testable packages pass (`go test ./...`); the 5 packages that fail
(`test/e2e`, `test/integration/epp`, `test/coordinator/e2e/coordinator`, `test/sidecar/e2e`,
`test/profiling/tokenizerbench`) fail for environment reasons only (no kind/K8s cluster, no
`kubectl` binary, no `envtest`/`etcd` control-plane binaries, unset `COORDINATOR_IMAGE`, no
reachable EPP endpoint) — not logic failures. The `pkg/epp/metrics` package itself, where this
reproduction lives, is fully green.
