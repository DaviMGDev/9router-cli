#!/usr/bin/env bash
# E2E Test Suite Runner for 9Router CLI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

export PYTHONPATH="${PROJECT_ROOT}/src:${PYTHONPATH:-}"
CLI="python3 -m ninerouter_cli.cli"

PASS_COUNT=0
FAIL_COUNT=0

assert_eq() {
  local expected="$1"
  local actual="$2"
  local msg="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "  ✅ PASS: $msg"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "  ❌ FAIL: $msg (expected '$expected', got '$actual')"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

assert_exit_code() {
  local expected="$1"
  local cmd="$2"
  local msg="$3"
  local code=0
  eval "$cmd" > /dev/null 2>&1 || code=$?
  assert_eq "$expected" "$code" "$msg"
}

export -f assert_eq
export -f assert_exit_code
export CLI PASS_COUNT FAIL_COUNT PROJECT_ROOT

echo "=== Running 9router-cli E2E Test Suite ==="

for test_file in "${SCRIPT_DIR}"/test_*.sh; do
  if [[ -f "$test_file" ]]; then
    echo "▶ Testing: $(basename "$test_file")"
    bash "$test_file"
  fi
done

echo "=========================================="
echo "Results: All test blocks executed."
