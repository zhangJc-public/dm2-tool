"""Guard that the committed dm2 agent artifacts still match their Python templates.

Specs: openspec/specs/skill-template-generation, openspec/specs/tool-command-adapter

``.claude/skills/dm2-*`` and ``.claude/commands/dm2/`` are generated from
``src/dm2/core/templates/workflows/*.py``, and they are committed because they are
dm2's own product surface: ``dm2 init`` produces exactly these files in a user's
project. That only stays honest if the committed copies never drift from the
templates, which is what this test enforces — the same pattern the repository
already uses for the derived knowledge indexes in ``test_knowledge_indexes.py``.

Only dm2-generated artifacts are covered. Third-party artifacts
(``.claude/skills/openspec-*``, ``.claude/commands/opsx/``) are deliberately not
version-controlled, because their lifecycle belongs to the openspec CLI; see
``.gitignore`` and ``docs/foundation.md``.
"""

import re
from pathlib import Path

import pytest

from dm2.core.adapters.claude import ClaudeCodeAdapter
from dm2.core.templates import WORKFLOWS
from dm2.core.templates.generator import generate_agent_config

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMITTED_SKILLS = REPO_ROOT / ".claude" / "skills"
COMMITTED_COMMANDS = REPO_ROOT / ".claude" / "commands" / "dm2"

#: The tool version is stamped into generated frontmatter. A release bump changes it
#: everywhere at once, so it is normalised out: this test guards *template* drift,
#: not version numbering.
_VERSION_FIELD = re.compile(r'^(  (?:version|generatedBy):\s*)"[^"]*"$', re.MULTILINE)


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
        "（在项目里跑 dm2 init，或调用 generate_agent_config）。"
    )


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory) -> Path:
    """Regenerate the full dm2 agent config into a throwaway directory."""
    target = tmp_path_factory.mktemp("agent-config")
    count = generate_agent_config(target, "0.0.0", ClaudeCodeAdapter())
    assert count == len(WORKFLOWS) * 2, "生成器产出的文件数与工作流数量不符"
    return target


def test_every_registered_workflow_skill_is_committed_and_current(regenerated):
    for workflow in WORKFLOWS:
        _assert_same(
            COMMITTED_SKILLS / workflow.skill_dir / "SKILL.md",
            regenerated / ".claude" / "skills" / workflow.skill_dir / "SKILL.md",
            f"技能 {workflow.skill_dir}",
        )


def test_every_registered_workflow_command_is_committed_and_current(regenerated):
    for workflow in WORKFLOWS:
        _assert_same(
            COMMITTED_COMMANDS / workflow.command_file,
            regenerated / ".claude" / "commands" / "dm2" / workflow.command_file,
            f"命令 {workflow.command_file}",
        )


def test_no_orphan_dm2_skill_directory_is_committed():
    """A workflow removed from the registry must not leave its skill tree behind."""
    registered = {workflow.skill_dir for workflow in WORKFLOWS}
    committed = {path.name for path in COMMITTED_SKILLS.glob("dm2-*") if path.is_dir()}
    assert committed == registered, (
        f"入库的 dm2 技能目录与注册表不符；多出 {sorted(committed - registered)}，"
        f"缺少 {sorted(registered - committed)}"
    )


def test_no_orphan_dm2_command_file_is_committed():
    registered = {workflow.command_file for workflow in WORKFLOWS}
    committed = {path.name for path in COMMITTED_COMMANDS.glob("*.md")}
    assert committed == registered, (
        f"入库的 dm2 命令与注册表不符；多出 {sorted(committed - registered)}，"
        f"缺少 {sorted(registered - committed)}"
    )


def test_third_party_agent_artifacts_are_not_version_controlled():
    """Ownership rule: dm2 guards its own output; the openspec CLI owns its own."""
    gitignore = _read(REPO_ROOT / ".gitignore")
    assert ".claude/skills/openspec-*/" in gitignore
    assert ".claude/commands/opsx/" in gitignore
