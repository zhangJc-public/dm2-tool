## ADDED Requirements

### Requirement: Knowledge query skill
The system SHALL provide a Claude Code skill (`dm2-knowledge`) that enables AI Agent to query DM2 knowledge base using `python3 -m dm2.cli.main knowledge` subcommands.

#### Scenario: Search DM2 terms
- **WHEN** AI Agent invokes `dm2-knowledge` skill with a search query
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main knowledge search "<query>" --json` and return structured results

#### Scenario: Get concept details
- **WHEN** AI Agent invokes `dm2-knowledge` skill to look up a concept
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main knowledge concept "<name>" --json`

#### Scenario: List all views
- **WHEN** AI Agent invokes `dm2-knowledge` skill to enumerate views
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main knowledge views --json`

### Requirement: Architecture analysis skill
The system SHALL provide a Claude Code skill (`dm2-analyze`) that enables AI Agent to run DoDAF architecture analysis.

#### Scenario: Cynefin assessment
- **WHEN** AI Agent invokes `dm2-analyze` skill for Cynefin analysis
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main cynefin "<description>" --json`

#### Scenario: 6W analysis with view recommendation
- **WHEN** AI Agent invokes `dm2-analyze` skill for full analysis
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main analyze "<description>" --json`

### Requirement: Agent-driven pipeline skill
The system SHALL provide a Claude Code skill (`dm2-pipeline`) that enables AI Agent to manage the 4-step Agent-driven DoDAF pipeline.

#### Scenario: Initialize pipeline
- **WHEN** AI Agent invokes `dm2-pipeline` skill to start a new pipeline
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main run --agent --json` and return first step instructions

#### Scenario: Get pipeline status
- **WHEN** AI Agent invokes `dm2-pipeline` skill to check status
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main run --status --json`

#### Scenario: Complete a step
- **WHEN** AI Agent invokes `dm2-pipeline` skill after completing a step
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main run --complete-step "<step_id>" --json`

### Requirement: Change management skill
The system SHALL provide a Claude Code skill (`dm2-change`) that enables AI Agent to manage dm2 architecture changes.

#### Scenario: Create a new change
- **WHEN** AI Agent invokes `dm2-change` skill to create a change
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main change new "<name>"`

#### Scenario: List active changes
- **WHEN** AI Agent invokes `dm2-change` skill to list changes
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main change list-changes --json`

#### Scenario: Get change status
- **WHEN** AI Agent invokes `dm2-change` skill for change status
- **THEN** the skill SHALL execute `python3 -m dm2.cli.main change status --json`

### Requirement: Install skills to target project
The system SHALL provide a mechanism to install dm2 Claude Code skills into a target project directory.

#### Scenario: Install via dm2 init
- **WHEN** user runs `dm2 init <name>`
- **THEN** the project SHALL include `.claude/skills/` with dm2 skill files

#### Scenario: Install to existing project
- **WHEN** user runs `dm2 setup-claude` in an existing dm2 project
- **THEN** the system SHALL copy skill files from dm2-tool's `.claude/skills/` to the project's `.claude/skills/`
