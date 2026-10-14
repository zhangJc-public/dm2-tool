"""Tests for Step1IntentScope (dm2.engine.pipeline.step1_intent_scope).

Step 1+2 is the first thing ``dm2 run`` executes and it decides the scope every
later step inherits.

Two defects used to live here. ``DM2_GROUP_TOKEN_ESTIMATES`` was keyed by group
directory names ("01-Performer") while its only caller passed bare names
("Performer"), so the intersection was empty and every group cost the same
default; the table is now keyed by what callers pass, with a coverage test. And
``_generate_clarification_questions`` read only ``templates[0]`` of each
dimension, with a fallback that re-asked a question already asked whenever the
primary was ``Why``; it now asks distinct questions and reaches both templates.
"""

import pytest

from dm2.cognitive.six_w_analyzer import SIX_W_TO_DM2_GROUPS, SixW
from dm2.engine.pipeline.step1_intent_scope import (
    DM2_GROUP_TOKEN_ESTIMATES,
    MAX_CLARIFICATION_QUESTIONS,
    REVERSE_QUESTION_TEMPLATES,
    Step1IntentScope,
)

DESCRIPTION = "某安全运营平台检测网络威胁，安全团队负责处置"


@pytest.fixture(scope="module")
def step1():
    return Step1IntentScope()


class TestClarificationQuestions:
    """Spec: 2-3 distinct clarification questions before scope definition."""

    @pytest.mark.parametrize("w", list(SixW))
    def test_between_two_and_three_questions(self, step1, w):
        questions = step1._generate_clarification_questions(w, [])

        assert 2 <= len(questions) <= MAX_CLARIFICATION_QUESTIONS

    @pytest.mark.parametrize("w", list(SixW))
    def test_questions_are_distinct(self, step1, w):
        """A repeated question addresses no second ambiguity."""
        questions = step1._generate_clarification_questions(w, [])

        assert len(questions) == len(set(questions))

    def test_a_why_primary_does_not_repeat_itself(self, step1):
        """The case the old fallback collapsed into a duplicate."""
        questions = step1._generate_clarification_questions(SixW.WHY, [])

        assert len(questions) == len(set(questions))
        assert questions.count(REVERSE_QUESTION_TEMPLATES[SixW.WHY][0]) == 1

    @pytest.mark.parametrize("w", list(SixW))
    def test_both_templates_of_a_dimension_are_reachable(self, step1, w):
        """Every dimension writes two questions; both must be askable."""
        questions = step1._generate_clarification_questions(w, [])

        for template in REVERSE_QUESTION_TEMPLATES[w]:
            assert template in questions, w

    def test_questions_come_from_the_matched_dimensions(self, step1):
        questions = step1._generate_clarification_questions(SixW.WHERE, [])

        assert set(questions) <= set(REVERSE_QUESTION_TEMPLATES[SixW.WHERE])

    def test_a_secondary_dimension_contributes_when_there_is_room(self, step1):
        questions = step1._generate_clarification_questions(SixW.WHAT, [SixW.WHO])

        assert REVERSE_QUESTION_TEMPLATES[SixW.WHO][0] in questions

    def test_secondaries_are_capped_by_the_limit(self, step1):
        questions = step1._generate_clarification_questions(
            SixW.WHAT, [SixW.HOW, SixW.WHERE, SixW.WHO]
        )

        assert len(questions) == MAX_CLARIFICATION_QUESTIONS

    def test_every_dimension_has_two_questions_to_draw_on(self):
        for w in SixW:
            assert len(REVERSE_QUESTION_TEMPLATES[w]) >= 2, w


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
    """Spec: the estimate reflects the groups in scope, so scopes differ in cost."""

    @staticmethod
    def _selectable_groups():
        return {g for w in SixW for g in SIX_W_TO_DM2_GROUPS[w]}

    def test_every_selectable_group_has_a_weight(self):
        """The drift guard: a group a 6W dimension can select must be costed."""
        selectable = self._selectable_groups()

        assert selectable
        assert not (selectable - set(DM2_GROUP_TOKEN_ESTIMATES))

    def test_the_table_has_no_unreachable_keys(self):
        """A key no caller can pass is dead weight — the shape of the old defect."""
        selectable = self._selectable_groups()

        assert not (set(DM2_GROUP_TOKEN_ESTIMATES) - selectable)

    def test_budget_is_base_plus_the_groups_own_weight(self, step1):
        weight = DM2_GROUP_TOKEN_ESTIMATES["Performer"]

        assert step1._estimate_context_budget(["Performer"], 0) == 2000 + weight

    def test_a_costlier_group_costs_more(self, step1):
        """A larger group must not be lost to a shared default."""
        cheap = step1._estimate_context_budget(["Location"], 0)
        dear = step1._estimate_context_budget(["Activity"], 0)

        assert DM2_GROUP_TOKEN_ESTIMATES["Activity"] > DM2_GROUP_TOKEN_ESTIMATES["Location"]
        assert dear > cheap

    def test_two_estimates_of_the_same_shape_still_differ(self, step1):
        """Two groups each, same description length, different totals."""
        a = step1._estimate_context_budget(["Location", "Location"], 0)
        b = step1._estimate_context_budget(["Activity", "Activity"], 0)

        assert a != b

    def test_budget_grows_with_the_description_length(self, step1):
        short = step1._estimate_context_budget([], 0)
        long = step1._estimate_context_budget([], 400)

        assert long - short == 100

    def test_an_empty_scope_costs_only_the_base(self, step1):
        assert step1._estimate_context_budget([], 0) == 2000


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
