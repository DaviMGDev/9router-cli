#!/usr/bin/env bash
# E2E Test: Ping & Status
set -euo pipefail

CLI="${PROJECT_ROOT}/.venv/bin/python -m ninerouter_cli.cli"

echo "  --- Test: ping command ---"
assert_exit_code 0 "${CLI} ping" "ping server responds 0"

PING_JSON=$(${CLI} --json ping)
assert_eq "true" "$(echo "$PING_JSON" | grep -q '"status": "ok"' && echo "true" || echo "false")" "ping json contains status ok"

echo "  --- Test: status command ---"
assert_exit_code 0 "${CLI} status" "status server responds 0"

STATUS_JSON=$(${CLI} --json status)
assert_eq "true" "$(echo "$STATUS_JSON" | grep -q '"keys_count"' && echo "true" || echo "false")" "status json has keys_count"
