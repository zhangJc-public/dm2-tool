# no-new-capability Specification

## Purpose
Constrain the propose workflow to orchestration rather than invention: dm2 does not gain a new capability for authoring analysis prose, and instead guides the agent to write its own analysis artifacts from the structured context dm2 emits.

## Requirements
### Requirement: propose workflow guides agent to write own analysis

The propose workflow SKILL.md SHALL guide the AI Agent to optionally save its own rich analysis artifacts to `dm2-changes/<name>/analysis/` for audit, rather than directing it to dump raw CLI JSON output.

#### Scenario: Agent writes own analysis

- **WHEN** the AI Agent executes `/dm2:propose`
- **AND** the SKILL.md says "Optionally save your own rich analysis"
- **THEN** the Agent MAY save its own reasoning to `analysis/cynefin-assessment.md` or `analysis/data-group-activation.md`
- **AND** the Agent SHALL NOT dump raw CLI JSON output as a file

