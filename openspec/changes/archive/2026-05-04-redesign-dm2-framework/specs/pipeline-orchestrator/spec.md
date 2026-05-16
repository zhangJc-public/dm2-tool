## MODIFIED Requirements

### Requirement: dm2 run command
The system SHALL provide a `dm2 run` command that executes the complete 6-step DODAF architecture development pipeline from a user-provided architecture description. In Agent-driven mode (new default for `dm2 run --agent`), the CLI generates step instructions that AI Agents execute; the CLI manages state and validates outputs. The legacy hardcoded mode SHALL remain available for backward compatibility.

#### Scenario: User starts a new pipeline run
- **WHEN** user executes `dm2 run -d "描述某个系统的架构意图"`
- **THEN** the system SHALL execute Step 1+2 through Step 6 sequentially and output progress at each step

#### Scenario: Agent starts a pipeline run
- **WHEN** AI Agent executes `dm2 run -d "描述" --agent --json`
- **THEN** the system SHALL return step-by-step instructions as JSON and wait for the Agent to call `--complete-step` between each step
