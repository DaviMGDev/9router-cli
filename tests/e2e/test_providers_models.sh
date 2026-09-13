#!/usr/bin/env bash
# E2E Test: Providers and Models
set -euo pipefail

CLI="${PROJECT_ROOT}/.venv/bin/python -m ninerouter_cli.cli"

echo "  --- Test: providers list ---"
assert_exit_code 0 "${CLI} providers list" "providers list responds 0"

PROVIDERS_JSON=$(${CLI} --json providers list)
assert_eq "true" "$(echo "$PROVIDERS_JSON" | grep -q 'provider' && echo "true" || echo "false")" "providers json has provider field"

echo "  --- Test: providers catalog ---"
assert_exit_code 0 "${CLI} providers catalog" "providers catalog responds 0"
CATALOG_JSON=$(${CLI} --json providers catalog --free)
assert_eq "true" "$(echo "$CATALOG_JSON" | grep -q 'opencode' && echo "true" || echo "false")" "catalog has opencode"

echo "  --- Test: providers enable-free & delete ---"
assert_exit_code 0 "${CLI} providers enable-free opencode" "enable-free opencode succeeds"
assert_exit_code 0 "${CLI} providers delete opencode --yes" "delete opencode succeeds"

echo "  --- Test: providers add (free provider) ---"
assert_exit_code 0 "${CLI} providers add opencode" "add opencode succeeds"

echo "  --- Test: models list ---"
assert_exit_code 0 "${CLI} models list" "models list responds 0"

MODELS_JSON=$(${CLI} --json models list)
assert_eq "true" "$(echo "$MODELS_JSON" | grep -q 'id' && echo "true" || echo "false")" "models list has model ids"

echo "  --- Test: models search ---"
SEARCH_JSON=$(${CLI} --json models list --search gemini)
assert_eq "true" "$(echo "$SEARCH_JSON" | grep -q 'gemini' && echo "true" || echo "false")" "models search filters gemini"

echo "  --- Test: models list --free ---"
FREE_MODELS_JSON=$(${CLI} --json models list --free)
assert_eq "true" "$(echo "$FREE_MODELS_JSON" | grep -q 'oc/' && echo "true" || echo "false")" "models list --free contains oc models"

echo "  --- Test: models list --catalog ---"
CATALOG_MODELS_JSON=$(${CLI} --json models list --catalog --free)
assert_eq "true" "$(echo "$CATALOG_MODELS_JSON" | grep -q 'id' && echo "true" || echo "false")" "catalog models list returns items"
