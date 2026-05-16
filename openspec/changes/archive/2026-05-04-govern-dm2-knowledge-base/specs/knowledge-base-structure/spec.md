## ADDED Requirements

### Requirement: Three-layer directory structure
The dm2-reference directory SHALL be organized into three layers: `core/` (DM2 standard data, packaged with pip), `reference/` (supplementary reading material, optional download), and `examples/` (project-specific instances, not packaged).

#### Scenario: Core data is in core/ directory
- **WHEN** the knowledge base is loaded by DM2KnowledgeIndexer
- **THEN** `_dm2_v202_extract.json`, `views.yaml`, and 17 data group directories SHALL be located under `core/`

#### Scenario: Reference material is in reference/ directory
- **WHEN** a user browses dm2-reference for supplementary reading
- **THEN** detailed analysis reports, research papers, and overview documents SHALL be located under `reference/`

### Requirement: Core data packaging
Only files under `dm2-reference/core/` SHALL be included in the pip package via `package_data` in pyproject.toml. The total package size for knowledge data SHALL be under 1 MB.

#### Scenario: Pip package excludes non-core content
- **WHEN** `pip install dm2-tool` is executed
- **THEN** only core/ files SHALL be installed; reference/ and examples/ SHALL NOT be included

### Requirement: Remove PDF screenshot images
PNG images extracted from the DoDAF PDF (visual examples of views) SHALL be removed from the knowledge base. AI Agents use structured view templates from views.yaml, not visual screenshots.

#### Scenario: Images are excluded
- **WHEN** the knowledge base is packaged
- **THEN** no PNG files from the 详细分析/视图全集/images/ directory SHALL be present in core/ or reference/

### Requirement: Remove macOS and duplicate artifacts
DS_Store files and duplicate files (e.g., Common-Patterns.md / CommonPatterns.md) SHALL be removed from the knowledge base.

#### Scenario: No junk files in the repository
- **WHEN** listing all files in dm2-reference/
- **THEN** no .DS_Store files SHALL exist, and no duplicate content files with diverging names SHALL exist

### Requirement: Separate project examples from standard data
Project-specific data (specific firewall model instances, specific Chinese laws, specific organization types like 乙方/甲方) SHALL be moved to `examples/` and excluded from the pip package.

#### Scenario: Core is free of project-specific data
- **WHEN** loading core/ knowledge
- **THEN** no hardcoded instances of specific firewall models (e.g., 天清汉马), specific Chinese laws (e.g., 网络安全法), or specific organization role types (e.g., 乙方) SHALL be present

### Requirement: Indexer path backward compatibility
DM2KnowledgeIndexer SHALL detect the directory structure at load time: if `core/` subdirectory exists, load from new structure; otherwise fall back to old flat structure.

#### Scenario: New structure is detected and used
- **WHEN** dm2-reference/core/ exists
- **THEN** DM2KnowledgeIndexer SHALL load data from core/ subdirectory

#### Scenario: Old structure still works
- **WHEN** dm2-reference/core/ does NOT exist (e.g., git checkout before migration)
- **THEN** DM2KnowledgeIndexer SHALL fall back to loading from dm2-reference/ root directory
