# 9Router CLI (`9r`)

A fast, scriptable Python CLI client for managing your local [9Router](https://github.com/decolua/9router) AI Gateway daemon.

## Installation

```bash
# Clone repository
git clone https://github.com/DaviMGDev/9router-cli.git
cd 9router-cli

# Install in virtualenv or with pipx
pip install -e .
```

## Authentication

`9r` automatically authenticates with the running server on `localhost:20128` by deriving the `x-9r-cli-token` from `~/.9router/machine-id` and `~/.9router/auth/cli-secret`.

You can also explicitly pass `--token <token>` or `--url <url>`.

## Global Flags

* `--url <url>`: 9Router server URL (default: `http://localhost:20128`).
* `--token <token>`: Custom CLI auth token.
* `--json`: Output raw JSON instead of tables for scriptability.

## Command Reference

### Status & Health
```bash
9r ping             # Check if 9Router server is responding (exit code 0/1)
9r status           # Display server status, version, tunnel, and active keys count
```

### Combos Management (`9r combos`)
```bash
# List existing combos
9r combos list

# Inspect combo details
9r combos get default

# Create a combo with string model IDs (strictly validated)
9r combos create my-coding-combo -m ag/claude-sonnet-4-6 -m ag/gemini-3.8-flash

# Delete combo
9r combos delete my-coding-combo --yes
```

### Provider Connections (`9r providers`)
```bash
# List all connected providers (active/inactive)
9r providers list

# Get provider details
9r providers get <provider_id>

# Run connection test
9r providers test <provider_id>
```

### Models Discovery (`9r models`)
```bash
# List all active routed models
9r models list

# Filter models by provider or search term
9r models list --provider ag
9r models list --search claude
```

### API Keys (`9r keys`)
```bash
# List active keys
9r keys list

# Generate new gateway client key (sk-...)
9r keys create my-agent-token

# Revoke key
9r keys delete my-agent-token --yes
```

### Settings & Cloudflare Tunnel
```bash
# View server settings
9r settings get

# Check public tunnel status
9r tunnel status

# Inspect CLI tools integrations (Claude Code, Codex, Droid, etc.)
9r tools status
```

## E2E Testing

To run the end-to-end test suite against your running 9Router daemon:

```bash
./tests/e2e/runner.sh
```
