"""Models catalog and active models inspection."""

import sys
from typing import Optional, List, Dict, Any
import click
from rich.console import Console
from rich.table import Table

from ..client import RouterClient
from ..display import print_output

console = Console()

FREE_PROVIDER_ALIASES = {
    "oc", "opencode", "mmf", "mimo-free", "gc", "gemini-cli",
    "searxng", "tortoise", "coqui", "edge-tts", "google-tts", "local-device"
}


def _is_free_model(model_id: str, provider_alias: str) -> bool:
    """Check if a model represents a free-tier model."""
    m_lower = model_id.lower()
    p_lower = provider_alias.lower()
    if p_lower in FREE_PROVIDER_ALIASES:
        return True
    if ":free" in m_lower or "-free" in m_lower or "free" in m_lower.split("/"):
        return True
    return False


@click.group(name="models")
def models_group():
    """Discover available and catalog AI models."""
    pass


@models_group.command(name="list")
@click.option("-p", "--provider", help="Filter by provider alias (e.g. ag, oc, mmf)")
@click.option("-s", "--search", help="Search string in model name or ID")
@click.option("-c", "--catalog", is_flag=True, help="List models from global catalog instead of only active routes.")
@click.option("-f", "--free", is_flag=True, help="Filter to free / zero-cost models.")
@click.pass_context
def list_models(
    ctx: click.Context,
    provider: Optional[str],
    search: Optional[str],
    catalog: bool,
    free: bool,
):
    """List available routed models (from active providers & combos), or explore the catalog."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        if catalog:
            res = client.get("/api/models")
            raw_models = res.get("models", [])
            models: List[Dict[str, Any]] = []
            for rm in raw_models:
                m_id = rm.get("routedModel") or rm.get("fullModel") or f"{rm.get('provider')}/{rm.get('model')}"
                p_alias = rm.get("provider", "")
                models.append({
                    "id": m_id,
                    "owned_by": p_alias,
                    "name": rm.get("name", m_id),
                    "caps": rm.get("caps", {}),
                    "is_free": _is_free_model(m_id, p_alias),
                })
        else:
            res = client.get("/v1/models")
            raw_data = res.get("data", [])
            models = []
            for rm in raw_data:
                m_id = rm.get("id", "")
                p_alias = rm.get("owned_by", "")
                models.append({
                    "id": m_id,
                    "owned_by": p_alias,
                    "name": m_id,
                    "capabilities": rm.get("capabilities"),
                    "context_length": rm.get("context_length"),
                    "is_free": _is_free_model(m_id, p_alias),
                })

        if free:
            models = [m for m in models if m.get("is_free")]

        if provider:
            p_filter = provider.lower().strip()
            models = [m for m in models if m.get("owned_by", "").lower() == p_filter]

        if search:
            q = search.lower().strip()
            models = [
                m for m in models
                if q in m.get("id", "").lower() or q in m.get("name", "").lower()
            ]

        if as_json:
            print_output(models, as_json=True)
            return

        if not models:
            console.print("[yellow]No matching models found.[/yellow]")
            return

        title_suffix = " (Catalog)" if catalog else " (Active Routes)"
        if free:
            title_suffix += " [Free Tier]"

        table = Table(title=f"🤖 Available Models{title_suffix} ({len(models)})")
        table.add_column("Model ID", style="cyan bold")
        table.add_column("Owner/Provider", style="green")
        if free or catalog:
            table.add_column("Free", style="yellow")

        for m in models:
            row_items = [m.get("id", ""), m.get("owned_by", "")]
            if free or catalog:
                row_items.append("✔ Free" if m.get("is_free") else "—")
            table.add_row(*row_items)

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error listing models: {exc}[/red]")
        sys.exit(1)
