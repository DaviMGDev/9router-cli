---
name: 9router
description: >-
  Manage and inspect the local 9Router AI gateway daemon (port 20128) via the 9r CLI.
  Use for checking health/status, creating safe fallback combos without breaking WebUI,
  discovering active models/providers, issuing agent API keys, and querying tools/tunnel settings.
---

# 9Router CLI (`9r`)

`9r` manages the local 9Router server (`http://localhost:20128`).
It auto-authenticates via `~/.9router/machine-id` and `~/.9router/auth/cli-secret`.

## Global Flags
- `--url <url>`: Override gateway URL (default: `http://localhost:20128`).
- `--token <token>`: Explicit CLI auth token.
- `--json`: Format output as machine-readable JSON for script processing.

## 1. Gateway Status & Connectivity
- `9r ping`: Return exit code 0 if online, 1 if unavailable.
- `9r status`: Show endpoint, online status, version, tunnel state, and active keys count.

## 2. Combos Management (`9r combos`)
Combos allow ordered fallback or load-balancing across models.
**Safety Guarantee**: `9r combos create` strictly validates and stores string model IDs, preventing the WebUI-breaking object injection bug present in upstream TUI.

- `9r combos list`: List all combos and their model chains.
- `9r combos get <name_or_id>`: Show detailed combo structure.
- `9r combos create <name> -m <model1> -m <model2> [-m <modelN>...]`: Create a new combo (minimum 2 models).
- `9r combos delete <name_or_id> [--yes]`: Delete a combo.

## 3. Providers & Models Discovery
- `9r providers list`: List all connected providers and their active status.
- `9r providers get <conn_id>`: View configuration details for a specific provider.
- `9r providers test <conn_id>`: Execute connectivity test against the provider.
- `9r models list`: List all available models from active providers and combos.
- `9r models list --provider <alias>`: Filter models by provider (e.g. `ag`, `oc`, `mmf`).
- `9r models list --search <query>`: Search models by name or identifier.

## 4. Client API Keys (`9r keys`)
Issue and revoke bearer keys (`sk-...`) for local coding agents (OpenCode, Claude Code, Cursor, Cline).

- `9r keys list`: List all generated client keys.
- `9r keys create <name>`: Create a new API key.
- `9r keys delete <name_or_id> [--yes]`: Revoke a key.

## 5. Settings, Tunnel & Integrations
- `9r settings get`: View global gateway settings.
- `9r tunnel status`: Check Cloudflare public tunnel status.
- `9r tools status`: Check which local coding CLI tools (Claude, Codex, Droid, etc.) are installed and routed to 9Router.
