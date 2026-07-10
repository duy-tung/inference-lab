# Scenario D — Operated stack on Kubernetes

```text
inferops → infergate → vLLM → OTel / Prometheus / Grafana / Tempo
```

- **Owning milestone:** I5 — **owned by inferops**, not by this repo. Task here: IL-T005
  (consumer-side verification + evidence archiving).
- **Status:** defined (2026-07-10). Invocation pointers arrive with IL-T005; inputs unpinned.
- **Depends on:** I4 accepted (or its recorded CPU fallback); inferops release with runbooks.

## Purpose

The platform, operated: deployed on Kubernetes by inferops from **released images only**,
with warm-up-aware readiness, rolling updates under load, golden dashboards, and end-to-end
traces. This repo's role is the consumer side — verify the scenario runs per the inferops
runbooks and archive the I5 evidence set; execution and fixes are inferops's.

## Components (this repo references, never checks out)

| Component | Artifact | Pin entry (expected id) |
|---|---|---|
| Deployment stack | inferops release: manifests/config bundles, runbooks | `inferops-bundle` |
| Gateway | infergate image (digest-pinned) via Contract 5 descriptor | `infergate-image` |
| Engine | vLLM (pins carried over from Scenario C) | `engine-vllm` |
| Dashboards/collector | inferops dashboard + collector config bundle tags | `inferops-dashboards` |
| Load (for rolling-update test) | inferbench released binary | `inferbench-binary` |

**Pinned inputs: currently none — everything unpinned as of 2026-07-10.**
No compose file here: Scenario D is invoked through **inferops runbooks + released
manifests**; this directory holds pointers and the archiving procedure only. No source
checkouts, no local manifests duplicating inferops.

## Expected outcome

I5 accepted by its owner (inferops) on the local cluster + GPU node, and this repo holds the
complete, pinned evidence set proving it: deployment from released images only, warm-up-aware
readiness demonstrated, rolling update under load with zero client-visible errors, golden
dashboards live, traces end-to-end.

## Indicative invocation (executed at IL-T005, per inferops runbook — not before)

```bash
kubectl apply -k <inferops released manifest bundle>   # per inferops runbook
# scripted rolling-update test under inferbench load, per inferops runbook
```

## Archiving checklist (this repo's IL-T005 duty — executed copy goes to `evidence/i5/checklist.md`)

- [ ] **Deployment-from-released-images-only confirmed** (image digests in the applied
      manifests match pins; no source checkout anywhere in the procedure).
- [ ] Applied manifests archived (with digests) → `evidence/i5/`.
- [ ] Smoke outputs archived (health/readiness including warm-up-aware readiness behavior).
- [ ] **Rolling-update test log** archived: update under inferbench load, zero
      client-visible errors, drain semantics per Contract 5 (`preStop` drain, termination
      grace > max stream duration).
- [ ] **Golden dashboard exports** archived (JSON + rendered image, bundle version pinned);
      canonical Contract-2 metric names visible.
- [ ] **End-to-end trace export** archived (client → gateway → engine spans).
- [ ] Pins updated: inferops release + dashboard/config bundle versions, `proven_at: [I5]`.
- [ ] Compatibility matrix row added citing `evidence/i5/`.
- [ ] I5 acceptance by its owner (inferops) recorded + cross-checked against the archived
      smoke/rolling-update outputs.

## Failure handling

Probe/drain violations or observability gaps are inferops/infergate defects (a deployment
contract change ⇒ I1 re-run before re-claiming); this repo archives the failure evidence and
waits for the fixed release. Nothing is fixed here.
