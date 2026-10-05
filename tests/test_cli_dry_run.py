import inspect
from unittest.mock import patch

import click
import typer
from typer.testing import CliRunner

from phabfive.cli import app, preprocess_monograms
from tests.test_write_command_formats import a_maniphest, a_paste

runner = CliRunner()


def _write_commands(group: click.Group, path: str = ""):
    for name, command in group.commands.items():
        if isinstance(command, click.Group):
            yield from _write_commands(command, f"{path} {name}")
        elif any(param.name == "dry_run" for param in command.params):
            yield f"{path} {name}".strip(), command


def _comment(args, env=None):
    maniphest = a_maniphest(task_id=7)
    with patch("phabfive.cli.maniphest._get_maniphest_app", return_value=maniphest):
        result = runner.invoke(app, args, env=env)
    assert result.exit_code == 0, result.output
    return maniphest


class TestEveryWriteCommand:
    def test_reads_the_global_switch(self):
        # A command with its own --dry-run that skips resolve_dry_run writes
        # under `phabfive --dry-run`
        commands = dict(_write_commands(typer.main.get_command(app)))
        assert {"edit", "maniphest comment", "diffusion repo nudge"} <= set(commands)
        missing = [
            path
            for path, command in commands.items()
            if "resolve_dry_run(ctx, dry_run)"
            not in inspect.getsource(command.callback)
        ]
        assert missing == []


class TestGlobalDryRun:
    def test_previews_a_comment(self):
        maniphest = _comment(["--dry-run", "maniphest", "comment", "T7", "hi"])
        maniphest.add_task_comment.assert_not_called()

    def test_reaches_the_monogram_shortcut(self):
        args = preprocess_monograms(["phabfive", "--dry-run", "T7", "hi"])[1:]
        maniphest = _comment(args)
        maniphest.add_task_comment.assert_not_called()

    def test_previews_a_paste_comment(self):
        paste = a_paste(paste_id=42)
        with patch("phabfive.cli.paste._get_paste_app", return_value=paste):
            result = runner.invoke(app, ["--dry-run", "paste", "comment", "P42", "hi"])
        assert result.exit_code == 0, result.output
        paste.add_paste_comment.assert_not_called()

    def test_comes_from_the_environment(self):
        maniphest = _comment(
            ["maniphest", "comment", "T7", "hi"], env={"PHAB_DRY_RUN": "1"}
        )
        maniphest.add_task_comment.assert_not_called()

    def test_execute_overrides_the_environment(self):
        maniphest = _comment(
            ["--execute", "maniphest", "comment", "T7", "hi"],
            env={"PHAB_DRY_RUN": "1"},
        )
        maniphest.add_task_comment.assert_called_once()

    def test_no_dry_run_overrides_the_environment(self):
        maniphest = _comment(
            ["--no-dry-run", "maniphest", "comment", "T7", "hi"],
            env={"PHAB_DRY_RUN": "1"},
        )
        maniphest.add_task_comment.assert_called_once()

    def test_off_by_default(self):
        maniphest = _comment(["maniphest", "comment", "T7", "hi"])
        maniphest.add_task_comment.assert_called_once()

    def test_a_command_flag_still_previews(self):
        maniphest = _comment(["maniphest", "comment", "T7", "hi", "--dry-run"])
        maniphest.add_task_comment.assert_not_called()
