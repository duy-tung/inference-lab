# Aborted Scenario B attempt 1 (2026-07-11 00:44–00:53 UTC) — INVALID, kept as defect evidence

Aborted by the operator ~9 minutes in (during the chat-short-cpu-direct phase). **Nothing
here is usable as I3 evidence.**

## What happened

`run.sh`'s original `start_llama` captured the pid of a wrapper subshell instead of the
`llama-server` pid (`(cd … && nohup llama-server … & echo $!)` — the `&` backgrounds the
whole `&&` list, so `$!` was not the engine). Consequently a `llama-server` started during
pre-run preflight testing was never actually killed, kept port 18082 bound, and the run's
own per-phase engines all **failed to bind** (`logs/llama-server-calib.log` here shows
`couldn't bind HTTP server socket`) while the health checks passed against the stale
process.

## Why that invalidates the attempt

- The stale engine had identical binary + flags, so the traffic itself was well-formed —
  but the "fresh llama-server per phase/arm" premise of the run design was false (prompt
  cache and slot state carried across phases).
- The failover phase would have SIGKILLed a dead wrapper pid, not the engine.

## Fix (in the committed `scenarios/b/run.sh`)

`start_llama` now `exec`s the engine inside the backgrounded subshell so `$!` IS the
llama-server pid, refuses to start when the port already answers (`port_must_be_free`),
verifies its own pid is alive once the port is healthy, and `stop_llama` verifies the port
actually went dark. Attempt 2 ran with these guards.

Partial artifacts (calibration runs, run/gateway/llama logs, contention log) are preserved
under this directory unmodified; failed runs are evidence, never deleted.
