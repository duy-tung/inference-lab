# Scenario C — GPU inference (the GPU path)

```text
inferbench → infergate → vLLM (rented GPU) → observability
```

- **Owning milestone:** I4 (owner: inference-lab). Task: IL-T004.
- **Status:** defined (2026-07-10). Scripts arrive with IL-T004; inputs unpinned.
- **Depends on:** I3 accepted (Scenario B); gate **G6** (GPU session discipline).

## Purpose

Prove the gateway against a production-class engine on real GPU hardware: streaming and
cancellation verified via **engine metrics** (not just gateway-side observation), and the
gateway's overhead quantified with a direct-vs-via-gateway comparison. This is the scenario
where "I measured the gateway and engine independently and together" gains its GPU evidence.

## GPU session discipline (gate G6 — mandatory, pre-approved by the user)

Every GPU session requires, **written before the session**: a hypothesis; a full config
manifest (engine version/commit + flags, model + quantization + tokenizer, hardware/driver/
CUDA, instance type, gateway + config version); an **auto-stop script**; a **budget alert**.
Program GPU envelope ~$150–250 total (as of 2026-07 — user-confirmable). Session auto-stop
must be confirmed in the archived session log.

## Components (all released artifacts, pinned in `pins/pins.yaml`)

| Component | Artifact | Pin entry (expected id) |
|---|---|---|
| Gateway | infergate image (digest-pinned), vLLM adapter | `infergate-image` |
| Engine | vLLM — v0.24.x baseline + **exact commit** (as of 2026-07 — re-verify) | `engine-vllm` |
| Model | checkpoint revision + quantization + tokenizer hash | `model-checkpoint` |
| Hardware | instance type + driver/CUDA versions (per session) | `gpu-session-<date>` |
| Load/measurement | inferbench released binary | `inferbench-binary` |
| Telemetry | OTel/metrics stack as in Scenario A | `otel-collector-image` |

**Pinned inputs: currently none — everything unpinned as of 2026-07-10.**

## Expected outcome

The pinned gateway+vLLM configuration serves seeded workloads on a rented GPU; cancellation
release is visible in engine metrics; gateway overhead (direct vs via-gateway) is measured
with ≥3 runs per point; the session auto-stops; every artifact carries the full manifest.

## Indicative invocation (executed at IL-T004, not before)

```bash
# per GPU session runbook: provision → deploy pinned stack → warm-up →
inferbench sweep --target <direct-engine>  --rates <...>   # ≥3 runs/point
inferbench sweep --target <via-infergate>  --rates <...>   # ≥3 runs/point
# → capture engine metrics for cancellation verification → auto-stop
```

## Acceptance checklist (mirrors I4 — executed copy goes to `evidence/i4/checklist.md`)

- [ ] G6 satisfied **before** the session: written hypothesis + full config manifest +
      auto-stop script + budget alert; session plan pre-approved by the user.
- [ ] Stack deployed from pinned artifacts: vLLM version/commit, model checkpoint +
      quantization + tokenizer, driver/CUDA, instance type all recorded in pins.
- [ ] Streaming verified end-to-end via gateway against vLLM on GPU.
- [ ] **Cancellation verified via engine metrics**: KV usage / running-count drop within the
      declared bound after client disconnect; metrics export archived.
- [ ] **Gateway-overhead comparison** (direct vs via-gateway) measured with **≥3 runs per
      point**; comparability rule respected (single declared variable = gateway presence).
- [ ] Session **auto-stop confirmed in the session log**; spend within budget alert.
- [ ] All artifacts carry the full manifest.
- [ ] Evidence archived: session log, GPU benchmark report, cancellation-verification metrics
      export, GPU session manifest, this checklist → `evidence/i4/`.
- [ ] Reviewed (user acceptance) — or the CPU fallback deviation recorded (below).

## Failure handling & CPU fallback

- Engine metric-name drift → update the capability mapping (infergate defect/config), then
  re-verify; never rename locally.
- Budget alert trips → stop, record, fall back.
- **CPU fallback (documented deviation in `docs/implementation-notes.md`):** if GPU access is
  blocked, the llama.cpp variant (Scenario B) becomes the measured baseline; the deviation,
  its consequences for portfolio claims, and the repositioning are recorded — never silently
  substituted.
