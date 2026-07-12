# Postmortems

Postmortems from the failure campaign (I7) and any real incident during scenario work.
Target: **≥2 published** in the standard format by I7 (`postmortems/pm-001.md`,
`pm-002.md`, …). Fault scenarios are defined by Contract 6 (12 scenarios); execution is
owned by inferops, evidence and postmortems live here (IL-T007).

**Status (2026-07-10): empty** — no campaigns run yet. Template below is normative.

**Status (2026-07-12):** 3 published (`pm-001.md` scenario 4 slow client — the campaign's one
real defect-shaped finding; `pm-002.md` scenario 2 backend killed after first token — clean
textbook semantics; `pm-003.md` scenario 9 usage database failure — cleanest resilience
result), exceeding the ≥2 minimum. Built from the inferops fault campaign
(`/home/user/inferops`, commits `bfca054`/`a1e0af5`/`a07fd2f`); see `evidence/i7/checklist.md`.

## Standard format (every postmortem, no exceptions)

1. **Timeline from real metrics** — timestamps sourced from archived metrics/traces, not
   from memory or narrative. Every timeline entry cites its metric/trace artifact.
2. **Detection gap** — when the system knew vs when the operator knew; what alert existed,
   fired, or was missing.
3. **Root cause** — the defect or condition, stated plainly; routed to the owning repo as a
   defect report where applicable.
4. **Mitigation** — what restored service, and what evidence shows recovery.
5. **Action items** — each with an owner repo and a follow-up reference (defect report,
   contract change, runbook update).

Caveat carried from the study track: **quality regressions can pass latency SLOs** — a
postmortem's "recovered" claim must state what was and was not measured.

## Template file

Use [`template.md`](template.md) as the starting point for `pm-NNN.md`.
