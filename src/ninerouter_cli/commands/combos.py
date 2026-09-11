"""Combos management commands for 9router."""

import sys
from typing import List, Optional
import click
from rich.console import Console
from rich.table import Table

from ..client import RouterClient
from ..display import print_output

console = Console()


@click.group(name="combos")
def combos_group():
    """Manage fallback and multi-model combos."""
    pass


def _find_combo(client: RouterClient, name_or_id: str):
    combos = client.get("/api/combos").get("combos", [])
    for c in combos:
        if c.get("id") == name_or_id or c.get("name") == name_or_id:
            return c
    return None


@combos_group.command(name="list")
@click.pass_context
def list_combos(ctx: click.Context):
    """List all configured combos."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        combos = client.get("/api/combos").get("combos", [])
        if as_json:
            print_output(combos, as_json=True)
            return

        if not combos:
            console.print("[yellow]No combos found.[/yellow]")
            return

        table = Table(title="🔀 Model Combos")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="cyan bold")
        table.add_column("Models Chain", style="green")

        for c in combos:
            models = c.get("models", [])
            chain = " → ".join(models) if isinstance(models, list) else str(models)
            table.add_row(c.get("id", ""), c.get("name", ""), chain)

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error listing combos: {exc}[/red]")
        sys.exit(1)


@combos_group.command(name="get")
@click.argument("name_or_id")
@click.pass_context
def get_combo(ctx: click.Context, name_or_id: str):
    """Get combo details by name or ID."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        combo = _find_combo(client, name_or_id)
        if not combo:
            console.print(f"[red]Combo '{name_or_id}' not found.[/red]")
            sys.exit(1)

        if as_json:
            print_output(combo, as_json=True)
            return

        table = Table(title=f"Combo: {combo.get('name')}")
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        table.add_row("ID", combo.get("id", ""))
        table.add_row("Name", combo.get("name", ""))
        table.add_row("Kind", combo.get("kind", "llm"))
        models = combo.get("models", [])
        for i, m in enumerate(models, 1):
            table.add_row(f"Model #{i}", str(m))

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error fetching combo: {exc}[/red]")
        sys.exit(1)


@combos_group.command(name="create")
@click.argument("name")
@click.option("-m", "--model", "models", multiple=True, required=True, help="Model ID (e.g. ag/gemini-3.8-flash)")
@click.pass_context
def create_combo(ctx: click.Context, name: str, models: List[str]):
    """Create a new model combo (validates string IDs)."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    if len(models) < 2:
        console.print("[red]Error: A combo requires at least 2 models.[/red]")
        sys.exit(1)

    # String validation to prevent WebUI-breaking object injection
    clean_models = []
    for m in models:
        if not isinstance(m, str) or not m.strip():
            console.print(f"[red]Invalid model identifier: {m}[/red]")
            sys.exit(1)
        clean_models.append(m.strip())

    payload = {
        "name": name.strip(),
        "models": clean_models
    }

    try:
        res = client.post("/api/combos", json=payload)
        if as_json:
            print_output(res, as_json=True)
        else:
            console.print(f"[green]✔ Combo '{name}' created successfully with {len(clean_models)} models.[/green]")
    except Exception as exc:
        console.print(f"[red]Failed to create combo: {exc}[/red]")
        sys.exit(1)


@combos_group.command(name="delete")
@click.argument("name_or_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_combo(ctx: click.Context, name_or_id: str, yes: bool):
    """Delete a combo by name or ID."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        combo = _find_combo(client, name_or_id)
        if not combo:
            console.print(f"[red]Combo '{name_or_id}' not found.[/red]")
            sys.exit(1)

        combo_id = combo["id"]
        if not yes:
            if not click.confirm(f"Delete combo '{combo.get('name')}' ({combo_id})?"):
                console.print("Cancelled.")
                return

        client.delete(f"/api/combos/{combo_id}")
        if as_json:
            print_output({"status": "deleted", "id": combo_id, "name": combo.get("name")}, as_json=True)
        else:
            console.print(f"[green]✔ Combo '{combo.get('name')}' deleted successfully.[/green]")
    except Exception as exc:
        console.print(f"[red]Failed to delete combo: {exc}[/red]")
        sys.exit(1)
