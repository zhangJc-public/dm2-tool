## MODIFIED Requirements

### Requirement: Scaffold-only on create
The /dm2:new workflow SHALL create a change directory and initial state only, then wait for user direction. The cynefin assessment, 6W analysis, and view generation steps SHALL be removed from this workflow and only exist in /dm2:propose.

#### Scenario: User runs /dm2:new
- **WHEN** user runs `/dm2:new` with a system description or name
- **THEN** the workflow SHALL create a new change via `dm2 change new`
- **AND** SHALL display the change name and location
- **AND** SHALL prompt: "Ready for full analysis? Run `/dm2:propose` or say what you'd like to do."
- **AND** SHALL NOT execute cynefin, 6W analysis, or view generation
