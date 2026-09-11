"""Settings, tunnel, and integration tools commands."""

import sys
import click
from rich.console import Console
from rich.table import Table

from ..client import RouterClient
from ..display import print_output

console = Console()


@click.group(name="settings")
def settings_group():
    """Inspect and modify 9router global settings."""
    pass


@settings_group.command(name="get")
@click.pass_context
def get_settings(ctx: click.Context):
    """View global settings."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        settings = client.get("/api/settings")
        if as_json:
            print_output(settings, as_json=True)
            return

        table = Table(title="⚙ 9Router Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value")

        for k, v in settings.items():
            table.add_row(str(k), str(v))

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error fetching settings: {exc}[/red]")
        sys.exit(1)


@click.group(name="tunnel")
def tunnel_group():
    """Manage Cloudflare public tunnel."""
    pass


@tunnel_group.command(name="status")
@click.pass_context
def tunnel_status(ctx: click.Context):
    """Check tunnel status."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        status = client.get("/api/tunnel/status")
        if as_json:
            print_output(status, as_json=True)
            return

        enabled = status.get("enabled", False)
        console.print(f"Tunnel: [bold {'green' if enabled else 'yellow'}]{'ENABLED' if enabled else 'DISABLED'}[/]")
        if enabled:
            console.print(f"Public URL: [cyan]{status.get('tunnelUrl')}[/cyan]")
    except Exception as exc:
        console.print(f"[red]Error checking tunnel: {exc}[/red]")
        sys.exit(1)


@click.group(name="tools")
def tools_group():
    """Inspect CLI integration tools status (claude, codex, cline, droid)."""
    pass


@tools_group.command(name="status")
@click.pass_context
def tools_status(ctx: click.Context):
    """View integrations status."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        res = client.get("/api/cli-tools/all-statuses")
        if as_json:
            print_output(res, as_json=True)
            return

        table = Table(title="🛠 CLI Tools Integration Status")
        table.add_column("Tool", style="bold cyan")
        table.add_column("Installed", style="green")
        table.add_column("Routed to 9Router", style="magenta")

        statuses = res if isinstance(res, dict) else {}
        for tool, info in statuses.items():
            if isinstance(info, dict):
                table.add_row(
                    tool,
                    "✔" if info.get("installed") else "✖",
                    "✔" if info.get("has9Router") else "✖"
                )

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error getting tools status: {exc}[/red]")
        sys.exit(1)
