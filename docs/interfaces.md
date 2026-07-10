# Interfaces — inference-lab

This repo has no runtime API. Its interfaces are: (1) the contracts it consumes (owned by
serving-contracts, pinned by tag), (2) the pins file format it provides, and (3) the evidence
layout conventions it enforces.

## 1. Consumed artifacts (never a source import)

| Provider | Mechanism |
|---|---|
| serving-contracts | pinned released spec bundle (SemVer tag); compatibility matrix + pins reference it |
| infergate | released container images by digest (gateway + mock-backend) + deployment descriptor + capability descriptors |
| inferbench | released binary/version; benchmark-result + raw-event files; reports |
| fleetlab | capacity-recommendation files + reports |
| inferops | released manifests/config bundles, dashboards, runbooks, campaign logs |
| all five | released artifacts, result files, reports — archived here as milestone evidence |

## 2. Contract summaries this repo touches

Bundle owned by serving-contracts; pinned by SemVer tag in `pins/pins.yaml`.

### Contract 1 — Inference API (OpenAI-compatible subset)

- Endpoints: `POST /v1/chat/completions` (stream + non-stream), `GET /v1/models`, `/healthz`,
  `/readyz`, `/metrics`.
- Enumerated supported request fields: `model`, `messages`, `max_tokens`/`max_completion_tokens`,
  `temperature`, `top_p`, `stream`, `stream_options.include_usage`, `stop`, `seed`, `user`.
  Unsupported fields are rejected with typed errors, never ignored.
- SSE: `data: <json-chunk>` events, terminal `data: [DONE]`, usage in the final chunk when
  requested, no cross-request interleaving.
- Error envelope `{"error": {"message", "type", "code", "param"}}` + request ID; taxonomy
  includes `rate_limited` (429 + `Retry-After`), `overloaded` (503), `canceled`, etc.
- Cancellation: client disconnect propagates upstream; observable engine release is part of
  conformance; tokens emitted before cancel are billable.
- **Used here by:** quickstart smoke calls, demo scripts, scenario checklists.

### Contract 2 — Metrics/trace vocabulary

- Canonical Prometheus names: `inference_ttft_seconds`, `inference_itl_seconds`,
  `inference_queue_depth`, `inference_sheds_total`, … with a low-cardinality label policy.
- OTel GenAI semantic-convention trace attributes at a **pinned version** (semconv status
  "Development" as of 2026-07 — re-verify at use time).
- Gateway span sequence: `recv → queue.wait → upstream.connect → ttft → stream.relay → settle`.
- TTFT = first upstream body byte at gateway; client-side TTFT (inferbench) is a separate
  named series.
- **Used here by:** scenario evidence (traces/dashboards must show these names), I2 acceptance.

### Contract 3 — Benchmark data

- Workload schema: 8 named workloads — `chat-short`, `rag-long-in`, `gen-long-out`,
  `shared-prefix`, `mixed`, `bursty`, `cancel-storm`, `slow-client`; seeded, versioned.
- Benchmark-run manifest: engine version/commit + all flags, model revision + tokenizer,
  hardware/driver/CUDA, gateway + config version, warm-up policy, repetition count, hypothesis.
- Raw-event JSONL per request; benchmark-result with pooled percentiles (never averaged across
  runs), goodput@SLO with shed rate adjacent, validity block.
- **Used here by:** archived reports, reproducibility audit, compatibility-matrix
  comparability rule.

### Contract 5 — Deployment

- Image + digest, ports, env/config mounts, warm-up-aware readiness, model mount, resources
  incl. GPU, `preStop` drain with termination grace > max stream duration, secrets.
- **Used here by:** pins-file entries and Scenario D evidence.

### Contract 6 — Fault scenarios

- 12 scenarios with expected gateway semantics and client-visible behavior:
  1 backend killed pre-first-token; 2 killed post-first-token; 3 slow backend; 4 slow client;
  5 gateway termination during streaming; 6 queue saturation; 7 retry storm; 8 config reload
  under traffic; 9 usage-DB failure; 10 one unhealthy backend; 11 readiness during warm-up;
  12 rolling update with active requests.
- **Used here by:** postmortems and the I7 campaign-evidence archive.

### Contract 7 — Capacity recommendation (fleetlab → inferops)

- Input references (benchmark-result IDs, workload version, SLO, cost profile, hardware
  profiles); recommended topology (replica counts, engine config); predicted
  goodput/latency/cost **with stated uncertainty**; autoscaling signal + thresholds;
  assumptions and sensitivity notes.
- **Used here by:** Scenario E loop evidence (I6) — the recommendation file is a first-class
  evidence artifact.

## 3. Pins file format specification (`pins/pins.yaml`)

Machine-readable YAML, schema-checked by `pins/validate_pins.py`. Decision record: ADR-0001.

Top level:

```yaml
schema_version: 1          # integer; bump on breaking format change
updated: "YYYY-MM-DD"      # date of last edit
comparability_rule: >-     # the normative benchmark comparability rule, verbatim
  ...
milestone_evidence: {}     # map I1..I8 -> relative evidence path, filled as milestones land
artifacts: []              # list of pin entries (see below)
```

Each entry in `artifacts`:

| Field | Required | Rules |
|---|---|---|
| `id` | yes | unique, kebab-case, stable (e.g. `contracts-bundle`, `infergate-image`) |
| `component` | yes | one of: `serving-contracts`, `infergate`, `infergate-mock`, `inferbench`, `fleetlab`, `inferops`, `engine-vllm`, `engine-llamacpp`, `engine-sglang`, `model`, `hardware`, `otel-semconv`, `other` |
| `kind` | yes | one of: `contract-bundle`, `container-image`, `binary`, `git-commit`, `model-revision`, `config-bundle`, `dashboard-bundle`, `hardware-profile`, `spec-version` |
| `version` | yes | tag / SemVer / commit SHA / revision string; `null` only while unpinned |
| `digest` | conditional | **required** (`sha256:<64 hex>`) when `kind: container-image`; optional hash otherwise |
| `provenance` | yes | one of: `measured`, `source-reported`, `assumed` |
| `date` | yes | ISO date the pin (or its re-verification) was recorded |
| `proven_at` | yes | list drawn from `I1..I8`; may be empty (`[]`) until proven |
| `source` | yes | URL or in-program reference to the release/registry |
| `reverify` | no | boolean; `true` marks volatile facts ("as of 2026-07 — re-verify at use time") |
| `notes` | no | free text (e.g. quantization, tokenizer hash, driver/CUDA details) |

Version-pinning rules enforced through this format:

- contract bundle by SemVer tag;
- infergate + mock-backend images by **digest + tag**;
- engine versions: vLLM v0.24.x baseline + exact commit; llama.cpp commit; SGLang commit if
  ever used — all as of 2026-07, re-verify;
- model checkpoint revision + quantization + tokenizer hash;
- driver/CUDA per GPU run;
- inferops dashboard/collector config bundle tags.

**Benchmark comparability rule (normative; also printed in the compatibility matrix):**
results are comparable only when model revision, quantization, tokenizer, engine
version+flags, hardware, driver/CUDA, workload version+seed, and warm-up policy all match,
or the difference is the single declared experimental variable.

## 4. Evidence layout conventions

```text
evidence/i<N>/
├── checklist.md          # the executed acceptance checklist (item-by-item, with outcomes)
├── pins-snapshot.yaml    # copy of the pins entries the run used (or a pinned git ref)
├── logs/                 # run logs (bring-up, smoke, teardown), redacted per docs/security.md
├── raw/                  # raw-event JSONL, metrics exports, trace exports
├── reports/              # links/copies of generated reports (manifest + validity block)
└── notes.md              # dated observations, defects filed upstream, deviations
```

Conventions:

- Evidence is immutable once a milestone is accepted; corrections are **new dated entries**
  (ADR-0002). Nothing is deleted or rewritten.
- Every file that states a number carries provenance and a date.
- Every compatibility-matrix row links to the `evidence/i<N>/` directory that proves it.
- Failed runs are archived too (under `notes.md` + `logs/`), labelled invalid — they are
  defect evidence, not publishable results.
