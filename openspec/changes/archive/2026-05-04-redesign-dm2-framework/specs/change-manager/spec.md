## ADDED Requirements

### Requirement: Create a new architecture change
The system SHALL provide `dm2 change new <name>` that creates a standardized change directory under `dm2-changes/<name>/` with a `.change.yaml` state file, subdirectories for analysis/, views/, and delta-specs/, and an initial status of `open`.

#### Scenario: New change is created
- **WHEN** user executes `dm2 change new "防火墙升级"`
- **THEN** `dm2-changes/防火墙升级/` SHALL be created with `.change.yaml` containing status=open and creation timestamp

### Requirement: Query change status with artifact graph
The system SHALL provide `dm2 change status --change <name> --json` that returns the change's lifecycle status, artifact completion states, and the artifact dependency graph status.

#### Scenario: Change status is queried mid-workflow
- **WHEN** a change has artifacts OV-1 (done) and OV-2 (pending)
- **THEN** `dm2 change status --json` SHALL return artifact list showing OV-1=done, OV-2=pending, plus which artifacts are ready for generation

### Requirement: Change lifecycle states
A change SHALL progress through defined lifecycle states: `open` → `analyzing` → `generating` → `verifying` → `complete`. State transitions SHALL be recorded in `.change.yaml`.

#### Scenario: Change progresses through states
- **WHEN** analysis phase completes and generation begins
- **THEN** `.change.yaml` SHALL update status from `analyzing` to `generating`

### Requirement: Archive completed change
The system SHALL provide `dm2 change archive <name>` that moves a completed change from `dm2-changes/` to `dm2-archive/<date>-<name>/` and updates the archive index.

#### Scenario: Completed change is archived
- **WHEN** user executes `dm2 change archive "防火墙升级"` with status=complete
- **THEN** the change directory SHALL be moved to `dm2-archive/2026-05-03-防火墙升级/` and the archive index SHALL be updated

### Requirement: List active changes
The system SHALL provide `dm2 change list --json` that returns all non-archived changes with their current status, artifact completion counts, and last-modified timestamps.

#### Scenario: Changes are listed
- **WHEN** there are 3 active changes at different stages
- **THEN** the list SHALL show each change name, status, artifact progress (N/M), and last-modified time
