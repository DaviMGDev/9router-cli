#!/usr/bin/env bash
# E2E Test: API Keys, Settings & Tools
set -euo pipefail

CLI="${PROJECT_ROOT}/.venv/bin/python -m ninerouter_cli.cli"
TEST_KEY="e2e-test-agent-key"

echo "  --- Test: keys list ---"
assert_exit_code 0 "${CLI} keys list" "keys list responds 0"

echo "  --- Test: keys create and delete ---"
CREATE_OUT=$(${CLI} --json keys create "${TEST_KEY}")
assert_eq "true" "$(echo "$CREATE_OUT" | grep -q 'sk-' && echo "true" || echo "false")" "keys create returns an sk- token"

assert_exit_code 0 "${CLI} keys delete ${TEST_KEY} --yes" "keys delete succeeds"

echo "  --- Test: settings get ---"
assert_exit_code 0 "${CLI} settings get" "settings get responds 0"

echo "  --- Test: tunnel status ---"
assert_exit_code 0 "${CLI} tunnel status" "tunnel status responds 0"

echo "  --- Test: tools status ---"
assert_exit_code 0 "${CLI} tools status" "tools status responds 0"
