"""Tests for ConsistencyChecker (dm2.reasoning.consistency).

The checker is what ``dm2 validate`` runs, and its four rules are named in the
class docstring.

Rule 4 (temporal consistency) used to be unreachable: the parser read the name
after a prerequisite / successor marker and then assigned that node an *empty*
target list, so ``_find_cycles`` walked an adjacency map of empty lists and the
``circular_dependency`` branch could never fire. The parser now records the edge
it reads — subject before the marker, target after it — and the rule is live.
"""

import pytest

from dm2.reasoning.consistency import ConsistencyChecker, IssueSeverity

#: Content with an obvious A -> B -> A prerequisite cycle.
CYCLIC_VIEWS = {
    "OV-6c": (
        "活动A prerequisite: 活动B\n"
        "活动B prerequisite: 活动A\n"
    ),
}

#: The same shape, without the cycle.
ACYCLIC_VIEWS = {
    "OV-6c": (
        "活动A prerequisite: 活动B\n"
        "活动B prerequisite: 活动C\n"
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


class TestTemporalRule:
    """Spec: a declared prerequisite cycle is reported at ERROR severity."""

    def test_cyclic_prerequisites_are_reported(self, checker):
        issues = checker.check_views(CYCLIC_VIEWS)

        cycles = [i for i in issues if i.issue_type == "circular_dependency"]
        assert len(cycles) == 1
        assert cycles[0].severity is IssueSeverity.ERROR

    def test_the_report_names_the_nodes_on_the_cycle(self, checker):
        issues = checker.check_views(CYCLIC_VIEWS)
        cycle = next(i for i in issues if i.issue_type == "circular_dependency")

        assert "活动A" in cycle.suggestion
        assert "活动B" in cycle.suggestion

    def test_acyclic_prerequisites_are_not_reported(self, checker):
        issues = checker.check_views(ACYCLIC_VIEWS)

        assert not [i for i in issues if i.issue_type == "circular_dependency"]

    def test_successor_cycles_are_reported_too(self, checker):
        views = {"OV-6c": "活动A successor: 活动B\n活动B successor: 活动A\n"}

        issues = checker.check_views(views)

        assert any(i.issue_type == "circular_dependency" for i in issues)

    def test_a_marker_without_a_subject_contributes_no_edge(self, checker):
        """An edge needs two ends; one is not invented."""
        views = {"OV-6c": "prerequisite: 活动B\n"}

        issues = checker.check_views(views)

        assert not [i for i in issues if i.issue_type == "circular_dependency"]

    def test_views_without_temporal_markers_are_ignored(self, checker):
        issues = checker.check_views({"OV-5a": "## 活动\n- 检测流量\n"})

        assert not [i for i in issues if i.issue_type == "circular_dependency"]


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

    def test_table_rows_with_performers_are_bound(self, checker):
        ov5b = (
            "| 活动 | 输入 | 输出 | 执行者 | 前置条件 |\n"
            "|---|---|---|---|---|\n"
            "| A1 侦测探测 | 信号 | 点迹 | 阵地 | 设备在线 |\n"
        )
        issues = checker.check_views({"OV-5a": "x", "OV-5b": ov5b})

        assert not [i for i in issues if i.issue_type == "unbound_activity"]

    def test_table_row_without_a_performer_is_reported(self, checker):
        ov5b = (
            "| 活动 | 输入 | 输出 | 执行者 | 前置条件 |\n"
            "|---|---|---|---|---|\n"
            "| A1 侦测探测 | 信号 | 点迹 |  | 设备在线 |\n"
        )
        issues = checker.check_views({"OV-5a": "x", "OV-5b": ov5b})

        unbound = [i for i in issues if i.issue_type == "unbound_activity"]
        assert unbound
        assert unbound[0].severity is IssueSeverity.ERROR
        assert "A1" in unbound[0].suggestion

    def test_mermaid_label_with_a_performer_is_bound(self, checker):
        ov5b = '    A1["A1 侦测探测<br/>执行者：阵地<br/>输入：信号"]\n'
        issues = checker.check_views({"OV-5a": "x", "OV-5b": ov5b})

        assert not [i for i in issues if i.issue_type == "unbound_activity"]

    def test_mermaid_label_with_an_empty_performer_is_reported(self, checker):
        ov5b = '    A1["A1 侦测探测<br/>执行者：<br/>输入：信号"]\n'
        issues = checker.check_views({"OV-5a": "x", "OV-5b": ov5b})

        assert [i for i in issues if i.issue_type == "unbound_activity"]

    def test_untracked_ov5a_leaves_are_not_reported(self, checker):
        """OV-5a decomposes further than OV-5b tracks; that is not a defect."""
        ov5a = 'A0 --> A1["A1 侦测探测"]\nA1 --> A11["A1.1 雷达探测"]\n'
        ov5b = "| 活动 | 执行者 |\n|---|---|\n| A1 侦测探测 | 阵地 |\n"
        issues = checker.check_views({"OV-5a": ov5a, "OV-5b": ov5b})

        assert not [i for i in issues if i.issue_type == "unbound_activity"]

    def test_mermaid_node_identifier_is_not_an_activity(self, checker):
        """`A53["A5.3 ..."]` names a node; the activity is the label's `A5.3`."""
        ov5b = '    X --> A53["A5.3 双人确认"]\n'
        issues = checker.check_views({"OV-5a": "x", "OV-5b": ov5b})

        unbound = [i for i in issues if i.issue_type == "unbound_activity"]
        assert unbound
        assert "A5.3" in unbound[0].suggestion
        assert "A53" not in unbound[0].suggestion


class TestResourceFlowIntegrity:
    def test_orphan_resources_are_reported_as_info(self, checker):
        issues = checker.check_views({"OV-2": "## 资源\n- 防火墙\n"})

        orphans = [i for i in issues if i.issue_type == "orphan_resource"]
        assert orphans
        assert orphans[0].severity is IssueSeverity.INFO

    def test_no_ov2_means_no_resource_check(self, checker):
        issues = checker.check_views({"OV-5a": "x"})

        assert not [i for i in issues if i.issue_type == "orphan_resource"]

    def test_bilingual_title_is_not_a_resource(self, checker):
        """The English "Resource" in an H1 title is not a resource name."""
        ov2 = "# OV-2 作战资源流描述（Operational Resource Flow Description）\n\n## 1. 资源流拓扑\n"
        issues = checker.check_views({"OV-2": ov2})

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
