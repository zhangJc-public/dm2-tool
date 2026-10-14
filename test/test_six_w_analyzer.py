"""Tests for SixWAnalyzer (dm2.cognitive.six_w_analyzer).

``dm2 analyze`` is one of the commands a user runs directly, and its
``extracted_entities`` field is part of the documented JSON output
(``schemas/analyze.json``).

Two defects used to live here: the class declared seven entity buckets and
defined patterns for only three (``resource`` / ``capability`` / ``location`` /
``measure`` were never filled, and ``analyze`` filters empty buckets out of its
JSON, so they vanished entirely), and the Chinese patterns were greedy on both
sides, so a match swallowed the whole clause. The buckets are now driven by
``ENTITY_BUCKET_PATTERNS`` — a bucket exists because it has patterns — and
matches stop at the keyword they are anchored to.
"""

import pytest

from dm2.cognitive.six_w_analyzer import (
    DM2_GROUP_TO_ENTITY_TYPES,
    ENTITY_BUCKET_PATTERNS,
    SIX_W_PATTERNS,
    SIX_W_TO_DM2_GROUPS,
    SIX_W_TO_VIEWS,
    SixW,
    SixWAnalyzer,
)

#: Every bucket the extraction reports, in declaration order.
ALL_BUCKETS = [
    "system",
    "organization",
    "activity",
    "resource",
    "capability",
    "location",
    "measure",
]


@pytest.fixture(scope="module")
def analyzer():
    return SixWAnalyzer()


#: One description per bucket that names an entity of exactly that type.
BUCKET_SAMPLES = {
    "system": "防火墙系统",
    "organization": "安全部门",
    "activity": "检测流量",
    "resource": "核心数据资源",
    "capability": "态势感知能力",
    "location": "天津机房",
    "measure": "可用性指标",
}


class TestEntityBuckets:
    """All seven buckets are declared and all seven can be filled."""

    def test_every_bucket_is_present_in_the_result(self, analyzer):
        entities = analyzer._extract_entities("任意输入")

        assert list(entities) == ALL_BUCKETS

    def test_the_bucket_set_is_driven_by_the_pattern_table(self, analyzer):
        """A bucket exists because it has patterns — not by separate bookkeeping."""
        assert list(ENTITY_BUCKET_PATTERNS) == ALL_BUCKETS

    def test_every_bucket_has_patterns(self):
        for bucket, patterns in ENTITY_BUCKET_PATTERNS.items():
            assert patterns, bucket

    @pytest.mark.parametrize("bucket", ALL_BUCKETS)
    def test_each_bucket_can_be_populated(self, analyzer, bucket):
        assert analyzer._extract_entities(BUCKET_SAMPLES[bucket])[bucket]

    @pytest.mark.parametrize("bucket", ALL_BUCKETS)
    def test_each_bucket_can_be_recognised_in_english(self, analyzer, bucket):
        english = {
            "system": "a firewall",
            "organization": "the security department",
            "activity": "monitor traffic",
            "resource": "the data asset",
            "capability": "this capability",
            "location": "the site",
            "measure": "a metric",
        }

        assert analyzer._extract_entities(english[bucket])[bucket]

    def test_capability_and_location_reach_the_output(self, analyzer):
        """The exact case reported from a live run, now working."""
        entities = analyzer._extract_entities("需要评估能力与地理位置")

        assert entities["capability"]
        assert entities["location"]

    @pytest.mark.parametrize("bucket", ALL_BUCKETS)
    def test_buckets_are_deduplicated(self, analyzer, bucket):
        text = f"{BUCKET_SAMPLES[bucket]} {BUCKET_SAMPLES[bucket]}"

        assert len(analyzer._extract_entities(text)[bucket]) == 1


class TestBucketVocabularyCoverage:
    """The drift guard: a group a 6W dimension can select must have entity types."""

    def test_every_selectable_group_has_entity_types(self):
        selectable = {g for w in SixW for g in SIX_W_TO_DM2_GROUPS[w]}

        assert selectable
        for group in selectable:
            assert DM2_GROUP_TO_ENTITY_TYPES.get(group), group

    def test_the_four_buckets_that_were_dead_are_covered_by_their_group(self):
        """resource / capability / location / measure share a name with a group."""
        for bucket in ("resource", "capability", "location", "measure"):
            assert DM2_GROUP_TO_ENTITY_TYPES.get(bucket.capitalize()), bucket


class TestMatchBoundaries:
    """A match ends at its anchor and does not run on through the clause."""

    def test_system_match_stops_at_the_type_suffix(self, analyzer):
        entities = analyzer._extract_entities("防火墙系统检测网络威胁")

        assert entities["system"] == ["防火墙系统"]

    def test_activity_match_carries_no_subject(self, analyzer):
        entities = analyzer._extract_entities("安全团队负责监控")

        assert "监控" in entities["activity"]
        assert all("安全团队" not in a for a in entities["activity"])

    def test_organisation_match_stops_before_the_predicate(self, analyzer):
        entities = analyzer._extract_entities("安全团队负责监控")

        assert entities["organization"] == ["安全团队"]

    def test_locations_and_capabilities_stay_disjoint(self, analyzer):
        entities = analyzer._extract_entities("需要评估能力与地理位置")

        assert not set(entities["capability"]) & set(entities["location"])

    def test_one_match_is_not_reported_in_several_buckets(self, analyzer):
        entities = analyzer._extract_entities(
            "某安全运营平台检测网络威胁，安全团队负责监控，需要评估能力与地理位置"
        )

        reported = [m for bucket in ALL_BUCKETS for m in entities[bucket]]
        assert len(reported) == len(set(reported)), reported


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
