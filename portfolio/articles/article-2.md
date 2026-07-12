# Correct Cancellation, Retry and Token Accounting for Streaming Inference

*Part of the inference-systems portfolio. Evidence: `evidence/i2/checklist.md`, `evidence/i3/checklist.md`, `infergate docs/usage-invariants.md`, `infergate docs/adr/0003-transaction-boundaries.md`, `infergate docs/adr/0004-retry-budget.md`.*

## Why streaming makes this hard

A non-streaming request either completes or it doesn't — accounting is a single number at the
end. A streaming completion is different: tokens leave the gateway continuously, the client
can disconnect at any point along that stream, and by the time the gateway notices the
disconnect, the engine may have already produced (and be billable for) tokens the client never
received on the wire. Getting this right means answering three questions precisely, for every
point along the stream: *did the engine actually stop producing tokens, and how fast? what
happened to the tokens produced before the stop? and if this exact request is retried or
redelivered, does anything get double-counted?*

## Cancellation: measuring the propagation, not assuming it

This portfolio's cancellation claim is deliberately three-part, because "cancellation works"
is not one fact — it's at least three: does it work before the first token, mid-stream, and
near completion, and does the *engine itself* observably stop (not just the HTTP connection
closing)?

Against the composed stack — real gateway, real mock engine, `evidence/i2/checklist.md` item
4 — all three points were measured directly from raw abort-timing data:

| Cancellation point | Aborts observed | Abort-to-release delta |
|---|---|---|
| pre-first-token | 30/30 | 0.247 / 0.402 / 0.573 ms |
| mid-stream | 29 aborts + 1 raced completion | 0.310 / 0.413 / 0.724 ms |
| near-completion | 12 aborts + 187 completed (+1 race) | 0.318 / 0.367 / 0.638 ms |

All comfortably inside the declared 100ms bound, and the near-completion point's 188+12=200
accounting is a conservation check, not a rounding — nothing leaked.

Against the **real, pinned llama.cpp engine**, the composed-stack test measured **one** point
(mid-stream): 20/20 canceled, engine-observed release deltas from −32.2ms to +83.9ms against a
2.5s bound (`evidence/i3/checklist.md` item 5). A separate, adapter-level test (infergate's own
`IG-T005`) exercises all three points directly against a real `llama-server` process — queued
2.6µs-645µs, pre-first-token 0.77s-2.19s, mid-stream 1.25ms-5.24ms — but that test ran against
an **unpinned, locally-authored random-weight GGUF**, not the portfolio's pinned
Qwen2.5-1.5B-Instruct model. **The honest summary: 3-point, composed-stack, pinned-model
cancellation is proven on the mock engine; on the real engine, one composed-stack point plus a
separate adapter-level 3-point test on a different (unpinned) model together triangulate the
same conclusion, but do not equal one clean 3-point/pinned-model/composed-stack result.** No
GPU/vLLM cancellation claim exists anywhere in this program (gate G6 deferred).

## Accounting: what a ledger row actually means

`infergate`'s usage-settlement design (`IG-T008`, `docs/usage-invariants.md`) answers the
double-counting question with a specific, testable set of invariants, not a general assurance:

- **Exactly one ledger row per *dispatched* request**, never per HTTP call received. A request
  rejected before dispatch (auth failure, validation failure, pre-dispatch cancel, a drain
  rejection) incurred zero backend cost and produces zero rows — the ledger records what
  actually happened to a backend, not every request the gateway ever saw.
- **`request_id` is the sole de-duplication key**, enforced as the ledger's primary key via
  `INSERT ... ON CONFLICT (request_id) DO NOTHING`. This single mechanical fact is what makes
  three separate correctness properties fall out for free, each with its own test: redelivery
  never double-counts (`TestWriterDuplicateDeliveryNoDoubleCount`), delivery order is
  irrelevant (`TestWriterConcurrentReorderedDeliveryAllLand`, 100 concurrent records from 10
  goroutines), and crash/restart recovery is idempotent even when the replacement writer
  replays the *entire* original backlog (`TestWriterCrashRestartIdempotentRecovery`, 40 records
  in, exactly 40 rows out).
- **Estimate vs. settle are two independent numbers, never conflated**: the ledger records both
  the pre-dispatch estimate (for quota arithmetic) and the post-stream settled count (for
  billing), and measured input-token settle variance came back at **0.0000%** against
  calibrated mock traffic, with output settlement **byte-exact** against the upstream
  `completion_tokens` field.
- **Tokens emitted before a cancel are billable** — Contract 1's own rule, and exactly what the
  cancellation-point conservation check above (188+12=200) is verifying isn't silently dropped
  at the accounting layer, not just at the transport layer.

## Retry and quota: not the gateway's problem to solve twice

Two-sided per-tenant token-bucket quotas (`IG-T009`) enforce admission using the same
estimate-then-correct-at-settlement discipline: a typed `429 rate_limited` response with
`Retry-After` fires exactly when a bucket is exhausted (live-verified: RPM=2 burst → the 3rd
request 429s, `Retry-After: 30`, `inference_sheds_total{reason="tenant_rate_limit"}`
increments), and headroom is refunded once the true settled cost is known to be less than the
estimate. A DB outage during settlement doesn't lose billing data either: a 50-record backlog
enqueued during a real container stop took 47.95µs to accept, and the backlog drained 765ms
after recovery — accounting degrades to "delayed," never to "lost" or "duplicated."

## The throughline

None of this is a single "cancellation works" or "billing is correct" assertion. It's a
decomposed set of measured properties — three cancellation points, four idempotency
invariants, an estimate/settle pair, a DB-outage recovery number — each with its own test or
raw-event file, because streaming inference has enough distinct failure surfaces that a single
end-to-end "it works" claim would hide exactly the kind of gap (the llama.cpp scope nuance
above) that this program's own reproducibility audit exists to catch.
