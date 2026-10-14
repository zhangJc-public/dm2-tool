"""Tests for Step3DataRequirements (dm2.engine.pipeline.step3_data_requirements).

Step 3+4 turns the scope from Step 1+2 into concrete DM2 data groups, then asks
the knowledge base what it knows about them. It had no test coverage before this
file.

DEFECT-9 and DEFECT-10 are pinned rather than asserted as correct.

DEFECT-9   ``DataRequirement.required_concepts`` is declared as a list but every
           instance is built with ``required_concepts=[]``. No caller reads it
           back either, so the field is inert.

DEFECT-10  ``_build_taxonomy(requirements, concepts)`` accepts the retrieved
           concepts and never looks at them; the taxonomy is derived from
           ``requirements`` alone. The caller passes a real value, so the
           argument reads as meaningful when it is not.
"""

import pytest

from dm2.engine.pipeline.step3_data_requirements import (
    DM2_GROUP_TO_ENTITY_TYPES,
    DataRequirement,
    Step3DataRequirements,
)

PRIMARY = "Where"
SECONDARY = ["Who"]


@pytest.fixture(scope="module")
def step3():
    return Step3DataRequirements()


class TestBuildRequirements:
    def test_one_requirement_per_dimension(self, step3):
        reqs = step3._build_requirements(PRIMARY, SECONDARY, [])

        assert [r.dimension for r in reqs] == ["Where", "Who"]

    def test_at_most_two_secondary_dimensions(self, step3):
        reqs = step3._build_requirements(
            "What", ["How", "Where", "Who", "When", "Why"], []
        )

        assert len(reqs) == 3

    def test_unknown_dimension_is_skipped(self, step3):
        reqs = step3._build_requirements("Nonsense", ["Who"], [])

        assert [r.dimension for r in reqs] == ["Who"]

    def test_groups_come_from_the_dimension_mapping(self, step3):
        from dm2.cognitive.six_w_analyzer import SIX_W_TO_DM2_GROUPS, SixW

        reqs = step3._build_requirements("Where", [], [])

        assert reqs[0].dm2_groups == SIX_W_TO_DM2_GROUPS[SixW.WHERE]

    def test_selected_groups_narrow_the_result(self, step3):
        reqs = step3._build_requirements("Where", [], ["Location"])

        assert reqs[0].dm2_groups == ["Location"]

    def test_an_empty_intersection_falls_back_to_all_groups(self, step3):
        reqs = step3._build_requirements("Where", [], ["NotAGroup"])

        assert reqs[0].dm2_groups == ["Location", "Performer"]

    def test_entity_types_are_expanded_from_the_group_mapping(self, step3):
        reqs = step3._build_requirements("Where", [], [])

        assert set(DM2_GROUP_TO_ENTITY_TYPES["Location"]) <= set(reqs[0].entity_types)

    def test_every_mapped_group_has_entity_types(self):
        """Otherwise the ``["entity"]`` placeholder would leak into output."""
        from dm2.cognitive.six_w_analyzer import SIX_W_TO_DM2_GROUPS

        for groups in SIX_W_TO_DM2_GROUPS.values():
            for g in groups:
                assert DM2_GROUP_TO_ENTITY_TYPES.get(g), g

    def test_required_concepts_is_always_empty(self, step3):
        """DEFECT-9: declared as data, never populated."""
        for groups in ([], ["Location"], ["Performer", "Organization"]):
            for req in step3._build_requirements("Where", ["Who"], groups):
                assert req.required_concepts == []


class TestTaxonomy:
    def test_keys_are_dimension_scoped(self, step3):
        reqs = [DataRequirement("Where", ["location"], ["Location"], [])]

        taxonomy = step3._build_taxonomy(reqs, [])

        assert list(taxonomy) == ["6W-Where"]

    def test_entries_are_prefixed_by_kind(self, step3):
        reqs = [DataRequirement("Where", ["location"], ["Location"], [])]

        taxonomy = step3._build_taxonomy(reqs, [])

        assert "entity:location" in taxonomy["6W-Where"]
        assert "group:Location" in taxonomy["6W-Where"]

    def test_concepts_argument_does_not_affect_the_result(self, step3):
        """DEFECT-10: the parameter is accepted and ignored."""
        reqs = [DataRequirement("Where", ["location"], ["Location"], [])]

        without = step3._build_taxonomy(reqs, [])
        with_concepts = step3._build_taxonomy(
            reqs, [{"source": "x", "content": "location", "relevance": 1.0}]
        )

        assert without == with_concepts

    def test_empty_requirements_yield_an_empty_taxonomy(self, step3):
        assert step3._build_taxonomy([], []) == {}


class TestGapDetection:
    def test_no_retrieval_is_reported(self, step3):
        gaps = step3._detect_gaps([], [], [])

        assert gaps
        assert "未检索到任何相关概念" in gaps[0]

    def test_dimension_without_matching_concepts_is_flagged(self, step3):
        reqs = [DataRequirement("Where", ["location"], ["Location"], [])]

        gaps = step3._detect_gaps(reqs, [], [])

        assert any("Where 维度" in g for g in gaps)

    def test_dimension_with_matching_concepts_is_not_flagged(self, step3):
        reqs = [DataRequirement("Where", ["location"], ["Location"], [])]
        concepts = [{"source": "s", "content": "A Location is a place.", "relevance": 1.0}]

        gaps = step3._detect_gaps(reqs, concepts, [])

        assert not [g for g in gaps if "Where 维度" in g]


class TestExecute:
    """Spec: retrieval must return real concepts for Activity / Performer."""

    def test_produces_requirements_taxonomy_and_gaps(self, step3):
        result = step3.execute("某平台检测威胁", ["Performer", "Activity"], "Who", ["How"])

        assert result.requirements
        assert result.organized_taxonomy
        assert isinstance(result.gaps, list)

    def test_retrieves_concepts_from_the_knowledge_base(self, step3):
        result = step3.execute("执行者与活动", ["Performer", "Activity"], "Who", ["How"])

        assert result.retrieved_concepts

    def test_retrieved_concepts_carry_source_and_relevance(self, step3):
        result = step3.execute("执行者与活动", ["Performer", "Activity"], "Who", ["How"])

        for item in result.retrieved_concepts:
            assert item["source"]
            assert isinstance(item["relevance"], (int, float))
