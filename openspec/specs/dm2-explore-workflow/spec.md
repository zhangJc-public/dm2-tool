# dm2-explore-workflow Specification

## Purpose
TBD - created by archiving change add-dm2-explore-workflow. Update Purpose after archive.
## Requirements
### Requirement: dm2 explore workflow is registered and distributable
The `dm2-explore-workflow` SHALL be defined as a Python WorkflowTemplate in `core/templates/workflows/explore.py` and registered in the WORKFLOWS list alongside the other 7 workflows.

#### Scenario: dm2 init generates explore skill and command
- **WHEN** `dm2 init` is run in a project directory
- **THEN** `.claude/skills/dm2-explore-workflow/SKILL.md` SHALL be created
- **AND** `.claude/commands/dm2/explore.md` SHALL be created
- **AND** both files SHALL contain `generatedBy: dm2-tool` version metadata

#### Scenario: explore workflow appears in dm2 workflow list
- **WHEN** `dm2 init` completes
- **THEN** the user SHALL have access to the `/dm2:explore` slash command
- **AND** the command description SHALL indicate it is a read-only exploration mode

### Requirement: Explore workflow is read-only
The `/dm2:explore` skill SHALL instruct the AI Agent to only use `dm2 knowledge *` commands for querying information, and SHALL NOT trigger view generation, change creation, or any file modifications.

#### Scenario: Agent in explore mode only queries knowledge
- **WHEN** an AI Agent is invoked with `/dm2:explore`
- **THEN** the Agent MAY call `dm2 knowledge search`, `dm2 knowledge concept`, `dm2 knowledge view`, `dm2 knowledge views`, `dm2 knowledge stats`
- **AND** the Agent SHALL NOT call `dm2 generate`, `dm2 change new`, `dm2 run`, `dm2 validate`

#### Scenario: Agent encourages exploration without implementation
- **WHEN** the user asks a question in explore mode
- **THEN** the Agent SHALL respond with analysis, comparison, or visualization
- **AND** the Agent SHALL NOT implement code or modify files unless the user explicitly asks to exit explore mode

### Requirement: Explore workflow complements the propose-continue-ff pipeline
The `/dm2:explore` workflow SHALL be positioned as an optional pre-step before `/dm2:propose`, allowing users to understand DoDAF concepts and make informed architecture decisions before committing to a change.

#### Scenario: User transitions from explore to propose
- **WHEN** exploration crystallizes into a clear architecture decision
- **THEN** the Agent SHOULD suggest: "This feels solid enough to start a proposal. Run `/dm2:propose <description>` to kick off full analysis."

