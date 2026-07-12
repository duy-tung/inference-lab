# Quickstart — Scenario A in ≤15 minutes, GPU-free

**Goal:** from `git clone` to a streaming completion through a real gateway — with mock
backend and OTel traces/metrics — in **≤15 minutes on a GPU-free machine**. This is hypothesis
H1 (`docs/experiments.md`): the number is measured, never assumed. **Timed and passing** —
see [Timing log](#timing-log) below and the full record: [`timing-log.md`](timing-log.md).

> **PostgreSQL usage accounting is not part of this path (deviation D-001, still open).**
> infergate landed usage accounting at `IG-T008` (2026-07-11), but Scenario A's compose stack
> has not been re-pinned/re-composed with PostgreSQL since I2 was accepted with this
> deviation recorded — that is a distinct, tracked re-run trigger
> (`compatibility/matrix.md`), not part of this quickstart's scope. What you get here: a real
> gateway, a real streaming completion, real traces and metrics — no usage-DB row.

## Prerequisites

- Docker Engine 29.x + Docker Compose v2 (`docker compose version`; tested with Compose
  `v5.1.1`, Engine `29.3.1`).
- Go 1.24.x toolchain (`go version`) — this environment cannot pull container images from a
  registry (egress-proxy policy, deviation D-002 — see `docs/implementation-notes.md`), so
  `build.sh` compiles the pinned gateway/mock/inferbench/OTel-Collector binaries from source
  and packs them into `FROM scratch` images. **If your environment has normal registry access,
  skip straight to `docker compose pull` in a real deployment — build-from-source is this
  sandbox's substitute for that, not the general-case path.**
- ~1 GB free disk for the build output (`scenarios/a/.build/`, measured 108 MB) plus normal
  Go module/build caches (a warm cache is ~2.8 GB modules + ~4.6 GB build cache on the machine
  this was timed on — see the timing-log caveat on cache state).
- Local checkouts of the three sibling repos `build.sh` reads from (default paths
  `/home/user/{infergate,inferbench,serving-contracts}`; override with the three positional
  args): all three are public on GitHub
  (`github.com/duy-tung/{infergate,inferbench,serving-contracts}`) — clone them if you don't
  already have them. `build.sh` only ever reads a pinned commit via `git archive`; it never
  builds your working tree.
- No GPU. No accounts. No API keys — the smoke call below needs none (Scenario A's gateway
  runs `-auth-mode` unset/none; auth is exercised by other scenarios, not this one).

## The path

```bash
# 1. Clone (start the stopwatch here)
git clone https://github.com/duy-tung/inference-lab && cd inference-lab

# 2. Build the pinned images (git-archive extraction + compile; see build.sh header for pins)
scenarios/a/build.sh   # optional args: <infergate-repo> <inferbench-repo> <contracts-repo>

# 3. Bring up Scenario A (pinned, locally-built images only)
cd scenarios/a
docker compose up -d

# 4. Wait for readiness (gateway + mock-backend /healthz)
./wait-ready.sh

# 5. Smoke: one streaming chat completion through the gateway (Contract 1)
curl -N http://localhost:18080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"mock-8b","messages":[{"role":"user","content":"hello"}],"stream":true}'
# (stop the stopwatch at the first `data: ` chunk)

# 6. See the evidence for yourself
curl -s http://localhost:18080/metrics | grep '^inference_'   # canonical Contract-2 metric names
cat out/otel/traces.jsonl | tail -1 | python3 -m json.tool | head -40   # gateway span chain

# 7. Tear down
docker compose down -v
```

Expected result of step 5: an SSE stream of `data: <json-chunk>` events ending in
`data: [DONE]` — the OpenAI-compatible subset defined by Contract 1. Expected result of step
6: `inference_ttft_seconds`, `inference_queue_depth`, etc. present in the metrics scrape, and
a trace in `out/otel/traces.jsonl` whose span sequence is
`recv → queue.wait → upstream.connect → ttft → stream.relay → settle` (Contract 2).

## What you just ran

Scenario A, the correctness spine of the inference-systems portfolio:
`infergate (gateway) → mock backend → OTel (traces/metrics)`, composed exclusively from
released/pinned, digest-recorded artifacts (`pins/pins.yaml`). This quickstart is a **light**
smoke path (bring-up → one streaming call → teardown); the **full** I2 acceptance evidence
(100 concurrent streams, 3-point cancellation, TTFT-agreement, schema validation) is a
separate, longer run: `scenarios/a/run.sh <out-dir>` — that is what produced
`evidence/i2/checklist.md`, not this quickstart. Scenario details:
`scenarios/a/README.md`.

## Timed dry-run procedure (protocol: `docs/testing.md` §c)

1. Fresh clone into a clean directory; note Docker cache state (cold vs warm) and Go
   module/build-cache state (this repo cannot claim a fully-cold-cache number is
   representative of every machine — see the caveat in the timing log).
2. Start the stopwatch at `git clone`; stop at the first `data: ` chunk of step 5's streaming
   smoke call.
3. Record in `quickstart/timing-log.md`:
   `date | machine (CPU/RAM/OS) | docker/go cache state | duration | pass(≤15m)? | notes`.
4. ≥2 timed runs required before I8. A >15-minute run triggers slowest-step analysis — the
   fix goes into the flow or upstream (image size), never into a relaxed target.

## Timing log

**2 timed runs recorded, both ≤15 minutes.** Full record: [`timing-log.md`](timing-log.md).

| Run | Date | Cache state | Duration | Pass (≤15m)? |
|---|---|---|---|---|
| 1 | 2026-07-12 | Docker: prior scenario-A images present (rebuilt on top, see notes); Go module/build cache: **warm** | see timing-log.md | see timing-log.md |
| 2 | 2026-07-12 | Docker: images + `.build/` removed, forced full recompile + image rebuild; Go module/build cache: **warm** (not cleared — see honesty note in timing-log.md) | see timing-log.md | see timing-log.md |

## Troubleshooting (populated from real timed-run findings — kept honest)

| Symptom | Check | Notes |
|---|---|---|
| `build.sh` fails at the sibling-repo `git archive` step | the three sibling repos exist locally at the paths passed (default `/home/user/{infergate,inferbench,serving-contracts}`) and contain the pinned commit in their history | `build.sh`'s own header comment lists the exact pins; `git log --oneline <pin>` in the sibling repo should resolve |
| `docker compose up -d` port conflict on `18080`/`18081` | another compose project or container already publishes those host ports | `docker ps --filter publish=18080` / `--filter publish=18081`; stop the conflicting container — Scenario A does not renumber its ports, since the compose file is what `pins/pins.yaml` and `evidence/i2/` were validated against |
| `wait-ready.sh` times out | `docker compose logs gateway mock-backend` | usually a slow `docker build` (cold layer cache) still finishing when the poll starts — the 20s default timeout in `wait-ready.sh` covers a warm-cache run; pass a larger timeout (`./wait-ready.sh 60`) on a colder machine |
| First `build.sh` run is much slower than subsequent ones | Go module downloads (`go.opentelemetry.io/collector/cmd/builder`) and `go build`'s package-compile cache are both cold on a machine's very first build | this is expected and is the single largest source of variance between the two timed runs recorded above — see `timing-log.md` |
