# Scenario A — Local request path (correctness spine, GPU-free)

```text
inferbench → infergate → mock backend → PostgreSQL (usage) → OTel (traces/metrics)
```

- **Owning milestone:** I2 (owner: inference-lab). Task: IL-T002.
- **Status:** defined (2026-07-10). Compose file + run scripts arrive with IL-T002; inputs
  are unpinned until then.
- **Special role:** Scenario A is the **quickstart scenario** (`quickstart/`) and part of the
  never-cut core. It must run on a GPU-free machine, always.

## Purpose

Prove the correctness spine of the platform end-to-end with zero inference cost: streaming
correctness under concurrency, cancellation propagation, usage accounting to PostgreSQL, and
contract-conformant observability — all against the mock backend, so every behavior is
deterministic and assertable.

## Components (all released artifacts, pinned in `pins/pins.yaml`)

| Component | Artifact | Pin entry (expected id) |
|---|---|---|
| Gateway | infergate container image (digest-pinned) | `infergate-image` |
| Backend | infergate mock-backend image (digest-pinned) | `infergate-mock-image` |
| Load/measurement | inferbench released binary | `inferbench-binary` |
| Usage store | PostgreSQL (upstream image, digest-pinned) | `postgres-image` |
| Telemetry | OTel Collector (+ local trace/metrics sink), digest-pinned | `otel-collector-image` |
| Contracts | serving-contracts bundle v0.1.x | `contracts-bundle` |

**Pinned inputs: currently none — everything unpinned as of 2026-07-10.** This scenario
cannot be claimed until the pins exist and the validator is green.

## Expected outcome

A seeded `chat-short` workload completes against the composed stack: all streams
contract-clean, cancellations released at the mock within bound, usage rows in PostgreSQL
consistent with raw events, and traces/metrics visible under the canonical Contract-2 names.

## Indicative invocation (executed at IL-T002, not before)

```bash
docker compose up          # in scenarios/a
inferbench run --workload chat-short --seed 42 --target http://infergate:<port>
```

## Acceptance checklist (mirrors I2 — executed copy goes to `evidence/i2/checklist.md`)

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
      before cancel are billable).
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
