## ADDED Requirements

### Requirement: Template frontmatter expansion
Each of the 17 DM2 data group templates in `dm2-reference/core/groups/*/*-Template.md` SHALL include two new frontmatter fields: `keywords` (for activation detection) and `related_dm2_views` (for view mapping reference).

#### Scenario: Keywords exist for all groups
- **WHEN** the data group activator loads templates
- **THEN** each template frontmatter SHALL contain a `keywords` array with 5-15 Chinese and English keywords
- **AND** the keywords SHALL be representative terms for that DM2 data group

#### Scenario: Related views documented in templates
- **WHEN** the data group activator loads templates
- **THEN** each template frontmatter SHALL contain a `related_dm2_views` array listing the DoDAF view IDs that relate to this data group
- **AND** the views SHALL be consistent with the external `group-to-views.yaml` mapping

### Requirement: Group-to-views external mapping
The system SHALL provide an external YAML file at `dm2-reference/group-to-views.yaml` containing the definitive mapping from DM2 data groups to DoDAF views.

#### Scenario: Mapping loaded at runtime
- **WHEN** `ViewRecommender` initializes
- **THEN** it SHALL load `group-to-views.yaml` from the dm2-reference directory
- **AND** SHALL use this mapping for view recommendation
- **AND** SHALL fall back to the mapping if the file is missing or malformed

### Requirement: CLI outputs raw activation data
The enhanced `dm2 analyze --json` output SHALL include the data group activation vector, keywords matched, candidate views, and dependency context, leaving final prioritization to the AI Agent.

#### Scenario: JSON output includes activation vector
- **WHEN** `dm2 analyze -d "..." --json` runs
- **THEN** the output SHALL include `data_group_activation` as a mapping of group IDs to float scores
- **AND** SHALL include `data_group_keywords_matched` listing the specific keywords that matched per group

#### Scenario: No priority ranking in CLI output
- **WHEN** the enhanced `dm2 analyze --json` outputs candidate views
- **THEN** it SHALL NOT include priority ranking, phase classification, or sorting
- **AND** the AI Agent skill SHALL use the activation data together with user conversation context to decide the final priority order
