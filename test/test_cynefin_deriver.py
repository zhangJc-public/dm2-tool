"""Tests for the shared CynefinDeriver: polarity safety, evidence, golden corpus."""
import pytest

from dm2.cognitive.cynefin_analyzer import CynefinAnalyzer, Tendency
from dm2.cognitive.cynefin_deriver import (
    CynefinDeriver,
    CynefinKeywordsError,
    votes_from_user,
)

# 验收锚点：真实语料 → 期望域
GOLDEN_CORPUS = [
    ("Clear", "为单一办公室部署一台下一代防火墙，需求明确，采用成熟方案，规则完备，"
              "无合规要求，各团队目标一致，环境长期稳定。"),
    ("Complicated", "某三甲医院落实等保三级要求建设安全运营中心，需集成 HIS、LIS、PACS 等"
                    "多个业务系统，涉及院方、集成厂商、监管机构多方协调，等保2.0 标准完备，"
                    "需专家分析和多方案选型，需求分阶段明确。"),
    ("Complex", "建设 AI 驱动的自适应安全编排平台，需求不确定且持续涌现，业内尚无先例，"
                "威胁态势快速变化，安全团队与业务团队目标冲突，相关监管规则缺失，团队只能探索前行。"),
    ("Chaotic", "核心业务全站中断，应急指挥部已启动，正在应急处置，事态仍在蔓延，多个系统失控。"),
    ("Disorder", ""),
    ("Disorder", "今天天气不错，适合散步。"),
]


@pytest.fixture(scope="module")
def deriver():
    return CynefinDeriver()


@pytest.fixture(scope="module")
def analyzer():
    return CynefinAnalyzer()


def _vote_by_id(derivation, dim_id):
    return next(v for v in derivation.votes if v.dimension_id == dim_id)


class TestPolaritySafety:
    def test_uncertain_is_complex_not_clear(self, deriver):
        """Regression: 「不确定」must not be re-matched as 「确定」→ clear."""
        vote = _vote_by_id(deriver.derive("需求不确定"), "requirement_knowability")
        assert vote.tendency == Tendency.COMPLEX

    def test_negated_stable_blocked(self, deriver):
        # 「尚不稳定」: no positive clear vote may be cast
        votes = [v for v in deriver.derive("目标尚不稳定").votes if v.tendency == Tendency.CLEAR]
        assert votes == []

    def test_positive_anchor_still_matches(self, deriver):
        vote = _vote_by_id(deriver.derive("需求明确"), "requirement_knowability")
        assert vote.tendency == Tendency.CLEAR


class TestLongestMatch:
    def test_long_complicated_phrase_beats_inner_clear(self, deriver):
        vote = _vote_by_id(deriver.derive("需求分阶段明确"), "requirement_knowability")
        assert vote.tendency == Tendency.COMPLICATED

    def test_hard_coordination_beats_plain_coordination(self, deriver):
        vote = _vote_by_id(deriver.derive("各方难以协调"), "goal_alignment")
        assert vote.tendency == Tendency.COMPLEX

    def test_no_subsystem_double_count(self, deriver):
        # 「子系统」must count once, not also as 「系统」
        scale = deriver.derive("一个子系统").scale_profile
        assert scale.systems == 1


class TestTieAndEvidence:
    def test_cross_tendency_tie_abstains_with_evidence(self, deriver):
        vote = _vote_by_id(
            deriver.derive("方向明确，但细节未知"), "requirement_knowability"
        )
        assert vote.tendency is None
        assert "明确" in vote.evidence and "未知" in vote.evidence

    def test_winner_evidence_carries_matched_terms(self, deriver):
        vote = _vote_by_id(
            deriver.derive("需求不确定、模糊且持续涌现"), "requirement_knowability"
        )
        assert vote.tendency == Tendency.COMPLEX
        assert len(vote.evidence) >= 2
        assert "不确定" in vote.evidence


class TestCrisis:
    def test_crisis_forces_flag(self, deriver):
        d = deriver.derive("全站中断，正在应急处置")
        assert d.crisis is True
        assert d.crisis_evidence

    def test_crisis_spans_do_not_feed_dimensions(self, deriver, analyzer):
        d = deriver.derive("全站中断，应急处置，事态蔓延")
        # 危机词本身不得让任何维度投出 complex 票
        assert all(v.tendency != Tendency.COMPLEX for v in d.votes)
        assert analyzer.assess(d.votes, crisis=d.crisis).domain.value == "Chaotic"


class TestScaleProfile:
    def test_scale_fields(self, deriver):
        scale = deriver.derive("多团队在多个系统上长期运营，涉及组织和部门").scale_profile
        assert scale.systems in (1, 3, 8)
        assert scale.time_span == "long"
        assert scale.stakeholders and scale.stakeholders >= 1

    def test_scale_null_when_absent(self, deriver):
        scale = deriver.derive("一句话").scale_profile
        assert scale.systems is None
        assert scale.stakeholders is None
        assert scale.time_span is None


class TestGoldenCorpus:
    @pytest.mark.parametrize("expected,text", GOLDEN_CORPUS)
    def test_domain_anchor(self, deriver, analyzer, expected, text):
        d = deriver.derive(text)
        result = analyzer.assess(d.votes, crisis=d.crisis, scale=d.scale_profile)
        assert result.domain.value == expected, (
            f"{result.domain.value} != {expected}\n{result.reasoning_details}"
        )


class TestParity:
    def test_pipeline_path_matches_direct_derivation(self):
        """Step1IntentScope 与直接调用 deriver+analyzer 必须同输入同结果。"""
        from dm2.engine.pipeline.step1_intent_scope import Step1IntentScope

        for expected, text in GOLDEN_CORPUS:
            if not text:
                continue
            step1 = Step1IntentScope()
            d = step1.cynefin_deriver.derive(text)
            direct = step1.cynefin_analyzer.assess(
                d.votes, crisis=d.crisis, scale=d.scale_profile
            )
            result = step1.execute(text)
            assert expected in result.cynefin_domain
            assert result.cynefin_domain == direct.domain_label
            assert result.cynefin_confidence == direct.confidence

    def test_pipeline_disorder_is_non_blocking(self):
        from dm2.engine.pipeline.step1_intent_scope import Step1IntentScope

        result = Step1IntentScope().execute("")
        assert "Disorder" in result.cynefin_domain
        assert result.needs_clarification is True
        assert result.clarification_questions  # 6W 澄清问题照常产出
        assert result.selected_data_groups is not None  # 其余 step1 产出不受阻


class TestExternalizedLexicon:
    def test_custom_keywords_injected(self):
        custom = {
            "negation_prefixes": ["不"],
            "crisis": ["天塌了"],
            "dimensions": {
                "requirement_knowability": {
                    "clear": ["清晰"], "complicated": [], "complex": ["模糊"],
                },
                "practice_maturity": {"clear": [], "complicated": [], "complex": []},
                "environmental_dynamics": {"clear": [], "complicated": [], "complex": []},
                "goal_alignment": {"clear": [], "complicated": [], "complex": []},
                "constraint_clarity": {"clear": [], "complicated": [], "complex": []},
            },
            "scale": {},
        }
        deriver = CynefinDeriver(custom)
        assert deriver.derive("表述清晰").votes[0].tendency == Tendency.CLEAR
        assert deriver.derive("天塌了").crisis is True

    def test_missing_keyword_file_raises(self, monkeypatch, tmp_path):
        import dm2.cognitive.cynefin_deriver as mod

        empty = tmp_path / "empty"
        empty.mkdir()
        # get_reference_path 在 deriver 模块内以 from-import 绑定，须打该命名空间
        monkeypatch.setattr(mod, "get_reference_path", lambda: empty / "core")
        mod.load_cynefin_keywords.cache_clear()
        with pytest.raises(CynefinKeywordsError):
            mod.load_cynefin_keywords()
        mod.load_cynefin_keywords.cache_clear()  # 还原 lru_cache


class TestUserVotes:
    def test_partial_user_values_others_abstain(self):
        votes = votes_from_user({"requirement_knowability": "clear"})
        assert votes[0].tendency == Tendency.CLEAR
        assert votes[0].source == "user"
        assert all(v.tendency is None for v in votes[1:])
