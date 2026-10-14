"""Tests for ViewTemplateFiller (dm2.engine.view_generator).

This module is the one place that turns a view's metadata into document text,
and it feeds Step 6.

The filler used to try a file-template lookup before falling back to generating
from metadata. That lookup could never succeed — it handed an absolute pattern
to ``Path.glob``, which rejects them — so ``fill`` raised for every registered
view and Step 6 wrote placeholder text instead of documents. The lookup and its
file-filling helper are gone; these tests assert the behaviour that replaced
them, and would catch the failure coming back.
"""

import pytest

from dm2.engine.view_generator import ViewTemplateFiller
from dm2.kernel.indexer import DM2KnowledgeIndexer

#: One view per structural branch, plus a fourth viewpoint.
OV_VIEWS = ["OV-1", "OV-2", "OV-5a"]
OTHER_VIEWS = ["CV-1"]


@pytest.fixture(scope="module")
def indexer():
    """A fully loaded indexer over the built-in reference knowledge base."""
    idx = DM2KnowledgeIndexer()
    idx.load_all()
    return idx


@pytest.fixture(scope="module")
def filler(indexer):
    return ViewTemplateFiller(indexer)


class TestKnownViewLookup:
    def test_reference_views_are_registered(self, indexer):
        """Guard: the filler is only meaningful when templates actually load."""
        assert len(indexer.get_all_views()) == 52
        for view_id in OV_VIEWS + OTHER_VIEWS:
            assert indexer.get_view_template(view_id) is not None, view_id

    def test_unknown_view_returns_an_error_string(self, filler):
        """An unregistered id is reported as text, not raised."""
        result = filler.fill("NOPE-9", {})

        assert result == "# Error: Unknown view NOPE-9"


class TestFillProducesDocuments:
    """``fill`` must return content for every registered view, never raise."""

    @pytest.mark.parametrize("view_id", OV_VIEWS + OTHER_VIEWS)
    def test_fill_returns_a_document(self, filler, view_id):
        out = filler.fill(view_id, {"overview": "OVW", "details": "DET"})

        assert out.startswith(f"# {view_id} ")
        assert "Error" not in out

    @pytest.mark.parametrize("view_id", OV_VIEWS + OTHER_VIEWS)
    def test_document_carries_the_view_metadata(self, filler, view_id):
        out = filler.fill(view_id, {})

        assert "**视图类型**: " in out
        assert "**涉及数据组**: " in out

    def test_no_view_in_the_catalogue_raises(self, filler, indexer):
        """The whole catalogue, not just a sample: nothing is exempt."""
        for template in indexer.get_all_views():
            out = filler.fill(template.view_id, {})
            assert out.startswith(f"# {template.view_id} "), template.view_id

    def test_caller_data_reaches_the_document(self, filler):
        out = filler.fill("OV-1", {"overview": "UNIQUE-OVERVIEW-MARKER"})

        assert "UNIQUE-OVERVIEW-MARKER" in out

    def test_missing_data_leaves_sections_present_but_empty(self, filler):
        """Sections are structure, not data: they survive an empty payload."""
        out = filler.fill("OV-1", {})

        assert "## 1. 概览" in out
        assert "## 2. 详细描述" in out


class TestFillFromScratch:
    """The per-viewpoint structure the generator emits."""

    def test_ov_prefix_gets_overview_details_and_mermaid(self, filler):
        out = filler._fill_from_scratch("OV-1", {"overview": "OVW", "details": "DET"})

        assert out.startswith("# OV-1 ")
        assert "## 1. 概览" in out and "OVW" in out
        assert "## 2. 详细描述" in out and "DET" in out
        assert "```mermaid" in out

    def test_sv_prefix_gets_interface_sections(self, filler):
        out = filler._fill_from_scratch("SV-1", {"overview": "o", "interfaces": "i"})

        assert "## 1. 系统概览" in out
        assert "## 2. 接口描述" in out and "i" in out
        assert "## 3. 功能分解" in out

    def test_div_prefix_gets_er_diagram(self, filler):
        out = filler._fill_from_scratch("DIV-1", {"concepts": "c"})

        assert "## 1. 数据概念" in out and "c" in out
        assert "erDiagram" in out

    def test_prefix_without_a_branch_yields_header_only(self, filler):
        """No branch matches, so only the header block is emitted."""
        out = filler._fill_from_scratch("CV-1", {})

        assert out.startswith("# CV-1 ")
        assert "## 1." not in out
