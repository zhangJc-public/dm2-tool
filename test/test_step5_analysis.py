"""Tests for Step5Analysis (dm2.engine.pipeline.step5_analysis).

Step 5 is where the pipeline claims to do abductive reasoning, OODA resilience
analysis, TOC bottleneck identification and consistency checking — four things
the step5-analysis spec names as requirements. It had no test coverage before
this file.

DEFECT-11 and DEFECT-12 are pinned rather than asserted as correct.

DEFECT-11  Every abductive inference is built with placeholder endpoints:
           ``"未知"`` for the "pattern not detected" inferences and
           ``"(从描述提取)"`` for the "pattern matched" ones. The dataclass has
           ``entity_a`` / ``entity_b`` fields, so consumers see a two-ended
           relation whose ends are never actually identified.

DEFECT-12  ``TOCBottleneck.out_degree`` is hardcoded to ``1`` for every
           bottleneck. The spec asks the step to "identify the single most
           constraining node and quantify its impact"; the out-degree is the
           only degree field present and it carries no information.
"""

import pytest

from dm2.engine.pipeline.step5_analysis import (
    AbductiveInference,
    AnalysisResult,
    OODABreakpoint,
    Step5Analysis,
    TOCBottleneck,
)

DESCRIPTION = "平台采集模块汇聚流量，分析引擎检测威胁，安全团队负责处置"

#: Names a node for each of the four OODA phases, so nothing is reported missing.
FULL_OODA = "监控采集环境数据，分析评估态势，决策规则引擎下发指令，响应执行阻断动作"

#: Matches the PatternMatcher's WHOLE_PART / ACTIVITY_PERFORMER regexes.
PATTERNED = "系统包括采集模块和存储服务，由安全团队负责执行"


@pytest.fixture(scope="module")
def step5():
    return Step5Analysis()


class TestAbductiveReasoning:
    def test_reports_one_inference_per_missing_pattern(self, step5):
        inferences = step5._abductive_reasoning("", "")

        assert len(inferences) == 6

    def test_reports_the_documented_atomic_relations(self, step5):
        labels = {i.inferred_relation for i in step5._abductive_reasoning("", "")}

        assert "Activity-Performer 绑定" in labels
        assert "Resource-Flow 资源流" in labels

    def test_each_inference_carries_a_rationale_and_confidence(self, step5):
        for inf in step5._abductive_reasoning("", ""):
            assert inf.rationale
            assert 0.0 < inf.confidence <= 1.0

    def test_entity_endpoints_are_placeholders(self, step5):
        """DEFECT-11: the endpoints are never identified."""
        inferences = step5._abductive_reasoning("", "")

        assert inferences
        assert all(i.entity_a == "未知" and i.entity_b == "未知" for i in inferences)

    def test_matched_patterns_use_a_different_placeholder(self, step5):
        """DEFECT-11, second form."""
        matched = [
            i for i in step5._abductive_reasoning(PATTERNED, "")
            if i.entity_a != "未知"
        ]

        assert matched
        assert all(i.entity_a == "(从描述提取)" for i in matched)
        assert all(i.entity_b == "(从描述提取)" for i in matched)


class TestOODAAnalysis:
    def test_reports_every_missing_phase(self, step5):
        breakpoints = step5._ooda_analysis("这里什么都没有")

        assert {b.missing_phase for b in breakpoints} == {"Observe", "Orient", "Decide", "Act"}

    def test_a_complete_loop_reports_nothing(self, step5):
        assert step5._ooda_analysis(FULL_OODA) == []

    def test_each_breakpoint_explains_why(self, step5):
        for b in step5._ooda_analysis("这里什么都没有"):
            assert b.reason
            assert b.node

    def test_first_breakpoint_has_no_predecessor(self, step5):
        breakpoints = step5._ooda_analysis("这里什么都没有")
        observe = next(b for b in breakpoints if b.missing_phase == "Observe")

        assert observe.node == "入口"


class TestTOCAnalysis:
    def test_no_flow_nodes_means_no_bottleneck(self, step5):
        assert step5._toc_analysis("无关描述", "") == []

    def test_a_single_node_is_not_enough(self, step5):
        assert step5._toc_analysis("采集模块", "") == []

    def test_picks_the_most_referenced_node(self, step5):
        text = "分析引擎 分析引擎 分析引擎 存储服务"

        bottlenecks = step5._toc_analysis(text, "")

        assert len(bottlenecks) == 1
        assert bottlenecks[0].node == "分析引擎"

    def test_out_degree_is_hardcoded_to_one(self, step5):
        """DEFECT-12: the field carries no information."""
        text = "分析引擎 分析引擎 存储服务"

        bottlenecks = step5._toc_analysis(text, "")

        assert bottlenecks[0].out_degree == 1

    def test_in_degree_reflects_the_reference_count(self, step5):
        text = "分析引擎 分析引擎 存储服务"

        bottlenecks = step5._toc_analysis(text, "")

        assert bottlenecks[0].in_degree == 2

    def test_impact_mentions_the_node(self, step5):
        bottlenecks = step5._toc_analysis("分析引擎 分析引擎 存储服务", "")

        assert bottlenecks[0].node in bottlenecks[0].impact


class TestPrepareViewsData:
    def test_splits_on_view_headings(self, step5):
        text = "## OV-5a\n活动内容\n## OV-2\n资源内容"

        views = step5._prepare_views_data(text)

        assert set(views) == {"OV-5a", "OV-2"}
        assert "活动内容" in views["OV-5a"]

    def test_text_without_headings_yields_nothing(self, step5):
        assert step5._prepare_views_data("普通文本") == {}


class TestExecute:
    def test_returns_all_four_analysis_sections(self, step5):
        # "某系统" names no OODA phase, so breakpoints are reported.
        result = step5.execute("某系统")

        assert isinstance(result, AnalysisResult)
        assert result.abductive_inferences
        assert result.ooda_breakpoints
        assert isinstance(result.toc_bottlenecks, list)
        assert isinstance(result.consistency_issues, list)

    def test_json_projection_carries_the_sections(self, step5):
        payload = step5.to_json(step5.execute(DESCRIPTION))

        assert "abductive_inferences" in payload
        assert "ooda_breakpoints" in payload
        assert "toc_bottlenecks" in payload

    def test_consistency_issues_are_not_reported_for_cyclic_input(self, step5):
        """DEFECT-6 reaches here too: the temporal rule is unreachable."""
        result = step5.execute("活动A prerequisite: 活动B\n活动B prerequisite: 活动A")

        assert not [i for i in result.consistency_issues if i.issue_type == "circular_dependency"]


class TestDataclasses:
    def test_inference_defaults(self):
        inf = AbductiveInference("a", "b", "rel", 0.5, "why")

        assert inf.confidence == 0.5

    def test_breakpoint_fields(self):
        bp = OODABreakpoint(node="入口", missing_phase="Observe", reason="r")

        assert bp.node == "入口"

    def test_bottleneck_fields(self):
        bn = TOCBottleneck(node="n", in_degree=3, out_degree=1, impact="i")

        assert bn.in_degree == 3
