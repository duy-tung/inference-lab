# Compatibility — what is proven together

This directory holds the compatibility matrices: per integration milestone, exactly which
released versions are **proven together**, each row citing archived evidence. Together with
`pins/pins.yaml` (the ledger), this is the single source of "what is proven together" for
all repos and for the I8 reproducibility audit. Upkeep: task IL-T008 (ongoing, per consumed
release).

## Rules

1. **No unproven "compatible" claims.** A row exists only when the owning milestone's
   acceptance criteria were demonstrated and reviewed; every row links to `evidence/i<N>/`.
2. **Rows are pinned.** Every cell is a tag/digest/commit/revision that appears in
   `pins/pins.yaml` (validator green).
3. **Pin bumps invalidate.** Bumping any component invalidates the affected rows'
   "proven together" status until the owning scenario is re-run; superseded rows stay,
   annotated (evidence immutability, ADR-0002).
4. **Re-run triggers** (from `docs/integration.md`): every contract release re-runs I1;
   contract **MAJOR** ⇒ I1 re-run before any scenario is re-claimed; contracts v1.0.0 I1
   re-run is an I6 prerequisite.

## Benchmark comparability rule (normative — printed here on purpose)

> Results are comparable only when model revision, quantization, tokenizer, engine
> version+flags, hardware, driver/CUDA, workload version+seed, and warm-up policy all match,
> or the difference is the single declared experimental variable.

Any archived benchmark comparison that does not satisfy this rule is not comparable and must
not be presented as a comparison.

## Matrix format

One row per (milestone, proven set): milestone; contracts tag; infergate image digest; mock
image digest; inferbench version; engine version/commit; model revision+quantization;
inferops bundle; fleetlab release; date proven; evidence link. Empty cells = not part of that
milestone's proven set. The living matrix: [`matrix.md`](matrix.md).
