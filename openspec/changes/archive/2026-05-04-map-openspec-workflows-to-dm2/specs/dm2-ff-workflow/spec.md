## ADDED Requirements

### Requirement: Fast-forward architecture analysis and view generation
The system SHALL provide a Claude Code skill (`dm2-ff`) that runs the complete analysis and generates all recommended views in one shot, following openspec's "ff" pattern.

#### Scenario: Full analysis and generation from description
- **WHEN** user invokes `/dm2:ff` with a system description
- **THEN** the AI Agent SHALL create a change via `dm2 change new <name>`
- **AND** SHALL run `dm2 cynefin "<description>" --json`
- **AND** SHALL run `dm2 analyze "<description>" --json` to get recommended views
- **AND** SHALL loop through each recommended view: get instructions → generate content → mark as generated
- **AND** SHALL display summary of all generated views with their output paths

#### Scenario: No description provided
- **WHEN** user invokes `/dm2:ff` without a description
- **THEN** the AI Agent SHALL ask the user to describe the system

#### Scenario: Error during generation
- **WHEN** a view fails to generate
- **THEN** the AI Agent SHALL record the failure, continue with remaining views
- **AND** SHALL report which views succeeded and which failed at the end

#### Scenario: All done
- **WHEN** all recommended views have been generated
- **THEN** the AI Agent SHALL display a completion summary with view list and output paths
- **AND** SHALL suggest running `/dm2:verify` to check consistency
