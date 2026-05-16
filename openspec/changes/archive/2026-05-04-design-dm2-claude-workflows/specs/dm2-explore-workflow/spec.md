## ADDED Requirements

### Requirement: Architecture exploration workflow
The system SHALL provide a Claude Code skill (`dm2-explore`) that guides the AI Agent through the architecture exploration workflow: knowledge query → Cynefin assessment → 6W analysis → view recommendation.

#### Scenario: Explore with a problem description
- **WHEN** user invokes `/dm2:explore` with a system description
- **THEN** the AI Agent SHALL execute `dm2 cynefin "<description>" --json` to assess complexity
- **AND** SHALL execute `dm2 analyze "<description>" --json` for 6W analysis and view recommendations
- **AND** SHALL present findings in a structured format with recommended next steps

#### Scenario: Look up DM2 concepts during exploration
- **WHEN** AI Agent needs to explain a DM2 term or view during exploration
- **THEN** the skill SHALL instruct the Agent to call `dm2 knowledge search "<term>" --json` or `dm2 knowledge concept "<name>" --json`

#### Scenario: No description provided
- **WHEN** user invokes `/dm2:explore` without a description
- **THEN** the AI Agent SHALL ask the user to describe the system or problem they want to explore

### Requirement: Exploration output format
The exploration workflow SHALL produce structured output including Cynefin domain, confidence, recommended views, and key considerations.

#### Scenario: Output after analysis
- **WHEN** exploration workflow completes
- **THEN** the output SHALL include domain classification, confidence score, recommended view count, and reasoning
