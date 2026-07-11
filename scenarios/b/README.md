# Scenario B — Local inference (first real engine, CPU)

```text
inferbench → infergate → llama.cpp (CPU)
```

- **Owning milestone:** I3 (owner: inference-lab). Task: IL-T003.
- **Status:** executed (2026-07-11) — evidence in [`evidence/i3/`](../../evidence/i3/checklist.md);
  I3 user-acceptance review pending. Inputs pinned in `pins/pins.yaml` (Scenario B pin set).
- **Depends on:** I2 accepted (Scenario A).

## Purpose

Replace the mock with the first real inference engine, still GPU-free: prove the gateway's
llama.cpp adapter against real token generation, shake down the benchmark methodology
(report #0), verify cancellation against a real engine, and demonstrate mock↔llama.cpp
failover through the gateway.

## Components (pinned in `pins/pins.yaml`; Scenario B pin set, 2026-07-11)

| Component | Artifact | Pin entry (actual id) |
|---|---|---|
| Gateway | infergate **host binary** @74f2372 (llama.cpp adapter + failover), sha256-recorded | `infergate-binary` |
| Engine | llama.cpp llama-server at commit 8f114a9 (prebuilt, commit + binary sha256 verified at build) | `engine-llamacpp` |
| Model | Qwen2.5-1.5B-Instruct GGUF Q4_K_M; **file sha256 = pinned revision** (covers weights + quantization + embedded tokenizer) | `model-gguf` |
| Load/measurement | inferbench binary + analysis/report package @69a5abc | `inferbench-binary-69a5abc` |
| Failover peer | mock-backend **host binary** @74f2372 (mock↔llama.cpp failover demo) | `infergate-mock-binary` |
| Contracts | serving-contracts v0.2.0 (tag at 484b449) | `contracts-bundle-v0-2-0` |

**Deviation from the definition above as written at IL-T001:** Scenario B runs **host
processes, not containers** (binaries instead of digest-pinned images) — decision D-004 in
`docs/implementation-notes.md`. Scenario B is a local scenario; container/registry rigor was
proven at I2 and full operational rigor is I5's job. Every binary is built read-only via
`git archive <pinned commit>` with recorded sha256s (`evidence/i3/logs/build-info.txt`).

## Expected outcome

`chat-short` and `shared-prefix` workloads complete on CPU through the gateway against
llama.cpp; the first schema-valid benchmark report (report #0 — a methodology shakedown, not
a performance claim) is generated with full manifest + validity block; cancellation and
failover behave per contract.

## Actual invocation (as executed 2026-07-11)

```bash
scenarios/b/build.sh               # pinned extraction + host binaries + contracts bundle
scenarios/b/run.sh evidence/i3     # calibration -> SLO -> paired chat-short arms ->
                                   # shared-prefix -> cancellation -> failover ->
                                   # kit validation -> analysis + reports -> checks
```

The canonical `chat-short`/`shared-prefix` workloads are consumed as CPU-adapted variants
(`workloads/chat-short-cpu.json`, `workloads/shared-prefix-cpu.json`): distributions, seeds
and duration identical to the canonical files, **only the arrival rate changed** (8→0.08,
6→0.04 rps), with the measured derivation recorded in each file's description and in
`evidence/i3/logs/rate-calibration.log`. Workload rhythm: `run.sh` also runs the identical
chat-short-cpu schedule **engine-direct** (fresh llama-server per arm) so benchmark report #0
carries a real, falsifiable gateway-overhead hypothesis.

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
