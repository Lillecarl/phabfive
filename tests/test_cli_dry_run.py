import click

from phabfive.cli import main
from phabfive.constants import AutoOption, LogLevel


def _run_main(dry_run=False, no_dry_run=False):
    """Call the main CLI callback with given dry-run flags and a mock context."""
    ctx = click.Context(click.Command("phabfive"))
    ctx.ensure_object(dict)
    main(
        ctx=ctx,
        log_level=LogLevel.INFO,
        output_format=None,
        ascii_when=AutoOption.auto,
        hyperlink_when=AutoOption.auto,
        version=False,
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

    def test_env_var_parsed_as_true(self):
        """Click passes dry_run=True when PHABFIVE_DRY_RUN=true is set."""
        ctx = _run_main(dry_run=True)
        assert ctx.obj["dry_run"] is True

    def test_env_var_parsed_as_false(self):
        """Click passes dry_run=False when PHABFIVE_DRY_RUN=false is set."""
        ctx = _run_main(dry_run=False)
        assert ctx.obj["dry_run"] is False

    def test_execute_overrides_env_var(self):
        """--execute (no_dry_run) overrides dry_run=True from env var."""
        ctx = _run_main(dry_run=True, no_dry_run=True)
        assert ctx.obj["dry_run"] is False
