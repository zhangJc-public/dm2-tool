## MODIFIED Requirements

### Requirement: Template frontmatter expansion
Each of the 17 DM2 data group templates in `dm2-reference/core/groups/*/*-Template.md` SHALL include two frontmatter fields: `keywords` (for activation detection) and `related_dm2_views` (for view mapping reference). All 17 groups SHALL have a template file — groups 00, 11-16 that currently lack templates SHALL be created.

#### Scenario: Keywords exist for all 17 groups
- **WHEN** the data group activator loads templates
- **THEN** all 17 group directories under `dm2-reference/core/groups/` SHALL contain a `*-Template.md` file
- **AND** each template frontmatter SHALL contain a `keywords` array with 5-15 Chinese and English keywords
- **AND** groups 00, 12, 15 (abstract layers) MAY have keywords targeting meta-level architectural concepts rather than domain nouns

#### Scenario: Related views documented in templates
- **WHEN** the data group activator loads templates
- **THEN** each template frontmatter SHALL contain a `related_dm2_views` array listing the DoDAF view IDs that relate to this data group
- **AND** the views SHALL be consistent with the external `group-to-views.yaml` mapping

## ADDED Requirements

### Requirement: Activation vector covers all 17 groups
The `DataGroupActivator.activate()` SHALL return activation results for all 17 DM2 data groups, including groups that have zero keywords matched or no template. Missing groups SHALL NOT be silently omitted from the activation vector.

#### Scenario: All 17 groups in activation output
- **WHEN** `DataGroupActivator.activate(description)` is called
- **THEN** the returned list SHALL contain exactly 17 `DataGroupActivation` entries
- **AND** groups without templates SHALL appear with `score: 0.0`, `keywords_matched: []`, `keyword_count: 0`, `total_keywords: 0`

#### Scenario: Groups loaded from group-to-views.yaml as fallback
- **WHEN** a group directory exists but lacks a `*-Template.md` file
- **THEN** the group SHALL still appear in the activation vector
- **AND** the group's `keywords` SHALL be loaded from `group-to-views.yaml` if available
- **AND** otherwise the group SHALL appear with zero keywords (score 0.0)

### Requirement: analyze --json includes group-to-view mapping context
The `dm2 analyze --json` output SHALL include `group_to_views` mapping and dependency context fields to enable AI Agent decision-making without additional CLI calls.

#### Scenario: group_to_views included in output
- **WHEN** `dm2 analyze -d "..." --json` runs
- **THEN** the output SHALL include `group_to_views` as a mapping from group_id to its candidate view IDs
- **AND** each entry SHALL include the group's `name`, `label`, and `description` from `group-to-views.yaml`

#### Scenario: views_completed and view_dependencies in output
- **WHEN** `dm2 analyze -d "..." --json` runs
- **THEN** the output SHALL include `views_completed` listing already-generated view IDs (from ViewManager)
- **AND** SHALL include `view_dependencies` mapping each candidate view to its dependency list from views.yaml

### Requirement: CLI output has no priority ranking
The `dm2 analyze --json` `recommended_views` array SHALL NOT include priority ranking or sort order. The AI Agent SHALL determine final priority based on activation data and conversation context.

#### Scenario: recommended_views unsorted
- **WHEN** `dm2 analyze -d "..." --json` runs
- **THEN** the `recommended_views` array SHALL be unsorted (appearing in discovery order)
- **AND** SHALL NOT include a `priority` field on individual views
- **AND** the AI Agent skill SHALL determine priority from data group activation scores and user context
