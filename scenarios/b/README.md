# Scenario B — Local inference (first real engine, CPU)

```text
inferbench → infergate → llama.cpp (CPU)
```

- **Owning milestone:** I3 (owner: inference-lab). Task: IL-T003.
- **Status:** defined (2026-07-10). Compose/scripts arrive with IL-T003; inputs unpinned.
- **Depends on:** I2 accepted (Scenario A).

## Purpose

Replace the mock with the first real inference engine, still GPU-free: prove the gateway's
llama.cpp adapter against real token generation, shake down the benchmark methodology
(report #0), verify cancellation against a real engine, and demonstrate mock↔llama.cpp
failover through the gateway.

## Components (all released artifacts, pinned in `pins/pins.yaml`)

| Component | Artifact | Pin entry (expected id) |
|---|---|---|
| Gateway | infergate image (digest-pinned), llama.cpp adapter enabled | `infergate-image` |
| Engine | llama.cpp server at an **exact pinned commit** | `engine-llamacpp` |
| Model | GGUF checkpoint: pinned revision + quantization + tokenizer hash | `model-gguf` |
| Load/measurement | inferbench released binary + report generator | `inferbench-binary` |
| Failover peer | mock-backend image (for mock↔llama.cpp failover demo) | `infergate-mock-image` |
| Contracts | serving-contracts bundle | `contracts-bundle` |

**Pinned inputs: currently none — everything unpinned as of 2026-07-10.**

## Expected outcome

`chat-short` and `shared-prefix` workloads complete on CPU through the gateway against
llama.cpp; the first schema-valid benchmark report (report #0 — a methodology shakedown, not
a performance claim) is generated with full manifest + validity block; cancellation and
failover behave per contract.

## Indicative invocation (executed at IL-T003, not before)

```bash
docker compose up          # in scenarios/b
inferbench run --workload chat-short   --seed <s> --target http://infergate:<port>
inferbench run --workload shared-prefix --seed <s> --target http://infergate:<port>
inferbench report --run <id>
```

## Acceptance checklist (mirrors I3 — executed copy goes to `evidence/i3/checklist.md`)

- [ ] Stack composed from pinned artifacts only: llama.cpp **commit** pinned, GGUF **model
      revision + quantization + tokenizer hash** pinned; pins validator green.
- [ ] `chat-short` workload completes on CPU through the gateway (seeded, versioned).
- [ ] `shared-prefix` workload completes on CPU through the gateway (seeded, versioned).
- [ ] **Benchmark report #0** generated and **schema-valid** (Contract 3): full run manifest
      (engine commit + flags, model revision + tokenizer, hardware, gateway + config version,
      warm-up policy, repetition count, hypothesis) + **validity block**; pooled percentiles,
      never averaged across runs; goodput@SLO with shed rate adjacent. Labeled a methodology
      shakedown.
- [ ] **Cancellation verified against llama.cpp**: client disconnect propagates; engine
      release observable within bound.
- [ ] **Failover mock↔llama.cpp demonstrated** through the gateway, with client-visible
      behavior recorded.
- [ ] Evidence archived: benchmark report #0, campaign logs, this checklist → `evidence/i3/`;
      pins updated with `proven_at: [I3]` rows.
- [ ] Reviewed (user acceptance).

## Failure handling

- llama.cpp behavioral surprises → capability descriptor updated + adapter fixed **in
  infergate** (defect report with evidence); re-run after pin bump.
- Invalid report #0 → G4 methodology review before proceeding to any further benchmarking.
- Report numbers are shakedown data: they carry provenance + date and are never quoted as
  performance claims.
