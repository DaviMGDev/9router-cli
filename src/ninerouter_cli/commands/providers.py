"""Provider connections management commands."""

import sys
from typing import Optional
import click
from rich.console import Console
from rich.table import Table

from ..client import RouterClient
from ..display import print_output
from ..catalog import (
    find_catalog_provider,
    get_catalog_providers,
    is_no_auth_provider,
    register_free_provider,
    NO_AUTH_PROVIDER_IDS,
)

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
        table.add_column("Auth Type", style="magenta")
        table.add_column("Active", style="green")

        for conn in connections:
            table.add_row(
                conn.get("id", ""),
                conn.get("provider", ""),
                conn.get("name", ""),
                conn.get("authType", "apikey"),
                "✔" if conn.get("isActive") else "✖"
            )

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error listing providers: {exc}[/red]")
        sys.exit(1)


@providers_group.command(name="catalog")
@click.option("-f", "--free", is_flag=True, help="Filter to free / free-tier providers.")
@click.option("-s", "--search", help="Search by provider name or ID.")
@click.pass_context
def catalog_providers(ctx: click.Context, free: bool, search: Optional[str]):
    """List all providers supported by 9Router."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        # Fetch connected providers to show status
        connected_res = client.get("/api/providers")
        connected_ids = {c.get("provider") for c in connected_res.get("connections", [])}

        providers = get_catalog_providers()

        if free:
            providers = [p for p in providers if p.get("has_free")]

        if search:
            q = search.lower().strip()
            providers = [
                p for p in providers
                if q in p["id"].lower() or q in p.get("alias", "").lower() or q in p.get("name", "").lower()
            ]

        for p in providers:
            p["connected"] = p["id"] in connected_ids or p.get("alias") in connected_ids

        if as_json:
            print_output(providers, as_json=True)
            return

        if not providers:
            console.print("[yellow]No matching providers found in catalog.[/yellow]")
            return

        title_suffix = " (Free Tier)" if free else ""
        table = Table(title=f"📖 Provider Catalog{title_suffix} ({len(providers)})")
        table.add_column("ID", style="cyan bold")
        table.add_column("Alias", style="dim")
        table.add_column("Name", style="white")
        table.add_column("Auth Type", style="magenta")
        table.add_column("Free Tier", style="yellow")
        table.add_column("Status", style="green")

        for p in providers:
            is_conn = p["connected"]
            status_str = "[green]✔ Connected[/green]" if is_conn else "[dim]✖ None[/dim]"
            free_str = "✔ Free" if p.get("no_auth") else ("✔ Free Tier" if p.get("has_free") else "—")
            auth_str = "None (Free)" if p.get("no_auth") else p.get("auth_type", "apikey")

            table.add_row(
                p["id"],
                p.get("alias", ""),
                p.get("name", p["id"]),
                auth_str,
                free_str,
                status_str,
            )

        console.print(table)
    except Exception as exc:
        console.print(f"[red]Error fetching provider catalog: {exc}[/red]")
        sys.exit(1)


@providers_group.command(name="enable-free")
@click.argument("provider", default="opencode")
@click.option("-n", "--name", help="Friendly name for this connection.")
@click.pass_context
def enable_free_provider(ctx: click.Context, provider: str, name: Optional[str]):
    """Enable a free/no-auth provider directly from CLI (defaults to opencode)."""
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        cat_p = find_catalog_provider(provider)
        target_id = cat_p["id"] if cat_p else provider

        result = register_free_provider(target_id, name=name)

        if as_json:
            print_output(result, as_json=True)
            return

        action = result.get("action")
        p_name = result.get("name")
        conn_id = result.get("id")

        if action == "already_active":
            console.print(f"[yellow]Provider '{p_name}' ({target_id}) is already enabled and active.[/yellow]")
        elif action == "reactivated":
            console.print(f"[green]✔ Provider '{p_name}' ({target_id}) was re-activated successfully.[/green]")
        else:
            console.print(
                f"[green]✔ Free provider '{p_name}' ({target_id}) registered successfully! (ID: {conn_id})[/green]\n"
                f"[dim]Run '9r models list' to view its available models.[/dim]"
            )
    except Exception as exc:
        console.print(f"[red]Error enabling free provider '{provider}': {exc}[/red]")
        sys.exit(1)


@providers_group.command(name="add")
@click.argument("provider")
@click.option("-n", "--name", help="Friendly name (defaults to provider display name).")
@click.option("-k", "--key", "--api-key", "api_key", help="API key for authentication.")
@click.option("-p", "--priority", default=1, type=int, show_default=True, help="Routing priority.")
@click.pass_context
def add_provider(ctx: click.Context, provider: str, name: Optional[str], api_key: Optional[str], priority: int):
    """Add a new provider connection (free tier or API-key based)."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    cat_p = find_catalog_provider(provider)
    canonical_id = cat_p["id"] if cat_p else provider
    display_name = name or (cat_p["name"] if cat_p else canonical_id)

    # If it is a zero-auth provider (or no key given for a known free provider)
    if is_no_auth_provider(canonical_id) or (not api_key and canonical_id in NO_AUTH_PROVIDER_IDS):
        try:
            result = register_free_provider(canonical_id, name=display_name)
            if as_json:
                print_output(result, as_json=True)
                return
            console.print(
                f"[green]✔ Free provider '{display_name}' ({canonical_id}) enabled successfully![/green]\n"
                f"[dim]Models are now available via '9r models list'.[/dim]"
            )
            return
        except Exception as exc:
            console.print(f"[red]Failed to enable free provider: {exc}[/red]")
            sys.exit(1)

    # API key provider
    if not api_key:
        console.print(f"[red]Error: Provider '{canonical_id}' requires an API key (--api-key / -k).[/red]")
        sys.exit(1)

    payload = {
        "provider": canonical_id,
        "name": display_name,
        "apiKey": api_key.strip(),
        "priority": priority,
    }

    try:
        res = client.post("/api/providers", json=payload)
        if as_json:
            print_output(res, as_json=True)
        else:
            conn = res.get("connection", {})
            conn_id = conn.get("id", "")
            console.print(
                f"[green]✔ Provider '{display_name}' ({canonical_id}) connected successfully! (ID: {conn_id})[/green]"
            )
    except Exception as exc:
        console.print(f"[red]Failed to add provider: {exc}[/red]")
        sys.exit(1)


@providers_group.command(name="delete")
@click.argument("name_or_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt.")
@click.pass_context
def delete_provider(ctx: click.Context, name_or_id: str, yes: bool):
    """Delete/disconnect a provider connection by ID, name, or provider slug."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        conns_res = client.get("/api/providers")
        connections = conns_res.get("connections", [])

        target = None
        q = name_or_id.strip().lower()

        # 1. Exact ID match
        for c in connections:
            if c.get("id", "").lower() == q:
                target = c
                break

        # 2. Exact name match
        if not target:
            for c in connections:
                if c.get("name", "").lower() == q:
                    target = c
                    break

        # 3. Provider slug match
        if not target:
            for c in connections:
                if c.get("provider", "").lower() == q:
                    target = c
                    break

        if not target:
            console.print(f"[red]Provider connection '{name_or_id}' not found.[/red]")
            sys.exit(1)

        conn_id = target["id"]
        conn_name = target.get("name", conn_id)

        if not yes:
            if not click.confirm(f"Delete connection '{conn_name}' ({target.get('provider')} / {conn_id})?"):
                console.print("Cancelled.")
                return

        client.delete(f"/api/providers/{conn_id}")

        if as_json:
            print_output({"status": "deleted", "id": conn_id, "name": conn_name}, as_json=True)
        else:
            console.print(f"[green]✔ Provider connection '{conn_name}' deleted successfully.[/green]")
    except Exception as exc:
        console.print(f"[red]Error deleting provider: {exc}[/red]")
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
