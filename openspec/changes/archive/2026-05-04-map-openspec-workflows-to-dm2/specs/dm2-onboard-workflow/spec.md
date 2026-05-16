## ADDED Requirements

### Requirement: Guided DoDAF architecture modeling onboarding
The system SHALL provide a Claude Code skill (`dm2-onboard`) that guides a new user through the complete dm2 workflow cycle using a real system description, following openspec's "onboard" pattern with the Explain → Do → Show → Pause rhythm.

#### Scenario: Welcome and task discovery
- **WHEN** user invokes `/dm2:onboard`
- **THEN** the AI Agent SHALL verify dm2 CLI is installed (`dm2 version`)
- **AND** SHALL display a welcome message explaining what will be covered (Cynefin → 6W → View Recommendation → View Generation → Validation → Archive)
- **AND** SHALL ask the user to describe a system they want to model, or suggest a simple example

#### Scenario: Walk through Cynefin assessment
- **WHEN** user provides a system description
- **THEN** the AI Agent SHALL explain what Cynefin assessment is
- **AND** SHALL execute `dm2 cynefin "<description>" --json`
- **AND** SHALL explain the domain result and its implications for view selection
- **AND** SHALL pause for user acknowledgment

#### Scenario: Walk through 6W analysis
- **WHEN** user acknowledges Cynefin result
- **THEN** the AI Agent SHALL explain 6W analysis
- **AND** SHALL execute `dm2 analyze "<description>" --json`
- **AND** SHALL explain the 6W dimensions (What, Who, Where, When, Why, hoW)
- **AND** SHALL present the recommended views with brief explanations of each

#### Scenario: Generate a view together
- **WHEN** user selects a view from recommendations
- **THEN** the AI Agent SHALL explain the view's purpose in DoDAF
- **AND** SHALL execute `dm2 instructions <view_id> --json` and explain the template structure
- **AND** SHALL generate the view content, narrating key decisions
- **AND** SHALL show the output path

#### Scenario: Validate and recap
- **WHEN** a view has been generated
- **THEN** the AI Agent SHALL offer to run validation
- **AND** SHALL explain what validation checks
- **AND** SHALL display a recap of the full cycle completed
- **AND** SHALL provide a command reference table for future use

#### Scenario: User wants quick reference instead
- **WHEN** user indicates they just want the command list
- **THEN** the AI Agent SHALL display a dm2 command reference table and exit without running the full tutorial
