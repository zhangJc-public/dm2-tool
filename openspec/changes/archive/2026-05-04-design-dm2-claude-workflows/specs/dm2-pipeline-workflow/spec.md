## ADDED Requirements

### Requirement: Agent-driven pipeline workflow
The system SHALL provide a Claude Code skill (`dm2-pipeline`) that guides the AI Agent through the 4-step agent-driven DoDAF pipeline: Intent & Scope → Data Requirements → Analysis → Documentation.

#### Scenario: Initialize pipeline
- **WHEN** user invokes `/dm2:pipeline start -d "<description>"`
- **THEN** the AI Agent SHALL execute `dm2 run --agent -d "<description>" --json`
- **AND** SHALL parse the returned `first_instructions` for step 1 context, rules, and template
- **AND** SHALL display current pipeline status to the user

#### Scenario: Get step instructions
- **WHEN** AI Agent needs instructions for the current step
- **THEN** the skill SHALL instruct the Agent to call `dm2 run --instructions <step_id> --json`
- **AND** SHALL use the returned context, rules, and template to complete the step

#### Scenario: Complete a step and advance
- **WHEN** AI Agent finishes executing a pipeline step
- **THEN** the Agent SHALL execute `dm2 run --complete-step <step_id> --json`
- **AND** SHALL check the returned `next_step` for the next step ID
- **AND** SHALL continue to the next step or report completion

#### Scenario: Check pipeline status
- **WHEN** user invokes `/dm2:pipeline status`
- **THEN** the AI Agent SHALL execute `dm2 run --status --json`
- **AND** SHALL display current step, iteration count, and step completion status

#### Scenario: Pipeline already running
- **WHEN** user tries to start a new pipeline while one is in progress
- **THEN** the AI Agent SHALL detect the existing pipeline via `dm2 run --status --json`
- **AND** SHALL ask user whether to continue the existing pipeline or reset
