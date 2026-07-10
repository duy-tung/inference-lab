# Non-Goals — inference-lab

These are hard exclusions, checked at every review gate. A pull request that violates any of
them is rejected regardless of how convenient the violation would be.

## 1. No runtime logic

This repo contains no services, no daemons, no request-path code. It is declarative
orchestration (compose files, scripts, pinned versions) plus documentation and evidence.
If a piece of logic is needed at runtime, it belongs to infergate, inferbench, fleetlab,
inferops, or serving-contracts — never here.

## 2. No duplicated capability

One gateway (infergate), one load-generation system (inferbench), one deployment stack
(inferops) exist in the whole program. inference-lab must never grow a second copy of any of
them — no "small helper proxy", no "quick load script" that duplicates inferbench, no ad-hoc
manifests that duplicate inferops. Glue scripts here orchestrate; they do not measure, route,
or deploy on their own authority.

## 3. No source checkouts of sibling repos

Never check out another repo's source to build it. Never vendor another repo's code. This repo
consumes **released artifacts only**: images by digest, binaries by version, contract bundles
by SemVer tag, config bundles by tag. If a needed artifact has no release, that is a blocking
request to the owning repo, not a reason to build from source here.

## 4. No local fixes

Runtime defects discovered during scenario runs are routed to the owning repo as
evidence-backed defect reports. This repo waits for the next release and bumps its pin.
Never patch a component here; never "fix it locally to make the demo work." A failed scenario
run is itself evidence — record it.

## 5. No brokers in the inference path

No Kafka/NATS/Redis or any broker appears in any scenario's synchronous inference request path
(program-wide rule; scenario compose files are reviewed against it).

## 6. No unproven claims

- Never claim tests/benchmarks/deployments succeeded without command output or artifacts to
  point at.
- Every number carries provenance (measured / source-reported / assumed) and a date.
- Invalid benchmark runs are invalidated, never published.
- No compatibility-matrix row without archived milestone evidence.
- This repo never generates new performance claims — it archives copies with provenance.

## 7. No GPU requirement for the core

Basic development, CI, the quickstart, and Scenario A are GPU-free. Any GPU session requires a
written hypothesis + full config manifest + auto-stop script + budget alert (program envelope
~$150–250 total, as of 2026-07 — user-confirmable).

## 8. Out-of-scope engineering (program-wide honesty boundary)

Not built anywhere in the portfolio, therefore never demonstrated here: CUDA/kernel work,
scheduler rewrites in upstream projects, multi-region topologies (design notes only),
fleet-scale production claims, a full agent runtime. The honest-limitations statement
(`portfolio/limitations.md`, published at I8) keeps this list current.
