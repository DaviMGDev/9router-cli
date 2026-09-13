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


def _get_combo_strategies(client: RouterClient) -> dict:
    """Retrieve all combo strategies from 9router settings."""
    try:
        settings = client.get("/api/settings")
        return dict(settings.get("comboStrategies") or {})
    except Exception:
        return {}


def _set_combo_strategy(client: RouterClient, name: str, strategy: str, judge_model: Optional[str] = None):
    """Update or persist combo strategy in 9router settings."""
    try:
        settings = client.get("/api/settings")
        strategies = dict(settings.get("comboStrategies") or {})
        strategy = strategy.lower()
        if strategy == "fallback" and not judge_model:
            strategies.pop(name, None)
        else:
            entry = {"fallbackStrategy": strategy}
            if judge_model:
                entry["judgeModel"] = judge_model.strip()
            strategies[name] = entry
        client.patch("/api/settings", json={"comboStrategies": strategies})
    except Exception as exc:
        console.print(f"[yellow]Warning: Failed to persist strategy '{strategy}' for combo '{name}': {exc}[/yellow]")


def _remove_combo_strategy(client: RouterClient, name: str):
    """Remove combo strategy mapping from 9router settings on deletion."""
    try:
        settings = client.get("/api/settings")
        strategies = dict(settings.get("comboStrategies") or {})
        if name in strategies:
            del strategies[name]
            client.patch("/api/settings", json={"comboStrategies": strategies})
    except Exception:
        pass


@combos_group.command(name="list")
@click.pass_context
def list_combos(ctx: click.Context):
    """List all configured combos."""
    client: RouterClient = ctx.obj["client"]
    as_json: bool = ctx.obj.get("as_json", False)

    try:
        combos = client.get("/api/combos").get("combos", [])
        strategies = _get_combo_strategies(client)

        for c in combos:
            c_name = c.get("name", "")
            s_info = strategies.get(c_name, {})
            c["strategy"] = s_info.get("fallbackStrategy", "fallback")
            if judge := s_info.get("judgeModel"):
                c["judgeModel"] = judge

        if as_json:
            print_output(combos, as_json=True)
            return

        if not combos:
            console.print("[yellow]No combos found.[/yellow]")
            return

        table = Table(title="🔀 Model Combos")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="cyan bold")
        table.add_column("Strategy", style="magenta")
        table.add_column("Models Chain", style="green")

        for c in combos:
            models = c.get("models", [])
            strat = c.get("strategy", "fallback")
            judge = c.get("judgeModel")
            strat_label = f"{strat} (judge: {judge})" if judge else strat

            sep = " ‖ " if strat == "fusion" else " → "
            chain = sep.join(models) if isinstance(models, list) else str(models)
            table.add_row(c.get("id", ""), c.get("name", ""), strat_label, chain)

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

        strategies = _get_combo_strategies(client)
        s_info = strategies.get(combo.get("name", ""), {})
        combo["strategy"] = s_info.get("fallbackStrategy", "fallback")
        if judge := s_info.get("judgeModel"):
            combo["judgeModel"] = judge

        if as_json:
            print_output(combo, as_json=True)
            return

        table = Table(title=f"Combo: {combo.get('name')}")
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        table.add_row("ID", combo.get("id", ""))
        table.add_row("Name", combo.get("name", ""))
        table.add_row("Kind", combo.get("kind") or "llm")
        table.add_row("Strategy", combo.get("strategy", "fallback"))
        if combo.get("judgeModel"):
            table.add_row("Judge Model", combo.get("judgeModel"))

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
@click.option(
    "-s",
    "--strategy",
    type=click.Choice(["fallback", "round-robin", "fusion"], case_sensitive=False),
    default="fallback",
    show_default=True,
    help="Routing strategy: fallback (sequential), round-robin (rotate), fusion (parallel ensemble + judge).",
)
@click.option(
    "-j",
    "--judge",
    "--judge-model",
    "judge_model",
    default=None,
    help="Judge model for fusion strategy (e.g. ag/claude-opus-4-6-thinking).",
)
@click.pass_context
def create_combo(ctx: click.Context, name: str, models: List[str], strategy: str, judge_model: Optional[str]):
    """Create a new model combo (validates string IDs and strategy)."""
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

    strategy = strategy.lower()
    if judge_model and strategy != "fusion":
        strategy = "fusion"

    payload = {
        "name": name.strip(),
        "models": clean_models
    }

    try:
        res = client.post("/api/combos", json=payload)
        _set_combo_strategy(client, name.strip(), strategy, judge_model)

        if as_json:
            if isinstance(res, dict):
                res["strategy"] = strategy
                if judge_model:
                    res["judgeModel"] = judge_model.strip()
            print_output(res, as_json=True)
        else:
            strat_desc = strategy
            if strategy == "fusion" and judge_model:
                strat_desc += f", judge: {judge_model.strip()}"
            console.print(
                f"[green]✔ Combo '{name}' created successfully with {len(clean_models)} models "
                f"(strategy: {strat_desc}).[/green]"
            )
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
        _remove_combo_strategy(client, combo.get("name", ""))
        if as_json:
            print_output({"status": "deleted", "id": combo_id, "name": combo.get("name")}, as_json=True)
        else:
            console.print(f"[green]✔ Combo '{combo.get('name')}' deleted successfully.[/green]")
    except Exception as exc:
        console.print(f"[red]Failed to delete combo: {exc}[/red]")
        sys.exit(1)
