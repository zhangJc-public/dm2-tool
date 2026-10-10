"""Guard that the committed dm2 agent artifacts still match their Python templates.

Specs: openspec/specs/skill-template-generation, openspec/specs/tool-command-adapter

``.claude/skills/dm2-*`` + ``.claude/commands/dm2/`` (Claude Code) and
``.dsh/skills/dm2-*`` (DeepSeek Harness) are generated from
``src/dm2/core/templates/workflows/*.py``, and they are committed because they are
dm2's own product surface: ``dm2 init`` produces exactly these files in a user's
project. That only stays honest if the committed copies never drift from the
templates, which is what this test enforces — the same pattern the repository
already uses for the derived knowledge indexes in ``test_knowledge_indexes.py``.

Only dm2-generated artifacts are covered. Third-party artifacts
(``.claude/skills/openspec-*``, ``.claude/commands/opsx/``,
``.agents/skills/openspec-*``) are deliberately not version-controlled, because
their lifecycle belongs to the openspec CLI; see ``.gitignore`` and
``docs/foundation.md``.

Regenerate the committed copies with ``python3 scripts/render_agent_config.py``.
"""

import re
from pathlib import Path

import pytest

from dm2.core.adapters.claude import ClaudeCodeAdapter
from dm2.core.adapters.dsh import DshAdapter
from dm2.core.templates import WORKFLOWS
from dm2.core.templates.generator import generate_agent_config

REPO_ROOT = Path(__file__).resolve().parent.parent

#: Committed skill root per tool adapter.
COMMITTED_SKILLS = {
    "claude": REPO_ROOT / ".claude" / "skills",
    "dsh": REPO_ROOT / ".dsh" / "skills",
}

#: Tools with a command surface (the dsh adapter emits skills only).
COMMITTED_COMMANDS = {
    "claude": REPO_ROOT / ".claude" / "commands" / "dm2",
}

_ADAPTERS = {"claude": ClaudeCodeAdapter, "dsh": DshAdapter}

#: The tool version is stamped into generated frontmatter. A release bump changes it
#: everywhere at once, so it is normalised out: this test guards *template* drift,
#: not version numbering.
_VERSION_FIELD = re.compile(r'^(  (?:version|generatedBy):\s*)"[^"]*"$', re.MULTILINE)


def _adapter(tool_id: str):
    return _ADAPTERS[tool_id]()


def _normalize(text: str) -> str:
    return _VERSION_FIELD.sub(r'\1"<version>"', text)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_same(committed: Path, fresh: Path, label: str) -> None:
    assert committed.exists(), f"{label} 未入库：{committed.relative_to(REPO_ROOT)}"
    committed_text = _normalize(_read(committed))
    fresh_text = _normalize(_read(fresh))
    assert committed_text == fresh_text, (
        f"{label} 与模板不一致：{committed.relative_to(REPO_ROOT)}\n"
        "改了 src/dm2/core/templates/workflows/ 之后必须重新生成并提交"
        "（运行 python3 scripts/render_agent_config.py）。"
    )


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory) -> Path:
    """Regenerate every adapter's agent config into a throwaway directory."""
    target = tmp_path_factory.mktemp("agent-config")
    for tool_id, adapter_cls in _ADAPTERS.items():
        adapter = adapter_cls()
        count = generate_agent_config(target, "0.0.0", adapter)
        expected = len(WORKFLOWS) * (2 if adapter.supports_commands else 1)
        assert count == expected, f"{tool_id} 生成器产出的文件数与工作流数量不符"
    return target


@pytest.mark.parametrize("tool_id", sorted(COMMITTED_SKILLS))
def test_every_registered_workflow_skill_is_committed_and_current(tool_id, regenerated):
    adapter = _adapter(tool_id)
    for workflow in WORKFLOWS:
        rel = Path(adapter.get_skills_dir()) / workflow.skill_dir / "SKILL.md"
        _assert_same(
            COMMITTED_SKILLS[tool_id] / workflow.skill_dir / "SKILL.md",
            regenerated / rel,
            f"{tool_id} 技能 {workflow.skill_dir}",
        )


def test_every_registered_workflow_command_is_committed_and_current(regenerated):
    adapter = _adapter("claude")
    for workflow in WORKFLOWS:
        rel = Path(adapter.get_commands_dir()) / workflow.command_file
        _assert_same(
            COMMITTED_COMMANDS["claude"] / workflow.command_file,
            regenerated / rel,
            f"命令 {workflow.command_file}",
        )


def test_dsh_adapter_emits_no_command_files(regenerated):
    """DSH has no project-level command directory; skills are the only surface."""
    assert not (regenerated / ".dsh" / "commands").exists()


@pytest.mark.parametrize("tool_id", sorted(COMMITTED_SKILLS))
def test_no_orphan_dm2_skill_directory_is_committed(tool_id):
    """A workflow removed from the registry must not leave its skill tree behind."""
    registered = {workflow.skill_dir for workflow in WORKFLOWS}
    committed = {path.name for path in COMMITTED_SKILLS[tool_id].glob("dm2-*") if path.is_dir()}
    assert committed == registered, (
        f"{tool_id}: 入库的 dm2 技能目录与注册表不符；多出 {sorted(committed - registered)}，"
        f"缺少 {sorted(registered - committed)}"
    )


def test_no_orphan_dm2_command_file_is_committed():
    registered = {workflow.command_file for workflow in WORKFLOWS}
    committed = {path.name for path in COMMITTED_COMMANDS["claude"].glob("*.md")}
    assert committed == registered, (
        f"入库的 dm2 命令与注册表不符；多出 {sorted(committed - registered)}，"
        f"缺少 {sorted(registered - committed)}"
    )


def test_third_party_agent_artifacts_are_not_version_controlled():
    """Ownership rule: dm2 guards its own output; the openspec CLI owns its own."""
    gitignore = _read(REPO_ROOT / ".gitignore")
    assert ".claude/skills/openspec-*/" in gitignore
    assert ".claude/commands/opsx/" in gitignore
    assert ".agents/skills/openspec-*/" in gitignore
    assert ".agents/skills/.openspec-target" in gitignore
