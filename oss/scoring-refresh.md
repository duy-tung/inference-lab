# OSS Scoring Refresh — IL-T010 (2026-07-11)

Live re-verification of `docs/oss-opportunities.md` §1 candidate scoring, performed before any
upstream commitment, per the IL-T010 requirement to re-verify volatile facts live (especially
the GAIE → llm-d migration) before choosing a target. This refresh is read-only research;
no issues, comments, PRs, or reactions were posted anywhere in the course of producing it.

Method note: GitHub API access from the executing session is proxy-scoped to the user's own
repositories, so facts below were gathered from public github.com pages via web fetch rather
than the REST API. Two dates that originally rendered as relative ("last month") were resolved
via surrounding context and are marked `(~)` where residual uncertainty remains.

## 1. The GAIE → llm-d migration question — ANSWERED: it happened

- kubernetes-sigs/gateway-api-inference-extension is active but post-migration: latest `main`
  commit 2026-07-07 (dependabot), latest substantive human commits 2026-06-29/30. Latest release
  v1.5.0 (~2026-04-19); nothing newer. 709 stars, Go 88.6%, self-described GA.
- The GAIE README (checked 2026-07-11) states the Endpoint Picker (EPP), `InferenceObjective`,
  and Body-Based Router have **migrated to llm-d ecosystem repositories**; community meetings
  moved to "llm-d Router".
- The new home is **llm-d/llm-d-router** ("formerly known as the Inference Scheduler"), which
  absorbed the EPP core and the `InferenceObjective`/`InferenceModelRewrite` APIs. Go 96.7%,
  249 stars, latest release v0.9.0 (2026-06-23), 30 releases, Apache-2.0.
- kubernetes-sigs GAIE retains the `InferencePool` API surface, conformance suite, and
  site/docs. Its open-issue pool is small (12 open) and partly migration-cleanup themed.
- The pre-agreed contingency in `docs/oss-opportunities.md` ("if EPP work has moved, follow it
  into llm-d") has triggered.

## 2. Small-issue availability (verified 2026-07-11)

- kubernetes-sigs GAIE: **zero** open `good first issue` items. Remaining candidates are
  docs-shaped; the one attractive conformance issue (#2933, echo→llm-d-inference-sim) is
  assigned to a maintainer.
- llm-d/llm-d-router: 7 open `good first issue`, 12 open `help wanted` at scoring time.
  **Re-verified again at execution time (same day, a few hours later, see §5 below): by
  execution the entire newcomer-labeled pool had turned over to assigned/PR-linked.** This repo
  moves fast — see merge-throughput note below.

## 3. Maintainer responsiveness (llm-d-router, sampled external PRs)

- PR #1902 (docs fix, external contributor anxkhn): opened 2026-07-06, first maintainer
  response ~1 hour same day, merged 2026-07-09.
- PR #1835 (DumpState feature, external contributor thc1006): opened 2026-06-27, first
  maintainer review next day, two review cycles, merged 2026-07-10.
- ~20 PRs merged 2026-07-09..11 alone, majority from external human contributors.
- Read: median time-to-first-maintainer-response on external PRs is hours to ~1 day.

## 4. Contribution process

- kubernetes-sigs GAIE: Kubernetes/CNCF CLA required; standard k8s contributor guide + OWNERS.
- llm-d org: **DCO, not CLA** (`git commit -s`); k8s-convention OWNERS; lazy consensus; new
  features/test methodologies/API changes must be discussed first (issue or SIG channel before
  code); rebase-and-squash. llm-d-router: #sig-router Slack, bi-weekly meetings Wed 10AM PDT.

## 5. OTel GenAI semantic conventions — target repo changed

- At v1.42.0 (2026-06-12) all `gen_ai.*` attributes/metrics/events/spans were deprecated in
  `open-telemetry/semantic-conventions` and moved to a **new repo**,
  `open-telemetry/semantic-conventions-genai`. Core repo latest release v1.43.0 (2026-07-03) has
  no gen-ai content left.
- New repo status (2026-07-11): Development, no releases published yet, 152 stars, 123 open
  issues, 35 open PRs, active commits.
- Impact on the metrics-contract's v1.34.0 pin: `gen_ai.system` was renamed to
  `gen_ai.provider.name` in v1.37.0, chat-message events deprecated in favor of attributes;
  v1.38–v1.41 added streaming/cache-token/agent attributes. Any attribute list pinned at v1.34.0
  must be re-audited against `semantic-conventions-genai` before feeding gaps upstream.
- The secondary OTel track is **re-pointed at `semantic-conventions-genai`**, not the core repo.

## 6. vLLM (light check)

- Latest release v0.24.0 (2026-06-29), current. 85.9k stars, ~2k open issues, ~3.7k open PRs —
  enormous review competition. Fallback-only role (docs/metrics/tests) unchanged.

## 7. Updated scoring (0–3 × 8 columns, per `docs/oss-opportunities.md` rubric)

| Candidate | Go/DS | Portfolio | CPU repro | Maintainer ✓ | Small issues ✓ | Testability | Learning | Hiring | Total | Δ vs plan |
|---|---|---|---|---|---|---|---|---|---|---|
| **llm-d/llm-d-router** (EPP's new home) | 3 | 3 | 3 | **3** (1h–1d first response, sampled) | **3** (7 GFI + 12 HW at scoring time) | 3 | 3 | 2 | **23** | was "llm-d ≈19"; router repo is Go 96.7% and directly the EPP |
| GAIE (kubernetes-sigs, post-migration remainder) | 3 | 2 (EPP gone; API/conformance remain) | 3 | 2 | **1** (0 GFI, ~12 open issues) | 3 | 2 | 2 | **18** | was 21; drops on portfolio fit + issue pool |
| OTel GenAI semconv (**new repo: semantic-conventions-genai**) | 2 | 3 | 3 | 2 (new repo, latency unverified) | **3** (123 open issues, pre-1.0) | 2 | 2 | 2 | **19** | unchanged total; target repo changed |
| vLLM | 1 | 3 | 2 | 3 | 2 | 2 | 3 | 3 | **19** | unchanged |

## 8. Decision (user sign-off 2026-07-11)

- **Primary: llm-d/llm-d-router** (EPP's new home; ~23). Highest score, exactly the
  infergate routing/scheduling boundary, CPU-testable via `llm-d-inference-sim`, DCO not CLA.
- **Secondary surface: GAIE** (kubernetes-sigs) — kept for conformance/docs items; newcomer
  issue pool effectively empty as of 2026-07-11.
- **Secondary track: OpenTelemetry GenAI semantic conventions**, re-pointed at
  `open-telemetry/semantic-conventions-genai` (target repo changed post v1.42.0 split).
- **Fallback: vLLM** — unchanged, docs/metrics/tests scope only.

## 9. Issue shortlist volatility — re-verified again at IL-T010 execution time

The candidate issue shortlist compiled during scoring (#1798, #1803, #1625, #1693, #1694) was
re-checked live again at execution time, several hours later, per the IL-T010 requirement to
"re-verify live that your pick is still unassigned with no linked PR before investing." Result:
**every one of the five had already gained an assignee and/or a linked PR** in the intervening
hours:

| Issue | At scoring time | Re-verified at execution (2026-07-11, same day) |
|---|---|---|
| #1798 DumpState (program-aware-fairness) | unassigned, no PR | open PR **#1839** ("Fixes #1798") |
| #1803 DumpState (pluginName default) | — | assigned **@MOHITPARMAR007**, PR **#1853** |
| #1625 metrics cardinality DoS | unassigned, no PR | open PR **#1909** ("Fixes #1625") — **but scoped to `model_name` only; `fairness_id`/pod/namespace/port untouched (verified from the PR diff)** |
| #1693 Add span for filter | — | assigned **@sudoalok** |
| #1694 Add span for picker | — | assigned **@chinmaychahar** |

A further sweep of the live `good first issue`/`help wanted` label queries turned up the same
pattern on adjacent issues (#1794 → PR #1840; #1782 → assigned @zhouyou9505; #1630 → assigned
@umakantv). This is consistent with the merge-throughput signal in §3 (~20 PRs/3 days) — this
repo's newcomer-labeled backlog turns over on an hours-to-a-day cadence, faster than the
scoring-to-execution gap in a single session.

**Consequence for IL-T010 step 4 (reproduction):** rather than claim a nominally "available"
issue that is stale by the time of writing, the reproduction targets the **residual, unaddressed
half of #1625** — the `fairness_id`/pod-label cardinality vectors that open PR #1909 does not
fix (it bounds only `model_name`, via `pkg/epp/metrics/cardinality.go`). This keeps the
strongest portfolio-alignment candidate (#1625 is directly the metrics-contract/SC-T005
territory) while producing evidence that is additive to, not duplicative of, PR #1909. See
`oss/reproductions/2026-07-11-llm-d-router-1625-fairness-id-cardinality.md`.

---
*All interaction with upstream projects (claiming issues, commenting, PRs) requires user
approval per the log rules; nothing was posted in the course of this refresh or the
reproduction work it fed into.*
