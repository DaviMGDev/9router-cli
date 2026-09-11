"""Provider connections management commands."""

import sys
import click
from rich.console import Console
from rich.table import Table

from ..client import RouterClient
from ..display import print_output

console = Console()


@click.group(name="providers")
def providers_group():
    """Manage and inspect AI provider connections."""
    pass


@providers_group.command(name="list")
@click.pass_context
def list_providers(ctx: click.Context):
    """List all connected providers."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        res = client.get("/api/providers")
        connections = res.get("connections", [])

        if as_json:
            print_output(connections, as_json=True)
            return

        if not connections:
            console.print("[yellow]No providers connected.[/yellow]")
            return

        table = Table(title="🔌 Connected Providers")
        table.add_column("ID", style="dim")
        table.add_column("Provider", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Active", style="green")

        for conn in connections:
            table.add_row(
                conn.get("id", ""),
                conn.get("provider", ""),
                conn.get("name", ""),
                "✔" if conn.get("isActive") else "✖"
            )

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error listing providers: {exc}[/red]")
        sys.exit(1)


@providers_group.command(name="get")
@click.argument("conn_id")
@click.pass_context
def get_provider(ctx: click.Context, conn_id: str):
    """Get details for a provider connection."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        conn = client.get(f"/api/providers/{conn_id}").get("connection", {})
        if not conn:
            console.print(f"[red]Provider connection '{conn_id}' not found.[/red]")
            sys.exit(1)

        if as_json:
            print_output(conn, as_json=True)
            return

        table = Table(title=f"Provider: {conn.get('name')}")
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        for k, v in conn.items():
            table.add_row(str(k), str(v))

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error getting provider: {exc}[/red]")
        sys.exit(1)


@providers_group.command(name="test")
@click.argument("conn_id")
@click.pass_context
def test_provider(ctx: click.Context, conn_id: str):
    """Test a provider connection health/credentials."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        res = client.post(f"/api/providers/{conn_id}/test")
        if as_json:
            print_output(res, as_json=True)
        else:
            if res.get("valid"):
                console.print(f"[green]✔ Provider '{conn_id}' connection is valid.[/green]")
            else:
                console.print(f"[red]✖ Provider '{conn_id}' test failed: {res.get('error')}[/red]")
    except Exception as exc:
        console.print(f"[red]Error testing provider: {exc}[/red]")
        sys.exit(1)
