## ADDED Requirements

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
