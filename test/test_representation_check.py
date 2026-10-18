"""Tests for `dm2.reasoning.representation.RepresentationChecker`.

The checker compares a view's *representation* (what structure it conveys) and
its resolved *format* (how that structure is carried) with what the file
actually contains. These tests pin each carrier's evidence rule and the severity
policy. Format resolution is injected so the tests stay independent of config.
"""
from types import SimpleNamespace

from dm2.reasoning.consistency import IssueSeverity
from dm2.reasoning.representation import RepresentationChecker

MERMAID_GRAPH = "```mermaid\ngraph TD\n    A --> B\n```"
MERMAID_STATE = "```mermaid\nstateDiagram\n    [*] --> A\n```"
SVG_REF = "![图示](OV-1.svg)"
PNG_REF = "![图示](OV-1.png)"
XLSX_REF = "明细见 data.xlsx"
MP4_REF = "概念动画见 concept.mp4"


class _FakeKnowledge:
    """Minimal stand-in for KnowledgeAPI.get_view()."""

    def __init__(self, representations: dict[str, str]):
        self._representations = representations

    def get_view(self, view_id):
        if view_id not in self._representations:
            return None
        return SimpleNamespace(representation=self._representations[view_id])


def _check(representation: str, content: str, fmt: str, source: str = "test"):
    checker = RepresentationChecker(
        _FakeKnowledge({"X-1": representation}),
        format_resolver=lambda _view_id, _rep: (fmt, source),
    )
    return checker.check({"X-1": content})


class TestMarkdownCarrier:
    def test_mermaid_in_a_markdown_view_is_reported(self):
        issues = _check("table", MERMAID_GRAPH, "markdown")
        assert [i.issue_type for i in issues] == ["representation_unexpected_diagram"]

    def test_plain_table_is_accepted(self):
        assert _check("table", "| a | b |\n|---|---|", "markdown") == []

    def test_supporting_figure_is_allowed(self):
        """A markdown view may reference an illustration; only Mermaid is the carrier."""
        assert _check("table", "见 " + SVG_REF, "markdown") == []


class TestMermaidCarrier:
    def test_matching_mermaid_is_accepted(self):
        assert _check("state-diagram", MERMAID_STATE, "mermaid") == []

    def test_graph_family_is_interchangeable(self):
        # node-link maps to `graph`; `flowchart` is the same family.
        assert _check(
            "node-link", "```mermaid\nflowchart TD\n    A --> B\n```", "mermaid"
        ) == []

    def test_missing_diagram_is_reported(self):
        issues = _check("state-diagram", "# 只有文字", "mermaid")
        assert [i.issue_type for i in issues] == ["representation_missing_diagram"]
        assert issues[0].severity is IssueSeverity.WARNING
        assert issues[0].view_id == "X-1"

    def test_wrong_mermaid_type_is_reported(self):
        issues = _check("state-diagram", MERMAID_GRAPH, "mermaid")
        assert [i.issue_type for i in issues] == ["representation_mismatch"]

    def test_figure_instead_of_declared_mermaid_is_reported(self):
        issues = _check("node-link", SVG_REF, "mermaid")
        assert [i.issue_type for i in issues] == ["representation_mismatch"]

    def test_mermaid_and_figure_together_is_informational(self):
        issues = _check("node-link", MERMAID_GRAPH + "\n" + SVG_REF, "mermaid")
        assert [i.issue_type for i in issues] == ["representation_mixed"]
        assert issues[0].severity is IssueSeverity.INFO


class TestFigureCarrier:
    def test_svg_reference_is_accepted(self):
        assert _check("pictorial", SVG_REF, "svg") == []

    def test_plain_mention_counts(self):
        assert _check("pictorial", "详见 OV-1.svg 的版面标注", "svg") == []

    def test_missing_svg_is_reported(self):
        issues = _check("pictorial", "# 只有文字", "svg")
        assert [i.issue_type for i in issues] == ["representation_missing_artifact"]

    def test_mermaid_in_a_declared_svg_view_is_reported(self):
        issues = _check("pictorial", MERMAID_GRAPH, "svg")
        assert [i.issue_type for i in issues] == ["representation_mismatch"]

    def test_png_carrier_accepts_a_jpeg(self):
        assert _check("pictorial", "![图](shot.jpeg)", "png") == []


class TestExternalCarrier:
    def test_xlsx_reference_is_accepted(self):
        assert _check("table", XLSX_REF, "xlsx") == []

    def test_missing_xlsx_is_reported(self):
        issues = _check("table", "| a | b |", "xlsx")
        assert [i.issue_type for i in issues] == ["representation_missing_artifact"]

    def test_video_reference_is_accepted(self):
        assert _check("pictorial", MP4_REF, "mp4") == []


class TestSeverityPolicy:
    def test_warning_by_default(self):
        issues = _check("table", MERMAID_GRAPH, "markdown")
        assert issues[0].severity is IssueSeverity.WARNING

    def test_strict_mode_promotes_to_error(self, tmp_dm2_project_cwd):
        (tmp_dm2_project_cwd / ".dm2" / "config.yaml").write_text(
            "consistency:\n  strict_mode: true\n", encoding="utf-8"
        )
        issues = _check("table", MERMAID_GRAPH, "markdown")
        assert issues[0].severity is IssueSeverity.ERROR


class TestRobustness:
    def test_unknown_representation_is_skipped(self):
        assert _check("not-a-representation", MERMAID_GRAPH, "mermaid") == []

    def test_unknown_view_is_skipped(self):
        checker = RepresentationChecker(_FakeKnowledge({}))
        assert checker.check({"GHOST-9": MERMAID_GRAPH}) == []

    def test_missing_content_is_skipped(self):
        checker = RepresentationChecker(_FakeKnowledge({"X-1": "table"}))
        assert checker.check({"X-1": None}) == []

    def test_empty_views_data(self):
        assert RepresentationChecker(_FakeKnowledge({})).check({}) == []
