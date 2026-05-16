## ADDED Requirements

### Requirement: Single-change archive
The dm2-archive-workflow SHALL archive a single completed dm2 change, providing a simple confirmation-based flow distinct from `/dm2:bulk-archive`.

#### Scenario: Archive a completed change
- **WHEN** user runs `/dm2:archive` with a valid change name
- **THEN** the workflow SHALL check change status via `dm2 change status --json`
- **AND** SHALL read tasks.md for task completion summary
- **AND** SHALL optionally run `dm2 validate --all --change "<name>" --json` before archiving
- **AND** SHALL display a summary of what will be archived and ask for confirmation
- **AND** SHALL execute `dm2 archive "<name>" --json` upon confirmation
- **AND** SHALL display the archive result and location

#### Scenario: Archive warns on incomplete tasks
- **WHEN** user runs `/dm2:archive` on a change with incomplete tasks in tasks.md
- **THEN** the workflow SHALL warn about incomplete tasks
- **AND** SHALL allow the user to proceed or cancel

#### Scenario: No change name provided
- **WHEN** user runs `/dm2:archive` without specifying a change name
- **THEN** the workflow SHALL run `dm2 change list-changes --json` and prompt user to select
