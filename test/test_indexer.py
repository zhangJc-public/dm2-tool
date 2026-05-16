"""Tests for DM2KnowledgeIndexer"""
import pytest
from dm2.kernel.indexer import (
    DM2KnowledgeIndexer,
    DM2Term,
    DM2Concept,
    ViewTemplate,
)


class TestLoadTerms:
    def test_loads_terms_from_json(self, mock_reference_root):
        indexer = DM2KnowledgeIndexer(str(mock_reference_root))
        indexer._load_terms_from_json()

        assert len(indexer._terms_cache) == 2
        assert "Activity" in indexer._terms_cache
        assert indexer._terms_cache["Activity"].definition == "An action performed by a performer"

    def test_load_all_loads_terms_and_concepts(self, mock_reference_root):
        indexer = DM2KnowledgeIndexer(str(mock_reference_root))
        indexer.load_all()

        assert len(indexer._terms_cache) == 2
        assert len(indexer._concepts_cache) >= 1
        assert "Firewall" in indexer._concepts_cache


class TestSearchTerms:
    def test_search_by_term_name(self, mock_reference_root):
        indexer = DM2KnowledgeIndexer(str(mock_reference_root))
        indexer._load_terms_from_json()

        results = indexer.search_terms("Activity")
        assert len(results) >= 1
        assert any(t.term == "Activity" for t in results)

    def test_search_by_definition(self, mock_reference_root):
        indexer = DM2KnowledgeIndexer(str(mock_reference_root))
        indexer._load_terms_from_json()

        results = indexer.search_terms("performer")
        assert len(results) >= 1
        assert any(t.term == "Performer" for t in results)

    def test_case_insensitive_search(self, mock_reference_root):
        indexer = DM2KnowledgeIndexer(str(mock_reference_root))
        indexer._load_terms_from_json()

        results = indexer.search_terms("activity")
        assert len(results) >= 1


class TestViewTemplates:
    def test_all_views_loaded(self, mock_reference_root):
        indexer = DM2KnowledgeIndexer(str(mock_reference_root))
        indexer._load_view_templates()

        views = indexer.get_all_views()
        assert len(views) >= 40
        assert "OV-1" in indexer._view_templates
        assert "SV-4" in indexer._view_templates

    def test_get_view_template(self, mock_reference_root):
        indexer = DM2KnowledgeIndexer(str(mock_reference_root))
        indexer._load_view_templates()

        tmpl = indexer.get_view_template("OV-1")
        assert tmpl is not None
        assert tmpl.view_name == "高层作战概念图"
        assert tmpl.viewpoint == "OV"

    def test_get_views_by_viewpoint(self, mock_reference_root):
        indexer = DM2KnowledgeIndexer(str(mock_reference_root))
        indexer._load_view_templates()

        ov_views = indexer.get_views_by_viewpoint("OV")
        assert len(ov_views) >= 9
        for v in ov_views:
            assert v.view_id.startswith("OV-")


class TestStatistics:
    def test_get_statistics(self, mock_reference_root):
        indexer = DM2KnowledgeIndexer(str(mock_reference_root))
        indexer._load_terms_from_json()
        indexer._load_view_templates()

        stats = indexer.get_statistics()
        assert stats["total_terms"] == 2
        assert stats["total_views"] >= 40
        assert "total_concepts" in stats
