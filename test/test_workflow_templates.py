"""Tests for workflow skill templates (Python source of .claude/skills/ and .claude/commands/).

Pins instruction-text contracts from the wire-view-dependency-supplement change:
- propose: dependency-completeness step + pictorial communication-baseline rule
- explore: dependency-chain hint (dependencies / downstream)
- generator: templates still render to valid skill markdown
- dsh adapter: .dsh/skills output with Claude-specific references rewritten
"""
import re

import pytest
import yaml

import dm2.core.templates.workflows  # noqa: F401 — side-effect: populates WORKFLOWS
from dm2.core.templates import WORKFLOWS


def _workflow(workflow_id: str):
    return next(wf for wf in WORKFLOWS if wf.workflow_id == workflow_id)


class TestProposeTemplate:
    def test_has_view_completeness_step(self):
        instr = _workflow("propose").skill.instructions
        assert "视图完整性确认" in instr
        # scans the analyze JSON dependency map
        assert "view_dependencies" in instr
        # supplements missing transitive ancestors
        assert "transitive ancestors" in instr
        assert "P3 supplement" in instr
        # worked example names the OV-2/OV-5a → OV-1 chain
        assert "OV-2" in instr and "OV-5a" in instr and "OV-1" in instr

    def test_has_pictorial_communication_baseline_rule(self):
        instr = _workflow("propose").skill.instructions
        # names all three pictorial views explicitly
        assert "OV-1" in instr and "CV-1" in instr and "AV-1" in instr
        # data-lightness in the monster matrix is not grounds for exclusion
        assert "communication baseline" in instr
        assert "data-light" in instr
        assert "monster matrix" in instr

    def test_guardrails_carry_completeness_and_baseline(self):
        instr = _workflow("propose").skill.instructions
        assert "dependency-complete" in instr
        assert "decision-maker communication baseline" in instr


class TestExploreTemplate:
    def test_has_dependency_chain_hint(self):
        instr = _workflow("explore").skill.instructions
        # agents check both directions of the dependency edge
        assert "dependencies" in instr
        assert "downstream" in instr
        # concrete example: OV-1 is a prerequisite of OV-2 and OV-5a
        assert "OV-1" in instr and "OV-2" in instr and "OV-5a" in instr
        assert "prerequisite of OV-2 and OV-5a" in instr


class TestSkillRegeneration:
    def test_generator_produces_valid_skill_markdown(self, tmp_path):
        from dm2.core.adapters.claude import ClaudeCodeAdapter
        from dm2.core.templates.generator import generate_agent_config

        count = generate_agent_config(tmp_path, "0.0.0-test", ClaudeCodeAdapter())
        # 10 workflows × 2 files (SKILL.md + command .md)
        assert count == len(WORKFLOWS) * 2

        skill_file = tmp_path / ".claude" / "skills" / "dm2-propose-workflow" / "SKILL.md"
        assert skill_file.exists()
        content = skill_file.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert "name: dm2-propose-workflow" in content
        # generated skill carries the new instructions
        assert "视图完整性确认" in content
        assert "communication baseline" in content

        cmd_file = tmp_path / ".claude" / "commands" / "dm2" / "propose.md"
        assert cmd_file.exists()
        assert cmd_file.read_text(encoding="utf-8").startswith("---\n")


class TestDshRenderMapping:
    """Unit tests for the Claude -> DSH reference rewrite layer."""

    @pytest.fixture(scope="class")
    def adapter(self):
        from dm2.core.adapters.dsh import DshAdapter
        return DshAdapter()

    def test_backticked_workflow_reference(self, adapter):
        out = adapter.render_skill_body("Run `/dm2:verify` afterwards.")
        assert out == "Run the `dm2-verify-workflow` skill afterwards."

    def test_backticked_reference_with_angle_arg(self, adapter):
        out = adapter.render_skill_body("Input: `/dm2:propose <system-description>`.")
        assert out == (
            "Input: the `dm2-propose-workflow` skill "
            "(input: <system-description>)."
        )

    def test_bare_workflow_reference(self, adapter):
        out = adapter.render_skill_body(
            "Use after /dm2:apply and /dm2:verify to finalize a change."
        )
        assert out == (
            "Use after the dm2-apply-workflow skill and "
            "the dm2-verify-workflow skill to finalize a change."
        )

    def test_knowledge_pseudo_command_becomes_cli(self, adapter):
        out = adapter.render_skill_body("Run `/dm2:knowledge search <q>` now.")
        assert out == "Run `dm2 knowledge search <q>` now."

    def test_ask_user_tool_renamed(self, adapter):
        out = adapter.render_skill_body("Use the **AskUserQuestion tool** to ask.")
        assert "AskUserQuestion" not in out
        assert "**ask_user_question tool**" in out

    def test_module_invocation_normalized_in_backticks_and_fences(self, adapter):
        out = adapter.render_skill_body(
            "`python3 -m dm2.cli.main change list --json`\n\n"
            "    python3 -m dm2.cli.main knowledge views --json"
        )
        assert "python3 -m dm2.cli.main" not in out
        assert "`dm2 change list --json`" in out
        assert "dm2 knowledge views --json" in out

    def test_unknown_slash_id_left_intact(self, adapter):
        out = adapter.render_skill_body("Run `/dm2:nonexistent` please.")
        assert out == "Run `/dm2:nonexistent` please."

    def test_identity_for_unrelated_text(self, adapter):
        text = "Dependencies OV-1 → OV-2, prerequisite chain. `dm2 knowledge view OV-2`"
        assert adapter.render_skill_body(text) == text


class TestDshAdapterGeneration:
    """DSH project output: .dsh/skills only, frontmatter valid, bodies rewritten."""

    @pytest.fixture(scope="class")
    def generated(self, tmp_path_factory):
        from dm2.core.adapters.dsh import DshAdapter
        from dm2.core.templates.generator import generate_agent_config
        root = tmp_path_factory.mktemp("dsh-project")
        count = generate_agent_config(root, "0.0.0-test", DshAdapter())
        return root, count

    def test_skills_only_file_count(self, generated):
        root, count = generated
        assert count == len(WORKFLOWS)
        assert not (root / ".claude").exists()
        assert not (root / ".dsh" / "commands").exists()

    def test_every_skill_present_with_valid_frontmatter(self, generated):
        root, _ = generated
        name_re = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        for wf in WORKFLOWS:
            skill_file = root / ".dsh" / "skills" / wf.skill_dir / "SKILL.md"
            assert skill_file.exists(), wf.workflow_id
            content = skill_file.read_text(encoding="utf-8")
            assert content.startswith("---\n")
            parts = content.split("---", 2)
            frontmatter = yaml.safe_load(parts[1])
            assert frontmatter["name"] == wf.skill.name
            assert name_re.match(frontmatter["name"])
            assert isinstance(frontmatter["description"], str)
            assert frontmatter["description"].strip()
            assert frontmatter["user-invocable"] is True
            assert frontmatter["metadata"]["generatedBy"] == "dm2-tool/0.0.0-test"

    def test_bodies_have_no_claude_specific_tokens(self, generated):
        root, _ = generated
        ask_user_files = 0
        for wf in WORKFLOWS:
            content = (root / ".dsh" / "skills" / wf.skill_dir / "SKILL.md").read_text()
            assert "/dm2:" not in content, wf.workflow_id
            assert "AskUserQuestion" not in content, wf.workflow_id
            assert "python3 -m dm2.cli.main" not in content, wf.workflow_id
            if "ask_user_question" in content:
                ask_user_files += 1
        # 8 workflows prompt the user interactively (explore/onboard do not)
        assert ask_user_files == 8

    def test_rendered_references_point_to_skills_and_cli(self, generated):
        root, _ = generated
        onboard = (root / ".dsh" / "skills" / "dm2-onboard-workflow" / "SKILL.md").read_text()
        assert "`dm2 knowledge search <q>`" in onboard
        assert "the `dm2-new-workflow` skill" in onboard
        archive = (root / ".dsh" / "skills" / "dm2-archive-workflow" / "SKILL.md").read_text()
        assert "the dm2-apply-workflow skill" in archive
