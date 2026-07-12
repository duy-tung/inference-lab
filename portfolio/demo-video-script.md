# Demo video script — 5-minute class

Condensed narration track for a screen recording following `portfolio/demo-script.md`.
Timings are targets, not measured recording durations (no video was recorded in this text-only
session — this is the script that would drive one; see `portfolio/limitations.md` if this
file is read as a claim that a recording exists).

| Time | Screen | Narration |
|---|---|---|
| 0:00-0:20 | Terminal, `git clone` + `build.sh` running | "This is inference-lab — six repos, one gateway, one benchmark tool, one capacity simulator, one ops repo, contracts tying them together. Everything you'll see is built from pinned source, live." |
| 0:20-1:00 | `docker compose up -d`, streaming curl | "Contract 1 — an OpenAI-compatible streaming completion through a real gateway to a real backend. SSE framing, terminal DONE. Validated at scale — 100 concurrent streams, zero frame-mixing — in evidence/i2." |
| 1:00-1:40 | Cancellation curl + `/debug/state` JSON | "Cancel a stream, and check the *engine* saw it — not just that the socket closed. Sub-millisecond release, every point measured separately. And here's the honest version: on the real llama.cpp engine, that's one composed-stack point proven, not three — the audit caught that gap, so the demo says it out loud." |
| 1:40-2:40 | `reports/benchmark-report-1.md` scrolled | "How much does the gateway cost? Two milliseconds at p95, confirmed. Does admission control survive 5x overload? The original target was refuted — twice — and the program re-baselined the gate instead of hiding the miss. Both are in this file." |
| 2:40-3:40 | `evidence/i6/loop-report.md` scrolled | "The central story: a capacity prediction, applied for real, re-measured, published including where it needed correcting. +1.3% at the fitted rate. The 6-replica number was never measured — it's an extrapolation, and it says so, everywhere." |
| 3:40-4:15 | `evidence/i7/campaign-matrix.md` + `postmortems/pm-001.md` | "12 injected faults, 11 matched. The one that didn't — a slow-client write-deadline that should have fired and didn't — is the lead postmortem, not a footnote." |
| 4:15-4:45 | `oss/log.md` tail | "One sentence in the story isn't fully closed yet: the OSS contribution. Real local reproduction, drafted comment, not posted — that's disclosed plainly, not rounded up to 'contributed.'" |
| 4:45-5:00 | `evidence/i8/reproducibility-audit.md` | "Every number in this video traces to a pinned artifact. This file is the mechanical check of that — anything that didn't survive it isn't in this portfolio anymore." |
