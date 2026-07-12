#!/usr/bin/env bash
# Scenario A quickstart: poll the gateway + mock-backend /healthz until both
# are up (or time out). Pure orchestration — no runtime logic, just a curl
# poll loop extracted from run.sh's wait_healthy() so the quickstart doc has
# a real script to reference instead of an inline snippet duplicated in two
# places.
#
# Usage: scenarios/a/wait-ready.sh [timeout-seconds]
set -euo pipefail

TIMEOUT=${1:-20}
GW=http://127.0.0.1:18080
MOCK=http://127.0.0.1:18081
DEADLINE=$((SECONDS + TIMEOUT))

until curl -fsS "$GW/healthz" >/dev/null 2>&1 && curl -fsS "$MOCK/healthz" >/dev/null 2>&1; do
  if [ "$SECONDS" -ge "$DEADLINE" ]; then
    echo "wait-ready: stack did not become healthy within ${TIMEOUT}s" >&2
    exit 1
  fi
  sleep 0.2
done

echo "wait-ready: gateway ($GW) and mock-backend ($MOCK) both healthy"
