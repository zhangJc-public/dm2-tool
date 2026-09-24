# View Validation (delta)

This delta extends the validation pipeline to write results into the reasoning trace, and gates the `verified` transition on pedigree completeness.

## MODIFIED Requirements

### Requirement: View validation CLI command
The system SHALL provide a `dm2 validate` command that runs consistency checks on generated DoDAF views using the existing `ConsistencyChecker` from `dm2.reasoning`. After validation completes, the system SHALL persist validation results into the view's pedigree record.

#### Scenario: Validate a single view
- **WHEN** user executes `dm2 validate OV-2`
- **THEN** the system SHALL run `ConsistencyChecker.check_views()` with the specified view's content
- **AND** SHALL display issues grouped by severity (ERROR, WARNING, INFO)
- **AND** SHALL write the issues array to `pedigree.validation.issues` for view `OV-2`
- **AND** SHALL update `pedigree.validation.ran_R1`-`ran_R5` based on which rules ran
- **AND** SHALL set `pedigree.validation.last_validated` to the current time

#### Scenario: Validate all generated views
- **WHEN** user executes `dm2 validate --all`
- **THEN** the system SHALL load all views with status `generated` or `verified` from ViewManager
- **AND** SHALL run consistency checks across all loaded views
- **AND** SHALL persist validation results to each view's pedigree record

#### Scenario: JSON output for validation
- **WHEN** user executes `dm2 validate OV-2 --json`
- **THEN** the system SHALL output a JSON object with `view_id`, `issues` array (each containing `type`, `severity`, `message`, `suggestion`), and `summary` (counts by severity)
- **AND** SHALL include a `pedigree_updated: true|false` field indicating whether the trace was written

#### Scenario: No issues found
- **WHEN** consistency check finds no issues
- **THEN** the system SHALL report "No consistency issues found" and exit with code 0
- **AND** SHALL write an empty issues array to the pedigree (preserving last_validated timestamp)

#### Scenario: View not found
- **WHEN** user executes `dm2 validate <view_id>` for a view that has not been generated
- **THEN** the system SHALL report error "View <view_id> not found in project" and exit with code 1

### Requirement: Validation mark in view state
After successful validation, the system SHALL update the view status to `verified` if and only if the view's pedigree is complete; otherwise, the status remains unchanged and a new validation issue is added.

#### Scenario: Auto-update on clean validation
- **WHEN** validation runs and finds zero ERROR-level issues
- **AND** the view's pedigree has all core fields (author, creation_date, source) populated
- **THEN** the system SHALL update the view status to `verified` in ViewManager
- **AND** SHALL append a ModificationRecord to the pedigree with `change_description="verified: validation passed"`

#### Scenario: Blocked verification due to incomplete pedigree
- **WHEN** validation runs and finds zero ERROR-level issues
- **BUT** the view's pedigree is missing core fields
- **THEN** the system SHALL NOT transition the view to `verified`
- **AND** SHALL add a validation issue: `rule: pedigree`, `severity: error`, `message: "Pedigree incomplete: missing [field names]"`
- **AND** SHALL report the pedigree incompleteness in the command output

#### Scenario: No status change on validation failure
- **WHEN** validation finds ERROR-level issues
- **THEN** the view status SHALL remain unchanged
- **AND** the issues SHALL be persisted to the pedigree

## ADDED Requirements

### Requirement: Validation issues carry suggested fixes
Each validation issue persisted to pedigree SHALL include, when applicable, a `suggested_fix` field that the AI Agent can act on.

#### Scenario: Suggested fix included
- **WHEN** `ConsistencyChecker` produces an issue of type `missing-reference` or `term-mismatch`
- **THEN** the system SHALL attach a `suggested_fix` field with concrete guidance (e.g., "Add reference to CV-1 capability X" or "Replace 'capability' with 'Capability' to match DM2 term")
- **AND** the fix SHALL be machine-parseable (string or list of strings)

#### Scenario: Issue without fix
- **WHEN** an issue type has no automated fix available
- **THEN** the system SHALL persist the issue without a `suggested_fix` field
- **AND** the audit report SHALL display "No automated fix available" for that issue
