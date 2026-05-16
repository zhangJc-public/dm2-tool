## MODIFIED Requirements

### Requirement: Intent convergence with reverse questioning
The system SHALL, before confirming the architecture intent, explicitly pose 2-3 fundamental clarification questions (反向质问) to prevent premature convergence. In Agent-driven mode, these questions SHALL be included in the step instructions' `context` field as structured JSON.

#### Scenario: System asks clarifying questions
- **WHEN** user provides an initial architecture description
- **THEN** the system SHALL generate at least 2 clarification questions addressing potential ambiguities in the description before proceeding to scope definition

#### Scenario: Agent-mode outputs structured questions
- **WHEN** Step 1+2 runs in Agent mode with --json
- **THEN** the questions SHALL be returned as a JSON array in the instructions' `clarification_questions` field
