"""Command to inspect and install the 9router agent skill."""

import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console

from ..display import print_output

console = Console()

SKILL_RESOURCE_PATH = Path(__file__).parent.parent / "resources" / "SKILL.md"


def get_skill_content() -> str:
    if not SKILL_RESOURCE_PATH.is_file():
        raise FileNotFoundError(f"Skill resource not found at {SKILL_RESOURCE_PATH}")
    return SKILL_RESOURCE_PATH.read_text(encoding="utf-8")


@click.group(name="skill")
def skill_group():
    """View and install the 9Router agent skill."""
    pass


@skill_group.command(name="show")
def show_skill():
    """Print the 9Router skill markdown to stdout."""
    try:
        content = get_skill_content()
        print(content)
    except Exception as exc:
        console.print(f"[red]Error loading skill: {exc}[/red]")
        sys.exit(1)


@skill_group.command(name="install")
@click.option(
    "--target",
    "-t",
    type=click.Path(),
    help="Target directory for the skill (e.g. ~/.pi/agent/skills/9router or ./.pi/skills/9router)",
)
@click.option(
    "--global",
    "is_global",
    is_flag=True,
    help="Install to user global agent skills (~/.pi/agent/skills/9router)",
)
@click.pass_context
def install_skill(ctx: click.Context, target: Optional[str], is_global: bool):
    """Install the 9Router skill for agents."""
    as_json = ctx.obj.get("as_json", False) if ctx.obj else False

    if target:
        dest_dir = Path(target).expanduser().resolve()
    elif is_global:
        dest_dir = Path.home() / ".pi" / "agent" / "skills" / "9router"
    else:
        # Check current working directory for .pi/skills or default to global
        cwd_skills = Path.cwd() / ".pi" / "skills"
        if cwd_skills.is_dir():
            dest_dir = cwd_skills / "9router"
        else:
            dest_dir = Path.home() / ".pi" / "agent" / "skills" / "9router"

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / "SKILL.md"
        content = get_skill_content()
        dest_file.write_text(content, encoding="utf-8")

        if as_json:
            print_output({"status": "installed", "path": str(dest_file)}, as_json=True)
        else:
            console.print(f"[green]✔ 9Router skill installed successfully at:[/green] [cyan]{dest_file}[/cyan]")
    except Exception as exc:
        if as_json:
            print_output({"status": "error", "error": str(exc)}, as_json=True)
        else:
            console.print(f"[red]Error installing skill: {exc}[/red]")
        sys.exit(1)
