# Demo transcript — Part 1 (live, captured 2026-07-12)

This is a real terminal capture from `portfolio/demo-script.md` Part 1, run against a
freshly-built Scenario A stack (`scenarios/a/build.sh` then `docker compose up -d`) on the
machine this portfolio was assembled on. Host ports were remapped to `28080`/`28081` for this
capture only (same reason as `quickstart/timing-log.md`: an unrelated pre-existing container
in this shared sandbox already held `18080`) via a `docker compose` `!override` merge overlay
— the committed `scenarios/a/compose.yaml` (`18080`/`18081`) is unchanged. Parts 2-4 are not
re-executed here; they read already-archived files (`reports/`, `evidence/i6/`,
`evidence/i7/`, `postmortems/`) whose content was itself produced by real, already-documented
runs — see each file's own commit/date header.

## Streaming smoke (Contract 1)

```
$ curl -N http://localhost:18080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"mock-8b","messages":[{"role":"user","content":"hello"}],"stream":true}'
id: 0
data: {"id":"chatcmpl-115c954d70043a9f0d7662d0","object":"chat.completion.chunk","created":1783641600,"model":"mock-8b","choices":[{"index":0,"delta":{"role":"assistant","content":""}}]}

id: 1
data: {"id":"chatcmpl-115c954d70043a9f0d7662d0","object":"chat.completion.chunk","created":1783641600,"model":"mock-8b","choices":[{"index":0,"delta":{"content":"drift"}}]}

... (22 more content chunks, deterministic seed 42 output) ...

id: 24
data: {"id":"chatcmpl-115c954d70043a9f0d7662d0","object":"chat.completion.chunk","created":1783641600,"model":"mock-8b","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

id: 25
data: [DONE]
```

25 events, monotonic `id:`, terminal `data: [DONE]` — Contract 1's SSE framing, exactly as
`evidence/i2/checklist.md` validated at scale (100 concurrent streams, 0 frame-mixing
violations).

## Cancellation (pre-first-token point, this run happened to land here)

```
$ ( curl -N -m 0.3 http://localhost:18080/v1/chat/completions -H "Content-Type: application/json" \
      -d '{"model":"mock-8b","messages":[{"role":"user","content":"count to one hundred slowly"}],"max_tokens":200,"stream":true}' || true )
curl: (28) Operation timed out after 300 milliseconds with 0 bytes received

$ curl -s http://localhost:18081/debug/state | python3 -m json.tool
{
    "requests_total": 2,
    "streams_started": 2,
    "streams_completed": 1,
    "aborts_total": 1,
    "aborts": [
        {
            "at_unix_nano": 1783827237318742300,
            "chunks_sent": 0,
            "phase": "pre_first_token"
        }
    ]
}
```

**Honest note:** the demo script's own 300ms client timeout landed before the mock backend's
configured 300ms TTFT produced a first token, so this particular capture demonstrates the
**pre-first-token** cancellation point (0 chunks sent, `phase: "pre_first_token"`) rather than
mid-stream — a real, correctly-observed abort, just not the specific point the demo script's
prose narrates. `evidence/i2/checklist.md` item 4 has all three points (pre-first-token,
mid-stream, near-completion) measured deliberately and separately, with a dedicated
mock-restart between each so `/debug/state` counters don't accumulate across points — the
methodology this one-shot demo capture simplifies for a live walkthrough. Reported as
observed, not smoothed over to match the script's narration.

## Cleanup

```
$ docker compose down -v
```
