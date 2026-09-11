"""Authentication and token generation for 9router server."""

import hashlib
import os
from pathlib import Path
from typing import Optional

CLI_TOKEN_SALT = "9r-cli-auth"
CLI_TOKEN_HEADER = "x-9r-cli-token"


def get_data_dir() -> Path:
    """Resolve the 9router local configuration directory."""
    if env_dir := os.environ.get("DATA_DIR"):
        return Path(env_dir)
    return Path.home() / ".9router"


def get_cli_token() -> Optional[str]:
    """Derive the deterministic 16-char hex token using machine-id and cli-secret."""
    data_dir = get_data_dir()
    machine_id_file = data_dir / "machine-id"
    cli_secret_file = data_dir / "auth" / "cli-secret"

    if not machine_id_file.is_file() or not cli_secret_file.is_file():
        return None

    try:
        raw_machine_id = machine_id_file.read_text(encoding="utf-8").strip()
        cli_secret = cli_secret_file.read_text(encoding="utf-8").strip()
    except Exception:
        return None

    if not raw_machine_id or not cli_secret:
        return None

    content = f"{raw_machine_id}{CLI_TOKEN_SALT}{cli_secret}"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return digest[:16]
