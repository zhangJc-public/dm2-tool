# View Validation (delta)

## ADDED Requirements

### Requirement: Metamodel-grounded conformance checks
The system SHALL provide a `MetamodelConformanceChecker` that validates
structured instance data (note frontmatter `dm2-type` and typed relationships)
against `associations.json` and `taxonomy.json`, distinct from the existing
prose-level `ConsistencyChecker` regex rules.

#### Scenario: Unknown relationship is flagged
- **WHEN** a note declares a relationship whose label is not in the
  association catalog (e.g. `measuredByOrg`)
- **THEN** the checker SHALL report a WARNING issue with the nearest catalog
  association name as a suggestion

#### Scenario: Endpoint type conformance is subtype-aware
- **WHEN** a relationship instance connects endpoint types that are not
  compatible with the catalog definition
- **THEN** the checker SHALL report an ERROR listing the relationship label,
  actual endpoint types, and expected endpoint types
- **AND** a subtype endpoint (e.g. System where Performer is expected) SHALL
  pass via the taxonomy transitive closure

#### Scenario: Required association completeness at view level
- **WHEN** a view is validated against `view-content-spec.json`
- **THEN** the checker SHALL report a WARNING for each necessary association
  absent from the project's structured data within the view's scope

#### Scenario: Type/Individual layering consistency
- **WHEN** a note carries `dm2-layer: Individual` or `dm2-layer: Type`
- **THEN** the checker SHALL report an INFO issue when the layer is
  inconsistent with the powertype pairs in `taxonomy.json`

#### Scenario: Unknown DM2 type
- **WHEN** a note's `dm2-type` does not match any term in `terms.json`
- **THEN** the checker SHALL report a WARNING suggesting the closest term

### Requirement: Conformance checks tolerate missing structure
Conformance checks SHALL operate only on structured frontmatter and skip
notes lacking typed relationships without failing; missing structure produces
INFO-level guidance, never ERROR.

#### Scenario: Prose-only note is checked by legacy rules
- **WHEN** a view note contains free-text Markdown without typed
  relationships
- **THEN** the legacy regex-based `ConsistencyChecker` rules SHALL still run
- **AND** the combined report SHALL label which checker produced each issue

### Requirement: Validation report separates layers
The `dm2 validate` output SHALL distinguish metamodel conformance issues from
prose heuristic issues.

#### Scenario: JSON output includes checker source
- **WHEN** `dm2 validate <view> --json` runs
- **THEN** each issue in the JSON output SHALL include a `source` field with
  value `metamodel-conformance` or `prose-heuristic`
- **AND** issue severities SHALL remain error/warning/info with counts in the
  summary
