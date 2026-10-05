from unittest import mock

import click

from phabfive.cli import main
from phabfive.constants import AutoOption
from phabfive.core import Phabfive

URL = "https://phorge.example.com/api/"
TOKEN = "api-" + "a" * 28


def _run_main(dry_run=False, no_dry_run=False):
    """Call the main CLI callback with given dry-run flags and a mock context."""
    ctx = click.Context(click.Command("phabfive"))
    ctx.ensure_object(dict)
    ctx.invoked_subcommand = "maniphest"
    main(
        ctx=ctx,
        verbose=0,
        quiet=0,
        output_format=None,
        ascii_when=AutoOption.auto,
        hyperlink_when=AutoOption.auto,
        version=False,
        skill=False,
        dry_run=dry_run,
        no_dry_run=no_dry_run,
    )
    return ctx


class TestDryRunResolution:
    def test_dry_run_flag(self):
        ctx = _run_main(dry_run=True)
        assert ctx.obj["dry_run"] is True

    def test_no_dry_run_flag(self):
        ctx = _run_main(no_dry_run=True)
        assert ctx.obj["dry_run"] is False

    def test_dry_run_defaults_false(self):
        ctx = _run_main()
        assert ctx.obj["dry_run"] is False

    def test_no_dry_run_overrides_dry_run(self):
        ctx = _run_main(dry_run=True, no_dry_run=True)
        assert ctx.obj["dry_run"] is False

    def test_execute_overrides_env_var(self):
        """--execute (no_dry_run) overrides dry_run=True from env var."""
        ctx = _run_main(dry_run=True, no_dry_run=True)
        assert ctx.obj["dry_run"] is False


class TestPhabfiveDryRunConfig:
    def test_defaults_false(self):
        assert Phabfive._dry_run is False

    def test_config_sets_class_attribute(self):
        with mock.patch("phabfive.core.Phabricator"):
            Phabfive(
                config={
                    "PHAB_URL": URL,
                    "PHAB_TOKEN": TOKEN,
                    "PHABFIVE_DRY_RUN": True,
                }
            )
        assert Phabfive._dry_run is True
        Phabfive._dry_run = False
