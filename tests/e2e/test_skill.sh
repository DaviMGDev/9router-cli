#!/usr/bin/env bash
# E2E Test: Skill Commands
set -euo pipefail

CLI="${PROJECT_ROOT}/.venv/bin/python -m ninerouter_cli.cli"

echo "  --- Test: skill show ---"
SHOW_OUT=$(${CLI} skill show)
assert_eq "true" "$(echo "$SHOW_OUT" | grep -q 'name: 9router' && echo "true" || echo "false")" "skill show outputs frontmatter"

echo "  --- Test: skill install ---"
TMP_TARGET="/tmp/pi-test-skill-$(date +%s)"
assert_exit_code 0 "${CLI} skill install --target ${TMP_TARGET}" "skill install to custom directory succeeds"
assert_eq "true" "$([[ -f "${TMP_TARGET}/SKILL.md" ]] && echo "true" || echo "false")" "SKILL.md exists in target"
rm -rf "${TMP_TARGET}"
