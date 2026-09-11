"""Formatting helpers for rich tables, trees and json."""

import json
from typing import Any
from rich.console import Console

console = Console()


def print_output(data: Any, as_json: bool = False) -> None:
    if as_json:
        # Use standard print for clean scriptable JSON output to stdout
        print(json.dumps(data, indent=2, default=str))
    else:
        if isinstance(data, (dict, list)):
            console.print(data)
        else:
            console.print(str(data))
