# OSS Opportunities — inference-lab

Executed via IL-T010–T012; all activity logged in `oss/log.md`. OSS work is externally paced
and **never on the critical path** — it must never block a milestone.

## Minimum completion target (mandatory for I8)

- one acknowledged issue reproduction;
- one PR merged **or under substantive review**;
- one public benchmark or design artifact;
- documented maintainer interaction.

## Targets

- **Primary: Gateway API Inference Extension (GAIE)** — Go; EPP routing/scheduling is exactly
  the infergate boundary; kind-testable without GPU. **Re-verify the llm-d migration first**
  (`InferenceModel`→`InferenceObjective` rename; repo layout reported as of 2026-07 —
  re-verify live at IL-T010): if EPP work has moved, follow it into llm-d (same score
  profile).
- **Secondary (parallel, cheap): OpenTelemetry GenAI semantic conventions** — spec/docs work;
  status "Development" as of 2026-07 ⇒ conventions still moving; the metrics-contract work
  will surface real gaps to feed upstream; no GPU.
- **Fallback: vLLM** — docs/metrics/tests scope only (e.g. metric-documentation drift found
  during gateway adapter work, or a reproducible behavior report with full manifests from GPU
  experiments).

## Progression (gated)

1. Read contribution guide + architecture docs of the primary target.
2. Build and test locally (kind-based for GAIE; record versions).
3. Reproduce an existing open issue (prefer `good-first-issue`/`help-wanted` with a testable
   behavior).
4. Create a minimal reproducer (smallest config/cluster/test that shows it).
5. Communicate evidence upstream (issue comment with reproducer + environment manifest).
6. Submit a small contribution: test, fix, benchmark, validation, Kubernetes example, or
   documentation improvement.
7. Address review promptly; keep scope fixed.
8. Record public evidence + lessons in the OSS log.

**Gates:** step 3 requires user sign-off on target choice; **the user reviews every
submission before posting** (steps 5 and 6).

## Contingency (slow/unresponsive review)

- **2 weeks silence on an issue** → one polite ping + start a second candidate item in
  parallel (never block on one thread).
- **4 weeks silence on a PR** → switch active effort to the fallback target, leave the PR open
  ("under substantive review" may be satisfied by the fallback).
- **Both primary and fallback stall by I8** → documented graceful degradation: the
  acknowledged reproduction + a public benchmark/design artifact (e.g. reproducible
  engine-behavior report, or the "infergate router vs EPP" analysis), with the stall
  documented in the OSS log — a documented contingency, never a silent scope cut.

## Avoid regardless of target

Scheduler rewrites, CUDA kernels, architecture replacements, large unsolicited refactors,
unverified performance claims.

## Review gate & honesty

- The OSS log records **real interactions only**; planned-but-not-sent communications are
  marked as drafts.
- No upstream issues or PRs existed at planning time — all public links are created at
  execution time.
- Candidate scoring is refreshed with live checks at IL-T010 (`oss/scoring-refresh.md`)
  before any commitment: maintainer responsiveness and issue availability were scored as
  expectations at planning time, not verified.
