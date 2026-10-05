"""Resolve the global dry-run switch against a command's own --dry-run flag."""

from __future__ import annotations

import typer


def resolve_dry_run(ctx: typer.Context, dry_run: bool) -> bool:
    """Whether a write previews only.

    The command's own --dry-run always previews. Otherwise the global switch
    decides: --dry-run or PHABFIVE_DRY_RUN at the top level, unless
    --no-dry-run/--execute turned it off in the main callback.
    """
    if dry_run:
        return True
    if ctx.obj:
        return bool(ctx.obj.get("dry_run", False))
    return False
