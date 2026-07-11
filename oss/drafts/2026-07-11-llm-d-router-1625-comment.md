# [DRAFT — NOT POSTED] Comment on llm-d/llm-d-router#1625

**Status: DRAFT.** This has not been posted anywhere. It is prepared for user review at
IL-T011 per `docs/oss-opportunities.md` step 5 ("communicate evidence upstream ... user reviews
every submission before posting") and the hard local-only rule for IL-T010. Do not post without
explicit user sign-off, and re-verify #1625's live status (assignee, linked PRs, PR #1909's
merge state) immediately before posting — both can have changed since 2026-07-11 given the
repo's fast issue/PR turnover (see `oss/scoring-refresh.md` §9).

Target: https://github.com/llm-d/llm-d-router/issues/1625

---

## Proposed comment body

Reproduced this locally against `main` @ `30385f8e17f7400dec99542fc4148988b33c295f` and wanted
to share findings that seem useful alongside #1909.

`RecordRequestCounter`/`RecordRequestErrCounter`/`RecordRequestSizes`/`RecordRequestLatencies`/
`RecordNormalizedTimePerOutputToken`/`RecordRequestTTFT` and the flow-control queue/dispatch
histograms all take `fairnessID` straight into `WithLabelValues(...)` with no bounding
(`pkg/epp/metrics/metrics.go:547` onward; `modelLabelsWithFairnessPriority` in
`llm_d_router_metrics.go` puts `fairness_id` on 6+ metric families). `fairnessID` itself comes
from `reqCtx.SchedulingRequest.FairnessID`
(`pkg/epp/handlers/server.go:224-231`, `extractFairnessAndPriority`), which in turn can be
populated straight from a client-supplied header via the in-tree `agent-identity` PreAdmitter
plugin (`x-claude-code-session-id`, `x-session-affinity`, `session-id`/`session_id`, or any
operator-configured additional header) with no closed-set validation.

I wrote a small local test that calls the real `RecordRequestCounter`/`RecordRequestErrCounter`
functions with 5000 distinct, client-controlled `fairness_id` values (simulating a client that
varies its session header per request) and confirmed via
`prometheus/client_golang/prometheus/testutil.CollectAndCount` that all 5000 produce permanent,
distinct series on both `llm_d_epp_request_total` and `llm_d_epp_request_err_total` — no cap, no
"other" bucket, no rejection. Happy to share the test if useful (it's ~30 lines, follows the
same pattern as the existing `metrics_test.go`).

Worth calling out explicitly: #1909 (thank you for that — nice pattern with `boundModel()`)
scopes its fix to `model_name` only (confirmed from the diff: `pkg/epp/datastore/*.go` +
new `pkg/epp/metrics/cardinality.go`). `fairness_id`, and the pod/namespace/port vector
mentioned in the original issue body, are untouched by that PR and remain exploitable on `main`
after it merges. If it's useful, I'd be glad to look at extending the same
bounded-label-with-overflow approach (`boundModel()`/`boundModels()`) to `fairness_id`, gated
similarly (e.g. pin configured/allowlisted fairness classes, cap+"other" for the rest) — but per
the CONTRIBUTING guide I understand new test methodologies/design choices here should be
discussed first, so wanted to post the reproduction and get a read on direction (allowlist vs.
cap-with-overflow vs. something else) before writing code.

---

## Notes for the user's review (not part of the posted text)

- Tone check: this is written to be additive to #1909, not a "gotcha" — the PR author gets
  credit, the gap is framed as a known scope boundary rather than an oversight.
- Offers to contribute the fix but explicitly defers to maintainer direction first, matching the
  llm-d CONTRIBUTING guide's "new features / API changes must be discussed first" norm noted in
  `oss/scoring-refresh.md` §4.
- Before posting: (1) re-check #1625 and #1909 are still open/unmerged; (2) re-check no one else
  has since covered `fairness_id`; (3) decide whether to attach the actual test file as a gist or
  inline diff — not included by default since it currently lives only in the local clone at
  `/home/user/tools/oss/llm-d-router/pkg/epp/metrics/cardinality_repro_test.go` (outside
  `inference-lab`, never pushed).
- DCO note for any follow-on PR: llm-d requires `git commit -s` (DCO, not CLA).
