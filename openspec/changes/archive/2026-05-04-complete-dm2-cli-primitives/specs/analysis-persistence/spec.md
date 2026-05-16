## ADDED Requirements

### Requirement: Analysis result persistence
The `dm2 cynefin` and `dm2 analyze` commands SHALL persist their JSON results to `.dm2/analysis-state.yaml` as a side effect of normal execution.

#### Scenario: Cynefin result persisted
- **WHEN** user executes `dm2 cynefin "<description>" --json`
- **THEN** the system SHALL output JSON to stdout
- **AND** SHALL write the same result to `.dm2/analysis-state.yaml` under the key `cynefin`

#### Scenario: Analyze result persisted
- **WHEN** user executes `dm2 analyze "<description>" --json`
- **THEN** the system SHALL output JSON to stdout
- **AND** SHALL write the result to `.dm2/analysis-state.yaml` under the key `analysis`

#### Scenario: Successive analyses overwrite
- **WHEN** a second analysis is run
- **THEN** the new result SHALL overwrite the previous analysis data in `.dm2/analysis-state.yaml`

#### Scenario: Read analysis state via project status
- **WHEN** user executes `dm2 status --json`
- **THEN** the response SHALL include an `analysis` field with the latest Cynefin domain and analysis summary if available
- **AND** SHALL include `null` for the analysis field if no analysis has been run

#### Scenario: No project context
- **WHEN** `dm2 cynefin` or `dm2 analyze` is executed outside a dm2 project
- **THEN** the system SHALL output JSON to stdout normally but SHALL NOT persist state (no `.dm2/` directory)
