"""`views.include_mermaid` / `views.diagram_output` must actually steer the
diagram section the instruction builder injects.

Both keys were documented (`README.md`, `docs/readme.md`) but never read: the
Mermaid section was appended unconditionally, so `views.include_mermaid: false`
silently did nothing. These tests pin the contract.

Config resolution reads the project config from the *current working directory*
at call time, hence the `tmp_dm2_project_cwd` fixture.
"""
import pytest

from dm2.core.agent.instructions import InstructionBuilder
from dm2.core.knowledge.api import KnowledgeAPI


@pytest.fixture(scope="module")
def builder():
    return InstructionBuilder(KnowledgeAPI())


def _write_config(root, body: str) -> None:
    (root / ".dm2" / "config.yaml").write_text(body, encoding="utf-8")


def _sections(builder, view_id: str = "OV-1") -> list[str]:
    return builder.build_view_instructions(view_id, "测试").template["sections"]


class TestIncludeMermaid:
    def test_default_config_injects_mermaid(self, builder, tmp_dm2_project_cwd):
        assert any("Mermaid" in s for s in _sections(builder))

    def test_false_suppresses_the_mermaid_section(self, builder, tmp_dm2_project_cwd):
        _write_config(tmp_dm2_project_cwd, "views:\n  include_mermaid: false\n")
        assert not any("Mermaid" in s for s in _sections(builder))

    def test_table_view_never_gets_a_diagram(self, builder, tmp_dm2_project_cwd):
        assert not any("Mermaid" in s for s in _sections(builder, "OV-3"))


class TestDiagramOutput:
    def test_svg_channel_replaces_mermaid(self, builder, tmp_dm2_project_cwd):
        _write_config(tmp_dm2_project_cwd, "views:\n  diagram_output: svg\n")
        sections = _sections(builder)
        assert not any("Mermaid" in s for s in sections)
        assert any("SVG" in s for s in sections)

    def test_svg_channel_adds_an_explicit_rule(self, builder, tmp_dm2_project_cwd):
        _write_config(tmp_dm2_project_cwd, "views:\n  diagram_output: svg\n")
        rules = builder.build_view_instructions("OV-1", "测试").rules
        assert any("SVG" in r for r in rules)

    def test_unknown_value_falls_back_to_mermaid(self, builder, tmp_dm2_project_cwd):
        _write_config(tmp_dm2_project_cwd, "views:\n  diagram_output: bogus\n")
        assert any("Mermaid" in s for s in _sections(builder))

    def test_svg_channel_leaves_diagram_free_views_alone(self, builder, tmp_dm2_project_cwd):
        _write_config(tmp_dm2_project_cwd, "views:\n  diagram_output: svg\n")
        sections = _sections(builder, "OV-3")
        assert not any("SVG" in s or "Mermaid" in s for s in sections)

    def test_svg_wins_over_include_mermaid(self, builder, tmp_dm2_project_cwd):
        """Explicit `diagram_output: svg` is not overridden by include_mermaid."""
        _write_config(
            tmp_dm2_project_cwd,
            "views:\n  diagram_output: svg\n  include_mermaid: true\n",
        )
        sections = _sections(builder)
        assert not any("Mermaid" in s for s in sections)
        assert any("SVG" in s for s in sections)
