# Spec Delta

## MODIFIED Requirements

### Requirement: Intent convergence with reverse questioning
The system SHALL, before confirming the architecture intent, explicitly pose 2-3 fundamental clarification questions (反向质问) to prevent premature convergence, as recommended by the DoDAF-6Step LLM research.

#### Scenario: System asks clarifying questions
- **WHEN** user provides an initial architecture description
- **THEN** the system SHALL generate at least 2 clarification questions addressing potential ambiguities in the description before proceeding to scope definition

#### Scenario: Questions are distinct
- **WHEN** the system generates its clarification questions
- **THEN** no two questions in the set SHALL be the same text
- **AND** each question SHALL address a different ambiguity in the description

#### Scenario: Questions track the identified dimensions
- **WHEN** the analysis identifies a primary dimension and secondary dimensions
- **THEN** the questions SHALL be drawn from those dimensions' question sets

### Requirement: Context budget estimation
The system SHALL estimate the context budget required for the architecture scope and warn if the scope exceeds practical LLM context limits. The estimate SHALL reflect the known size of the DM2 data groups in scope, so that different scopes yield different estimates.

#### Scenario: Scope exceeds context budget
- **WHEN** the determined scope requires more DM2 data groups than can fit in the estimated context window
- **THEN** the system SHALL warn the user and suggest scope reduction or phased approach

#### Scenario: The estimate reflects the groups in scope
- **WHEN** two scopes select data groups of different known size
- **THEN** the two estimates SHALL differ, so that a larger group's cost is not lost to a common default

#### Scenario: Scope within budget is reported as such
- **WHEN** the estimate is below the safety threshold
- **THEN** the system SHALL report the scope as within range rather than warning
