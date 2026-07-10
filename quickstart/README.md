# Quickstart — Scenario A in ≤15 minutes, GPU-free

**Goal:** from `git clone` to a streaming completion through a real gateway — with mock
backend, PostgreSQL usage accounting, and OTel traces — in **≤15 minutes on a GPU-free
machine**. This is hypothesis H1 (`docs/experiments.md`): the number is measured, never
assumed.

> **Status (2026-07-10, IL-T002):** Scenario A is now runnable —
> `scenarios/a/build.sh && cd scenarios/a && docker compose up -d` (this environment builds
> the pinned images locally, deviation D-002; registry-pulled images arrive with remote
> hosting, RQ-4). PostgreSQL usage accounting is **not composed yet** (deviation D-001:
> infergate gains usage writes at IG-T008) — the usage step below stays aspirational until
> then. No timed quickstart runs yet; timing protocol executes before I8.

## Prerequisites

- Docker + Docker Compose (versions recorded at first timed run).
- ~N GB free disk for images (N measured and filled in at IL-T002).
- No GPU. No accounts. No API keys beyond a throwaway demo key generated locally.

## The path (target shape; finalized at IL-T002)

```bash
# 1. Clone
git clone <inference-lab-url> && cd inference-lab

# 2. Bring up Scenario A (pinned released images only)
cd scenarios/a && docker compose up -d

# 3. Wait for readiness (gateway /readyz)
./wait-ready.sh

# 4. Smoke: one streaming chat completion through the gateway (Contract 1)
curl -N http://localhost:<port>/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"mock","messages":[{"role":"user","content":"hello"}],"stream":true}'

# 5. See the evidence for yourself
#    - usage row in PostgreSQL           (./show-usage.sh)
#    - trace with the gateway span chain (recv → queue.wait → upstream.connect →
#                                         ttft → stream.relay → settle)
#    - metrics: inference_ttft_seconds, inference_queue_depth, ...

# 6. Tear down
docker compose down -v
```

Expected result of step 4: an SSE stream of `data: <json-chunk>` events ending in
`data: [DONE]` — the OpenAI-compatible subset defined by Contract 1.

## What you just ran

Scenario A, the correctness spine of the inference-systems portfolio:
`infergate (gateway) → mock backend → PostgreSQL (usage) → OTel (traces/metrics)`, composed
exclusively from released, digest-pinned artifacts recorded in `pins/pins.yaml`. Details and
the full acceptance checklist: `scenarios/a/README.md`.

## Timed dry-run procedure (protocol: `docs/testing.md` §c)

1. Fresh clone into a clean directory; note Docker cache state (cold vs warm).
2. Start the stopwatch at `git clone`; stop at first successful streaming smoke call
   (step 4).
3. Record in `quickstart/timing-log.md`:
   `date | machine (CPU/RAM/OS) | docker cache | duration | pass(≤15m)? | notes`.
4. ≥2 timed runs required before I8. A >15-minute run triggers slowest-step analysis — the
   fix goes into the flow or upstream (image size), never into a relaxed target.

## Timing log

See [`timing-log.md`](timing-log.md). No timed runs yet (nothing runnable until IL-T002).

## Troubleshooting (populated from real timed-run findings — kept honest)

| Symptom | Check | Notes |
|---|---|---|
| *(none recorded yet)* | | first entries expected at IL-T002 dry runs |
