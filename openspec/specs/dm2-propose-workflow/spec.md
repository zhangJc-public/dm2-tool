# DM2 Propose Workflow Specification

## Purpose
Define the `/dm2:propose` workflow — one-shot artifact generation using DM2 data group activation.

## Requirements

### Requirement: One-shot artifact generation
The dm2-propose-workflow SHALL create all architecture artifacts (proposal.md, design.md, tasks.md) in a single pass from a user-provided system description, using DM2 data group activation detection for view recommendations (not 6W-only).

#### Scenario: User describes a system
- **WHEN** user runs `/dm2:propose` with a system description
- **THEN** the workflow SHALL create a new change via `dm2 change new`
- **AND** SHALL run `dm2 cynefin` and `dm2 analyze --json` with the description
- **AND** SHALL generate proposal.md, design.md, and tasks.md
- **AND** SHALL present the generated artifacts and prompt the user to run `/dm2:apply` as the recommended next step, with `/dm2:continue` and `/dm2:ff` listed as alternatives

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

### Requirement: Concern matching and human selection
The dm2-propose-workflow SHALL include a concern matching step after `dm2 analyze`. The AI Agent SHALL compare activation data against concern templates, present candidate concerns to the Human, and generate a focused view set based on Human selection.

#### Scenario: Agent presents concern candidates
- **WHEN** `/dm2:propose` runs with a system description
- **AFTER** `dm2 analyze --json` returns activation data
- **THEN** the AI Agent SHALL load `dm2-reference/concerns.yaml`
- **AND** SHALL compute concern match scores using activation vector × concern expected_groups + keyword overlap
- **AND** SHALL present top 3-5 matching concerns to the Human

#### Scenario: Human selects concerns
- **WHEN** the Agent presents concern candidates
- **AND** the Human selects one or more concerns (or adds custom concerns)
- **THEN** the Agent SHALL merge the selected concerns' core_views into a focused view set
- **AND** the resulting view set SHALL contain 5-12 views (not 15+ unfiltered)

#### Scenario: Agent uses concern views for planning
- **WHEN** the focused view set is determined
- **THEN** the generated proposal.md and tasks.md SHALL be scoped to the focused view set
- **AND** views outside the selected concerns SHALL be listed as "additional candidates" in a separate section

### Requirement: View-set completeness confirmation step
The propose workflow SHALL include a dependency-completeness step after phase (P1/P2/P3)
assignment: the AI agent SHALL scan the focused view set against `view_dependencies` and
supplement any missing transitive ancestors, marking them as supplement rather than phase
output.

#### Scenario: OV-1 restored when OV-2/OV-5a selected without it
- **WHEN** the focused view set contains OV-2 or OV-5a but not OV-1
- **THEN** the workflow instructions SHALL direct the agent to add OV-1 (and other missing
  ancestors) to the set, marked as supplement
- **AND** the supplement SHALL be listed with its dependency rationale

#### Scenario: Human focus on concerns without OV-1 still yields it when dependencies require
- **WHEN** the user selects concerns whose `core_views` exclude OV-1 (e.g.
  data-security-and-compliance), but the focused set includes OV-2/OV-5a
- **THEN** the completeness step SHALL supplement OV-1 into the set

### Requirement: Pictorial views are a communication baseline
Pictorial communication views (OV-1 High-Level Operational Concept Graphic, CV-1 Vision, AV-1 Overview) SHALL NOT be excluded from the view set solely because the DM2 monster matrix marks them data-light (few necessary terms / no necessary associations).

#### Scenario: Data-light pictorial view is not auto-dropped
- **WHEN** the workflow instruction text is generated
- **THEN** it SHALL state that `pictorial` views are the decision-maker communication
  baseline and data-lightness is not grounds for exclusion
- **AND** it SHALL name OV-1, CV-1, AV-1 explicitly
