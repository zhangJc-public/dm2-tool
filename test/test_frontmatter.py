"""Tests for FrontmatterParser"""
from dm2.utils.frontmatter import FrontmatterParser


class TestParse:
    def test_parse_valid_frontmatter(self, sample_markdown_with_frontmatter):
        result = FrontmatterParser.parse(sample_markdown_with_frontmatter)
        assert result is not None
        assert result["name"] == "Firewall"
        assert result["dm2-type"] == "Performer"
        assert result["dm2-layer"] == "Individual"
        assert result["tags"] == ["security", "network"]

    def test_parse_no_frontmatter(self, sample_markdown_no_frontmatter):
        result = FrontmatterParser.parse(sample_markdown_no_frontmatter)
        assert result is None

    def test_parse_malformed_yaml(self):
        content = """---
name: [unclosed
---
body"""
        result = FrontmatterParser.parse(content)
        assert result is None


class TestExtract:
    def test_extract_existing_key(self, sample_markdown_with_frontmatter):
        result = FrontmatterParser.extract(sample_markdown_with_frontmatter, "name")
        assert result == "Firewall"

    def test_extract_missing_key(self, sample_markdown_with_frontmatter):
        result = FrontmatterParser.extract(sample_markdown_with_frontmatter, "nonexistent", "default")
        assert result == "default"

    def test_extract_no_frontmatter(self, sample_markdown_no_frontmatter):
        result = FrontmatterParser.extract(sample_markdown_no_frontmatter, "name", "default")
        assert result == "default"


class TestPedigreeBlock:
    """The nested `pedigree` frontmatter block (view provenance)."""

    PEDIGREE = {
        "pedigree_id": "pid-1",
        "author": {"type": "agent-assisted", "model": "deepseek-v3", "operator": "vano"},
        "creation_date": "2026-10-10T10:00:00",
        "source": {
            "standard": "DoDAF V2.02 Vol 2",
            "section": "CV-1",
            "dm2_terms_used": [{"term": "Capability", "definition_ref": "terms.json#Capability"}],
        },
    }

    def test_set_pedigree_then_extract(self):
        content = "---\nname: CV-1\n---\n# CV-1\n"
        block = FrontmatterParser.extract_pedigree(FrontmatterParser.set_pedigree(content, self.PEDIGREE))
        assert block["pedigree_id"] == "pid-1"
        assert block["author"]["model"] == "deepseek-v3"
        assert block["source"]["dm2_terms_used"][0]["term"] == "Capability"

    def test_set_pedigree_preserves_other_fields_and_body(self):
        content = "---\nname: CV-1\ntags: [a]\n---\n# body\n\ntext\n"
        updated = FrontmatterParser.set_pedigree(content, self.PEDIGREE)
        assert updated.endswith("# body\n\ntext\n")
        parsed = FrontmatterParser.parse(updated)
        assert parsed["name"] == "CV-1"
        assert parsed["tags"] == ["a"]
        assert parsed["pedigree"]["pedigree_id"] == "pid-1"

    def test_set_pedigree_is_idempotent(self):
        content = "---\nname: CV-1\n---\n# CV-1\n"
        once = FrontmatterParser.set_pedigree(content, self.PEDIGREE)
        assert FrontmatterParser.set_pedigree(once, self.PEDIGREE) == once

    def test_extract_pedigree_id(self):
        updated = FrontmatterParser.set_pedigree("---\nname: CV-1\n---\n# CV-1\n", self.PEDIGREE)
        assert FrontmatterParser.extract_pedigree_id(updated) == "pid-1"

    def test_missing_pedigree_is_none(self):
        content = "---\nname: CV-1\n---\n# CV-1\n"
        assert FrontmatterParser.extract_pedigree(content) is None
        assert FrontmatterParser.extract_pedigree_id(content) is None

    def test_non_mapping_pedigree_is_none(self):
        content = "---\npedigree: not-a-mapping\n---\n# CV-1\n"
        assert FrontmatterParser.extract_pedigree(content) is None
        assert FrontmatterParser.extract_pedigree_id(content) is None


class TestUpdate:
    def test_update_existing_frontmatter_preserves_body(self, sample_markdown_with_frontmatter):
        """Verify the bugfix: updating frontmatter no longer truncates body text"""
        result = FrontmatterParser.update(
            sample_markdown_with_frontmatter,
            {"dm2-layer": "Type"}
        )
        # Should contain the updated value
        assert "dm2-layer: Type" in result
        # Should preserve body content that was after the frontmatter
        assert "# Firewall" in result
        assert "A network security device" in result
        assert "一些详细说明文本。" in result
        assert "[[IDS]]" in result

    def test_update_adds_frontmatter_when_missing(self, sample_markdown_no_frontmatter):
        result = FrontmatterParser.update(
            sample_markdown_no_frontmatter,
            {"name": "SimpleDoc"}
        )
        assert result.startswith("---\n")
        assert "name: SimpleDoc" in result
        assert "# Simple Document" in result

    def test_update_adds_multiple_fields(self):
        content = "Body only"
        result = FrontmatterParser.update(content, {"a": 1, "b": 2})
        assert result.startswith("---\n")
        after_fm = result.split("---\n", 2)[-1]
        assert after_fm == "Body only"


class TestExtractAllLinks:
    def test_extract_links(self, sample_markdown_with_frontmatter):
        links = FrontmatterParser.extract_all_links(sample_markdown_with_frontmatter)
        assert "IDS" in links
        assert "NetworkSegment" in links

    def test_no_links(self):
        links = FrontmatterParser.extract_all_links("Plain text without links")
        assert links == []


class TestExtractTags:
    def test_extract_tags(self):
        content = """---
name: Test
tags:
  - python
  - cli
---
# Title

Some text with #inline-tag and #another_tag
"""
        tags = FrontmatterParser.extract_tags(content)
        assert "inline-tag" in tags
        assert "another_tag" in tags

    def test_no_tags(self):
        tags = FrontmatterParser.extract_tags("Plain text")
        assert tags == []
