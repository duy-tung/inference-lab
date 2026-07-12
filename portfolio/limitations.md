# Honest limitations (published at I8, kept current)

This section exists because every claim in this portfolio must survive the I8 reproducibility
audit (`evidence/i8/reproducibility-audit.md`) — a claim nobody can re-derive from pinned
artifacts is removed or re-measured, never softened into vague marketing language instead.
This page states plainly what this portfolio is **not**, immediately next to what it is.

## 1. Scale

- **Single-node, single-machine throughout.** Every scenario in this program (A, B, D, E; C
  never ran) executed on one 4-vCPU/15GB host. There is no multi-node cluster, no multi-region
  deployment, and no fleet of GPUs anywhere in this evidence set.
- **No GPU was ever rented.** Gate G6 (the GPU session gate) was deferred by an explicit user
  decision on 2026-07-11 — "no GPU rental this program wave." Every engine measurement in this
  portfolio ran on **llama.cpp, CPU-only**, not vLLM. `infergate`'s vLLM adapter (`IG-T014`)
  and `inferbench`'s GPU experiment set (`IB-T011`) were never built or executed. Any mention
  of vLLM anywhere in this repo's docs is a **target description**, never a result.
- **No Kubernetes pod was ever scheduled.** `inferops`'s own recorded deviation (RQ-14): this
  sandbox cannot run a CRI-based container runtime under a real kubelet/scheduler — proven at
  the `runc`/`nsexec` level, not a configuration gap. What *was* demonstrated: Kustomize
  manifests, authored for real and validated against a live k3s API server
  (`clusters/{local,gpu-node}/validate-k3s.sh`), and the full operational behavior (warm-up
  readiness, zero-error rolling update, golden dashboards, end-to-end traces) running for real
  on Docker Compose. **"I deployed and operated the system on Kubernetes" (the program's final
  narrative, `docs/charter.md`) is true only in the qualified sense that the manifests are
  validated against a real Kubernetes API server, not that any workload ever ran as a
  scheduled pod.** The landing page states this qualification next to the sentence, not only
  here.

## 2. Model and engine coverage

- **One model throughout:** Qwen2.5-1.5B-Instruct, GGUF Q4_K_M quantization
  (`sha256:6a1a2eb6…`). No other model size, architecture, or quantization was ever measured.
  Every benchmark number in this portfolio is conditioned on this one model.
- **CPU/llama.cpp, not GPU/vLLM (G6).** The gateway-overhead, cancellation, and admission
  evidence sets are real, but they characterize a CPU inference engine under `-np 2 -c 8192
  -t 4`. Nothing here demonstrates KV-cache pressure, continuous-batching interaction at GPU
  throughput, or vLLM-specific engine metrics.
- **"3-point cancellation, engine-verified" needs a scope qualifier.** The composed-stack,
  full 3-point test (pre-first-token / mid-stream / near-completion) ran for real against the
  **mock backend** (`evidence/i2/checklist.md`). Against the **real, pinned llama.cpp engine**,
  the composed-stack test covered **one** point (mid-stream, `evidence/i3/checklist.md`
  item 5). A separate, adapter-level 3-point test exists (infergate `IG-T005`), but it ran
  against an **unpinned, locally-authored random-weight test GGUF**, not the portfolio's
  pinned Qwen2.5-1.5B model. The landing page's cancellation claim states this breakdown
  explicitly rather than saying "3-point cancellation, mock and llama.cpp" as one undifferentiated
  fact.

## 3. Simulation ≠ production

- **fleetlab's capacity predictions carry stated, sometimes large, error.** The G8 holdout
  gate (`reports/capacity-report.md`) is a **MISS** for the `ib-t010` E2/E2b engine-config
  corpus (12.6-20.4% error, 4-9x the measurement-noise floor) — this is the exact corpus the
  I6 loop's 6-replica recommendation was fitted from. The loop's own re-measurement at the
  fitted rate (+1.3%) is real and good, but it does not retroactively validate the
  higher-rate/6-replica extrapolation, which **was never measured** at all.
- **The recommended 1→6 replica scale-out was applied only as far as 1→2** (a disclosed
  compose-substrate scope reduction, the same RQ-14 constraint as above — there is no
  orchestrator in this sandbox that can actually run 6 replicas as scheduled units). Every
  number describing "6 replicas" in this portfolio is an extrapolation, clearly labeled as
  such, never a measurement.
- **fleetlab's fitted profiles here are entirely mock-backend.** No llama.cpp or vLLM capacity
  profile was ever fitted or holdout-validated. Loop-mechanics purposes only, per fleetlab's
  own scope decision (`FL-T004`).

## 4. Benchmark methodology scope

- **Benchmark numbers are valid only for the pinned hardware/model/engine/workload
  configuration they were measured under** — the comparability rule printed in
  `compatibility/matrix.md` and `pins/pins.yaml` is not decorative; a config that differs in
  model revision, quantization, tokenizer, engine version/flags, hardware, driver/CUDA,
  workload version/seed, or warm-up policy is **not comparable** to any number in this
  portfolio, full stop.
- **Gate G5 (admission control at ~5× capacity) passed under a re-framed criterion, not the
  original one.** The original ≤20% accepted-TTFT-degradation-ratio target was **REFUTED
  twice** (`reports/benchmark-report-1.md`, `reports/benchmark-report-1b.md`: +25.16% and
  +26.08% respectively). The program owner re-baselined the gate to a different, still
  rigorous criterion (100% typed shedding + bounded queue-wait + no starvation) after
  concluding the original ratio is architecture-inappropriate for an admission-by-queueing
  gateway. Any statement that "admission control meets its overload SLO" must carry this
  context; the original target is not deleted from the record, it is disclosed as REFUTED.
- **Single-host co-location.** Client, gateway, and engine shared one machine over loopback in
  every CPU benchmark. Host-level noise (a documented tail-cluster anomaly in the E1-mock
  direct arm; large run-to-run variance in the E1-llama.cpp arm) is a real, disclosed
  confound, not eliminated by dedicated hardware.
- **PostgreSQL usage accounting is not composed in the quickstart or Scenario A's evidence**
  (deviation D-001). infergate itself landed real usage accounting (`IG-T008`, 2026-07-11,
  0.0000% settle variance, crash-safe, idempotent by request ID) — but Scenario A's compose
  stack has not been re-pinned to include it since I2 was accepted with this deviation
  recorded. The usage-accounting *correctness* evidence that exists (`IG-T008`'s own tests) is
  real; it is simply not wired into this repo's own composed demonstration yet.

## 5. Design-only, not built

- **Multi-region deployment and multi-replica-gateway HA** exist only as design notes
  (`infergate docs/adr/0007-multi-gateway-design.md` and related architecture docs) — never
  built, never tested, no evidence exists.
- **SGLang and PD-disaggregation** appear only at the study/benchmark-comparison level (if at
  all) — no implementation, no measurement.
- **No CUDA or GPU-kernel work of any kind** exists anywhere in this program.

## 6. Open-source contribution track

- **The OSS minimum completion target is not fully met at this release.** What is real: a
  clean local build+test of `llm-d-router` (116/121 testable packages green), a genuine local
  reproduction of an unaddressed gap in a real upstream issue (#1625's `fairness_id`
  cardinality subset, with a runnable Go test as evidence), and a drafted, ready
  issue-comment. **The comment has not been posted** — posting requires user review and
  action (a standing program gate: "the user reviews every submission before posting"), which
  has not happened as of this release. This is the documented contingency per
  `09-open-source-track.md` §4 and `oss/log.md`'s 2026-07-12 framing note, not a claimed
  public interaction. No public link is claimed anywhere in this portfolio for this thread.

## 7. Process gaps found and corrected during this release (I8), disclosed for completeness

- `evidence/i1/` (contract-compatibility archiving) did not exist until this release, despite
  I2-I7 evidence citing I1 status throughout — corrected (IL-T008 consistency pass).
- `reports/` sat empty from 2026-07-10 through I3-I7 despite those milestones' own checklists
  citing inferbench's and fleetlab's reports extensively by path — corrected (IL-T009).
- I2-I7 acceptance review by the user remains **pending** for I3 onward at the time of this
  I8 release (I2 and I3 are accepted; I4-I7 and I6 are recorded with acceptance review
  pending, per each milestone's own status line in `docs/tasks.md`). I8 itself is likewise
  marked **acceptance-review-pending** in this same release — nothing in this document should
  be read as claiming user sign-off that has not happened.
