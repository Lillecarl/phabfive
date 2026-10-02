"""The global --dry-run, as every write command reads it."""

from __future__ import annotations

import typer


def resolve_dry_run(ctx: typer.Context, dry_run: bool) -> bool:
    """Whether a write only previews: the command's own --dry-run, or the global switch."""
    return dry_run or bool((ctx.obj or {}).get("dry_run"))
