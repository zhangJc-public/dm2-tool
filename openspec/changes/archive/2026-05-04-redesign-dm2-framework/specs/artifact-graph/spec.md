## ADDED Requirements

### Requirement: View dependency graph
The system SHALL maintain a dependency graph of all 52 DoDAF views, where each view declares its prerequisite views (must be generated first) and downstream views (depend on this view). The graph SHALL be derived from `dm2-reference/views.yaml`.

#### Scenario: Dependencies are resolved
- **WHEN** querying the graph for OV-5a's dependencies
- **THEN** the system SHALL return that OV-5a depends on OV-1 and OV-2 (or other views as defined in views.yaml)

### Requirement: Artifact status computation
For each artifact in a change context, the system SHALL compute its status as one of: `pending` (unmet dependencies), `ready` (all dependencies satisfied), `in_progress` (currently being generated), or `done` (output file exists).

#### Scenario: Artifact becomes ready after dependency completion
- **WHEN** OV-1 artifact is marked done
- **THEN** OV-2 SHALL transition from `pending` to `ready`

#### Scenario: Artifact is pending with unmet dependencies
- **WHEN** an artifact has 3 dependencies and only 2 are done
- **THEN** its status SHALL be `pending`

### Requirement: Query ready artifacts
The system SHALL provide a method to query all artifacts with status `ready`, enabling AI agents to determine "what to generate next" without understanding the full dependency graph.

#### Scenario: AI agent queries next steps
- **WHEN** an AI agent queries which artifacts are ready to generate
- **THEN** the system SHALL return a list of artifact IDs whose dependencies are all satisfied and whose output does not yet exist

### Requirement: Artifact status via CLI
The `dm2 change status --json` command SHALL include artifact graph information: a list of all artifacts with their status, dependencies, and output paths.

#### Scenario: Change status includes artifact graph
- **WHEN** `dm2 change status --change "firewall-upgrade" --json` is executed
- **THEN** the response SHALL include an `artifacts` array with each artifact's id, status, dependencies, and output_path
