"""Tests for Step1IntentScope (dm2.engine.pipeline.step1_intent_scope).

Step 1+2 is the first thing ``dm2 run`` executes and it decides the scope every
later step inherits. It had no test coverage before this file.

DEFECT-7 and DEFECT-8 are pinned rather than asserted as correct.

DEFECT-7  ``DM2_GROUP_TOKEN_ESTIMATES`` is unreachable. Its keys are numbered
          ("01-Performer") while the only caller passes bare DM2 group names
          ("Performer"), so the intersection is empty and every lookup falls
          through to the 2500 default. The table matches neither its callers nor
          the real group directory names (which are lower-case English, e.g.
          ``dm2-reference/core/groups/00-foundation``).

DEFECT-8  ``_generate_clarification_questions`` only ever reads
          ``templates[0]``, so the second reverse-question written for each of
          the six dimensions can never be asked.
"""

import pytest

from dm2.cognitive.six_w_analyzer import SIX_W_TO_DM2_GROUPS, SixW
from dm2.engine.pipeline.step1_intent_scope import (
    DM2_GROUP_TOKEN_ESTIMATES,
    REVERSE_QUESTION_TEMPLATES,
    Step1IntentScope,
)

DESCRIPTION = "某安全运营平台检测网络威胁，安全团队负责处置"


@pytest.fixture(scope="module")
def step1():
    return Step1IntentScope()


class TestClarificationQuestions:
    """Spec: at least 2 clarification questions before scope definition."""

    def test_at_least_two_questions_are_produced(self, step1):
        questions = step1._generate_clarification_questions(SixW.WHAT, [])

        assert len(questions) >= 2

    def test_questions_come_from_the_matched_dimensions(self, step1):
        questions = step1._generate_clarification_questions(SixW.WHERE, [])

        assert REVERSE_QUESTION_TEMPLATES[SixW.WHERE][0] in questions

    def test_secondary_dimensions_contribute_questions(self, step1):
        questions = step1._generate_clarification_questions(SixW.WHAT, [SixW.WHO])

        assert REVERSE_QUESTION_TEMPLATES[SixW.WHO][0] in questions

    def test_at_most_three_dimensions_are_asked_about(self, step1):
        questions = step1._generate_clarification_questions(
            SixW.WHAT, [SixW.HOW, SixW.WHERE, SixW.WHO]
        )

        assert len(questions) <= 3

    def test_a_why_primary_does_not_repeat_itself(self, step1):
        """DEFECT-8a: the fallback re-appends a question already asked.

        With WHY as the primary the loop already contributes
        ``REVERSE_QUESTION_TEMPLATES[WHY][0]``; the ``len < 2`` fallback then
        appends the very same string.
        """
        questions = step1._generate_clarification_questions(SixW.WHY, [])

        assert len(questions) != len(set(questions))

    def test_the_second_template_of_each_dimension_is_unreachable(self, step1):
        """DEFECT-8: every dimension has two questions; only the first is used."""
        for w, templates in REVERSE_QUESTION_TEMPLATES.items():
            assert len(templates) == 2, w
            for secondary in ([], [SixW.HOW], [SixW.WHERE], [SixW.WHO, SixW.WHEN]):
                questions = step1._generate_clarification_questions(w, secondary)
                assert templates[1] not in questions, (w, secondary)


class TestDataGroupSelection:
    def test_primary_dimension_groups_are_included(self, step1):
        groups = step1._select_data_groups(SixW.WHAT, [])

        assert set(SIX_W_TO_DM2_GROUPS[SixW.WHAT]) <= set(groups)

    def test_secondary_dimension_groups_are_included(self, step1):
        groups = step1._select_data_groups(SixW.WHAT, [SixW.WHO])

        assert set(SIX_W_TO_DM2_GROUPS[SixW.WHO]) <= set(groups)

    def test_result_is_sorted_and_deduplicated(self, step1):
        groups = step1._select_data_groups(SixW.WHAT, [SixW.WHO, SixW.HOW])

        assert groups == sorted(set(groups))

    def test_at_most_two_secondary_dimensions_contribute(self, step1):
        groups = step1._select_data_groups(
            SixW.WHAT, [SixW.WHO, SixW.HOW, SixW.WHERE, SixW.WHEN, SixW.WHY]
        )

        assert len(groups) < len({g for w in SixW for g in SIX_W_TO_DM2_GROUPS[w]})


class TestContextBudget:
    """DEFECT-7: the weight table is never consulted."""

    def test_table_keys_never_match_what_callers_pass(self, step1):
        callable_groups = {g for w in SixW for g in SIX_W_TO_DM2_GROUPS[w]}

        assert callable_groups
        assert set(DM2_GROUP_TOKEN_ESTIMATES) & callable_groups == set()

    def test_table_keys_never_match_the_real_group_directories(self, step1):
        groups_dir = step1.indexer.reference_root / "groups"
        real = {p.name for p in groups_dir.iterdir() if p.is_dir()} if groups_dir.is_dir() else set()

        assert real
        assert set(DM2_GROUP_TOKEN_ESTIMATES) & real == set()

    def test_every_group_falls_through_to_the_default(self, step1):
        callable_groups = {g for w in SixW for g in SIX_W_TO_DM2_GROUPS[w]}

        for g in callable_groups:
            assert DM2_GROUP_TOKEN_ESTIMATES.get(g, 2500) == 2500, g

    def test_budget_is_base_plus_the_default_per_group(self, step1):
        assert step1._estimate_context_budget(["Performer"], 0) == 2000 + 2500

    def test_budget_grows_with_the_description_length(self, step1):
        short = step1._estimate_context_budget([], 0)
        long = step1._estimate_context_budget([], 400)

        assert long - short == 100


class TestScopeBoundaries:
    """Spec: warn when the scope exceeds a practical context limit."""

    def test_small_scope_is_reported_as_within_range(self, step1):
        text = step1._describe_boundaries(["Performer"], _domain(), 3000, "d")

        assert "在安全范围内" in text

    def test_large_budget_raises_a_warning(self, step1):
        text = step1._describe_boundaries(["Performer"], _domain(), 9000, "d")

        assert "预算警告" in text
        assert "分阶段" in text

    def test_lists_the_selected_groups(self, step1):
        text = step1._describe_boundaries(["Performer", "Activity"], _domain(), 3000, "d")

        assert "Performer" in text
        assert "Activity" in text

    def test_disorder_domain_gets_an_extra_note(self, step1):
        from dm2.cognitive.cynefin_analyzer import Domain

        text = step1._describe_boundaries([], Domain.DISORDER, 3000, "d")

        assert "域判定不明" in text


class TestExecute:
    def test_returns_a_fully_populated_result(self, step1):
        result = step1.execute(DESCRIPTION)

        assert result.intent_description == DESCRIPTION
        assert result.clarification_questions
        assert result.cynefin_domain
        assert result.selected_data_groups
        assert result.context_budget_estimate > 0
        assert result.scope_boundaries
        assert result.primary_w

    def test_json_projection_carries_the_core_fields(self, step1):
        payload = step1.to_json(step1.execute(DESCRIPTION))

        assert payload["intent_description"] == DESCRIPTION
        assert "context_budget_estimate" in payload
        assert "selected_data_groups" in payload


def _domain():
    """A non-DISORDER domain, for boundary text tests."""
    from dm2.cognitive.cynefin_analyzer import Domain

    return Domain.COMPLICATED
