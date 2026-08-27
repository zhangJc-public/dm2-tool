"""Tests for workflow skill templates (Python source of .claude/skills/ and .claude/commands/).

Pins instruction-text contracts from the wire-view-dependency-supplement change:
- propose: dependency-completeness step + pictorial communication-baseline rule
- explore: dependency-chain hint (dependencies / downstream)
- generator: templates still render to valid skill markdown
"""
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
