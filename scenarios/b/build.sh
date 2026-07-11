#!/usr/bin/env bash
# Scenario B build: produce the pinned host binaries + contracts bundle.
#
# READ-ONLY source consumption: everything program-owned is extracted via
# `git archive <pinned ref>` — never a working tree, never a source import.
# Pins (also in pins/pins.yaml):
#   infergate         74f2372acea62645fa3c1d91689574ea9de7c589 (IG-T005: llama.cpp adapter + failover)
#   inferbench        69a5abc604a737235ea3f1721ddb6b7f64334289 (IB-T006: analysis + report)
#   serving-contracts v0.2.0 (tag at 484b44904233da569d76bafe4a4acb8d71bbbe4d)
#   llama.cpp         8f114a9b573b69035299f9b924047f53c1e22c7e (PREBUILT binary at
#                     /home/user/tools/llama.cpp/build/bin/llama-server — consumed
#                     read-only, commit verified here; not rebuilt)
#   model             /home/user/tools/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
#                     (sha256 verified here = the pinned model revision)
#
# Scenario B runs HOST PROCESSES, not containers (decision A-007 in
# docs/implementation-notes.md): binaries are compiled on the host
# (toolchain recorded) and the inferbench analysis package is used from the
# extracted pinned source via PYTHONPATH. Outputs land in .build/ (gitignored):
#   gateway, mock-backend, inferbench
#   src/inferbench/analysis/    (pinned analysis package source, via git archive)
#   workloads/                  (canonical inferbench workload files, for reference)
#   contracts-bundle/           (pinned v0.2.0 bundle incl. validation kit)
#   build-info.txt              (pins, toolchain, sha256s)
#
# Usage: scenarios/b/build.sh [infergate-repo] [inferbench-repo] [contracts-repo]
set -euo pipefail

INFERGATE_PIN=74f2372acea62645fa3c1d91689574ea9de7c589
INFERBENCH_PIN=69a5abc604a737235ea3f1721ddb6b7f64334289
CONTRACTS_PIN=v0.2.0
CONTRACTS_PIN_COMMIT=484b44904233da569d76bafe4a4acb8d71bbbe4d
LLAMACPP_COMMIT=8f114a9b573b69035299f9b924047f53c1e22c7e
LLAMACPP_DIR=/home/user/tools/llama.cpp
MODEL_FILE=/home/user/tools/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
MODEL_SHA256=6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e

INFERGATE_REPO=${1:-/home/user/infergate}
INFERBENCH_REPO=${2:-/home/user/inferbench}
CONTRACTS_REPO=${3:-/home/user/serving-contracts}

HERE=$(cd "$(dirname "$0")" && pwd)
BUILD="$HERE/.build"
mkdir -p "$BUILD"
INFO="$BUILD/build-info.txt"

# --- verify the prebuilt engine + model pins before anything else -------------
ACTUAL_LLAMA=$(git -C "$LLAMACPP_DIR" rev-parse HEAD)
if [ "$ACTUAL_LLAMA" != "$LLAMACPP_COMMIT" ]; then
  echo "FATAL: llama.cpp checkout is $ACTUAL_LLAMA, pinned $LLAMACPP_COMMIT" >&2
  exit 1
fi
echo "verifying model sha256 (~1 GiB, a few seconds)..."
ACTUAL_MODEL=$(sha256sum "$MODEL_FILE" | cut -d' ' -f1)
if [ "$ACTUAL_MODEL" != "$MODEL_SHA256" ]; then
  echo "FATAL: model sha256 $ACTUAL_MODEL != pinned $MODEL_SHA256" >&2
  exit 1
fi
LLAMA_VERSION=$(cd "$LLAMACPP_DIR/build/bin" && LD_LIBRARY_PATH=. ./llama-server --version 2>&1 | head -1)

{
  echo "scenario-b build $(date -u +%FT%TZ)"
  echo "infergate pin:  $INFERGATE_PIN"
  echo "inferbench pin: $INFERBENCH_PIN"
  echo "contracts pin:  $CONTRACTS_PIN (tag object at $CONTRACTS_PIN_COMMIT)"
  echo "llama.cpp:      $LLAMACPP_COMMIT (prebuilt, verified; llama-server '$LLAMA_VERSION')"
  echo "llama-server:   $LLAMACPP_DIR/build/bin/llama-server (sha256 $(sha256sum "$LLAMACPP_DIR/build/bin/llama-server" | cut -d' ' -f1))"
  echo "model:          $MODEL_FILE"
  echo "model sha256:   $MODEL_SHA256 (verified)"
  echo "go toolchain:   $(go version)"
  echo "python:         $(python3 --version) numpy=$(python3 -c 'import numpy;print(numpy.__version__)') jsonschema=$(python3 -c 'import importlib.metadata as m;print(m.version("jsonschema"))')"
} >"$INFO"

# --- extract pinned sources (read-only) ---------------------------------------
SRC="$BUILD/src"
rm -rf "$SRC" && mkdir -p "$SRC/infergate" "$SRC/inferbench"
git -C "$INFERGATE_REPO" archive "$INFERGATE_PIN" | tar -x -C "$SRC/infergate"
git -C "$INFERBENCH_REPO" archive "$INFERBENCH_PIN" | tar -x -C "$SRC/inferbench"

rm -rf "$BUILD/contracts-bundle" && mkdir -p "$BUILD/contracts-bundle"
git -C "$CONTRACTS_REPO" archive "$CONTRACTS_PIN" | tar -x -C "$BUILD/contracts-bundle"

# Canonical workload files (reference lineage for the CPU-adapted variants).
rm -rf "$BUILD/workloads" && mkdir -p "$BUILD/workloads"
cp "$SRC/inferbench/workloads/"*.json "$BUILD/workloads/"

# The pinned capability descriptor for the composed engine (evidence input).
cp "$SRC/infergate/internal/backend/llamacpp/llamacpp.backend-capability.json" "$BUILD/"

# --- compile (static, CGO off; host binaries — decision A-007) -----------------
(cd "$SRC/infergate" && CGO_ENABLED=0 go build -trimpath -o "$BUILD/gateway" ./cmd/gateway)
(cd "$SRC/infergate" && CGO_ENABLED=0 go build -trimpath -o "$BUILD/mock-backend" ./cmd/mock-backend)
(cd "$SRC/inferbench" && CGO_ENABLED=0 go build -trimpath -o "$BUILD/inferbench" ./cmd/inferbench)

{
  echo "binary sha256:"
  (cd "$BUILD" && sha256sum gateway mock-backend inferbench | sed 's/^/  /')
  echo "gateway config sha256 (config_version = v<seq>-<first 8 hex>):"
  (cd "$HERE/config" && sha256sum gateway-llamacpp.json gateway-failover.json | sed 's/^/  /')
  echo "analysis package: inferbench@$INFERBENCH_PIN analysis/src via PYTHONPATH (not pip-installed)"
} >>"$INFO"

echo "build complete:"
cat "$INFO"
