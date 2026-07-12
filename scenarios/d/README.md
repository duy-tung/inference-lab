# Scenario D — Operated stack on Kubernetes

```text
inferops → infergate → vLLM → OTel / Prometheus / Grafana / Tempo
```

**As actually executed (2026-07-12, CPU-fallback, D-005 continued):**
`inferops (Docker Compose, RQ-14) → infergate v0.1.0 → llama.cpp@8f114a9 → OTel Collector /
Prometheus / Grafana / Tempo` — no vLLM, no GPU, no scheduled Kubernetes pod. See the Status
line and `evidence/i5/checklist.md` §0 for the full, honest deviation text.

- **Owning milestone:** I5 — **owned by inferops**, not by this repo. Task here: IL-T005
  (consumer-side verification + evidence archiving).
- **Status:** executed (2026-07-12) — evidence archived in
  [`evidence/i5/`](../../evidence/i5/checklist.md); **I5 acceptance review by the user is
  pending** (I2/I3 precedent). Inputs pinned in `pins/pins.yaml` (Scenario D / I5 pin set).
  **Headline deviation:** inferops's own RQ-14 compose-pivot — the runtime stack runs on
  Docker Compose, not a scheduled Kubernetes cluster (this sandbox cannot schedule any pod, on
  any distribution); Kubernetes manifests are authored and validated against a live k3s API
  server instead. **No pod scheduling is claimed.** GPU node continues I4's own CPU-fallback
  (D-005): the engine is real llama.cpp (CPU), not vLLM — no GPU claim either. Full detail:
  `evidence/i5/checklist.md` §0.
- **Depends on:** I4 accepted (or its recorded CPU fallback, satisfied — D-005); inferops
  release with runbooks (satisfied — inferops IO-T002…IO-T010, commit `db30279`).

## Purpose

The platform, operated: deployed on Kubernetes by inferops from **released images only**,
with warm-up-aware readiness, rolling updates under load, golden dashboards, and end-to-end
traces. This repo's role is the consumer side — verify the scenario runs per the inferops
runbooks and archive the I5 evidence set; execution and fixes are inferops's.

## Components (this repo references, never checks out)

| Component | Artifact | Pin entry (actual id) |
|---|---|---|
| Deployment stack | inferops release: manifests/config bundles, runbooks (repo @ `db30279`, compose-pivot per RQ-14) | `inferops-bundle` |
| Gateway | infergate **v0.1.0 release** image (digest-pinned), commit `49236a3` | `inferops-infergate-image` |
| Mock backend | infergate-mock v0.1.0 release image (same commit) | `inferops-mock-backend-image` |
| Engine | **llama.cpp@8f114a9 (CPU-fallback, D-005 continued — no vLLM pin exists)** | `inferops-llamacpp-engine-image` (+ `engine-llamacpp`, `model-gguf`) |
| Observability | OTel Collector 0.112.0, Prometheus v2.55.1, Grafana 11.3.1, Tempo 2.6.1 (upstream digests) | `inferops-otel-collector-image`, `inferops-prometheus-image`, `inferops-grafana-image`, `inferops-tempo-image` |
| Dashboards | golden dashboard, uid `inferops-golden`, 11/11 Contract-2 metric names | `inferops-dashboards` |
| Load (rolling-update / config-rollout tests) | inferops's own scripted clients (not an inferbench-driven run this milestone) | — |

**Pinned 2026-07-12** (Scenario D / I5 pin set, `pins/pins.yaml`). No compose file here:
Scenario D is invoked through **inferops's own compose stack + validated manifests**; this
directory holds pointers and the archiving procedure only. No source checkouts, no local
manifests duplicating inferops.

## Expected outcome

I5's acceptance criteria demonstrated on inferops's operational stack (Docker Compose runtime,
RQ-14; Kubernetes manifests validated against a live k3s API server but never scheduled — see
Status above): deployment from released images only, warm-up-aware readiness demonstrated,
rolling update under load with zero client-visible errors, golden dashboards live, traces
end-to-end. **All five demonstrated** — full mapping in `evidence/i5/checklist.md` §1.
**I5 acceptance by its owner (inferops) / user review of this record is pending**, same as
I2/I3 before it.

## Actual invocation (as executed 2026-07-12)

```bash
# inferops's own compose stack (already running; this repo never starts/stops it):
#   docker compose -f docker-compose.yml -f docker-compose.observability.yml \
#     -f docker-compose.lifecycle.yml --profile llamacpp up -d   (per inferops's own compose files)
# This repo's consumer-side verification (light, archived to evidence/i5/raw/demo-20260712T005146Z/):
curl -s http://127.0.0.1:8082/v1/chat/completions -d '{...}'   # gateway-llamacpp, real llama.cpp
curl -s http://127.0.0.1:9090/api/v1/query --data-urlencode 'query=inference_requests_total{backend="llamacpp"}'
curl -s http://127.0.0.1:9090/api/v1/query_exemplars --data-urlencode 'query=inference_ttft_seconds_bucket{backend="llamacpp"}'
docker exec inferops-gateway-llamacpp wget -qO- http://tempo:3200/api/traces/<trace_id>
```

## Archiving checklist (this repo's IL-T005 duty — executed copy in `evidence/i5/checklist.md`)

- [x] **Deployment-from-released-images-only confirmed** (image digests in the applied
      manifests match pins; no source checkout anywhere in the procedure) — RQ-14 caveat on
      runtime substrate (Compose, not scheduled k8s); see `evidence/i5/checklist.md` §1 item 1.
- [x] Applied manifests archived (with digests) → `evidence/i5/` (by reference to `inferops/`,
      per the no-duplication rule; k3s-validation transcripts cited, not copied).
- [x] Smoke outputs archived (health/readiness including warm-up-aware readiness behavior).
- [x] **Rolling-update test log** archived: update under load, zero client-visible errors,
      drain semantics per Contract 5 (`preStop` drain, termination grace > max stream
      duration).
- [~] **Golden dashboard exports** archived (JSON + live API/query render; bundle version
      pinned); canonical Contract-2 metric names visible — **no rendered screenshot image**
      exists yet (a completeness gap noted in `evidence/i5/checklist.md` §2/§6, not a
      blocker).
- [x] **End-to-end trace export** archived (client → gateway → engine spans) — mock-backed
      (IO-T003) and, newly this session, llama.cpp-backed (`evidence/i5/raw/demo-20260712T005146Z/`).
- [x] Pins updated: inferops release + dashboard/config bundle versions, `proven_at: [I5]`.
- [x] Compatibility matrix row added citing `evidence/i5/`.
- [ ] I5 acceptance by its owner (inferops) recorded + cross-checked against the archived
      smoke/rolling-update outputs — **pending user review** (I2/I3 precedent).

## Failure handling

Probe/drain violations or observability gaps are inferops/infergate defects (a deployment
contract change ⇒ I1 re-run before re-claiming); this repo archives the failure evidence and
waits for the fixed release. Nothing is fixed here.
