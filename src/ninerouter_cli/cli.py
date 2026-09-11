"""Main CLI entrypoint for 9router-cli (9r)."""

import sys
import click
from rich.console import Console
from rich.table import Table

from .client import RouterClient
from .display import print_output
from .commands.combos import combos_group

console = Console()


@click.group()
@click.option("--url", default="http://localhost:20128", help="9Router server URL")
@click.option("--token", default=None, help="Custom auth token")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx: click.Context, url: str, token: str, as_json: bool):
    """9Router CLI - Manage local AI Gateway routes, combos, and keys."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = RouterClient(base_url=url, token=token)
    ctx.obj["as_json"] = as_json


cli.add_command(combos_group)


@cli.command()
@click.pass_context
def ping(ctx: click.Context):
    """Quick connectivity test against 9router daemon."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)
    try:
        res = client.get("/api/health")
        if res.get("ok") is True:
            if as_json:
                print_output({"status": "ok"}, as_json=True)
            else:
                console.print("[green]✔ 9Router is healthy and responding.[/green]")
            return
    except Exception as exc:
        if as_json:
            print_output({"status": "error", "error": str(exc)}, as_json=True)
        else:
            console.print(f"[red]✖ Connection failed: {exc}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context):
    """Show status of 9router daemon, version, tunnel, and keys."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)
    try:
        health = client.get("/api/health")
        version_info = client.get("/api/version")
        keys_info = client.get("/api/keys")
        tunnel_info = client.get("/api/tunnel/status")

        data = {
            "health": health,
            "version": version_info,
            "keys_count": len(keys_info.get("keys", [])),
            "tunnel": tunnel_info,
            "url": client.base_url,
        }

        if as_json:
            print_output(data, as_json=True)
            return

        table = Table(title="📡 9Router Server Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Endpoint", client.base_url)
        table.add_row("Status", "Online" if health.get("ok") else "Degraded")
        table.add_row("Version", str(version_info.get("version", "unknown")))
        table.add_row("Active Keys", str(len(keys_info.get("keys", []))))
        table.add_row("Tunnel", "Active" if tunnel_info.get("enabled") else "Disabled")

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Failed to retrieve status: {exc}[/red]")
        sys.exit(1)


def main():
    cli(prog_name="9r")


if __name__ == "__main__":
    main()
