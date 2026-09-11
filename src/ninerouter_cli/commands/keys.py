"""Client API keys management commands."""

import sys
import click
from rich.console import Console
from rich.table import Table

from ..client import RouterClient
from ..display import print_output

console = Console()


@click.group(name="keys")
def keys_group():
    """Manage 9Router gateway client API keys."""
    pass


@keys_group.command(name="list")
@click.pass_context
def list_keys(ctx: click.Context):
    """List all client API keys."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        keys = client.get("/api/keys").get("keys", [])
        if as_json:
            print_output(keys, as_json=True)
            return

        if not keys:
            console.print("[yellow]No API keys found.[/yellow]")
            return

        table = Table(title="🔑 9Router Client API Keys")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="cyan bold")
        table.add_column("Key", style="green")

        for k in keys:
            table.add_row(k.get("id", ""), k.get("name", ""), k.get("key", ""))

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error listing keys: {exc}[/red]")
        sys.exit(1)


@keys_group.command(name="create")
@click.argument("name")
@click.pass_context
def create_key(ctx: click.Context, name: str):
    """Create a new client API key."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        res = client.post("/api/keys", json={"name": name.strip()})
        if as_json:
            print_output(res, as_json=True)
        else:
            console.print(f"[green]✔ Key created for '{name}':[/green] [bold cyan]{res.get('key')}[/bold cyan]")
    except Exception as exc:
        console.print(f"[red]Error creating key: {exc}[/red]")
        sys.exit(1)


@keys_group.command(name="delete")
@click.argument("name_or_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_key(ctx: click.Context, name_or_id: str, yes: bool):
    """Delete an API key by name or ID."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        keys = client.get("/api/keys").get("keys", [])
        target = None
        for k in keys:
            if k.get("id") == name_or_id or k.get("name") == name_or_id:
                target = k
                break

        if not target:
            console.print(f"[red]Key '{name_or_id}' not found.[/red]")
            sys.exit(1)

        key_id = target["id"]
        if not yes:
            if not click.confirm(f"Delete API key '{target.get('name')}'?"):
                console.print("Cancelled.")
                return

        client.delete(f"/api/keys/{key_id}")
        if as_json:
            print_output({"status": "deleted", "id": key_id, "name": target.get("name")}, as_json=True)
        else:
            console.print(f"[green]✔ Key '{target.get('name')}' deleted successfully.[/green]")
    except Exception as exc:
        console.print(f"[red]Error deleting key: {exc}[/red]")
        sys.exit(1)
