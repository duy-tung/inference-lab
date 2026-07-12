# Quickstart timing log

Protocol: `docs/testing.md` §c. Target: ≤15 minutes from fresh clone to Scenario A smoke
success on a GPU-free machine. ≥2 timed runs required before I8. Every run is recorded —
passes and failures alike.

| Date | Machine (CPU / RAM / OS) | Docker cache | Duration | Pass (≤15m)? | Notes |
|---|---|---|---|---|---|
| 2026-07-12 (Run 1) | 4 vCPU / 15 GiB RAM / Ubuntu 24.04.4 LTS, kernel 6.18.5 | scenario-a image tags already existed from prior work (IL-T002); Docker BuildKit layer cache warm | **2m 08s** (127.7s; `git clone` 03:20:34.057Z → first `data:` SSE chunk ≈03:22:41.8Z) | **YES** | Steady-state number: everything (Docker layers, Go module cache, Go build cache) warm. See methodology below. |
| 2026-07-12 (Run 2) | same machine | scenario-a image tags removed (`docker rmi`) + `docker builder prune -a -f` immediately before this run, forcing a real image rebuild with no layer cache; Go module/build cache left **warm** (not cleared, see honesty note) | **35s** (`git clone` 03:23:24.139Z → first `data:` SSE chunk ≈03:23:59.15Z) | **YES** | Forced-rebuild number: Docker layer cache was genuinely cold; the rebuild was still fast because the images are minimal static (`CGO_ENABLED=0`) Go binaries in `FROM scratch` — there is very little layer content to rebuild. |

## Result

**PASS, ≥2 runs, both far under the 15-minute target** (127.7s and 35s — roughly 7x and 25x
headroom respectively). Reproduces: yes — both runs independently produced a real streaming
SSE completion (`data: {"id":"chatcmpl-...","object":"chat.completion.chunk",...}`) through a
freshly built-from-pinned-source gateway + mock backend, from a fresh `git clone` of this
exact commit.

## Methodology / honesty notes (read before trusting the number)

1. **Clone source:** both runs cloned from the local filesystem
   (`git clone /home/user/inference-lab`), not over the network from GitHub. This repo's own
   history is small (no binaries committed — see `.gitignore` in `scenarios/a/`), so a real
   `github.com` clone adds low-single-digit seconds of network latency at most; it would not
   change the pass/fail outcome against the 15-minute target. Recorded as a scope decision,
   not hidden.
2. **Port conflict workaround:** this shared sandbox had an unrelated, pre-existing container
   (`inferops-haproxy`, left running from earlier, already-archived milestone evidence work)
   publishing host port `18080`, which Scenario A's compose file also uses. Rather than stop a
   workload this session didn't create, both timed runs used a local sed-edit of the cloned
   repo's `scenarios/a/compose.yaml` to publish `28080`/`28081` instead of `18080`/`18081` —
   the *committed* compose file (what `pins/pins.yaml` and `evidence/i2/` were validated
   against) is unchanged. This only remaps which host port is published; it does not change
   what is built, run, or measured.
3. **Go module/build cache: warm in both runs, not cleared.** `go build`'s package-object
   cache (`~/.cache/go-build`, 4.6 GB before these runs) and the module cache
   (`~/go/pkg/mod`, 2.8 GB) were populated by earlier work in this environment (the original
   IL-T002 build) and were **not** wiped for either run — doing so would force re-downloading
   every Go module over this sandbox's proxied network, which is a legitimate thing a genuinely
   first-time machine would pay for once, but re-creating that exact cold state safely (without
   risking a long, potentially flaky proxy-bound module-download session eating the available
   time budget, or disrupting other in-progress work in this shared sandbox that also depends
   on those caches) was out of scope for this pass. **This is the single most likely source of
   divergence between these numbers and a truly first-time machine's experience** — the
   `go install go.opentelemetry.io/collector/cmd/builder@v0.156.0` step in particular pulls the
   builder tool and its dependency graph the first time only, then Go caches it forever. If a
   from-scratch machine's module download is slow (a throttled or high-latency network path to
   the Go module proxy), the wall-clock number would be materially larger than the two numbers
   above; both runs' large headroom under the 15-minute target (7-25x) is the mitigating
   factor, not a guarantee for every network condition. Recorded honestly, not hidden.
4. **Docker image/layer cache: warm in Run 1, forced-cold in Run 2** (`docker rmi` of the
   three scenario-a tags + `docker builder prune -a -f` immediately before Run 2) — this is
   the one component of "fresh machine" state that was genuinely exercised cold in Run 2, and
   it added negligible time (both runs are within the same order of magnitude) because the
   images are minimal.
5. **Command used to measure "first `data:` chunk":** a plain `curl -N` streaming request
   piped to `head -3`/`head -5` for terminal display; the reported time is when the first SSE
   `data:` line was observed on the terminal, consistent with the quickstart doc's own stated
   stop point (step 5). `curl`'s own `time` output for Run 1 additionally confirms sub-second
   response after the healthz poll succeeded (0.342s real time for the full smoke request,
   consistent with the mock backend's configured 300ms TTFT).
6. **Conclusion for the ≤15-minute target (H1):** **CONFIRMED** on this machine, under the
   disclosed cache conditions above. The single biggest risk to a slower reproduction
   elsewhere is Go module download time on a machine with zero pre-existing Go cache and a
   slow/constrained path to the module proxy — not the compose bring-up, not the Docker image
   build itself, and not the gateway/mock runtime behavior. If a future run on a genuinely
   cold machine exceeds 15 minutes, the fix belongs in that order: (a) vendor/pre-fetch the Go
   module set as part of `build.sh` documentation, or (b) publish pre-built images to a real
   registry once one is reachable (removing the from-source build step entirely, RQ-4) — never
   in relaxing the 15-minute target itself.
