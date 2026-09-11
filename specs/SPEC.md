# 9Router CLI Specification (SPEC.md)

## 1. Overview
The `9router-cli` (executable: `9r`) provides a scriptable, non-interactive command-line interface for the running `9router` server daemon (`http://localhost:20128`).

## 2. Authentication Model
The CLI interacts directly with the local server API without needing a user password:
- Reads `~/.9router/machine-id` and `~/.9router/auth/cli-secret`
- Computes SHA256: `hex(sha256(machineId + "9r-cli-auth" + cliSecret))[:16]`
- Injects header: `x-9r-cli-token: <hash>`
- Fallback: Accepts `--token` or environment variable `NINEROUTER_TOKEN` or `NINEROUTER_URL` (default: `http://localhost:20128`).

## 3. Command Hierarchy

### Global Options
- `--url <url>`: 9Router server URL (default: `http://localhost:20128`)
- `--json`: Output raw JSON instead of formatted tables/trees
- `-v, --verbose`: Verbose debug logs
- `--version`: Print CLI version

### 3.1 Status & Health
- `9r status`: Checks connectivity, prints server version, endpoint, tunnel status, active keys count.
- `9r ping`: Exit code 0 if server responds, exit code 1 if down.

### 3.2 Combos (`9r combos`)
- `9r combos list`: List all model combos (id, name, strategy, models count).
- `9r combos get <name_or_id>`: Show detailed combo model fallback chain and strategy.
- `9r combos create <name> --model <m1> --model <m2> [--strategy fallback|round-robin|fusion]`:
  **Validation rule**: Models MUST be string identifiers (`provider/model` or `fullModel`). Any object payload is rejected client-side.
- `9r combos update <name_or_id> [--name <new_name>] [--models <m1,m2...>]`: Update combo.
- `9r combos delete <name_or_id> [--yes]`: Delete combo.

### 3.3 Providers (`9r providers`)
- `9r providers list`: List configured provider connections.
- `9r providers get <id>`: Inspect provider details.
- `9r providers test <id>`: Trigger connection test against provider endpoint.
- `9r providers delete <id> [--yes]`: Remove provider connection.

### 3.4 Models (`9r models`)
- `9r models list [--provider <alias>] [--search <query>]`: List available models from active providers and combos (`/v1/models`).
- `9r models catalog`: List all internal catalog models (`/api/models`).

### 3.5 API Keys (`9r keys`)
- `9r keys list`: List client API keys.
- `9r keys create <name>`: Generate a new 9Router client API key (`sk-9...`).
- `9r keys delete <id> [--yes]`: Revoke a client API key.

### 3.6 Settings & Tunnel (`9r settings`, `9r tunnel`)
- `9r settings get`: View current router settings.
- `9r tunnel status`: Check public Cloudflare tunnel status.
- `9r tunnel enable` / `9r tunnel disable`: Toggle public tunnel.

### 3.7 CLI Tools (`9r tools`)
- `9r tools status`: Display integration statuses for Claude Code, Codex, Droid, etc.
