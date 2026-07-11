# Benchmark report — i3-chat-short-cpu-gw

| | |
|---|---|
| result_id | `i3-chat-short-cpu-gw` |
| result created_at | 2026-07-11T06:28:20Z |
| report generated_at | 2026-07-11T06:28:20Z |
| contracts bundle pin | 8d81492 (v0.2.0 tag pending) |
| generator | inferbench-analysis 0.2.0 (IB-T006 honest-report machine) |
| repetitions pooled | 1 |

**Source of the numbers:** in-memory analysis of the linked raw events (same pipeline that emits the benchmark-result file; bootstrap CIs and cross-run dispersion shown here cannot ride in the result file at the pinned contracts version)

## Hypothesis under test

Every run manifest declares the hypothesis it was executed for; a report is only interpretable against it (experiments.md rule 6).

> **i3-chat-short-cpu-gw:** Gateway-overhead shakedown, VIA-GATEWAY arm: routing the identical seeded chat-short-cpu schedule (v1.0.0, seed 1003001) through infergate adds less than 100 ms to pooled client-measured TTFT p50 relative to the engine-direct arm (fresh llama-server per arm, same host, single run per arm). The bound is deliberately coarse: infergate's I2-measured internal TTFT contribution was ~2 ms, but on this 4-core host client, gateway, and engine share cores, so the bound mostly absorbs CPU-contention noise; this run pair cannot resolve a <10 ms overhead claim and does not make one.

## Interpretation rules — what may and may not be concluded

These rules are embedded by the report generator and cannot be omitted; a reading of this report that violates them misquotes it.

1. **Comparability (verbatim, serving-contracts compatibility/compatibility-policy.md §7, pin 8d81492 (v0.2.0 tag pending)):** results are comparable only when model revision, quantization, tokenizer, engine version+flags, hardware, driver/CUDA, workload version+seed, and warm-up policy all match, **or** the difference is the single declared experimental variable. No cross-hardware or cross-tool comparison may be drawn from this report.
2. **Pooled percentiles:** every percentile below is computed on the pooled raw per-request events across all 1 repetition(s) of this run set (method `pooled-raw-events`). Percentiles are NEVER averaged across runs; cross-run dispersion, where shown, is median ± range of per-run summaries and is not a percentile table.
3. **Arrival process:** latency and goodput claims are valid only under open-loop arrivals; closed-loop contributions are flagged here and support throughput-ceiling statements only (closed-loop hides queueing delay — coordinated omission).
4. **Saturation:** no extrapolation past the saturation knee; when the knee estimate below is null, NO saturation or capacity claim may be made from this report.
5. **Goodput:** only meaningful next to its SLO reference, shed rate, and stall rate — they are printed adjacent below; quoting the goodput ratio without them misrepresents this report (a system can inflate goodput by shedding early or stalling mid-stream).
6. **Measurement points:** all latency series are CLIENT-side series measured from the scheduled send time (coordinated-omission-safe basis; contracts metrics mirror rule). Client TTFT is a different series from gateway TTFT — never conflate them.
7. **No mean-only reading:** means appear only beside full percentile columns; the mean of a latency distribution is not a summary of it.
8. **Provenance:** numbers in this report are measured (from the linked raw events) unless explicitly labeled otherwise; every external number carries basis + date where cited.

## Run manifest(s) — full, embedded

The complete manifest of every pooled run (pins, flags, topology, hardware, warm-up policy, hypothesis). A result without its manifest is not publishable.

### i3-chat-short-cpu-gw

- manifest: `evidence/i3/raw/runs/chat-short-cpu-gw/manifest.json`
- workload file: `evidence/i3/raw/runs/chat-short-cpu-gw/workload.json`
- arrival process: open-loop Poisson, rate 0.08 req/s; workload_ref = chat-short-cpu@1.0.0 seed 1003001
- target topology: `via-gateway`

```json
{
  "run_id": "i3-chat-short-cpu-gw",
  "target_topology": "via-gateway",
  "workload_ref": {
    "name": "chat-short-cpu",
    "version": "1.0.0",
    "seed": 1003001
  },
  "engine": {
    "name": "llamacpp",
    "version": "1 (8f114a9)",
    "commit": "8f114a9b573b69035299f9b924047f53c1e22c7e",
    "flags": {
      "alias": "qwen2.5-1.5b-instruct-q4_k_m",
      "ctx_size": 8192,
      "defaults_note": "all remaining llama-server options at 8f114a9 build defaults (fresh process for this arm)",
      "host": "127.0.0.1",
      "log_timestamps": true,
      "metrics": true,
      "model": "/home/user/tools/models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
      "parallel": 2,
      "port": 18082,
      "slots": true,
      "threads": 4,
      "webui": false
    }
  },
  "model": {
    "checkpoint": "qwen2.5-1.5b-instruct-q4_k_m.gguf (Qwen2.5-1.5B-Instruct, GGUF Q4_K_M)",
    "revision": "sha256:6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e",
    "tokenizer": "gguf-embedded (Qwen2 BPE as packaged in the checkpoint; identity covered by the model-file sha256 above)"
  },
  "hardware": {
    "gpu_model": null,
    "gpu_count": 0,
    "vram_gb": null,
    "driver_version": null,
    "cuda_version": null,
    "instance_type": "local-dev-host (linux/amd64, 4 CPU cores, 15 GiB RAM; llama-server -t 4, infergate, and inferbench co-located on the same cores)"
  },
  "gateway": {
    "version": "74f2372 (infergate@74f2372acea62645fa3c1d91689574ea9de7c589, host binary built read-only via git archive; binary sha256 in evidence/i3/logs/build-info.txt)",
    "config_version": "v1-24d2072b (scenarios/b/config/gateway-llamacpp.json: llamacpp backend, no fallback, upstream_timeout 300s, stream_write_timeout 30s)"
  },
  "client": {
    "location": "same host (inferbench on host -> infergate 127.0.0.1:18080 -> llama-server 127.0.0.1:18082, loopback; client shares the 4 CPU cores with the engine)",
    "rtt_ms": 0.941009
  },
  "warm_up": {
    "policy": "discard-requests",
    "value": 4
  },
  "repetitions": 1,
  "hypothesis": "Gateway-overhead shakedown, VIA-GATEWAY arm: routing the identical seeded chat-short-cpu schedule (v1.0.0, seed 1003001) through infergate adds less than 100 ms to pooled client-measured TTFT p50 relative to the engine-direct arm (fresh llama-server per arm, same host, single run per arm). The bound is deliberately coarse: infergate's I2-measured internal TTFT contribution was ~2 ms, but on this 4-core host client, gateway, and engine share cores, so the bound mostly absorbs CPU-contention noise; this run pair cannot resolve a <10 ms overhead claim and does not make one.",
  "started_at": "2026-07-11T01:08:54Z",
  "contracts_bundle_version": "8d81492 (v0.2.0 tag pending)",
  "notes": "I3 / Scenario B primary arm: BENCHMARK REPORT #0 (methodology shakedown, not a performance claim). Single repetition, ~48 requests, CPU-adapted 0.08 rps."
}
```

## Results

### Throughput (measured window)

| metric | value |
|---|---|
| ok-requests / second | 0.0711 |
| output tokens / second | 6.73 |
| total requests (all statuses) | 36 |
| total output tokens | 3409 |
| measured window | 506.366 s |
| pooled events (post warm-up) | 36 |

### Latency — pooled percentiles

Method: `pooled-raw-events` — percentiles computed on the pooled raw per-request samples across repetitions (never averaged across runs). Seconds.

| signal | n | p50 | p90 | p95 | p99 | p999 | max | mean |
|---|---|---|---|---|---|---|---|---|
| `ttft_seconds` | 36 | 2.313273 | 4.700656 | 11.380367 | 15.793155 | — | 16.610011 | 3.397250 |
| `e2e_duration_seconds` | 36 | 9.346352 | 17.024418 | 24.252327 | 26.317331 | — | 26.852271 | 10.809743 |
| `itl_seconds` | 3354 | 0.072853 | 0.084833 | 0.087206 | 0.095284 | 2.880588 | 3.141737 | 0.079190 |
| `max_stall_seconds` | 36 | 0.091827 | 2.817248 | 2.941625 | 3.096957 | — | 3.141737 | 0.925282 |

(p999 is only resolved at n ≥ 1000 pooled samples; '—' means the pool cannot support it. The mean column is context for the percentiles, never a substitute.)

**Bootstrap 95% confidence intervals** — nonparametric percentile bootstrap on the pooled samples (B=1000 resamples, 95% interval, seeded — ADR-0002); CIs are report-surface only, the pinned result schema carries no CI fields:

| signal | percentile | 95% CI (seconds) |
|---|---|---|
| `ttft_seconds` | p50 | [2.056082, 2.912373] |
| `ttft_seconds` | p90 | [3.337366, 14.276136] |
| `ttft_seconds` | p95 | [3.916692, 16.610011] |
| `ttft_seconds` | p99 | [4.772491, 16.610011] |
| `e2e_duration_seconds` | p50 | [8.476845, 11.318252] |
| `e2e_duration_seconds` | p90 | [11.941940, 25.323872] |
| `e2e_duration_seconds` | p95 | [12.579017, 26.852271] |
| `e2e_duration_seconds` | p99 | [17.738798, 26.852271] |
| `itl_seconds` | p50 | [0.063276, 0.076154] |
| `itl_seconds` | p90 | [0.084529, 0.085181] |
| `itl_seconds` | p95 | [0.086710, 0.087835] |
| `itl_seconds` | p99 | [0.092485, 0.100712] |
| `itl_seconds` | p999 | [2.363036, 3.013794] |
| `max_stall_seconds` | p50 | [0.075106, 1.080644] |
| `max_stall_seconds` | p90 | [2.183556, 3.013794] |
| `max_stall_seconds` | p95 | [2.705037, 3.141737] |
| `max_stall_seconds` | p99 | [2.832908, 3.141737] |

### Goodput @ SLO `scenario-b-llamacpp-cpu-shakedown@1.0.0` — with shed and stall rates adjacent

Shed and stall rates are part of the goodput figure, not footnotes: goodput can be gamed by shedding early, and a stream can meet its TTFT target and still stall mid-generation. All three are computed in one pass over the same measured window.

| goodput block | value |
|---|---|
| goodput ratio (meeting / ALL offered, incl. shed+canceled+errored) | 1.0000 (36/36 offered) |
| requests/second meeting SLO | 0.0711 |
| **shed rate (adjacent by rule)** | 0.0000 |
| **stall rate (adjacent by rule)** | 0.0000 (0/36 streaming requests) at stall threshold 30s |

### Saturation knee

`knee_estimate: null` — no rate sweep contributed to this run set, so no saturation point was measured and **no capacity or saturation claim may be made from this report** (interpretation rule 4; also listed under threats to validity).

### Cost

`cost: null` — **why:** no cost profile applies to this run set — cost is null (cost figures are only computed from a declared, provenanced cost-profile file, never from assumed rates)

## Validity block (mandatory)

- **Warm-up handling:** manifest warm-up policy 'discard-requests' (4 requests per repetition, ordered by scheduled_send_ts): 4 events excluded, 36 kept (i3-chat-short-cpu-gw/rep1: 4 excluded)
- **Run count / pooling statement:** 1 repetition(s) pooled; all percentile tables above are computed on the pooled raw events of these repetitions (never on averaged per-run percentiles).
- **Declared error/shed gate:** latency percentiles are withheld above error+shed rate 0.05; this run set measured error rate 0.0000 + shed rate 0.0000.
- **Closed-loop flag:** no contributing workload declares closed-loop arrival.

### Threats to validity (mandatory)

- single-host client+server co-location: llama-server (-t 4), infergate, and inferbench share one 4-core host; measured interval-CPU during this run: gateway mean 0.2% / max 1.0% of one core, inferbench mean 0.1% / max 0.6% of one core, llama-server mean 178.6% / max 397.6% of one core. Client-side timing competes with the engine for CPU.
- single repetition, small sample (CPU-adapted rate): bootstrap CIs are wide and cross-run dispersion does not exist; numbers are a methodology shakedown, not a performance claim
- arrival rate CPU-adapted from same-day single-stream calibration (evidence/i3/logs/rate-calibration.log); results characterize this host + engine build + quantized model only
- SLO thresholds derived from same-host calibration probe maxima (x1.5 headroom, seeds distinct from the measured runs): goodput@SLO exercises the machinery, it is not an external target
- paired arm ran minutes apart against its own fresh llama-server process (OS page cache warm in both arms after calibration); arm-to-arm drift is not controlled beyond that
- run_count=1 is below the >=3-repetitions methodology minimum (experiments.md rule 4); cross-run dispersion is not assessable
- no rate sweep in this run set — knee_estimate is null; no claim is made about saturation behavior
- no cost profile applies to this run set — cost is null (cost figures are only computed from a declared, provenanced cost-profile file, never from assumed rates)

### Unexplained anomalies (mandatory — never silently empty)

**None observed.** We looked and found none; an anomaly-free claim is only honest next to the checks that were run:

- manifest(s) and every raw event schema-validated against the pinned contracts bundle (the loader refuses manifest-less or schema-invalid data outright)
- run_id/repetition consistency between events and manifest enforced by the loader
- comparability keys (target_topology, workload_ref, engine, model, hardware, gateway, warm_up) verified identical across all pooled runs; duplicate run_ids refused (double-count/cherry-pick guard)
- warm-up exclusion counted per repetition in scheduled-send order and reconciled into the validity block
- declared error/shed gate evaluated over the measured window: error rate 0.0000 + shed rate 0.0000 vs declared threshold 0.05 — below threshold
- zero-sample check on the contract-required latency signals (ttft_seconds, e2e_duration_seconds)
- goodput ratio, shed rate, and stall rate computed in one pass over the same measured window (506.366s post-warm-up window, 36 events, 1 repetition(s))
- per-run p50 dispersion (median ± range) computed beside the pooled tables where run_count > 1

## Reproduction — one command

This report regenerates from the linked artifacts with exactly:

```sh
python3 -m inferbench_analysis report --bundle scenarios/b/.build/contracts-bundle --run evidence/i3/raw/runs/chat-short-cpu-gw --slo evidence/i3/raw/slo/scenario-b-llamacpp-cpu-shakedown.slo.json --result-id i3-chat-short-cpu-gw --threat 'single-host client+server co-location: llama-server (-t 4), infergate, and inferbench share one 4-core host; measured interval-CPU during this run: gateway mean 0.2% / max 1.0% of one core, inferbench mean 0.1% / max 0.6% of one core, llama-server mean 178.6% / max 397.6% of one core. Client-side timing competes with the engine for CPU.' --threat 'single repetition, small sample (CPU-adapted rate): bootstrap CIs are wide and cross-run dispersion does not exist; numbers are a methodology shakedown, not a performance claim' --threat 'arrival rate CPU-adapted from same-day single-stream calibration (evidence/i3/logs/rate-calibration.log); results characterize this host + engine build + quantized model only' --threat 'SLO thresholds derived from same-host calibration probe maxima (x1.5 headroom, seeds distinct from the measured runs): goodput@SLO exercises the machinery, it is not an external target' --threat 'paired arm ran minutes apart against its own fresh llama-server process (OS page cache warm in both arms after calibration); arm-to-arm drift is not controlled beyond that' --out evidence/i3/reports
```

Pinned versions: serving-contracts bundle 8d81492 (v0.2.0 tag pending); inferbench-analysis 0.2.0.

## Provenance links

- run manifests: `evidence/i3/raw/runs/chat-short-cpu-gw/manifest.json`
- raw events: `evidence/i3/raw/runs/chat-short-cpu-gw/events.jsonl`
