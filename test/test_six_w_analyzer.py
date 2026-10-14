"""Tests for SixWAnalyzer (dm2.cognitive.six_w_analyzer).

``dm2 analyze`` is one of the commands a user runs directly, and its
``extracted_entities`` field is part of the documented JSON output
(``schemas/analyze.json``). This module had no test coverage before this file.

DEFECT-4 is pinned rather than asserted as correct.

DEFECT-4  ``_extract_entities`` declares seven entity buckets but defines
          patterns for only three of them (system / organization / activity).
          ``resource``, ``capability``, ``location`` and ``measure`` are
          initialised empty and never filled, whatever the input says. The
          ``analyze`` command filters empty buckets out of its JSON
          (src/dm2/cli/main.py:791), so they vanish from the output entirely.

DEFECT-5  The Chinese patterns are greedy character classes
          (``[一-龥]*(?:系统|防火墙|…)``), so a match swallows every adjacent
          Chinese word up to the suffix. The extracted "entity" is usually a
          whole clause rather than a name.
"""

import pytest

from dm2.cognitive.six_w_analyzer import (
    SIX_W_PATTERNS,
    SIX_W_TO_DM2_GROUPS,
    SIX_W_TO_VIEWS,
    SixW,
    SixWAnalyzer,
)

#: Buckets the class declares but never populates.
DEAD_BUCKETS = ["resource", "capability", "location", "measure"]

#: Buckets that do get populated.
LIVE_BUCKETS = ["system", "organization", "activity"]


@pytest.fixture(scope="module")
def analyzer():
    return SixWAnalyzer()


class TestEntityBuckets:
    """DEFECT-4: seven buckets declared, three implemented."""

    def test_all_seven_buckets_are_present_in_the_result(self, analyzer):
        entities = analyzer._extract_entities("任意输入")

        assert list(entities) == LIVE_BUCKETS + DEAD_BUCKETS

    @pytest.mark.parametrize("bucket", LIVE_BUCKETS)
    def test_live_buckets_can_be_populated(self, analyzer, bucket):
        """Each implemented bucket has at least one input that fills it."""
        samples = {
            "system": "防火墙系统",
            "organization": "安全部门",
            "activity": "检测流量",
        }

        assert analyzer._extract_entities(samples[bucket])[bucket]

    @pytest.mark.parametrize("bucket", DEAD_BUCKETS)
    def test_dead_buckets_are_never_populated(self, analyzer, bucket):
        """No input fills them: the patterns were never written."""
        inputs = [
            "需要评估这个能力",          # capability
            "位于天津的机房",            # location
            "资源包括服务器",            # resource
            "性能度量指标",              # measure
            "capability location resource measure",
        ]

        for text in inputs:
            assert analyzer._extract_entities(text)[bucket] == []

    def test_capability_and_location_words_do_not_reach_the_output(self, analyzer):
        """The exact case reported from a live run."""
        entities = analyzer._extract_entities("需要评估能力与地理位置")

        assert entities["capability"] == []
        assert entities["location"] == []

    def test_buckets_are_deduplicated(self, analyzer):
        entities = analyzer._extract_entities("防火墙系统 防火墙系统")

        assert len(entities["system"]) == 1


class TestGreedyChinesePatterns:
    """DEFECT-5: matches swallow neighbouring words."""

    def test_system_match_swallows_the_whole_clause(self, analyzer):
        entities = analyzer._extract_entities("防火墙系统检测网络威胁")

        assert entities["system"] == ["防火墙系统检测网络威胁"]

    def test_the_same_clause_is_also_reported_as_an_activity(self, analyzer):
        """One clause lands in several buckets, so the buckets are not disjoint."""
        entities = analyzer._extract_entities("防火墙系统检测网络威胁")

        assert entities["activity"] == ["防火墙系统检测网络威胁"]

    def test_organization_match_swallows_a_verb_phrase(self, analyzer):
        entities = analyzer._extract_entities("安全团队负责监控")

        assert entities["organization"] == ["安全团队负责监控"]


class TestSixWScoring:
    def test_defaults_to_what_when_nothing_matches(self, analyzer):
        result = analyzer.analyze("zzz")

        assert result.primary_w is SixW.WHAT
        assert result.confidence == 0.5
        assert result.secondary_ws == []

    def test_picks_the_highest_scoring_dimension(self, analyzer):
        result = analyzer.analyze("为什么需要这个规则和标准")

        assert result.primary_w is SixW.WHY

    def test_secondary_dimensions_are_ranked_and_capped_at_two(self, analyzer):
        result = analyzer.analyze("谁负责在什么地方用什么方式执行")

        assert len(result.secondary_ws) <= 2

    def test_confidence_is_the_primary_share_of_the_total(self, analyzer):
        result = analyzer.analyze("为什么需要这个规则")

        assert 0.0 < result.confidence <= 1.0

    def test_reasoning_names_the_primary_dimension(self, analyzer):
        result = analyzer.analyze("为什么需要这个规则")

        assert result.primary_w.value in result.reasoning

    def test_every_dimension_has_patterns(self):
        assert set(SIX_W_PATTERNS) == set(SixW)
        for w, patterns in SIX_W_PATTERNS.items():
            assert patterns, w


class TestSuggestedViews:
    def test_primary_viewpoint_views_are_included(self, analyzer):
        result = analyzer.analyze("谁负责执行")

        assert set(SIX_W_TO_VIEWS[result.primary_w]) <= set(result.suggested_views)

    def test_secondary_viewpoint_views_are_included(self, analyzer):
        result = analyzer.analyze("谁负责在什么地方执行")
        secondary = result.secondary_ws[0]

        assert set(SIX_W_TO_VIEWS[secondary]) <= set(result.suggested_views)

    def test_result_is_sorted_and_deduplicated(self, analyzer):
        result = analyzer.analyze("谁负责执行")

        assert result.suggested_views == sorted(set(result.suggested_views))

    def test_every_dimension_maps_to_views_and_groups(self):
        for w in SixW:
            assert SIX_W_TO_VIEWS[w], w
            assert SIX_W_TO_DM2_GROUPS[w], w


class TestViewpointMapping:
    def test_every_dimension_has_a_viewpoint_list(self, analyzer):
        for w in SixW:
            assert analyzer.get_viewpoint_for_w(w), w

    def test_what_maps_to_av_and_div(self, analyzer):
        assert analyzer.get_viewpoint_for_w(SixW.WHAT) == ["AV", "DIV"]
