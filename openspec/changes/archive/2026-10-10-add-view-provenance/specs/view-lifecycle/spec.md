# View Lifecycle (delta)

This is a delta spec modifying the existing `view-lifecycle` capability to integrate with the view provenance system.

## MODIFIED Requirements

### Requirement: View lifecycle state management
The system SHALL provide a `ViewManager` class in `dm2.core.views.manager` that manages the lifecycle state of DoDAF views within a dm2 project. The ViewManager SHALL also expose pedigree state information for each view, including whether core pedigree fields are present and complete.

#### Scenario: View state transitions
- **WHEN** a view is first created or detected in the project output
- **THEN** its status SHALL be `pending`
- **WHEN** view generation begins
- **THEN** its status SHALL transition to `in_progress`
- **WHEN** view content is written to the output path
- **THEN** its status SHALL transition to `generated`
- **WHEN** the view passes consistency validation
- **AND** the view's pedigree has all required core fields (author, creation_date, source) populated
- **THEN** its status SHALL transition to `verified`
- **WHEN** the view passes consistency validation
- **BUT** the view's pedigree is missing one or more core fields
- **THEN** its status SHALL remain `generated` and a validation issue "Pedigree incomplete: missing [field names]" SHALL be reported

#### Scenario: State persistence
- **WHEN** ViewManager updates any view status
- **THEN** the change SHALL be immediately persisted to `.dm2/view-state.yaml`

#### Scenario: Load existing state
- **WHEN** ViewManager is initialized with a project root
- **THEN** it SHALL load existing state from `.dm2/view-state.yaml` if present
- **AND** SHALL create an empty state if no state file exists

## ADDED Requirements

### Requirement: Pedigree status in view state
The `view-state.yaml` schema SHALL include pedigree status information for each view.

#### Scenario: View state includes pedigree status
- **WHEN** a view's state is persisted
- **THEN** the YAML entry SHALL include a `pedigree_status` field with one of:
  - `complete` — all core fields present
  - `incomplete` — some core fields missing (lists missing fields in `pedigree_missing`)
  - `absent` — no pedigree record exists at `.dm2/pedigree/<view_id>.yaml`

#### Scenario: List views with pedigree filter
- **WHEN** user runs `dm2 view list --pedigree-status incomplete`
- **THEN** the system SHALL display only views whose `pedigree_status` is `incomplete`
- **AND** SHALL include the list of missing fields in the table

#### Scenario: JSON list includes pedigree status
- **WHEN** user runs `dm2 view list --json`
- **THEN** each view object SHALL include `pedigree_status` and `pedigree_missing` fields

### Requirement: State transition requires pedigree validation
The `verified` state transition SHALL be gated by pedigree completeness, with a documented override path.

#### Scenario: Auto-blocked verified transition
- **WHEN** view validation passes with no errors
- **AND** pedigree core fields are missing
- **THEN** the ViewManager SHALL refuse the transition
- **AND** SHALL append a `ModificationRecord` to the pedigree with `change_description="verified blocked: pedigree incomplete"`

#### Scenario: Force override transition
- **WHEN** user runs `dm2 validate <view_id> --force-pedigree`
- **THEN** the ViewManager SHALL allow the verified transition despite missing fields
- **AND** SHALL append a `ModificationRecord` with `actor=<operator>`, `change_description="verified via --force-pedigree override"`
