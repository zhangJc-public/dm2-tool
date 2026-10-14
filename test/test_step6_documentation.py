"""Tests for Step6Documentation (dm2.engine.pipeline.step6_documentation).

Step 6 is what turns the pipeline's analysis into the documents a user ends up
reading, and it had no test coverage at all before this file.

DEFECT-3 is pinned rather than asserted as correct. It is the downstream half of
DEFECT-1/DEFECT-2 in test_view_generator.py: because ``ViewTemplateFiller.fill``
raises for every registered view, the ``except Exception`` below swallows the
error and every per-view document is written as placeholder text. The
placeholder also names an LLM, which the project's own contract forbids
(openspec/specs/dm2-no-llm-dependency: source must not import, declare or
document an LLM dependency).
"""

import pytest

from dm2.engine.pipeline.step6_documentation import Step6Documentation

DESCRIPTION = "某安全运营平台监测网络流量，安全团队负责处置告警"
ANALYSIS = "平台检测到异常流量，团队分析后下发阻断策略，并同步通知值班人员"


@pytest.fixture(scope="module")
def step6():
    return Step6Documentation()


@pytest.fixture(scope="module")
def result(step6):
    return step6.execute(DESCRIPTION, ANALYSIS)


class TestExecuteContract:
    """The shape of DocumentationResult — relied on by the orchestrator."""

    def test_returns_the_three_views_step6_owns(self, result):
        assert set(result.views) == {"OV-1", "OV-2", "OV-5a"}

    def test_returns_a_composite_view(self, result):
        assert result.composite_view.startswith("# Composite View")

    def test_returns_a_knowledge_delta(self, result):
        assert result.knowledge_delta.new_entities
        assert result.knowledge_delta.iteration_suggestions

    def test_output_dir_is_reported(self, result):
        assert result.output_dir


class TestPerViewDocumentsArePlaceholders:
    """DEFECT-3: every per-view document is placeholder text, never real content."""

    @pytest.mark.parametrize("view_id", ["OV-1", "OV-2", "OV-5a"])
    def test_view_body_is_the_placeholder(self, result, view_id):
        assert result.views[view_id] == f"# {view_id}\n\n视图生成待 LLM 填充"

    def test_placeholder_names_an_llm(self, result):
        """The project is zero-LLM by contract; this string contradicts it."""
        assert "LLM" in result.views["OV-1"]

    def test_no_wikilinks_reach_the_view_documents(self, result):
        """``_add_wikilinks`` runs after ``fill`` raised, so it never applies.

        The step6-documentation spec requires generated view documents to carry
        ``[[wikilinks]]`` back to DM2 concepts.
        """
        assert "[[" not in result.views["OV-1"]


class TestCompositeView:
    """The composite view is real content and satisfies its spec requirement."""

    def test_carries_description_and_entities(self, result):
        assert DESCRIPTION[:20] in result.composite_view
        assert "- [[" in result.composite_view

    def test_offers_both_documented_pairings(self, result):
        """Spec: at least one composite view, e.g. OV-2+OV-5a or SV-4+DIV-1."""
        assert "OV-2+OV-5a" in result.composite_view
        assert "SV-4+DIV-1" in result.composite_view

    def test_marks_itself_as_generated(self, result):
        assert "Pipeline Step 6" in result.composite_view


class TestEntityExtraction:
    def test_finds_chinese_system_nouns(self, step6):
        entities = step6._extract_entities("某安全运营平台监测网络流量")

        assert "平台" in "".join(entities) or any("平台" in e for e in entities)

    def test_finds_capitalised_english_names(self, step6):
        entities = step6._extract_entities("The IDS forwards to Splunk")

        assert "IDS" in entities
        assert "Splunk" in entities

    def test_deduplicates_case_insensitively(self, step6):
        entities = step6._extract_entities("IDS ids IDS")

        assert [e.lower() for e in entities].count("ids") == 1

    def test_drops_short_matches(self, step6):
        """Matches of two characters or fewer are discarded."""
        assert step6._extract_entities("AB") == []

    def test_caps_the_result(self, step6):
        """Distinct 3-letter names, so deduplication cannot mask the cap."""
        text = " ".join(f"{a}{b}Z" for a in "ABCDEFGH" for b in "ABCDEFGH")

        assert len(step6._extract_entities(text)) == 20

    def test_scans_every_text_argument(self, step6):
        entities = step6._extract_entities("Alpha", "Bravo")

        assert "Alpha" in entities and "Bravo" in entities


class TestRelationshipExtraction:
    def test_finds_chinese_verbs(self, step6):
        relations = step6._extract_relationships("平台检测并阻断异常")

        assert "检测" in relations
        assert "阻断" in relations

    def test_finds_english_verbs(self, step6):
        relations = step6._extract_relationships("detect then forward")

        assert "detect" in relations
        assert "forward" in relations

    def test_deduplicates(self, step6):
        assert step6._extract_relationships("检测 检测 检测") == ["检测"]

    def test_empty_input_yields_nothing(self, step6):
        assert step6._extract_relationships("") == []


class TestWikilinks:
    def test_every_entity_gets_an_entry(self, step6):
        mapping = step6._build_wikilinks(["Performer", "SomeUnknownThing"])

        assert set(mapping) == {"Performer", "SomeUnknownThing"}

    def test_known_concept_is_linked_to_itself(self, step6):
        assert "Performer" in step6._build_wikilinks(["Performer"])["Performer"]

    def test_entries_are_capped_at_five(self, step6):
        for links in step6._build_wikilinks(["Performer"]).values():
            assert len(links) <= 5

    def test_appends_a_related_knowledge_section(self, step6):
        out = step6._add_wikilinks("# OV-1\n", {"Performer": ["Performer"]})

        assert out.startswith("# OV-1")
        assert "## 关联知识" in out
        assert "[[Performer]]" in out


class TestKnowledgeDelta:
    def test_flags_thin_entity_coverage(self, step6):
        delta = step6._build_knowledge_delta(["one"], ["r"], "")

        assert any("实体" in s for s in delta.iteration_suggestions)

    def test_flags_thin_relationship_coverage(self, step6):
        delta = step6._build_knowledge_delta(["a", "b", "c"], ["r"], "")

        assert any("活动流程" in s for s in delta.iteration_suggestions)

    def test_flags_gaps_mentioned_in_the_analysis(self, step6):
        delta = step6._build_knowledge_delta(["a", "b", "c"], ["r1", "r2", "r3"], "发现数据缺失")

        assert any("缺口" in s for s in delta.iteration_suggestions)

    def test_the_gap_trigger_word_is_missing_not_que_kou(self, step6):
        """Pinned vocabulary mismatch: the suggestion says 缺口, the trigger is 缺失.

        Text that says 缺口 — the very word the suggestion uses — does not fire.
        Harmless today, but the two spellings should agree.
        """
        delta = step6._build_knowledge_delta(["a", "b", "c"], ["r1", "r2", "r3"], "发现数据缺口")

        assert not any("缺口" in s for s in delta.iteration_suggestions)

    def test_falls_back_to_a_positive_suggestion(self, step6):
        delta = step6._build_knowledge_delta(["a", "b", "c"], ["r1", "r2", "r3"], "一切正常")

        assert len(delta.iteration_suggestions) == 1
        assert "可进一步细化" in delta.iteration_suggestions[0]

    def test_carries_the_inputs_through(self, step6):
        delta = step6._build_knowledge_delta(["a"], ["r"], "")

        assert delta.new_entities == ["a"]
        assert delta.new_relationships == ["r"]


class TestSaveViews:
    """Spec: step 6 writes view files and registers them as ``generated``."""

    def test_writes_composite_and_per_view_files(self, step6, result, tmp_project):
        out = step6.save_views(result, tmp_project / "output")

        assert (out / "composite-view.md").exists()
        for view_id in ("OV-1", "OV-2", "OV-5a"):
            assert (out / f"{view_id}.md").exists()

    def test_registers_each_view_in_the_view_manager(self, step6, result, tmp_project):
        from dm2.core.views.manager import ViewManager

        step6.save_views(result, tmp_project / "output")

        registered = {v.id for v in ViewManager(project_root=tmp_project).list_views()}
        assert {"OV-1", "OV-2", "OV-5a"} <= registered

    def test_creates_the_output_directory(self, step6, result, tmp_project):
        target = tmp_project / "deeply" / "nested"

        step6.save_views(result, target)

        assert target.is_dir()
