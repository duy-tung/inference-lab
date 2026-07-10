# Scenario A — Local request path (correctness spine, GPU-free)

```text
inferbench → infergate → mock backend → OTel (traces/metrics)
                                └─ PostgreSQL (usage) — ABSENT in v1, deviation D-001 (see below)
```

- **Owning milestone:** I2 (owner: inference-lab). Task: IL-T002.
- **Status:** executed (2026-07-10) — I2 evidence recorded under `evidence/i2/`;
  **acceptance review pending**, with the PostgreSQL usage-write criterion recorded as a
  documented deviation (below).
- **Special role:** Scenario A is the **quickstart scenario** (`quickstart/`) and part of the
  never-cut core. It must run on a GPU-free machine, always.

## Purpose

Prove the correctness spine of the platform end-to-end with zero inference cost: streaming
correctness under concurrency, cancellation propagation, usage accounting to PostgreSQL, and
contract-conformant observability — all against the mock backend, so every behavior is
deterministic and assertable.

## Components (pinned in `pins/pins.yaml`; digests in `evidence/i2/pins-snapshot.yaml`)

| Component | Artifact | Pin entry |
|---|---|---|
| Gateway | infergate@5d69aeb, local image `scenario-a/gateway:5d69aeb` | `infergate-image` |
| Backend | infergate mock-backend@5d69aeb, local image | `infergate-mock-image` |
| Load/measurement | inferbench@caa5074 binary (host-side) | `inferbench-binary` |
| Usage store | PostgreSQL — **not composed in v1** (deviation D-001) | *(none yet)* |
| Telemetry | OTel Collector v0.156.0 (ocb build, deviation D-003) | `otel-collector-image` |
| Contracts | serving-contracts 8d81492 (v0.2.0 tag pending) | `contracts-bundle-prerelease` |

## Documented deviation — PostgreSQL usage write (D-001)

infergate@5d69aeb has **no tenancy/usage accounting yet** — IG-T007/IG-T008 are Wave-3
tasks. Scenario A v1 therefore composes **without PostgreSQL**, and the I2 acceptance item
"PostgreSQL usage write observed and consistent with raw events" is recorded as
**DEVIATION, not claimable** in `evidence/i2/checklist.md`. The scenario **re-runs with
PostgreSQL** (and the usage criterion is executed for real) once IG-T008 lands and a new
infergate release is pinned. Nothing here fakes a usage store.

## How to run

```bash
scenarios/a/build.sh   # pinned read-only builds (git archive) → images + .build/
scenarios/a/run.sh <out-dir>   # bring-up, smoke, 5 acceptance runs, checks, teardown
```

`build.sh` consumes sibling repos **only** via `git archive <pinned commit>` (never a
working tree) and records toolchain, binary sha256s, and image digests in
`.build/build-info.txt`. Because this environment's egress proxy denies all container
registry blob CDNs, binaries are host-compiled into `FROM scratch` images (deviation D-002)
and the OTel Collector is built from pinned released modules with the official builder
(D-003) — see `docs/implementation-notes.md`.

`run.sh` executes the I2 items: (a) seeded canonical `chat-short` (from the inferbench
suite, extracted at build time), (b) `concurrency-100` (≥100 concurrent streams,
zero-frame-mixing verification), (c) 3-point cancellation
(`cancel-pre-first-token` / `cancel-mid-stream` / `cancel-near-completion`, derived from the
inferbench IB-T004 profiles with mutations recorded in each file), (d) client-vs-gateway
TTFT agreement from the `/metrics` scrape delta, (e) OTel trace capture via the collector's
file exporter. `checks.py` computes every acceptance number from the raw artifacts; the kit
(`serving-contracts@8d81492`) validates events/manifests/workloads/SSE transcript.

## Expected outcome

A seeded `chat-short` workload completes against the composed stack: all streams
contract-clean, cancellations released at the mock within the declared 100 ms bound,
and traces/metrics visible under the canonical Contract-2 names. (Usage rows in PostgreSQL:
deferred per D-001.)

## Acceptance checklist (mirrors I2 — executed copy: `evidence/i2/checklist.md`)

- [ ] All components brought up from pinned released images/versions only (digests logged);
      pins validator green on the pins used.
- [ ] Seeded workload run: `chat-short`, seed recorded, workload version recorded.
- [ ] 100 concurrent streams completed with **zero frame mixing** (SSE framing per
      Contract 1: `data:` chunks, terminal `data: [DONE]`, no cross-request interleaving).
- [ ] **3-point cancellation verified**: cancel before first token, mid-stream, and near
      completion; mock abort observed within the declared bound each time.
- [ ] Raw-event JSONL **schema-valid** against the pinned contracts bundle.
- [ ] **Client-vs-gateway TTFT agreement** within the declared tolerance; the
      measurement-tolerance statement (both measurement-point definitions + tolerance value)
      archived with the evidence.
- [ ] PostgreSQL **usage write** observed and consistent with raw events (tokens emitted
      before cancel are billable). *(D-001: deviation in v1 — re-run when IG-T008 lands.)*
- [ ] Traces show the full gateway span sequence
      `recv → queue.wait → upstream.connect → ttft → stream.relay → settle`; metrics show
      canonical names (`inference_ttft_seconds`, `inference_itl_seconds`,
      `inference_queue_depth`, `inference_sheds_total`).
- [ ] Evidence archived: run logs, raw-event files, trace export, this checklist executed
      item-by-item → `evidence/i2/`.
- [ ] Reviewed (user acceptance) — I2 is claimed only after demonstration + review.

## Failure handling

- Frame mixing or cancellation leak → **stop**; file defect to infergate with evidence;
  re-run after the fixed release is pinned.
- Client/gateway TTFT disagreement → check measurement-point definitions (Contract 2) before
  suspecting code.
- Any component failure → archived as defect evidence; never patched here.
