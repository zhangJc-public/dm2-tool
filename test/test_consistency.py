"""Tests for ConsistencyChecker (dm2.reasoning.consistency).

The checker is what ``dm2 validate`` runs, and its four rules are named in the
class docstring. This module had no test coverage before this file.

DEFECT-6 is pinned rather than asserted as correct.

DEFECT-6  Rule 4 (temporal consistency) can never fire. ``_check_temporal_
          consistency`` parses the names on either side of a prerequisite /
          successor marker, then assigns an *empty list* as that node's targets
          (``temporal_relations.setdefault(node, {})['prerequisite'] = []``).
          The successor list is filled the same way. ``_find_cycles`` therefore
          walks an adjacency map whose every value is empty and always returns
          ``[]``, so the ``if cycles:`` branch that raises ``circular_dependency``
          is unreachable.

          ``_find_cycles`` itself is correct — the tests below exercise it
          directly — so the fix belongs in the caller.

The step5-analysis spec requires this rule explicitly: "circular dependency
detection" is one of the four checks Step 5 SHALL run.
"""

import re

import pytest

from dm2.reasoning.consistency import ConsistencyChecker, IssueSeverity

#: Content with an obvious A -> B -> A prerequisite cycle.
CYCLIC_VIEWS = {
    "OV-6c": (
        "活动A prerequisite: 活动B\n"
        "活动B prerequisite: 活动A\n"
    ),
}


@pytest.fixture
def checker():
    return ConsistencyChecker()


class TestFindCycles:
    """The graph walk is sound; it is handed an empty graph by its caller."""

    def test_detects_a_two_node_cycle(self, checker):
        cycles = checker._find_cycles({"A": {"prerequisite": ["B"]}, "B": {"prerequisite": ["A"]}})

        assert cycles
        assert set(cycles[0]) == {"A", "B"}

    def test_detects_a_three_node_cycle(self, checker):
        relations = {
            "A": {"prerequisite": ["B"]},
            "B": {"prerequisite": ["C"]},
            "C": {"prerequisite": ["A"]},
        }

        assert checker._find_cycles(relations)

    def test_acyclic_graph_yields_nothing(self, checker):
        relations = {"A": {"prerequisite": ["B"]}, "B": {"prerequisite": []}}

        assert checker._find_cycles(relations) == []

    def test_empty_relations_yield_nothing(self, checker):
        assert checker._find_cycles({}) == []

    def test_nodes_with_empty_target_lists_yield_nothing(self, checker):
        """This is the shape the caller actually produces."""
        relations = {"活动A": {"prerequisite": []}, "活动B": {"prerequisite": []}}

        assert checker._find_cycles(relations) == []


class TestTemporalRuleIsUnreachable:
    """DEFECT-6: rule 4 can never report anything."""

    def test_cyclic_content_produces_no_circular_dependency_issue(self, checker):
        issues = checker.check_views(CYCLIC_VIEWS)

        assert not [i for i in issues if i.issue_type == "circular_dependency"]

    def test_every_node_gets_an_empty_target_list(self, checker):
        """The line that makes the rule vacuous."""
        relations = {}
        for text in CYCLIC_VIEWS.values():
            for match in re.finditer(
                r"(?:prerequisite|pre|前置)[:\s]+([^\n,]+)", text, re.IGNORECASE
            ):
                node = match.group(1).strip()
                relations.setdefault(node, {})["prerequisite"] = []

        assert relations
        assert all(v["prerequisite"] == [] for v in relations.values())


class TestActivityPerformerBinding:
    def test_ov5a_without_ov5b_is_a_warning(self, checker):
        issues = checker.check_views({"OV-5a": "## 活动\n- 检测流量\n"})

        assert any(i.issue_type == "missing_mapping" for i in issues)
        assert any(i.severity is IssueSeverity.WARNING for i in issues)

    def test_both_present_does_not_raise_missing_mapping(self, checker):
        issues = checker.check_views({"OV-5a": "## 活动\n- 检测流量\n", "OV-5b": "## 追踪\n"})

        assert not [i for i in issues if i.issue_type == "missing_mapping"]

    def test_empty_input_yields_no_issues(self, checker):
        assert checker.check_views({}) == []


class TestResourceFlowIntegrity:
    def test_orphan_resources_are_reported_as_info(self, checker):
        issues = checker.check_views({"OV-2": "## 资源\n- 防火墙\n"})

        orphans = [i for i in issues if i.issue_type == "orphan_resource"]
        assert orphans
        assert orphans[0].severity is IssueSeverity.INFO

    def test_no_ov2_means_no_resource_check(self, checker):
        issues = checker.check_views({"OV-5a": "x"})

        assert not [i for i in issues if i.issue_type == "orphan_resource"]


class TestCapabilityMapping:
    def test_many_capabilities_without_activities_is_a_warning(self, checker):
        # The extractor wants `能力:` followed by content on the same line.
        cv2 = "能力: 态势感知\n能力: 应急响应\n能力: 安全审计\n能力: 数据防护\n"

        issues = checker.check_views({"CV-2": cv2})

        assert any(i.issue_type == "capability_without_activity" for i in issues)

    def test_few_capabilities_do_not_warn(self, checker):
        """The rule only fires above three capabilities."""
        issues = checker.check_views({"CV-2": "能力: 态势感知\n"})

        assert not [i for i in issues if i.issue_type == "capability_without_activity"]

    def test_no_cv2_means_no_capability_check(self, checker):
        issues = checker.check_views({"OV-5a": "x"})

        assert not [i for i in issues if i.issue_type == "capability_without_activity"]


class TestIssueShape:
    def test_issues_carry_severity_and_message(self, checker):
        issues = checker.check_views({"OV-5a": "## 活动\n- 检测流量\n"})

        assert issues
        for issue in issues:
            assert isinstance(issue.severity, IssueSeverity)
            assert issue.message

    def test_state_is_reset_between_runs(self, checker):
        first = checker.check_views({"OV-5a": "## 活动\n- 检测流量\n"})
        second = checker.check_views({})

        assert first
        assert second == []
