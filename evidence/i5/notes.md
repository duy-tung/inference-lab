# evidence/i5 — notes (Scenario D / IL-T005, assembled 2026-07-12)

## 2026-07-12 — evidence-assembly + light demo session

- **Nature of this session:** primarily evidence assembly from the inferops operational-stack
  work already completed (`inferops` commits `135dd34`..`db30279760dacc3f5af25595551365530f60bdac`),
  plus one light, fresh consumer-side demonstration (§3 of `checklist.md`) run against the
  already-running compose stack. No inferops source was read, patched, or checked out; the
  stack was exercised only as an HTTP/Prometheus/Tempo client, exactly as a real operator would.
- **Why the demo was run at all (not purely citation):** re-reading the cited inferops evidence
  closely showed a real gap — IO-T003's `verify-observability.sh` proved the full
  Prometheus-exemplar-Tempo pipeline only against the mock-backed main `gateway` service (the
  only engine that existed at IO-T003 time); IO-T005's `llamacpp-smoke.sh` (run later) verified
  real inference + cancellation against `gateway-llamacpp` but checked only `/metrics`
  reachability, not Prometheus scrape/exemplar/Tempo resolution. Nobody had checked the
  observability pipeline end-to-end against the *real* engine path. Since I5's own acceptance
  criteria say "golden dashboards live" and "traces end-to-end" without qualifying which
  backend, closing this specific gap seemed like the right amount of new evidence to generate —
  light (7 requests total), not a load test, and not a re-run of anything inferops already
  proved well (rolling-update-under-load, warm-up readiness, etc. are cited, not re-run).
- **Path-existence / digest spot checks performed before writing the checklist:** every
  `inferops/scripts/evidence/*` directory cited in `checklist.md` was `ls`-confirmed to exist;
  every digest cited was cross-checked against either `inferops/compose/*.yml` (`grep image:`)
  or a live `docker inspect` against the actually-running containers (not just the compose
  file text) — see `checklist.md` §5 and `raw/demo-20260712T005146Z/transcript.log` lines 1-10.
- **Model file digest re-verification:** `sha256sum /home/user/tools/models/qwen2.5-1.5b-instruct-q4_k_m.gguf`
  computed live this session = `6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e`,
  matching the `model-gguf` pin exactly — this is the same host file mounted into both this
  repo's own Scenario B llama-server process (I3/I4) and inferops's `inferops-llama-cpp`
  container; no separate model download happened for I5.
- **Stack state at assembly time:** `docker ps` showed 14 running containers (`inferops-*` plus
  one leftover `crazy_elbakyan` container from an earlier ad hoc test and `infergate-pg`, an
  unrelated container from a different repo's own work) — the stack was live and already
  serving traffic from prior IO-T00x sessions before this task's own demo added 7 more
  requests. This is a shared host; no attempt was made to reset or restart any service.
