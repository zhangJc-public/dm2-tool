## ADDED Requirements

### Requirement: Continue in-progress architecture work
The system SHALL provide a Claude Code skill (`dm2-continue`) that auto-detects the current state of a dm2 project and advances to the next step, following openspec's "continue" pattern.

#### Scenario: Auto-detect next pending view
- **WHEN** user invokes `/dm2:continue` in a dm2 project with pending views
- **THEN** the AI Agent SHALL run `dm2 status --json` to get project state including view progress
- **AND** SHALL identify the first view with status `pending`
- **AND** SHALL execute `dm2 instructions <view_id> --json` and begin generating that view

#### Scenario: Continue pipeline
- **WHEN** user invokes `/dm2:continue` and an agent-driven pipeline is in progress
- **THEN** the AI Agent SHALL run `dm2 run --status --json` to check pipeline state
- **AND** SHALL run `dm2 run --instructions <current_step> --json` for the current step
- **AND** SHALL complete the step and advance the pipeline

#### Scenario: All views generated, no pipeline running
- **WHEN** user invokes `/dm2:continue` and all recommended views are generated
- **THEN** the AI Agent SHALL suggest running `dm2 validate --all` to verify consistency
- **AND** SHALL suggest archiving the change

#### Scenario: Multiple active changes
- **WHEN** multiple dm2 changes exist
- **THEN** the AI Agent SHALL run `dm2 change list-changes --json` and ask user to select which to continue

#### Scenario: Nothing to continue
- **WHEN** the project has no pending views, no active pipeline, and no active changes
- **THEN** the AI Agent SHALL suggest starting a new analysis with `/dm2:new`
