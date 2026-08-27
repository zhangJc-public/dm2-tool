# DM2 Propose Workflow (delta)

## ADDED Requirements

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

### Requirement: Pictorial views are a communication baseline
Pictorial communication views (OV-1 High-Level Operational Concept Graphic, CV-1 Vision, AV-1 Overview) SHALL NOT be excluded from the view set solely because the DM2 monster matrix marks them data-light (few necessary terms / no necessary associations).

#### Scenario: Data-light pictorial view is not auto-dropped
- **WHEN** the workflow instruction text is generated
- **THEN** it SHALL state that `pictorial` views are the decision-maker communication
  baseline and data-lightness is not grounds for exclusion
- **AND** it SHALL name OV-1, CV-1, AV-1 explicitly

#### Scenario: Human focus on concerns without OV-1 still yields it when dependencies require
- **WHEN** the user selects concerns whose `core_views` exclude OV-1 (e.g.
  data-security-and-compliance), but the focused set includes OV-2/OV-5a
- **THEN** the completeness step SHALL supplement OV-1 into the set
