"""Tests for ViewTemplateFiller (dm2.engine.view_generator).

This module is the one place that turns a view template into document text, and
it feeds Step 6. It had no test coverage at all before this file.

Two behaviours are pinned here rather than asserted as correct, and each is
marked ``DEFECT`` with the reason. They are pinned so that the fix has a safety
net: when the test starts failing, that is the signal the defect was addressed
and the test needs to be rewritten to the correct expectation.

DEFECT-1  ``_find_template_file`` can never succeed. ``patterns`` are built by
          joining onto ``reference_root``, which is absolute, and ``Path.glob``
          rejects absolute patterns outright (``NotImplementedError``). The
          template directory it looks for (``dm2-reference/core/详细分析/``)
          does not exist either, so even a fixed glob would find nothing.

DEFECT-2  Because ``fill`` calls ``_find_template_file`` before any try/except,
          DEFECT-1 propagates out of ``fill`` for every registered view.
"""

import pytest

from dm2.engine.view_generator import (
    ArchitectureInput,
    GenerationResult,
    ViewTemplateFiller,
)
from dm2.kernel.indexer import DM2KnowledgeIndexer

#: Views Step 6 asks the filler for, plus one more from a different viewpoint.
KNOWN_VIEWS = ["OV-1", "OV-2", "OV-5a", "CV-1"]


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
        for view_id in KNOWN_VIEWS:
            assert indexer.get_view_template(view_id) is not None, view_id

    def test_unknown_view_returns_an_error_string(self, filler):
        """An unregistered id is reported as text, not raised."""
        result = filler.fill("NOPE-9", {})
        assert result == "# Error: Unknown view NOPE-9"


class TestTemplateFileLookup:
    """DEFECT-1: the lookup is structurally incapable of finding a template."""

    def test_find_template_file_raises_for_every_known_view(self, filler):
        for view_id in KNOWN_VIEWS:
            with pytest.raises(NotImplementedError, match="Non-relative patterns"):
                filler._find_template_file(view_id)

    def test_reference_root_is_absolute(self, indexer):
        """The precondition that makes the glob absolute and therefore invalid."""
        assert indexer.reference_root.is_absolute()

    def test_the_directory_it_searches_for_does_not_exist(self, indexer):
        """DEFECT-1, second half: the target directory is absent as well."""
        assert not (indexer.reference_root / "详细分析").exists()


class TestFillPropagatesTheDefect:
    """DEFECT-2: ``fill`` always raises for a registered view."""

    @pytest.mark.parametrize("view_id", KNOWN_VIEWS)
    def test_fill_raises_for_known_views(self, filler, view_id):
        with pytest.raises(NotImplementedError):
            filler.fill(view_id, {"overview": "x"})


class TestFillFromFile:
    """The file-filling path itself is sound; it is simply unreachable."""

    def test_substitutes_placeholders(self, filler, tmp_path):
        template = tmp_path / "OV-1.md"
        template.write_text("# OV-1 {name}\n\n{body}\n", encoding="utf-8")

        out = filler._fill_from_file(template, {"name": "Alpha", "body": "Details"})

        assert out == "# OV-1 Alpha\n\nDetails\n"

    def test_leaves_unknown_placeholders_alone(self, filler, tmp_path):
        template = tmp_path / "OV-2.md"
        template.write_text("{known} and {missing}", encoding="utf-8")

        out = filler._fill_from_file(template, {"known": "yes"})

        assert out == "yes and {missing}"


class TestFillFromScratch:
    """Directly exercised: the generator produces a usable skeleton."""

    def test_ov_prefix_gets_overview_details_and_mermaid(self, filler):
        out = filler._fill_from_scratch("OV-1", {"overview": "OVW", "details": "DET"})

        assert out.startswith("# OV-1 ")
        assert "**视图类型**: " in out
        assert "**涉及数据组**: " in out
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


class TestUnusedDataclasses:
    """``GenerationResult`` and ``ArchitectureInput`` have no consumers."""

    def test_generation_result_defaults(self):
        result = GenerationResult(view_id="OV-1", content="x", success=True)

        assert result.error == ""
        assert result.metadata == {}

    def test_architecture_input_defaults(self):
        data = ArchitectureInput(description="d")

        assert data.image_paths == []
        assert data.metadata == {}
