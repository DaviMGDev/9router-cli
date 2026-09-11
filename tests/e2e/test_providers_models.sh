#!/usr/bin/env bash
# E2E Test: Providers and Models
set -euo pipefail

CLI="${PROJECT_ROOT}/.venv/bin/python -m ninerouter_cli.cli"

echo "  --- Test: providers list ---"
assert_exit_code 0 "${CLI} providers list" "providers list responds 0"

PROVIDERS_JSON=$(${CLI} --json providers list)
assert_eq "true" "$(echo "$PROVIDERS_JSON" | grep -q 'provider' && echo "true" || echo "false")" "providers json has provider field"

echo "  --- Test: models list ---"
assert_exit_code 0 "${CLI} models list" "models list responds 0"

MODELS_JSON=$(${CLI} --json models list)
assert_eq "true" "$(echo "$MODELS_JSON" | grep -q 'id' && echo "true" || echo "false")" "models list has model ids"

echo "  --- Test: models search ---"
SEARCH_JSON=$(${CLI} --json models list --search gemini)
assert_eq "true" "$(echo "$SEARCH_JSON" | grep -q 'gemini' && echo "true" || echo "false")" "models search filters gemini"
