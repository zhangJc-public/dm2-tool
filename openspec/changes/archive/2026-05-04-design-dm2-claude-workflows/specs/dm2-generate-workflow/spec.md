## ADDED Requirements

### Requirement: View generation workflow
The system SHALL provide a Claude Code skill (`dm2-generate`) that guides the AI Agent through the view generation workflow: select view → get instructions → generate content → verify consistency.

#### Scenario: Generate a specific view
- **WHEN** user invokes `/dm2:generate OV-2`
- **THEN** the AI Agent SHALL execute `dm2 instructions OV-2 --json` to get context, rules, template, and output path
- **AND** SHALL generate view content following the returned template and rules
- **AND** SHALL write output to the specified output path

#### Scenario: Generate with project context
- **WHEN** user invokes `/dm2:generate OV-2` within a dm2 project
- **THEN** the AI Agent SHALL pass `--project .` to include project-level context in instructions

#### Scenario: Select from recommended views
- **WHEN** user invokes `/dm2:generate` without specifying a view
- **THEN** the AI Agent SHALL run `dm2 analyze` first to get view recommendations
- **AND** SHALL present recommended views for user to select from

#### Scenario: Verify generated view
- **WHEN** a view has been generated
- **THEN** the AI Agent SHALL update the view state to `generated` via ViewManager
- **AND** SHALL offer to run consistency checks against related views

### Requirement: Generate workflow state tracking
The generate workflow SHALL track which views are pending, in progress, generated, and verified.

#### Scenario: View state progression
- **WHEN** AI Agent starts generating a view
- **THEN** the view status SHALL transition from `pending` → `in_progress`
- **WHEN** content is written to output path
- **THEN** the view status SHALL transition from `in_progress` → `generated`
