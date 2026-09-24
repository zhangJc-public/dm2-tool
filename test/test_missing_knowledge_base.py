"""Guard: an unresolvable knowledge base is reported, never silently empty.

Spec: openspec/specs/dm2-metamodel-knowledge — "An unresolvable knowledge base is a
reported failure".

Before this, `get_reference_path()` returned a path that did not exist when neither the
project copy nor the packaged copy was present. A non-editable install therefore answered
`dm2 knowledge stats` with zeros and exit 0, and `dm2 concern list` with "no templates" —
a silent wrong answer rather than a failure. These tests pin the loud behaviour.
"""

import json
import sys

import pytest

from dm2.cli import main as cli_main
from dm2.cli.commands import concern as concern_cmd
from dm2.utils import paths

#: A module path whose four-parent walk lands on a directory with no `dm2-reference/`.
_FAKE_PATHS_FILE = "/tmp/dm2-missing-kb/a/b/c/d/paths.py"
#: Same trick for concern.py, which walks five parents up.
_FAKE_CONCERN_FILE = "/tmp/dm2-missing-kb/a/b/c/d/e/concern.py"


@pytest.fixture
def missing_knowledge_base(monkeypatch, tmp_path):
    """Make both reference candidates unresolvable without touching the real repo."""
    monkeypatch.chdir(tmp_path)  # tmp_path has no .dm2 project above it
    monkeypatch.setattr(paths, "__file__", _FAKE_PATHS_FILE)
    return tmp_path


# ── resolution ───────────────────────────────────────────────────────────────


def test_resolution_raises_when_neither_candidate_exists(missing_knowledge_base):
    with pytest.raises(paths.KnowledgeBaseNotFound):
        paths.get_reference_path()


def test_resolution_message_names_both_candidates(missing_knowledge_base):
    """The message must be actionable: what was checked, and how to fix it."""
    with pytest.raises(paths.KnowledgeBaseNotFound) as exc:
        paths.get_reference_path()
    message = str(exc.value)
    assert "项目本地副本" in message
    assert "包内置副本" in message
    assert "dm2 init" in message


def test_resolution_still_finds_the_real_knowledge_base():
    """Over-strictness guard: the normal checkout path keeps working."""
    resolved = paths.get_reference_path()
    assert resolved.is_dir()
    assert (resolved / "views.yaml").exists()


def test_concerns_resolution_raises_when_file_is_absent(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(concern_cmd, "__file__", _FAKE_CONCERN_FILE)
    with pytest.raises(paths.KnowledgeBaseNotFound):
        concern_cmd._get_concerns_path()


# ── CLI reporting ────────────────────────────────────────────────────────────


@pytest.mark.parametrize("json_flag", ["--json", "-j"])
def test_json_mode_emits_kb_not_found_envelope(
    missing_knowledge_base, monkeypatch, capsys, json_flag
):
    monkeypatch.setattr(sys, "argv", ["dm2", "knowledge", "stats", json_flag])
    with pytest.raises(SystemExit) as exc:
        cli_main._invoke_app()
    assert exc.value.code == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "KB_NOT_FOUND"
    assert payload["error"]["message"]


def test_human_mode_prints_a_message_not_a_traceback(
    missing_knowledge_base, monkeypatch, capsys
):
    monkeypatch.setattr(sys, "argv", ["dm2", "knowledge", "stats"])
    with pytest.raises(SystemExit) as exc:
        cli_main._invoke_app()
    assert exc.value.code == 1

    out = capsys.readouterr().out
    assert out.startswith("错误: ")
    assert "未找到 DM2 知识库" in out
    assert "Traceback" not in out


def test_debug_mode_reraises_for_developers(missing_knowledge_base, monkeypatch):
    """DM2_DEBUG keeps the traceback available instead of converting it."""
    monkeypatch.setenv("DM2_DEBUG", "1")
    monkeypatch.setattr(sys, "argv", ["dm2", "knowledge", "stats"])
    with pytest.raises(paths.KnowledgeBaseNotFound):
        cli_main._invoke_app()
