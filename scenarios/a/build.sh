#!/usr/bin/env bash
# Scenario A build: produce the pinned images + host-side inferbench binary.
#
# READ-ONLY source consumption: everything is extracted via `git archive
# <pinned commit>` — never a working tree, never a source import. Pins:
#   infergate         5d69aeb11228b5dcfbaca10c2e57f0a24603b8f9
#   inferbench        caa507498fa417b3e4f5cdb0285737ef3f36856e
#   serving-contracts 8d81492 (v0.2.0 tag pending; kit used for validation)
#   otel collector    v0.156.0 (ocb build, see otelcol-builder-manifest.yaml
#                     and deviation D-003)
#
# Registry access is policy-blocked in this environment (deviation D-002):
# binaries are compiled on the host (toolchain recorded) and packed into
# FROM-scratch images. Outputs land in .build/ (gitignored):
#   gateway, mock-backend, otelcol-scenario-a, inferbench,
#   workloads/            (canonical inferbench workload files, extracted)
#   contracts-bundle/     (pinned contracts bundle incl. validation kit)
#   build-info.txt        (pins, toolchain, binary sha256s, image digests)
#
# Usage: scenarios/a/build.sh [infergate-repo] [inferbench-repo] [contracts-repo]
set -euo pipefail

INFERGATE_PIN=5d69aeb11228b5dcfbaca10c2e57f0a24603b8f9
INFERBENCH_PIN=caa507498fa417b3e4f5cdb0285737ef3f36856e
CONTRACTS_PIN=8d81492
OTELCOL_VERSION=0.156.0

INFERGATE_REPO=${1:-/home/user/infergate}
INFERBENCH_REPO=${2:-/home/user/inferbench}
CONTRACTS_REPO=${3:-/home/user/serving-contracts}

HERE=$(cd "$(dirname "$0")" && pwd)
BUILD="$HERE/.build"
mkdir -p "$BUILD"
INFO="$BUILD/build-info.txt"

{
  echo "scenario-a build $(date -u +%FT%TZ)"
  echo "infergate pin:  $INFERGATE_PIN"
  echo "inferbench pin: $INFERBENCH_PIN"
  echo "contracts pin:  $CONTRACTS_PIN (v0.2.0 tag pending; v0.1.0 released)"
  echo "otel collector: v$OTELCOL_VERSION (ocb build per otelcol-builder-manifest.yaml)"
  echo "go toolchain:   $(go version)"
} >"$INFO"

# --- extract pinned sources (read-only) --------------------------------------
SRC="$BUILD/src"
rm -rf "$SRC" && mkdir -p "$SRC/infergate" "$SRC/inferbench"
git -C "$INFERGATE_REPO" archive "$INFERGATE_PIN" | tar -x -C "$SRC/infergate"
git -C "$INFERBENCH_REPO" archive "$INFERBENCH_PIN" | tar -x -C "$SRC/inferbench"

rm -rf "$BUILD/contracts-bundle" && mkdir -p "$BUILD/contracts-bundle"
git -C "$CONTRACTS_REPO" archive "$CONTRACTS_PIN" | tar -x -C "$BUILD/contracts-bundle"

# Canonical workload files (inferbench owns them; consumed as released files).
rm -rf "$BUILD/workloads" && mkdir -p "$BUILD/workloads"
cp "$SRC/inferbench/workloads/"*.json "$BUILD/workloads/"

# --- compile (static, CGO off; FROM-scratch images) --------------------------
(cd "$SRC/infergate" && CGO_ENABLED=0 go build -trimpath -o "$BUILD/gateway" ./cmd/gateway)
(cd "$SRC/infergate" && CGO_ENABLED=0 go build -trimpath -o "$BUILD/mock-backend" ./cmd/mock-backend)
(cd "$SRC/inferbench" && CGO_ENABLED=0 go build -trimpath -o "$BUILD/inferbench" ./cmd/inferbench)

# OTel Collector via the official builder (ocb), pinned manifest.
OCB="$BUILD/ocb"
if [ ! -x "$OCB" ]; then
  GOBIN="$BUILD" GOFLAGS=-mod=mod go install "go.opentelemetry.io/collector/cmd/builder@v$OTELCOL_VERSION"
  mv "$BUILD/builder" "$OCB"
fi
OTELWORK="$BUILD/otelcol-work"
mkdir -p "$OTELWORK"
cp "$HERE/otelcol-builder-manifest.yaml" "$OTELWORK/manifest.yaml"
(cd "$OTELWORK" && CGO_ENABLED=0 "$OCB" --config manifest.yaml >/dev/null)
cp "$OTELWORK/build/otelcol-scenario-a" "$BUILD/otelcol-scenario-a"

{
  echo "binary sha256:"
  (cd "$BUILD" && sha256sum gateway mock-backend inferbench otelcol-scenario-a | sed 's/^/  /')
} >>"$INFO"

# --- images -------------------------------------------------------------------
docker build -q -f "$HERE/Dockerfile.gateway" -t "scenario-a/gateway:${INFERGATE_PIN:0:7}" "$BUILD" >/dev/null
docker build -q -f "$HERE/Dockerfile.mock" -t "scenario-a/mock-backend:${INFERGATE_PIN:0:7}" "$BUILD" >/dev/null
docker build -q -f "$HERE/Dockerfile.otelcol" -t "scenario-a/otel-collector:$OTELCOL_VERSION" "$BUILD" >/dev/null

{
  echo "image digests (local image IDs — content-addressed config digests;"
  echo "no registry hosting yet, RQ-4; re-record RepoDigests once pushed):"
  for img in "scenario-a/gateway:${INFERGATE_PIN:0:7}" \
             "scenario-a/mock-backend:${INFERGATE_PIN:0:7}" \
             "scenario-a/otel-collector:$OTELCOL_VERSION"; do
    echo "  $img $(docker image inspect --format '{{.Id}}' "$img")"
  done
} >>"$INFO"

echo "build complete:"
cat "$INFO"
