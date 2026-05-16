## ADDED Requirements

### Requirement: One-shot artifact generation
The dm2-propose-workflow SHALL create all architecture artifacts (proposal.md, design.md, tasks.md) in a single pass from a user-provided system description, using DM2 data group activation detection for view recommendations (not 6W-only).

#### Scenario: User describes a system
- **WHEN** user runs `/dm2:propose` with a system description
- **THEN** the workflow SHALL create a new change via `dm2 change new`
- **AND** SHALL run `dm2 cynefin` and `dm2 analyze --json` with the description
- **AND** SHALL generate proposal.md, design.md, and tasks.md
- **AND** SHALL present the generated artifacts and prompt for `/dm2:continue`

### Requirement: DM2 data group activation
The workflow SHALL use 17 DM2 data group activation detection for view recommendation, replacing the current single-dimension 6W approach.

#### Scenario: Keywords from template frontmatter
- **WHEN** the workflow detects active data groups
- **THEN** the detection keywords SHALL be loaded from each data group template's `keywords` frontmatter field
- **AND** SHALL NOT use hardcoded keyword lists in Python code

#### Scenario: Group-to-views mapping from external YAML
- **WHEN** the workflow maps active data groups to DoDAF views
- **THEN** the mapping SHALL be loaded from `dm2-reference/group-to-views.yaml`
- **AND** the mapping SHALL be editable without modifying Python code

### Requirement: CLI-Agent data contract
The `dm2 analyze --json` output SHALL include raw data group activation vectors and all candidate views for AI Agent decision-making.

#### Scenario: Structured output for agent
- **WHEN** user runs `dm2 analyze -d "..." --json`
- **THEN** the output SHALL include `data_group_activation` (activation scores per group)
- **AND** SHALL include `data_group_keywords_matched` (which keywords triggered)
- **AND** SHALL include `group_to_views` (mapping view candidates)
- **AND** SHALL include `views_completed` and `view_dependencies` for context
- **AND** SHALL NOT include priority ranking (left for AI Agent to decide)
