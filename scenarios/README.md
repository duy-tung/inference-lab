# Scenarios — end-to-end orchestration (owned by inference-lab)

One directory per scenario. Each contains: a README (purpose, components, pinned inputs,
expected outcome, acceptance checklist mirroring the owning milestone's criteria) and — from
IL-T002 onward — compose file(s) or invocation scripts referencing **pinned images/versions
only**.

| Scenario | Path | Milestone | Task | GPU |
|---|---|---|---|---|
| [A](a/README.md) | infergate → mock backend → PostgreSQL → OTel | I2 | IL-T002 | no (never) |
| [B](b/README.md) | infergate → llama.cpp → inferbench | I3 | IL-T003 | no (CPU) |
| [C](c/README.md) | infergate → vLLM → inferbench → observability | I4 | IL-T004 | yes (rented; CPU fallback = recorded deviation) |
| [D](d/README.md) | inferops → infergate → vLLM → observability stack | I5 | IL-T005 | yes (K8s GPU node; owned by inferops) |
| [E](e/README.md) | inferbench → fleetlab → inferops → re-benchmark | I6 | IL-T006 | inherits D (may shrink to mock/llama.cpp scale) |

## Rules for every scenario

1. **Pin first, run second, archive third.** No scenario runs against unpinned artifacts; no
   scenario is claimed without its acceptance checklist executed and evidence archived under
   `evidence/`.
2. Scripts are sequential, idempotent, and split into four separately runnable steps with
   recorded output: **bring-up → smoke → evidence capture → teardown**.
3. Scripts fail loudly (non-zero exit, captured logs) and never mask a component failure. A
   failed run is evidence of a defect in the owning repo: record it, file it upstream
   (in-program), pin-bump when fixed, re-run. Never fix locally.
4. Released artifacts only — no source checkouts, no local patches, no brokers in the
   synchronous inference path.
5. Secrets per `docs/security.md`: env/`.env` (git-ignored), throwaway demo keys, redacted
   logs.
