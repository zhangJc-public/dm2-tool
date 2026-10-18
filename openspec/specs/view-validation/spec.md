# View Validation

## Purpose
Validate generated DoDAF views for consistency using the reasoning engine's check rules. TBD: extensible rule framework.

## Requirements

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

### Requirement: Representation conformance check
`dm2 validate` SHALL resolve each generated view's format from project configuration, then compare the view's content against the evidence that format requires, reporting every mismatch as a consistency issue.

#### Scenario: Diagram-bearing view ships no diagram
- **WHEN** a view's resolved format is `mermaid`
- **AND** its content contains neither a Mermaid block nor a figure reference
- **THEN** validation SHALL report a `representation_missing_diagram` issue for that view

#### Scenario: Mermaid type does not match the declaration
- **WHEN** a view's resolved format is `mermaid`
- **AND** its content contains a Mermaid block of a type the representation does not allow
- **THEN** validation SHALL report a `representation_mismatch` issue naming the found and allowed types

#### Scenario: External figure satisfies the requirement
- **WHEN** a view's resolved format is `svg` or `png`
- **AND** its content references an artefact with that format's extension
- **THEN** validation SHALL NOT report a representation issue for that view

#### Scenario: Diagram appears in a tabular view
- **WHEN** a view's resolved format is `markdown`
- **AND** its content contains a Mermaid block
- **THEN** validation SHALL report a `representation_unexpected_diagram` issue for that view

#### Scenario: Strict mode promotes representation issues
- **WHEN** the project config sets `consistency.strict_mode: true`
- **THEN** representation issues SHALL be reported at ERROR severity instead of WARNING

#### Scenario: Unknown view metadata is skipped
- **WHEN** a view has no `representation` in `views.yaml`
- **THEN** the representation check SHALL skip it without reporting an issue

#### Scenario: Mermaid carrier is satisfied
- **WHEN** a view's resolved format is `mermaid`
- **AND** its content contains a Mermaid block whose type matches its representation
- **THEN** validation SHALL NOT report a representation issue for that view

#### Scenario: Declared Mermaid but delivered as a figure
- **WHEN** a view's resolved format is `mermaid`
- **AND** its content references a figure instead of containing a Mermaid block
- **THEN** validation SHALL report a `representation_mismatch` issue

#### Scenario: Figure carrier references nothing
- **WHEN** a view's resolved format is an artefact format such as `svg`, `png` or `xlsx`
- **AND** its content references no matching artefact
- **THEN** validation SHALL report a `representation_missing_artifact` issue

#### Scenario: Artefact carrier contains Mermaid instead
- **WHEN** a view's resolved format is an artefact format
- **AND** its content contains a Mermaid block
- **THEN** validation SHALL report a `representation_mismatch` issue

#### Scenario: Markdown carrier attaches an illustration
- **WHEN** a view's resolved format is `markdown`
- **AND** its content references a figure but contains no Mermaid block
- **THEN** validation SHALL NOT report a representation issue

### Requirement: Activity performer binding is checked within OV-5b
Validation SHALL report an activity that OV-5b declares without a stated performer, recognising activities by identifier in both the Mermaid node labels and the activity table, and SHALL NOT require OV-5a decomposition leaves to appear in OV-5b.

#### Scenario: Activity in the table with a performer
- **WHEN** the OV-5b activity table has a row for `A1` whose performer column names a performer
- **THEN** validation SHALL NOT report `A1` as an unbound activity

#### Scenario: Activity in the table with an empty performer
- **WHEN** the OV-5b activity table has a row for `A1` whose performer column is empty
- **THEN** validation SHALL report an `unbound_activity` error naming `A1`

#### Scenario: Activity in a Mermaid label with an empty performer
- **WHEN** an OV-5b node label reads `执行者：<br/>` and names no performer
- **THEN** validation SHALL report that activity as unbound

#### Scenario: OV-5a decomposes deeper than OV-5b tracks
- **WHEN** OV-5a contains `A1.1` and OV-5b tracks only `A1`
- **THEN** validation SHALL NOT report `A1.1` as unbound

#### Scenario: Mermaid node identifiers are not activities
- **WHEN** an OV-5b line reads `X --> A53["A5.3 双人确认"]`
- **THEN** the activity SHALL be reported by its identifier `A5.3`, never as `A53`

### Requirement: Resource extraction ignores the view title
Resource extraction SHALL ignore level-1 headings, so a bilingual view title containing the English word "Resource" is not reported as an orphan resource.

#### Scenario: Bilingual title with the word Resource
- **WHEN** OV-2 starts with `# OV-2 作战资源流描述（Operational Resource Flow Description）`
- **THEN** validation SHALL NOT report an `orphan_resource` issue for that title

#### Scenario: A section heading still yields resources
- **WHEN** OV-2 contains a level-2 heading naming resources followed by a list item
- **THEN** validation SHALL extract the resource and report it as orphaned when nothing produces or consumes it
