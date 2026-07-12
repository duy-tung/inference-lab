# Demo script — the headline story, sentence by sentence over real evidence

Walks `docs/charter.md`'s final narrative in order: contracts → gateway streaming +
cancellation → benchmark → capacity loop. Every command below is real and runnable
(GPU-free); Part 1 was re-executed live for this script (transcript:
`portfolio/demo-transcript.md`) — Parts 2-3 point at already-archived, already-executed
evidence rather than re-running a multi-repo, multi-minute campaign inside a demo pass (each
command is nonetheless the real, documented reproduction command, not a fabricated one).
Dry-run discipline: every claim spoken below is checked against a specific evidence path
before it's said (`docs/experiments.md` §3).

## Part 0 — Setup (30s)

```bash
git clone https://github.com/duy-tung/inference-lab && cd inference-lab
scenarios/a/build.sh && cd scenarios/a && docker compose up -d && ./wait-ready.sh
```

**Say:** "Everything from here on is built from pinned source, not a pre-baked demo image —
`pins/pins.yaml` records exactly which commit of each of the five other repos this stack is."

## Part 1 — Contracts + a correct serving gateway (2 min)

**Say:** "This is `serving-contracts` v1.0.0 — versioned OpenAPI + JSON Schema, no runtime
code. Every artifact you're about to see gets validated against it."

```bash
# Contract 1: a streaming completion, real gateway, real mock engine
curl -N http://localhost:18080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"mock-8b","messages":[{"role":"user","content":"hello"}],"stream":true}'
```

**Say:** "SSE frames, terminal `[DONE]`, OpenAI-compatible — that's Contract 1. Now
cancellation: I disconnect mid-stream and check the engine actually stopped, not just that my
socket closed."

```bash
# Cancel a stream client-side, check the engine actually observed the abort (not just the
# socket closing). Which of the 3 points (pre-first-token / mid-stream / near-completion)
# this lands on depends on the timeout raced against the mock's configured TTFT -- the
# recorded transcript (portfolio/demo-transcript.md) landed pre-first-token; say whichever
# `phase` /debug/state actually reports, don't narrate a point that didn't happen.
( curl -N -m 0.3 http://localhost:18080/v1/chat/completions -H 'Content-Type: application/json' \
    -d '{"model":"mock-8b","messages":[{"role":"user","content":"count to one hundred slowly"}],"max_tokens":200,"stream":true}' || true )
curl -s http://localhost:18081/debug/state | python3 -m json.tool
```

**Say:** "`evidence/i2/checklist.md` has the full 3-point version of this against 100
concurrent streams, seeded and measured, not eyeballed: pre-first-token, mid-stream, and
near-completion aborts, each releasing the mock engine in under a millisecond, each conserved
— zero tokens lost, zero double-counted. Against the real llama.cpp engine, the honest version
of this claim is narrower — one composed-stack point, not three, on the pinned model
(`portfolio/limitations.md` §2) — and that caveat is said out loud here, not left for the
audit to find."

```bash
docker compose down -v
```

## Part 2 — Measured, not assumed (2 min)

**Say:** "Two questions: how much does the gateway itself cost, and does admission control
survive overload. Both are measured, and one of them came back a REFUTED result — which
stayed published."

```bash
cat /home/user/inference-lab/reports/benchmark-report-1.md   # gateway overhead + G5 admission
```

**Say (reading the headline table):** "Mock arm: the gateway adds a paired p95 of 2.21
milliseconds — confirmed under the program's own 10ms target. Real-engine arm: inconclusive,
because llama.cpp's own run-to-run noise on this shared host is two to three orders of
magnitude bigger than the bound we're testing — and that's reported as inconclusive, not
rounded up. Admission control at 5x overload: REFUTED on the original ≤20%-degradation target,
twice, in two separate experiments — then the program re-baselined the gate to a criterion
that's still rigorous (100% typed shedding, bounded queue-wait, no starvation) rather than
quietly moving the goalposts or hiding the miss. `reports/benchmark-report-1b.md` has the
re-baseline decision verbatim."

## Part 3 — Measurements into capacity decisions, including where the prediction was wrong (2 min)

**Say:** "This is the central story: fleetlab predicts a capacity change from real benchmark
data, inferops applies it for real, inferbench re-measures, and we publish the delta —
including the part where the prediction needed correcting."

```bash
cat /home/user/inference-lab/evidence/i6/loop-report.md   # predicted vs measured, in full
```

**Say:** "fleetlab fitted 33.159 requests-per-second per replica from real E1/E2 benchmark
data and recommended scaling 1 replica to 6. We actually applied and re-measured 1→2 — this
sandbox has no real Kubernetes scheduler to run 6 replicas as pods, and that's disclosed, not
hidden. At its own fitted rate, the prediction came back within **+1.3%** — genuinely good. At
every higher rate we *did* measure, the number leaned toward a different, unpublished
empirical estimate instead of the published fit — and fleetlab's own G8 holdout report already
flagged that exact corpus as a MISS before this loop ever ran. The 6-replica number itself was
never measured, ever, anywhere — it's an extrapolation, and it's labeled as one everywhere it
appears, including right here."

## Part 4 — Failures, injected and documented (1 min)

```bash
cat /home/user/inference-lab/evidence/i7/campaign-matrix.md | head -30
cat /home/user/inference-lab/postmortems/pm-001.md | head -40
```

**Say:** "12 fault scenarios from Contract 6, 11 matched expected gateway semantics. The 12th
— a slow client — didn't: the write-deadline should have closed an 8-second-stalled stream at
3 seconds and didn't. That's postmortem pm-001, and it's the *lead* postmortem, not buried
under the 11 that passed."

## Part 5 — OSS (30s)

**Say:** "One more sentence in the final narrative: 'I contributed reproducible evidence or a
fix upstream.' Here's the honest state of that one: a real local build and test of
`llm-d-router`, a real local reproduction of an unaddressed gap in issue #1625, and a drafted
issue comment that has **not been posted** — posting is gated on user review, which hasn't
happened yet. `oss/log.md`'s 2026-07-12 note says exactly this, in those words. This is the
one sentence in the narrative that isn't fully closed, and the portfolio says so."

## Close

**Say:** "Every number in this demo traces to a file under `evidence/` or `reports/` with a
commit hash next to it. The reproducibility audit (`evidence/i8/reproducibility-audit.md`)
is the mechanical version of this same check, run against every headline claim in the
portfolio — anything that didn't survive it was removed before this release, not after."
