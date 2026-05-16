"""pytest fixtures for dm2-tool tests"""
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def tmp_project():
    """Create a temporary .dm2 project directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / ".dm2").mkdir()
        (root / ".dm2" / "config.yaml").write_text(
            "views:\n  include_mermaid: true\n  include_timestamps: true\n"
        )
        (root / "dm2-changes").mkdir()
        (root / "dm2-archive").mkdir()
        (root / "output").mkdir()
        yield root


@pytest.fixture
def tmp_dm2_project_cwd(tmp_project, monkeypatch):
    """Change cwd to a temporary dm2 project"""
    import os
    monkeypatch.chdir(str(tmp_project))
    return tmp_project


@pytest.fixture
def sample_markdown_with_frontmatter():
    return """---
name: Firewall
dm2-type: Performer
dm2-layer: Individual
tags:
  - security
  - network
---

# Firewall

A network security device.

## 详细信息

一些详细说明文本。

## Related
[[IDS]] [[NetworkSegment]]
"""


@pytest.fixture
def sample_markdown_no_frontmatter():
    return """# Simple Document

This document has no frontmatter.

## Section 1

Content here.
"""


@pytest.fixture
def sample_terms_json():
    """Sample DM2 terms JSON content"""
    import json
    return json.dumps([
        {
            "term": "Activity",
            "definition": "An action performed by a performer",
            "alias": "Task, Function",
            "source": "DoDAF 2.02",
            "groups": ["Activity"]
        },
        {
            "term": "Performer",
            "definition": "Any entity that performs an activity",
            "alias": "",
            "source": "DM2",
            "groups": ["Performer"]
        },
    ])


@pytest.fixture
def mock_reference_root(tmp_path, sample_terms_json):
    """Create a mock dm2-reference directory with sample data"""
    ref_root = tmp_path / "dm2-reference"
    ref_root.mkdir()

    # Write terms JSON
    (ref_root / "_dm2_v202_extract.json").write_text(sample_terms_json, encoding="utf-8")

    # Write a concept markdown file
    concept_dir = ref_root / "01-Performer"
    concept_dir.mkdir()
    (concept_dir / "Firewall.md").write_text("""---
name: Firewall
dm2-type: Performer
dm2-layer: Individual
definition: A network security device
tags:
  - security
  - network
---

# Firewall

A network security device.

## Related
[[IDS]] [[NetworkSegment]]
""", encoding="utf-8")

    return ref_root
