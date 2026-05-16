## ADDED Requirements

### Requirement: View lifecycle state management
The system SHALL provide a `ViewManager` class in `dm2.core.views.manager` that manages the lifecycle state of DoDAF views within a dm2 project.

#### Scenario: View state transitions
- **WHEN** a view is first created or detected in the project output
- **THEN** its status SHALL be `pending`
- **WHEN** view generation begins
- **THEN** its status SHALL transition to `in_progress`
- **WHEN** view content is written to the output path
- **THEN** its status SHALL transition to `generated`
- **WHEN** the view passes consistency validation
- **THEN** its status SHALL transition to `verified`

#### Scenario: State persistence
- **WHEN** ViewManager updates any view status
- **THEN** the change SHALL be immediately persisted to `.dm2/view-state.yaml`

#### Scenario: Load existing state
- **WHEN** ViewManager is initialized with a project root
- **THEN** it SHALL load existing state from `.dm2/view-state.yaml` if present
- **AND** SHALL create an empty state if no state file exists

### Requirement: View list CLI command
The system SHALL provide a `dm2 view list` command that lists all views in the project with their generation status.

#### Scenario: List all views
- **WHEN** user executes `dm2 view list`
- **THEN** the system SHALL display a table with view_id, status, and last modified timestamp for each view

#### Scenario: List views with JSON output
- **WHEN** user executes `dm2 view list --json`
- **THEN** the system SHALL output JSON array with view objects containing id, status, generated_at, verified_at fields

#### Scenario: Filter by status
- **WHEN** user executes `dm2 view list --status generated`
- **THEN** the system SHALL display only views with status `generated`

### Requirement: Enhanced project status with view progress
The `dm2 status` command SHALL include view generation progress statistics.

#### Scenario: Status includes view counts
- **WHEN** user executes `dm2 status --json`
- **THEN** the response SHALL include a `views` object with counts for each status (pending, in_progress, generated, verified)
