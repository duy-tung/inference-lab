# Observability — inference-lab

This repo **consumes** observability rather than emitting it. Its job is to verify and archive
that the observability required by the contracts is actually visible in each scenario, using
the canonical names — and to treat any mismatch as an upstream defect, never a local rename.

## Canonical vocabulary the evidence must show (Contract 2)

- **Prometheus metric names** (gateway): `inference_ttft_seconds`, `inference_itl_seconds`,
  `inference_queue_depth`, `inference_sheds_total`, … with the low-cardinality label policy.
- **Gateway span sequence** in traces:
  `recv → queue.wait → upstream.connect → ttft → stream.relay → settle`.
- **OTel GenAI semantic-convention attributes** at the pinned semconv version
  (status "Development" as of 2026-07 — re-verify at use time; the pinned version lives in
  `pins/pins.yaml`).
- **Measurement-point definitions:** TTFT = first upstream body byte at gateway; client-side
  TTFT (inferbench) is a separate named series. Evidence comparing the two must state the
  declared tolerance.

## Per-scenario evidence requirements

| Scenario | Must show in archived evidence |
|---|---|
| A (I2) | gateway metrics scraped with canonical names; full span sequence in the OTel trace export; PostgreSQL usage-write visible; client-vs-gateway TTFT comparison with tolerance statement |
| B (I3) | same gateway vocabulary against llama.cpp; benchmark report #0 metrics traceable to raw events; cancellation observable in gateway metrics/spans |
| C (I4) | engine metrics (vLLM) proving cancellation release (KV usage / running-count drop within bound); gateway-overhead comparison series; full session manifest attached to every export |
| D (I5) | golden dashboards live (exported); traces end-to-end (client → gateway → engine); rolling-update window visible in metrics with zero client-visible errors |
| E (I6) | before/after benchmark metric series; autoscaling signal + thresholds from the recommendation visible in the operated stack |

## Archival forms

- Metrics: raw exports (Prometheus snapshots or query results) alongside dashboard
  screenshots/exports — screenshots alone are not sufficient for headline claims.
- Traces: exported trace files (OTLP/JSON) archived under `evidence/i<N>/raw/`.
- Dashboards: exported JSON + rendered image, with the dashboard bundle version pinned.

## Defect routing (no local renames — ever)

Any metric-name, label, or span mismatch between the contract vocabulary and what a component
emits is a **defect report to infergate/inferops** (or a contract defect to serving-contracts)
with the archived evidence attached. This repo never renames, relabels, or post-processes
telemetry to make evidence match the contract.
