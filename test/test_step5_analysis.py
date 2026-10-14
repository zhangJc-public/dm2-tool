"""Tests for Step5Analysis (dm2.engine.pipeline.step5_analysis).

Step 5 is where the pipeline does abductive reasoning, OODA resilience analysis,
TOC bottleneck identification and consistency checking — the four things the
step5-analysis spec names.

Two defects used to live here. Every abductive inference carried a placeholder
endpoint (``"未知"`` or ``"(从描述提取)"``), so a two-ended relation never named
its ends; inferences now report the DM2 types the relation connects. And
``TOCBottleneck.out_degree`` was hardcoded to ``1``, printed as ``入度/出度`` in
the step document; it is now a per-node co-occurrence count derived from the
architecture under analysis.
"""

import pytest

from dm2.engine.pipeline.step5_analysis import (
    PATTERN_ENDPOINTS,
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

    PLACEHOLDERS = {"未知", "(从描述提取)"}

    def test_no_inference_uses_an_unnamed_placeholder(self, step5):
        """Spec: an inference names the entities it concerns."""
        for text in ("", PATTERNED, DESCRIPTION):
            for inf in step5._abductive_reasoning(text, ""):
                assert inf.entity_a not in self.PLACEHOLDERS, inf
                assert inf.entity_b not in self.PLACEHOLDERS, inf

    def test_a_missing_pattern_inference_names_the_types_it_would_connect(self, step5):
        """No instance was observed, but the relation still has two ends."""
        inferences = step5._abductive_reasoning("", "")
        binding = next(i for i in inferences if i.inferred_relation == "Activity-Performer 绑定")

        assert binding.entity_a == "Activity"
        assert binding.entity_b == "Performer"

    def test_a_missing_pattern_inference_says_what_to_add(self, step5):
        inferences = step5._abductive_reasoning("", "")
        binding = next(i for i in inferences if i.inferred_relation == "Activity-Performer 绑定")

        assert "Activity" in binding.rationale
        assert "Performer" in binding.rationale

    def test_a_matched_pattern_inference_names_its_types(self, step5):
        matched = step5._abductive_reasoning(PATTERNED, "")

        assert matched
        assert all(i.entity_a and i.entity_b for i in matched)

    def test_a_matched_pattern_inference_quotes_the_evidence(self, step5):
        matched = step5._abductive_reasoning(PATTERNED, "")

        assert any("匹配文本" in i.rationale for i in matched)

    def test_every_pattern_type_has_endpoints(self):
        """A pattern without endpoints would reintroduce the placeholder."""
        for pattern_type, endpoints in PATTERN_ENDPOINTS.items():
            assert len(endpoints) == 2, pattern_type
            assert all(endpoints), pattern_type


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

    def test_out_degree_is_derived_not_fixed(self, step5):
        """Spec: degrees come from the architecture, not from a constant."""
        lone = step5._toc_analysis("分析引擎处理数据。存储服务保存结果。", "")
        paired = step5._toc_analysis(
            "采集模块汇聚流量，分析引擎与存储服务交换数据，采集模块也写入存储服务。", ""
        )

        assert lone[0].out_degree == 0
        assert paired[0].out_degree == 2
        assert lone[0].out_degree != paired[0].out_degree

    def test_out_degree_counts_nodes_sharing_a_sentence(self, step5):
        """A node alone in its sentence has nowhere to flow to."""
        bottlenecks = step5._toc_analysis(
            "分析引擎与存储服务交换数据。采集模块单独工作。", ""
        )

        assert bottlenecks[0].out_degree == 1

    def test_out_degree_is_per_node(self, step5):
        """Two nodes in one architecture need not share a degree."""
        text = "分析引擎与存储服务交换数据。存储服务独自归档。"

        assert step5._cooccurrence_degree("分析引擎", ["分析引擎", "存储服务"], text) == 1
        assert step5._cooccurrence_degree("存储服务", ["分析引擎", "存储服务"], text) == 1

    def test_cooccurrence_degree_ignores_the_node_itself(self, step5):
        assert step5._cooccurrence_degree("分析引擎", ["分析引擎"], "分析引擎分析引擎") == 0

    def test_impact_reports_the_derived_degree(self, step5):
        bottlenecks = step5._toc_analysis(
            "采集模块汇聚流量，分析引擎与存储服务交换数据，采集模块也写入存储服务。", ""
        )

        assert str(bottlenecks[0].out_degree) in bottlenecks[0].impact

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

    def test_a_declared_cycle_reaches_the_consistency_issues(self, step5):
        """The temporal rule works end to end through Step 5.

        The relations must arrive as view content: ``_prepare_views_data``
        splits the data text on view headings, so the same text in the
        description argument would never be checked.
        """
        result = step5.execute(
            "某系统",
            "## OV-6c\n活动A prerequisite: 活动B\n活动B prerequisite: 活动A\n",
        )

        assert [i for i in result.consistency_issues if i.issue_type == "circular_dependency"]

    def test_an_acyclic_architecture_reports_no_cycle(self, step5):
        result = step5.execute(
            "某系统",
            "## OV-6c\n活动A prerequisite: 活动B\n活动B prerequisite: 活动C\n",
        )

        assert not [
            i for i in result.consistency_issues if i.issue_type == "circular_dependency"
        ]


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
