# Benchmark report — i3-shared-prefix-cpu

| | |
|---|---|
| result_id | `i3-shared-prefix-cpu` |
| result created_at | 2026-07-11T06:28:21Z |
| report generated_at | 2026-07-11T06:28:21Z |
| contracts bundle pin | 8d81492 (v0.2.0 tag pending) |
| generator | inferbench-analysis 0.2.0 (IB-T006 honest-report machine) |
| repetitions pooled | 1 |

**Source of the numbers:** in-memory analysis of the linked raw events (same pipeline that emits the benchmark-result file; bootstrap CIs and cross-run dispersion shown here cannot ride in the result file at the pinned contracts version)

## Hypothesis under test

Every run manifest declares the hypothesis it was executed for; a report is only interpretable against it (experiments.md rule 6).

> **i3-shared-prefix-cpu:** Prefix-cache characterization: with 80% of requests sharing a 1024-token prefix (groups of 16), llama-server slot-level prefix-cache reuse is observable end-to-end from the client side: pooled client TTFT p50 through the gateway stays below the measured single-stream cold-prefill floor of ~15.2 s for a ~1354-token prompt (rate calibration 2026-07-11, evidence/i3/logs/rate-calibration.log) -- i.e. most requests do NOT pay a full cold prefill. Methodology shakedown: ~24 requests, single repetition, wide CIs.

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

### i3-shared-prefix-cpu

- manifest: `evidence/i3/raw/runs/shared-prefix-cpu/manifest.json`
- workload file: `evidence/i3/raw/runs/shared-prefix-cpu/workload.json`
- arrival process: open-loop Poisson, rate 0.04 req/s; workload_ref = shared-prefix-cpu@1.0.0 seed 1003004
- target topology: `via-gateway`

```json
{
  "run_id": "i3-shared-prefix-cpu",
  "target_topology": "via-gateway",
  "workload_ref": {
    "name": "shared-prefix-cpu",
    "version": "1.0.0",
    "seed": 1003004
  },
  "engine": {
    "name": "llamacpp",
    "version": "1 (8f114a9)",
    "commit": "8f114a9b573b69035299f9b924047f53c1e22c7e",
    "flags": {
      "alias": "qwen2.5-1.5b-instruct-q4_k_m",
      "ctx_size": 8192,
      "defaults_note": "all remaining llama-server options at 8f114a9 build defaults (fresh process for this run; slot prefix cache is engine-default behavior)",
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
    "rtt_ms": 1.361686
  },
  "warm_up": {
    "policy": "discard-requests",
    "value": 4
  },
  "repetitions": 1,
  "hypothesis": "Prefix-cache characterization: with 80% of requests sharing a 1024-token prefix (groups of 16), llama-server slot-level prefix-cache reuse is observable end-to-end from the client side: pooled client TTFT p50 through the gateway stays below the measured single-stream cold-prefill floor of ~15.2 s for a ~1354-token prompt (rate calibration 2026-07-11, evidence/i3/logs/rate-calibration.log) -- i.e. most requests do NOT pay a full cold prefill. Methodology shakedown: ~24 requests, single repetition, wide CIs.",
  "started_at": "2026-07-11T06:09:09Z",
  "contracts_bundle_version": "8d81492 (v0.2.0 tag pending)",
  "notes": "I3 / Scenario B shared-prefix run through the gateway. TTFT here includes open-loop queue wait at ~0.5 utilization; a failed hypothesis is recorded as a finding, not hidden."
}
```

## Results

### Throughput (measured window)

| metric | value |
|---|---|
| ok-requests / second | 0.0409 |
| output tokens / second | 4.09 |
| total requests (all statuses) | 21 |
| total output tokens | 2102 |
| measured window | 513.950 s |
| pooled events (post warm-up) | 21 |

### Latency — pooled percentiles

Method: `pooled-raw-events` — percentiles computed on the pooled raw per-request samples across repetitions (never averaged across runs). Seconds.

| signal | n | p50 | p90 | p95 | p99 | p999 | max | mean |
|---|---|---|---|---|---|---|---|---|
| `ttft_seconds` | 21 | 13.192586 | 28.765372 | 29.874211 | 42.226442 | — | 45.314500 | 14.666313 |
| `e2e_duration_seconds` | 21 | 24.742317 | 52.411887 | 52.992440 | 55.581281 | — | 56.228491 | 26.352594 |
| `itl_seconds` | 2066 | 0.080685 | 0.089566 | 0.092196 | 0.105546 | 12.868424 | 16.021004 | 0.118257 |
| `max_stall_seconds` | 21 | 0.109867 | 12.919025 | 15.095942 | 15.835992 | — | 16.021004 | 3.816450 |

(p999 is only resolved at n ≥ 1000 pooled samples; '—' means the pool cannot support it. The mean column is context for the percentiles, never a substitute.)

**Bootstrap 95% confidence intervals** — nonparametric percentile bootstrap on the pooled samples (B=1000 resamples, 95% interval, seeded — ADR-0002); CIs are report-surface only, the pinned result schema carries no CI fields:

| signal | percentile | 95% CI (seconds) |
|---|---|---|
| `ttft_seconds` | p50 | [6.692910, 16.247817] |
| `ttft_seconds` | p90 | [16.247817, 45.314500] |
| `ttft_seconds` | p95 | [20.911359, 45.314500] |
| `ttft_seconds` | p99 | [26.413963, 45.314500] |
| `e2e_duration_seconds` | p50 | [14.678950, 31.080870] |
| `e2e_duration_seconds` | p90 | [31.080870, 56.228491] |
| `e2e_duration_seconds` | p95 | [35.373130, 56.228491] |
| `e2e_duration_seconds` | p99 | [39.590219, 56.228491] |
| `itl_seconds` | p50 | [0.080251, 0.081117] |
| `itl_seconds` | p90 | [0.088966, 0.090169] |
| `itl_seconds` | p95 | [0.091707, 0.093022] |
| `itl_seconds` | p99 | [0.097885, 0.115461] |
| `itl_seconds` | p999 | [2.385864, 15.960875] |
| `max_stall_seconds` | p50 | [0.095332, 2.387996] |
| `max_stall_seconds` | p90 | [2.387996, 16.021004] |
| `max_stall_seconds` | p95 | [11.709416, 16.021004] |
| `max_stall_seconds` | p99 | [12.094135, 16.021004] |

### Goodput @ SLO `scenario-b-llamacpp-cpu-shakedown@1.0.0` — with shed and stall rates adjacent

Shed and stall rates are part of the goodput figure, not footnotes: goodput can be gamed by shedding early, and a stream can meet its TTFT target and still stall mid-generation. All three are computed in one pass over the same measured window.

| goodput block | value |
|---|---|
| goodput ratio (meeting / ALL offered, incl. shed+canceled+errored) | 0.9524 (20/21 offered) |
| requests/second meeting SLO | 0.0389 |
| **shed rate (adjacent by rule)** | 0.0000 |
| **stall rate (adjacent by rule)** | 0.0000 (0/21 streaming requests) at stall threshold 30s |

### Saturation knee

`knee_estimate: null` — no rate sweep contributed to this run set, so no saturation point was measured and **no capacity or saturation claim may be made from this report** (interpretation rule 4; also listed under threats to validity).

### Cost

`cost: null` — **why:** no cost profile applies to this run set — cost is null (cost figures are only computed from a declared, provenanced cost-profile file, never from assumed rates)

## Validity block (mandatory)

- **Warm-up handling:** manifest warm-up policy 'discard-requests' (4 requests per repetition, ordered by scheduled_send_ts): 4 events excluded, 21 kept (i3-shared-prefix-cpu/rep1: 4 excluded)
- **Run count / pooling statement:** 1 repetition(s) pooled; all percentile tables above are computed on the pooled raw events of these repetitions (never on averaged per-run percentiles).
- **Declared error/shed gate:** latency percentiles are withheld above error+shed rate 0.05; this run set measured error rate 0.0000 + shed rate 0.0000.
- **Closed-loop flag:** no contributing workload declares closed-loop arrival.

### Threats to validity (mandatory)

- single-host client+server co-location: llama-server (-t 4), infergate, and inferbench share one 4-core host; measured interval-CPU during this run: gateway mean 0.1% / max 0.8% of one core, inferbench mean 0.1% / max 0.8% of one core, llama-server mean 204.4% / max 398.5% of one core. Client-side timing competes with the engine for CPU.
- single repetition, small sample (CPU-adapted rate): bootstrap CIs are wide and cross-run dispersion does not exist; numbers are a methodology shakedown, not a performance claim
- arrival rate CPU-adapted from same-day single-stream calibration (evidence/i3/logs/rate-calibration.log); results characterize this host + engine build + quantized model only
- SLO thresholds derived from same-host calibration probe maxima (x1.5 headroom, seeds distinct from the measured runs): goodput@SLO exercises the machinery, it is not an external target
- prefix-cache reuse depends on llama-server slot LCP selection with only 2 slots; group-interleaved arrivals can evict a cached prefix — cache effectiveness here is a property of this configuration, not of the workload
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
- goodput ratio, shed rate, and stall rate computed in one pass over the same measured window (513.950s post-warm-up window, 21 events, 1 repetition(s))
- per-run p50 dispersion (median ± range) computed beside the pooled tables where run_count > 1

## Reproduction — one command

This report regenerates from the linked artifacts with exactly:

```sh
python3 -m inferbench_analysis report --bundle scenarios/b/.build/contracts-bundle --run evidence/i3/raw/runs/shared-prefix-cpu --slo evidence/i3/raw/slo/scenario-b-llamacpp-cpu-shakedown.slo.json --result-id i3-shared-prefix-cpu --threat 'single-host client+server co-location: llama-server (-t 4), infergate, and inferbench share one 4-core host; measured interval-CPU during this run: gateway mean 0.1% / max 0.8% of one core, inferbench mean 0.1% / max 0.8% of one core, llama-server mean 204.4% / max 398.5% of one core. Client-side timing competes with the engine for CPU.' --threat 'single repetition, small sample (CPU-adapted rate): bootstrap CIs are wide and cross-run dispersion does not exist; numbers are a methodology shakedown, not a performance claim' --threat 'arrival rate CPU-adapted from same-day single-stream calibration (evidence/i3/logs/rate-calibration.log); results characterize this host + engine build + quantized model only' --threat 'SLO thresholds derived from same-host calibration probe maxima (x1.5 headroom, seeds distinct from the measured runs): goodput@SLO exercises the machinery, it is not an external target' --threat 'prefix-cache reuse depends on llama-server slot LCP selection with only 2 slots; group-interleaved arrivals can evict a cached prefix — cache effectiveness here is a property of this configuration, not of the workload' --out evidence/i3/reports
```

Pinned versions: serving-contracts bundle 8d81492 (v0.2.0 tag pending); inferbench-analysis 0.2.0.

## Provenance links

- run manifests: `evidence/i3/raw/runs/shared-prefix-cpu/manifest.json`
- raw events: `evidence/i3/raw/runs/shared-prefix-cpu/events.jsonl`
