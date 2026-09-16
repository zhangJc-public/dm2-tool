"""Tests for `dm2 init --tool claude|dsh`."""

import json

import pytest
from typer.testing import CliRunner


@pytest.fixture
def chdir_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _run(*args: str):
    from dm2.cli.main import app
    return CliRunner().invoke(app, ["init", *args])


def _json_payload(result):
    return json.loads(result.stdout)


def test_init_dsh_emits_dsh_skills(chdir_tmp):
    result = _run(".", "--tool", "dsh", "--json")
    assert result.exit_code == 0, result.stdout
    payload = _json_payload(result)
    assert payload["status"] == "success"
    agent_config = payload["data"]["agent_config"]
    assert agent_config == {
        "tool": "dsh",
        "files_generated": 10,
        "skills_dir": ".dsh/skills",
        "commands_dir": None,
        "commands": False,
    }
    assert (chdir_tmp / ".dsh" / "skills" / "dm2-explore-workflow" / "SKILL.md").exists()
    assert not (chdir_tmp / ".claude").exists()
    assert (chdir_tmp / ".dm2" / "reference" / "views.yaml").exists()
    assert (chdir_tmp / ".dm2" / "reference" / "cynefin-keywords.yaml").exists()


def test_init_defaults_to_claude(chdir_tmp):
    result = _run(".", "--json")
    assert result.exit_code == 0, result.stdout
    agent_config = _json_payload(result)["data"]["agent_config"]
    assert agent_config["tool"] == "claude"
    assert agent_config["commands"] is True
    assert agent_config["files_generated"] == 20
    assert (chdir_tmp / ".claude" / "skills" / "dm2-explore-workflow" / "SKILL.md").exists()
    assert (chdir_tmp / ".claude" / "commands" / "dm2" / "explore.md").exists()


def test_init_explicit_claude_flag(chdir_tmp):
    result = _run(".", "-t", "claude", "--json")
    assert result.exit_code == 0
    assert _json_payload(result)["data"]["agent_config"]["tool"] == "claude"


def test_init_unknown_tool_returns_invalid_tool_json(chdir_tmp):
    result = _run(".", "-t", "bogus", "--json")
    assert result.exit_code == 1
    payload = _json_payload(result)
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "INVALID_TOOL"


def test_get_adapter_registry():
    from dm2.core.adapters import get_adapter
    from dm2.core.adapters.claude import ClaudeCodeAdapter
    from dm2.core.adapters.dsh import DshAdapter

    assert isinstance(get_adapter("claude"), ClaudeCodeAdapter)
    assert isinstance(get_adapter("dsh"), DshAdapter)
    with pytest.raises(ValueError):
        get_adapter("cursor")
