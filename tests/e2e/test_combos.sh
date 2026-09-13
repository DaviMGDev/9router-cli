#!/usr/bin/env bash
# E2E Test: Combos CRUD & Strategy Support
set -euo pipefail

CLI="${PROJECT_ROOT}/.venv/bin/python -m ninerouter_cli.cli"
TEST_COMBO="e2e-cli-test-combo"
TEST_COMBO_RR="e2e-cli-test-rr"
TEST_COMBO_FUSION="e2e-cli-test-fusion"

echo "  --- Test: combos list initial ---"
assert_exit_code 0 "${CLI} combos list" "combos list responds 0"

# Clean up any leftover test combos first
${CLI} combos delete "${TEST_COMBO}" --yes 2>/dev/null || true
${CLI} combos delete "${TEST_COMBO_RR}" --yes 2>/dev/null || true
${CLI} combos delete "${TEST_COMBO_FUSION}" --yes 2>/dev/null || true

echo "  --- Test: combos create (fallback default) ---"
assert_exit_code 0 "${CLI} combos create ${TEST_COMBO} -m ag/gemini-3.8-flash -m ag/gemini-3.8-flash-low -s fallback" "create fallback combo succeeds"
GET_JSON=$(${CLI} --json combos get ${TEST_COMBO})
assert_eq "true" "$(echo "$GET_JSON" | grep -q 'ag/gemini-3.8-flash' && echo "true" || echo "false")" "combo json contains model id"
assert_eq "true" "$(echo "$GET_JSON" | grep -q '"strategy": "fallback"' && echo "true" || echo "false")" "combo json strategy is fallback"

echo "  --- Test: combos create (round-robin) ---"
assert_exit_code 0 "${CLI} combos create ${TEST_COMBO_RR} -m ag/gemini-3.8-flash -m ag/gemini-3.8-flash-low -s round-robin" "create round-robin combo succeeds"
GET_RR_JSON=$(${CLI} --json combos get ${TEST_COMBO_RR})
assert_eq "true" "$(echo "$GET_RR_JSON" | grep -q '"strategy": "round-robin"' && echo "true" || echo "false")" "combo json strategy is round-robin"

echo "  --- Test: combos create (fusion with judge) ---"
assert_exit_code 0 "${CLI} combos create ${TEST_COMBO_FUSION} -m ag/gemini-3.8-flash -m ag/gemini-3.7-flash-high -j ag/claude-opus-4-6-thinking" "create fusion combo succeeds"
GET_FUSION_JSON=$(${CLI} --json combos get ${TEST_COMBO_FUSION})
assert_eq "true" "$(echo "$GET_FUSION_JSON" | grep -q '"strategy": "fusion"' && echo "true" || echo "false")" "combo json strategy is fusion"
assert_eq "true" "$(echo "$GET_FUSION_JSON" | grep -q 'ag/claude-opus-4-6-thinking' && echo "true" || echo "false")" "combo json contains judgeModel"

echo "  --- Test: combos list includes created combos ---"
LIST_JSON=$(${CLI} --json combos list)
assert_eq "true" "$(echo "$LIST_JSON" | grep -q "${TEST_COMBO_FUSION}" && echo "true" || echo "false")" "combos list contains fusion combo"

echo "  --- Test: combos delete ---"
assert_exit_code 0 "${CLI} combos delete ${TEST_COMBO} --yes" "delete fallback combo succeeds"
assert_exit_code 0 "${CLI} combos delete ${TEST_COMBO_RR} --yes" "delete round-robin combo succeeds"
assert_exit_code 0 "${CLI} combos delete ${TEST_COMBO_FUSION} --yes" "delete fusion combo succeeds"

assert_exit_code 1 "${CLI} combos get ${TEST_COMBO}" "get deleted fallback combo fails with 1"
assert_exit_code 1 "${CLI} combos get ${TEST_COMBO_FUSION}" "get deleted fusion combo fails with 1"
