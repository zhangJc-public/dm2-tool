"""Guard the CLI JSON contract.

Spec: openspec/specs/cli-json-contract

Two invariants are covered:

1. Every non-exempt command accepts ``--json``, including agent-facing commands that
   emit the envelope unconditionally (the skill templates say "always pass `--json`").
2. A project-guard failure emits a ``NOT_IN_PROJECT`` envelope on stdout instead of
   plain text, and leaves no stray ``.dm2/`` behind.
"""

import json

import pytest
from typer.testing import CliRunner

from dm2.cli.main import app

#: Commands that cannot honour the JSON contract, each for a stated reason.
#: ``completion`` prints a shell script; ``__complete`` is an internal shell protocol;
#: ``uninstall`` is an interactive human maintenance command. Keep in sync with the spec.
EXEMPT = {"completion", "__complete", "uninstall"}

#: Commands that read or mutate project/architecture state and therefore must fail
#: with an envelope when run outside a ``.dm2`` project.
PROJECT_COMMANDS = [
    ["list"],
    ["status"],
    ["change", "new", "demo-change"],
    ["change", "status"],
    ["change", "list-changes"],
    ["change", "archive-change", "demo-change"],
    ["view", "list"],
    ["view", "register", "OV-1", "-c", "demo-change"],
    ["validate", "--all"],
    ["run", "--status"],
    ["run", "--agent", "-d", "demo system"],
]


def _walk(typer_app, prefix=()):
    """Yield the argument path of every registered command, including sub-commands.

    Typer derives a command name from the callback's function name, replacing
    underscores with dashes, so the fallback must do the same or the paths will not
    be invocable.
    """
    for command in typer_app.registered_commands:
        name = command.name
        if not name and command.callback is not None:
            name = command.callback.__name__.replace("_", "-")
        if name:
            yield tuple(prefix) + (name,)
    for group in typer_app.registered_groups:
        if group.typer_instance is None:
            continue
        yield from _walk(group.typer_instance, tuple(prefix) + (group.name,))


ALL_COMMANDS = sorted(_walk(app))


def test_command_discovery_is_not_empty():
    """Guard against the enumeration silently returning nothing and passing vacuously."""
    assert len(ALL_COMMANDS) > 30, ALL_COMMANDS


def test_exempt_set_is_stable():
    """An exemption is a decision, not an accident: the documented set is pinned here."""
    assert EXEMPT == {"completion", "__complete", "uninstall"}


def test_every_non_exempt_command_accepts_json():
    """Non-exempt commands must accept the documented ``--json`` flag."""
    runner = CliRunner()
    offenders = []
    for path in ALL_COMMANDS:
        if path[-1] in EXEMPT:
            continue
        result = runner.invoke(app, [*path, "--help"])
        if "--json" not in result.stdout:
            offenders.append(" ".join(path))
    assert not offenders, f"以下命令未接受 --json（或应加入豁免清单）: {offenders}"


@pytest.mark.parametrize("args", PROJECT_COMMANDS, ids=lambda a: " ".join(a))
def test_guard_failure_emits_envelope(args, tmp_path, monkeypatch):
    """Outside a project, JSON mode must produce an envelope and write nothing."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, [*args, "--json"])

    payload = json.loads(result.stdout)
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "NOT_IN_PROJECT"
    assert result.exit_code != 0
    assert not (tmp_path / ".dm2").exists(), "项目外调用不得创建 .dm2/"


@pytest.mark.parametrize("args", PROJECT_COMMANDS[:2], ids=lambda a: " ".join(a))
def test_human_mode_keeps_chinese_message(args, tmp_path, monkeypatch):
    """Commands with a human-readable mode keep their plain-text failure."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, args)
    assert result.exit_code != 0
    assert "不在 .dm2 项目中" in result.stdout
    assert not (tmp_path / ".dm2").exists()
