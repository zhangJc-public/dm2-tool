## ADDED Requirements

### Requirement: Start new architecture analysis
The system SHALL provide a Claude Code skill (`dm2-new`) that creates a new architecture analysis session and guides the AI Agent through incremental artifact creation, following openspec's "new" pattern.

#### Scenario: Create a new analysis from a system description
- **WHEN** user invokes `/dm2:new` with a system description
- **THEN** the AI Agent SHALL create a change via `dm2 change new <name>`
- **AND** SHALL run `dm2 cynefin "<description>" --json` for complexity assessment
- **AND** SHALL run `dm2 analyze "<description>" --json` for 6W analysis and view recommendations
- **AND** SHALL present the Cynefin result, recommended views, and wait for user to select which view to generate first

#### Scenario: Next step after view selection
- **WHEN** user selects a view to generate
- **THEN** the AI Agent SHALL execute `dm2 instructions <view_id> --json` to get context, rules, and template
- **AND** SHALL generate the view content following the returned template

#### Scenario: After view generation
- **WHEN** a view is successfully generated
- **THEN** the AI Agent SHALL mark the view as generated (via ViewManager or CLI)
- **AND** SHALL present remaining recommended views for user to choose next action

#### Scenario: No system description provided
- **WHEN** user invokes `/dm2:new` without a description
- **THEN** the AI Agent SHALL ask the user to describe the system they want to model
