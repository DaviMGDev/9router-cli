#!/usr/bin/env bash
# E2E Test: Combos CRUD
set -euo pipefail

CLI="${PROJECT_ROOT}/.venv/bin/python -m ninerouter_cli.cli"
TEST_COMBO="e2e-cli-test-combo"

echo "  --- Test: combos list ---"
assert_exit_code 0 "${CLI} combos list" "combos list responds 0"

LIST_JSON=$(${CLI} --json combos list)
assert_eq "true" "$(echo "$LIST_JSON" | grep -q 'default' && echo "true" || echo "false")" "combos list contains default combo"

echo "  --- Test: combos create ---"
# Clean up any leftover test combo first
${CLI} combos delete "${TEST_COMBO}" --yes 2>/dev/null || true

assert_exit_code 0 "${CLI} combos create ${TEST_COMBO} -m ag/gemini-3.8-flash -m ag/gemini-3.8-flash-low" "create combo with 2 models succeeds"

echo "  --- Test: combos get ---"
assert_exit_code 0 "${CLI} combos get ${TEST_COMBO}" "get combo succeeds"
GET_JSON=$(${CLI} --json combos get ${TEST_COMBO})
assert_eq "true" "$(echo "$GET_JSON" | grep -q 'ag/gemini-3.8-flash' && echo "true" || echo "false")" "combo json contains string model id"

echo "  --- Test: combos delete ---"
assert_exit_code 0 "${CLI} combos delete ${TEST_COMBO} --yes" "delete combo succeeds"
assert_exit_code 1 "${CLI} combos get ${TEST_COMBO}" "get deleted combo fails with 1"
