"""`views.formats` decides a view's carrier.

A view has two independent properties:

* ``representation`` — what information structure it conveys (fixed by the view)
* ``format`` — how that structure is carried (a project decision)

These tests pin the resolution order, the per-representation defaults, and the
fact that the two pre-`formats` switches no longer have any effect.
"""
import pytest

from dm2.core.agent.instructions import InstructionBuilder
from dm2.core.knowledge.api import KnowledgeAPI

#: state-diagram → mermaid by default
MERMAID_VIEW = "OV-6b"
#: table → markdown by default
TABLE_VIEW = "OV-3"
#: pictorial → svg by default
PICTORIAL_VIEW = "OV-1"


@pytest.fixture(scope="module")
def builder():
    return InstructionBuilder(KnowledgeAPI())


def _write_config(root, body: str) -> None:
    (root / ".dm2" / "config.yaml").write_text(body, encoding="utf-8")


def _template(builder, view_id: str) -> dict:
    return builder.build_view_instructions(view_id, "测试").template


def _sections(builder, view_id: str) -> list[str]:
    return _template(builder, view_id)["sections"]


class TestRepresentationDefaults:
    def test_diagram_views_default_to_mermaid(self, builder, tmp_dm2_project_cwd):
        template = _template(builder, MERMAID_VIEW)
        assert template["format"] == "mermaid"
        assert template["format_source"] == "representation_default"
        assert any("Mermaid" in s for s in template["sections"])

    def test_table_views_default_to_markdown(self, builder, tmp_dm2_project_cwd):
        template = _template(builder, TABLE_VIEW)
        assert template["format"] == "markdown"
        assert not any("Mermaid" in s or "SVG" in s for s in template["sections"])

    def test_pictorial_defaults_to_svg(self, builder, tmp_dm2_project_cwd):
        """A concept graphic carries meaning in layout; Mermaid flattens it."""
        template = _template(builder, PICTORIAL_VIEW)
        assert template["representation"] == "pictorial"
        assert template["format"] == "svg"
        assert any("SVG" in s for s in template["sections"])
        assert not any("Mermaid" in s for s in template["sections"])

    def test_template_always_reports_the_resolved_format(self, builder, tmp_dm2_project_cwd):
        for view_id in (MERMAID_VIEW, TABLE_VIEW, PICTORIAL_VIEW):
            template = _template(builder, view_id)
            assert template["format"]
            assert template["format_source"]


class TestFormatOverrides:
    def test_per_view_override(self, builder, tmp_dm2_project_cwd):
        _write_config(
            tmp_dm2_project_cwd,
            "views:\n  formats:\n    overrides:\n      OV-1: mermaid\n",
        )
        template = _template(builder, PICTORIAL_VIEW)
        assert template["format"] == "mermaid"
        assert template["format_source"] == "override"
        assert any("Mermaid" in s for s in template["sections"])

    def test_project_default_shifts_diagram_views(self, builder, tmp_dm2_project_cwd):
        _write_config(tmp_dm2_project_cwd, "views:\n  formats:\n    default: svg\n")
        template = _template(builder, MERMAID_VIEW)
        assert template["format"] == "svg"
        assert template["format_source"] == "project_default"
        assert any("SVG" in s for s in template["sections"])

    def test_project_default_leaves_prose_views_alone(self, builder, tmp_dm2_project_cwd):
        """`default: svg` shifts diagrams; a table view stays markdown."""
        _write_config(tmp_dm2_project_cwd, "views:\n  formats:\n    default: svg\n")
        assert _template(builder, TABLE_VIEW)["format"] == "markdown"

    def test_incompatible_override_is_ignored(self, builder, tmp_dm2_project_cwd):
        _write_config(
            tmp_dm2_project_cwd,
            "views:\n  formats:\n    overrides:\n      OV-3: mermaid\n",
        )
        template = _template(builder, TABLE_VIEW)
        assert template["format"] == "markdown"
        assert template["format_source"] == "representation_default"

    def test_override_beats_project_default(self, builder, tmp_dm2_project_cwd):
        _write_config(
            tmp_dm2_project_cwd,
            "views:\n  formats:\n    default: svg\n    overrides:\n      OV-6b: mermaid\n",
        )
        template = _template(builder, MERMAID_VIEW)
        assert template["format"] == "mermaid"
        assert template["format_source"] == "override"


class TestExternalFormats:
    def test_external_format_gets_an_artifact_section(self, builder, tmp_dm2_project_cwd):
        _write_config(
            tmp_dm2_project_cwd,
            "views:\n  formats:\n    overrides:\n      OV-3: xlsx\n",
        )
        template = _template(builder, TABLE_VIEW)
        assert template["format"] == "xlsx"
        assert any("xlsx" in s for s in template["sections"])
        rules = builder.build_view_instructions(TABLE_VIEW, "测试").rules
        assert any("外部提供" in rule for rule in rules)

    def test_video_is_a_valid_pictorial_carrier(self, builder, tmp_dm2_project_cwd):
        _write_config(
            tmp_dm2_project_cwd,
            "views:\n  formats:\n    overrides:\n      OV-1: mp4\n",
        )
        template = _template(builder, PICTORIAL_VIEW)
        assert template["format"] == "mp4"
        assert any("mp4" in s for s in template["sections"])


class TestRemovedKeys:
    """`include_mermaid` / `diagram_output` were removed in favour of `formats`."""

    def test_include_mermaid_is_no_longer_read(self, builder, tmp_dm2_project_cwd):
        _write_config(tmp_dm2_project_cwd, "views:\n  include_mermaid: false\n")
        assert _template(builder, MERMAID_VIEW)["format"] == "mermaid"

    def test_diagram_output_is_no_longer_read(self, builder, tmp_dm2_project_cwd):
        _write_config(tmp_dm2_project_cwd, "views:\n  diagram_output: svg\n")
        assert _template(builder, MERMAID_VIEW)["format"] == "mermaid"

    def test_formats_is_the_only_switch(self, builder, tmp_dm2_project_cwd):
        _write_config(tmp_dm2_project_cwd, "views:\n  formats:\n    default: svg\n")
        assert _template(builder, MERMAID_VIEW)["format"] == "svg"
