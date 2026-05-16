## ADDED Requirements

### Requirement: Intent convergence with reverse questioning
The system SHALL, before confirming the architecture intent, explicitly pose 2-3 fundamental clarification questions (反向质问) to prevent premature convergence, as recommended by the DoDAF-6Step LLM research.

#### Scenario: System asks clarifying questions
- **WHEN** user provides an initial architecture description
- **THEN** the system SHALL generate at least 2 clarification questions addressing potential ambiguities in the description before proceeding to scope definition

### Requirement: Cynefin complexity assessment
The system SHALL execute Cynefin analysis on the clarified intent to determine the complexity domain (Clear/Complicated/Complex/Chaotic), which SHALL inform the scope and approach of subsequent steps.

#### Scenario: Complexity domain is determined
- **WHEN** intent is clarified
- **THEN** the system SHALL output Cynefin domain, confidence score, and implications for scope breadth

### Requirement: Context budget estimation
The system SHALL estimate the context budget required for the architecture scope and warn if the scope exceeds practical LLM context limits.

#### Scenario: Scope exceeds context budget
- **WHEN** the determined scope requires more DM2 data groups than can fit in the estimated context window
- **THEN** the system SHALL warn the user and suggest scope reduction or phased approach

### Requirement: Scope definition output
Step 1+2 SHALL produce a scope definition document containing: clarified intent, Cynefin assessment, selected DM2 data groups, context budget estimate, and explicit scope boundaries.

#### Scenario: Scope document is produced
- **WHEN** Step 1+2 completes
- **THEN** `.dm2/steps/step1-intent-scope.md` SHALL contain all four sections (intent, cynefin, data groups, boundaries)
