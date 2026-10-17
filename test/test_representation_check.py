"""Tests for `dm2.reasoning.representation.RepresentationChecker`.

The checker closes a real gap: dm2 declared a `representation` per view but
nothing verified the generated file honoured it. These tests pin both the
reporting rules and the severity policy (`consistency.strict_mode`).
"""
from types import SimpleNamespace

from dm2.reasoning.consistency import IssueSeverity
from dm2.reasoning.representation import RepresentationChecker

MERMAID_GRAPH = "```mermaid\ngraph TD\n    A --> B\n```"
MERMAID_STATE = "```mermaid\nstateDiagram\n    [*] --> A\n```"
FIGURE = "![图示](OV-1.svg)"


class _FakeKnowledge:
    """Minimal stand-in for KnowledgeAPI.get_view()."""

    def __init__(self, representations: dict[str, str]):
        self._representations = representations

    def get_view(self, view_id):
        if view_id not in self._representations:
            return None
        return SimpleNamespace(representation=self._representations[view_id])


def _check(representation: str, content: str) -> list:
    return RepresentationChecker(_FakeKnowledge({"X-1": representation})).check({"X-1": content})


class TestDiagramExpected:
    def test_matching_mermaid_is_accepted(self):
        assert _check("state-diagram", MERMAID_STATE) == []

    def test_graph_family_is_interchangeable(self):
        # node-link maps to `graph`; `flowchart` is the same family.
        assert _check("node-link", "```mermaid\nflowchart TD\n    A --> B\n```") == []

    def test_missing_diagram_is_reported(self):
        issues = _check("state-diagram", "# 只有文字")
        assert [i.issue_type for i in issues] == ["representation_missing_diagram"]
        assert issues[0].severity is IssueSeverity.WARNING
        assert issues[0].view_id == "X-1"

    def test_wrong_mermaid_type_is_reported(self):
        issues = _check("state-diagram", MERMAID_GRAPH)
        assert [i.issue_type for i in issues] == ["representation_mismatch"]

    def test_external_figure_satisfies_the_requirement(self):
        assert _check("node-link", FIGURE) == []

    def test_mermaid_and_figure_together_is_informational(self):
        issues = _check("node-link", MERMAID_GRAPH + "\n" + FIGURE)
        assert [i.issue_type for i in issues] == ["representation_mixed"]
        assert issues[0].severity is IssueSeverity.INFO


class TestDiagramFree:
    def test_table_view_with_mermaid_is_reported(self):
        issues = _check("table", MERMAID_GRAPH)
        assert [i.issue_type for i in issues] == ["representation_unexpected_diagram"]

    def test_table_view_without_diagram_is_accepted(self):
        assert _check("table", "| a | b |\n|---|---|") == []

    def test_text_view_with_mermaid_is_reported(self):
        issues = _check("text", MERMAID_GRAPH)
        assert [i.issue_type for i in issues] == ["representation_unexpected_diagram"]


class TestSeverityPolicy:
    def test_warning_by_default(self):
        assert _check("table", MERMAID_GRAPH)[0].severity is IssueSeverity.WARNING

    def test_strict_mode_promotes_to_error(self, tmp_dm2_project_cwd):
        (tmp_dm2_project_cwd / ".dm2" / "config.yaml").write_text(
            "consistency:\n  strict_mode: true\n", encoding="utf-8"
        )
        assert _check("table", MERMAID_GRAPH)[0].severity is IssueSeverity.ERROR


class TestRobustness:
    def test_unknown_representation_is_skipped(self):
        assert _check("not-a-representation", MERMAID_GRAPH) == []

    def test_unknown_view_is_skipped(self):
        checker = RepresentationChecker(_FakeKnowledge({}))
        assert checker.check({"GHOST-9": MERMAID_GRAPH}) == []

    def test_missing_content_is_skipped(self):
        checker = RepresentationChecker(_FakeKnowledge({"X-1": "table"}))
        assert checker.check({"X-1": None}) == []

    def test_empty_views_data(self):
        assert RepresentationChecker(_FakeKnowledge({})).check({}) == []
