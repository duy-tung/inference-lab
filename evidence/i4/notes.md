# evidence/i4 — notes (I4 CPU-fallback record, IL-T004, assembled 2026-07-12)

## 2026-07-12 — evidence-assembly session

- **Nature of this session:** assembly only, no new measurement. Two other agents were
  running compute-heavy compose stacks + llama.cpp on this host at the time; per instruction,
  no new benchmark/measurement run was started. Every number in `checklist.md` is a reference
  to already-published evidence: `evidence/i3/` (this repo, IL-T003/I3, accepted 2026-07-11 —
  commit `61132b2`), infergate `docs/implementation-notes.md` (IG-T005 log entry, commit
  `74f2372`), and inferbench `docs/evidence/ib-t010/` (IB-T010 E1, commit `6a3fb53`).
- **Why no `logs/`/`raw/`/`reports/` subdirectories exist here:** nothing new was run, so
  there is nothing to log/capture beyond the checklist + the pins snapshot. This differs from
  `evidence/i2/` and `evidence/i3/`, which each archive a real composed-stack run's logs, raw
  events, and generated reports. The convention in `docs/interfaces.md` §4 lists those
  directories as part of the standard layout; they are omitted here because they would be
  empty, not because the convention was skipped.
- **Path-existence spot check performed before writing the checklist** (all confirmed present
  on disk before citing them): `evidence/i3/checklist.md`, `evidence/i3/raw/runs/{chat-short-cpu-gw,
  chat-short-cpu-direct,shared-prefix-cpu,cancel-mid-stream-cpu,cancel-mid-stream-cpu-attempt1,
  chat-short-failover}/`, `evidence/i3/reports/i3-*.report.md`, `evidence/i3/raw/failover-timeline.json`,
  `evidence/i3/raw/mock-debug-state-failover.json`; infergate `docs/implementation-notes.md`
  (IG-T005 entry + evidence-links table row); inferbench `docs/evidence/ib-t010/benchmark-report-1.md`,
  `e1-mock-overhead.json`, `e1-llamacpp-overhead.json`, `ib-t010-e1-{mock,llamacpp}-{direct,gateway}.report.md`.
- **Key honesty finding during assembly:** the inferbench IB-T010 E1 gateway-overhead
  comparison (`checklist.md` §2.3) was produced against a **later** infergate commit
  (`6827d8c`) than the one this repo pins for Scenario B/I3 (`74f2372`), and its llama.cpp
  arm used different engine flags (`-np 1 -c 4096`, single slot) than Scenario B's
  (`-np 2 -c 8192`). Both facts are recorded in `checklist.md` §2.3/§4 so the comparison is
  not misrepresented as proof about this repo's own pinned `infergate-binary`/engine-flag
  combination — it is cited as independent sibling-repo evidence of the same underlying
  claim (gateway overhead, llama.cpp engine), consistent with this repo's evidence-archivist
  role for evidence it did not itself produce (the same pattern as the I1/I5/I7 archiving
  duties in `docs/integration.md`).
- **No new `pins/pins.yaml` artifact entries were added** for the two sibling-repo commits
  above (infergate@`6827d8c`, inferbench@`6a3fb53`) — see `checklist.md` §4 for the
  rationale (they were not built/verified by this repo's own scenario tooling).

## Deviations affecting this evidence

- **CPU-fallback deviation (D-005, `docs/implementation-notes.md`)** — I4's normative GPU
  acceptance is not claimed; the llama.cpp variant (I3) plus infergate IG-T005 and inferbench
  IB-T010 evidence stands in as the measured baseline, per `scenarios/c/README.md`'s own
  contingency clause and program charter §7 (`portfolio-planning/00-program-charter.md`).
- Deviations already recorded against the underlying I3 evidence (D-004, A-007, A-008) still
  apply unchanged to everything cited under `checklist.md` §2.1/§2.2(b)/§2.4 — see
  `evidence/i3/notes.md` for the full accounting. Nothing here supersedes or re-derives them.

## Defects filed upstream

None filed by this evidence-assembly task. Open, unreproduced observations already on file
(I3's cancellation log-census discrepancy) are unchanged — see `evidence/i3/checklist.md`
item 5 and `evidence/i3/notes.md`.
