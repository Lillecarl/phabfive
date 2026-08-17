# -*- coding: utf-8 -*-
"""Edit commands for phabfive CLI."""

import sys
from typing import List, Optional

import typer

from phabfive.cli.completers import (
    complete_column,
    complete_priority,
    complete_status,
    complete_tag,
)
from phabfive.exceptions import PhabfiveConfigException


def _get_edit_app():
    """Get Edit app instance with config error handling."""
    import requests

    from phabfive.edit import Edit

    try:
        return Edit()
    except PhabfiveConfigException as e:
        from phabfive.setup import offer_setup_on_error

        if not offer_setup_on_error(str(e)):
            raise typer.Exit(1)
        # If setup succeeded, try again
        return Edit()
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"Error: Failed to connect to Phabricator API: {e}\n")
        raise typer.Exit(1)


def edit_command(
    ctx: typer.Context,
    object_id: Optional[str] = typer.Argument(
        None,
        help="Object monogram(s) to edit (e.g., T123 or T123,T124,T125). Routes to app-specific edit command. If omitted, reads YAML from stdin.",
    ),
    priority: Optional[str] = typer.Option(
        None,
        "--priority",
        help="Set priority (unbreak, high, normal, low, wish) or use raise/lower to navigate",
        autocompletion=complete_priority,
    ),
    status: Optional[str] = typer.Option(
        None,
        "--status",
        help="Set status: open, resolved, wontfix, invalid, duplicate, etc.",
        autocompletion=complete_status,
    ),
    tag: Optional[str] = typer.Option(
        None,
        "--tag",
        help="Specify board context for --column (also adds task to board if needed)",
        autocompletion=complete_tag,
    ),
    column: Optional[str] = typer.Option(
        None,
        "--column",
        help="Set column by name, or use forward/backward to navigate",
        autocompletion=complete_column,
    ),
    assign: Optional[str] = typer.Option(
        None,
        "--assign",
        help="Set assignee (username or @me for yourself)",
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        help="Set description (use - to read from stdin, or omit all options to open $EDITOR)",
    ),
    subscribe: Optional[List[str]] = typer.Option(
        None,
        "--subscribe",
        help="Add subscriber (username or @me, repeatable)",
    ),
    comment: Optional[str] = typer.Option(
        None,
        "--comment",
        help="Add comment with changes",
    ),
    parents: Optional[str] = typer.Option(
        None,
        "--parents",
        help="Set parent tasks (comma-separated monograms, e.g., T456,T789)",
    ),
    depends_on: Optional[str] = typer.Option(
        None,
        "--depends-on",
        help="Set subtasks (comma-separated monograms, e.g., T456,T789)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Skip confirmation prompt (required for non-interactive use)",
    ),
) -> None:
    """Edit monograms (routes to app-specific edit command)

    Expands to app-specific edit commands based on monogram prefix:
    - phabfive edit T123 → phabfive maniphest edit T123
    - phabfive edit P456 → phabfive paste edit P456 (planned)
    - phabfive edit K789 → phabfive passphrase edit K789 (planned)

    For piped input, this command reads YAML from stdin.

    Examples:
        phabfive edit T123 --priority=raise --status=resolved
        phabfive maniphest search --tag "Backend" | phabfive edit --column=Done
        phabfive edit T123 --tag="Sprint" --column=forward --comment="Moving forward"
        phabfive edit T123 --parents=T456,T789
        phabfive edit T123 --depends-on=T456,T789
    """
    dry_run = ctx.obj["dry_run"]
    edit_handler = _get_edit_app()

    # Parse parents list
    parent_list = None
    if parents:
        parent_list = [p.strip() for p in parents.split(",") if p.strip()]

    # Parse depends-on list
    depends_on_list = None
    if depends_on:
        depends_on_list = [p.strip() for p in depends_on.split(",") if p.strip()]

    retcode = edit_handler.edit_objects(
        object_id=object_id,
        priority=priority,
        status=status,
        tag=tag,
        column=column,
        assign=assign,
        description=description,
        subscribe=subscribe,
        comment=comment,
        parents=parent_list,
        depends_on=depends_on_list,
        dry_run=dry_run,
        force=force,
    )

    raise typer.Exit(retcode)
