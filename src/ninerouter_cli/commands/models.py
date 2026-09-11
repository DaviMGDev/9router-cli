"""Models catalog and active models inspection."""

import sys
from typing import Optional
import click
from rich.console import Console
from rich.table import Table

from ..client import RouterClient
from ..display import print_output

console = Console()


@click.group(name="models")
def models_group():
    """Discover available and catalog AI models."""
    pass


@models_group.command(name="list")
@click.option("-p", "--provider", help="Filter by provider alias (e.g. ag, oc, mmf)")
@click.option("-s", "--search", help="Search string in model name or ID")
@click.pass_context
def list_models(ctx: click.Context, provider: Optional[str], search: Optional[str]):
    """List available routed models (from active providers & combos)."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        res = client.get("/v1/models")
        models = res.get("data", [])

        if provider:
            models = [m for m in models if m.get("owned_by") == provider]

        if search:
            q = search.lower()
            models = [m for m in models if q in m.get("id", "").lower()]

        if as_json:
            print_output(models, as_json=True)
            return

        if not models:
            console.print("[yellow]No matching models found.[/yellow]")
            return

        table = Table(title=f"🤖 Available Models ({len(models)})")
        table.add_column("Model ID", style="cyan bold")
        table.add_column("Owner/Provider", style="green")

        for m in models:
            table.add_row(m.get("id", ""), m.get("owned_by", ""))

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error listing models: {exc}[/red]")
        sys.exit(1)
