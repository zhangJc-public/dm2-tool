# View Validation

**Purpose**: Validate generated DoDAF views for consistency using the reasoning engine's check rules. TBD: extensible rule framework.

## Requirements

### Requirement: View validation CLI command
The system SHALL provide a `dm2 validate` command that runs consistency checks on generated DoDAF views using the existing `ConsistencyChecker` from `dm2.reasoning`.

#### Scenario: Validate a single view
- **WHEN** user executes `dm2 validate OV-2`
- **THEN** the system SHALL run `ConsistencyChecker.check_views()` with the specified view's content
- **AND** SHALL display issues grouped by severity (ERROR, WARNING, INFO)

#### Scenario: Validate all generated views
- **WHEN** user executes `dm2 validate --all`
- **THEN** the system SHALL load all views with status `generated` or `verified` from ViewManager
- **AND** SHALL run consistency checks across all loaded views

#### Scenario: JSON output for validation
- **WHEN** user executes `dm2 validate OV-2 --json`
- **THEN** the system SHALL output a JSON object with `view_id`, `issues` array (each containing `type`, `severity`, `message`, `suggestion`), and `summary` (counts by severity)

#### Scenario: No issues found
- **WHEN** consistency check finds no issues
- **THEN** the system SHALL report "No consistency issues found" and exit with code 0

#### Scenario: View not found
- **WHEN** user executes `dm2 validate <view_id>` for a view that has not been generated
- **THEN** the system SHALL report error "View <view_id> not found in project" and exit with code 1

### Requirement: Validation mark in view state
After successful validation, the system SHALL update the view status to `verified`.

#### Scenario: Auto-update on clean validation
- **WHEN** validation runs and finds zero ERROR-level issues
- **THEN** the system SHALL update the view status to `verified` in ViewManager

#### Scenario: No status change on validation failure
- **WHEN** validation finds ERROR-level issues
- **THEN** the view status SHALL remain unchanged
