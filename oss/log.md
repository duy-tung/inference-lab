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
| 1 | One acknowledged issue reproduction | not started | — |
| 2 | One PR merged or under substantive review | not started | — |
| 3 | One public benchmark or design artifact | not started | — |
| 4 | Documented maintainer interaction | not started | — |

## Targets (selection: `docs/oss-opportunities.md`; re-scored live at IL-T010)

| Role | Target | Pre-commitment check |
|---|---|---|
| Primary | Gateway API Inference Extension (GAIE) | **re-verify the llm-d migration first** (`InferenceModel`→`InferenceObjective` rename; as of 2026-07); if EPP work has moved, follow it into llm-d |
| Secondary | OpenTelemetry GenAI semantic conventions | status "Development" as of 2026-07 — re-verify; feed real gaps from the metrics-contract work |
| Fallback | vLLM | docs/metrics/tests scope only |

Live re-scoring at IL-T010 goes to `oss/scoring-refresh.md` (created then; maintainer
responsiveness and issue availability were expectations at planning time, not verified).

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

*(none yet — the log starts with IL-T010, gated on program wave ≥3 equivalent and user
sign-off on target choice)*
