## ADDED Requirements

### Requirement: View state tracking
The system SHALL track the generation status of each DoDAF view within a dm2 project, persisting state to `.dm2/view-state.yaml`.

#### Scenario: View lifecycle states
- **WHEN** a view is first recommended by analysis
- **THEN** its status SHALL be `pending`
- **WHEN** an AI Agent begins generating a view
- **THEN** its status SHALL be `in_progress`
- **WHEN** view content is written to the output path
- **THEN** its status SHALL be `generated`
- **WHEN** the view passes consistency verification
- **THEN** its status SHALL be `verified`

#### Scenario: Query view status
- **WHEN** AI Agent or user queries view state
- **THEN** the system SHALL return a list of views with their current status and timestamps

### Requirement: ViewManager API
The system SHALL provide a `ViewManager` class in `dm2.core.views.manager` that manages view lifecycle state.

#### Scenario: Initialize ViewManager
- **WHEN** ViewManager is constructed with a project root
- **THEN** it SHALL read existing state from `.dm2/view-state.yaml` if it exists
- **AND** SHALL initialize an empty state if the file does not exist

#### Scenario: Update view status
- **WHEN** `update_status(view_id, status)` is called
- **THEN** the state file SHALL be updated with the new status and current timestamp
- **AND** the change SHALL be immediately persisted to `.dm2/view-state.yaml`

#### Scenario: List views by status
- **WHEN** `list_views(status_filter)` is called
- **THEN** the system SHALL return views matching the given status filter
- **AND** SHALL include timestamps for each view

#### Scenario: Get view generation progress
- **WHEN** `get_progress()` is called
- **THEN** the system SHALL return counts of views in each status (pending, in_progress, generated, verified)

### Requirement: View state CLI command
The system SHALL expose view state through a `dm2 status` command enhancement.

#### Scenario: Show view progress in project status
- **WHEN** user runs `dm2 status --json`
- **THEN** the output SHALL include `views` section with progress counts
- **AND** SHALL list views currently in `in_progress` or `generated` status
