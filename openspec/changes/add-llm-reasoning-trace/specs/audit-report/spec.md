# Audit Report

**Purpose**: Generate human-readable audit reports from Pedigree records, supporting engineering compliance review and "why was this built this way" questions. Distinct from `dm2 validate` (which checks view correctness) — audit reports explain view provenance and rationale.

## ADDED Requirements

### Requirement: Single view audit report
The system SHALL provide a `dm2 audit <view_id>` command that produces a human-readable Markdown report explaining the provenance and rationale of a single view.

#### Scenario: Audit an existing view with pedigree
- **WHEN** user runs `dm2 audit CV-1`
- **AND** the view `CV-1` has a complete pedigree record
- **THEN** the system SHALL output a Markdown report containing:
  - **Author and timestamp** section (from `pedigree.author` and `pedigree.creation_date`)
  - **Standard provenance** section (from `pedigree.source`)
  - **Reasoning summary** section (from `pedigree.reasoning.summary`)
  - **Decision factors** table (from `pedigree.reasoning.decision_factors`)
  - **Alternatives considered** section (from `pedigree.reasoning.alternatives_considered`)
  - **Modification history** table (from `pedigree.modification_history`)
  - **Validation history** section (from `pedigree.validation`)
  - **Known limitations** section (from `pedigree.known_limitations`)

#### Scenario: Audit a view without pedigree
- **WHEN** user runs `dm2 audit <view_id>`
- **AND** the view has no pedigree record
- **THEN** the system SHALL output a report stating "No pedigree record found for view <view_id>"
- **AND** SHALL include the view's current lifecycle state from view-state.yaml
- **AND** SHALL suggest running `dm2 trace record <view_id>` to add provenance

#### Scenario: Audit with JSON output
- **WHEN** user runs `dm2 audit CV-1 --json`
- **THEN** the system SHALL output a JSON object with sections matching the Markdown structure
- **AND** the structure SHALL include: `view_id`, `pedigree` (or null), `lifecycle_state`, `generated_at`

### Requirement: Project-wide audit report
The system SHALL provide a `dm2 audit-report` command that produces a project-level audit report covering all views.

#### Scenario: Generate project audit report
- **WHEN** user runs `dm2 audit-report`
- **THEN** the system SHALL aggregate pedigree data from all views
- **AND** SHALL output a Markdown report containing:
  - **Project summary**: total views, count by lifecycle state, count with/without pedigree
  - **Per-data-group coverage**: which DM2 data groups are represented in view sources
  - **Per-view entries**: each view's title, author, creation date, confidence, validation status
  - **Trace gaps section**: list of views missing pedigree core fields

#### Scenario: Audit report with confidence filter
- **WHEN** user runs `dm2 audit-report --min-confidence 0.7`
- **THEN** the system SHALL only include views with `pedigree.confidence >= 0.7` in the per-view entries
- **AND** SHALL include a "filtered out" count in the project summary

#### Scenario: Audit report JSON output
- **WHEN** user runs `dm2 audit-report --json`
- **THEN** the system SHALL output a JSON object with `summary`, `data_group_coverage`, `views` (array), `trace_gaps` (array of view_ids missing core fields)

### Requirement: Audit report output paths
The system SHALL write audit reports to a configurable output path, defaulting to `.dm2/audit/`.

#### Scenario: Default output path
- **WHEN** user runs `dm2 audit <view_id>` (without `--output`)
- **THEN** the system SHALL write the report to `.dm2/audit/<view_id>-audit.md`
- **AND** SHALL create `.dm2/audit/` if it does not exist

#### Scenario: Custom output path
- **WHEN** user runs `dm2 audit CV-1 --output reports/cv1-audit.md`
- **THEN** the system SHALL write the report to `reports/cv1-audit.md` (relative to project root)
- **AND** SHALL create parent directories as needed

#### Scenario: Project audit report path
- **WHEN** user runs `dm2 audit-report`
- **THEN** the system SHALL write to `.dm2/audit/project-audit-<YYYYMMDD>.md`
- **AND** SHALL include the date in the filename to prevent overwrites

### Requirement: Audit report references DoDAF standard sections
The audit report SHALL include the DoDAF V2.02 Vol 2 section reference for each view, sourced from the view's pedigree.

#### Scenario: Section reference in report
- **WHEN** an audit report is generated for a view
- **AND** the view's pedigree has `source.standard` and `source.section` populated
- **THEN** the report SHALL include a "Standard Reference" section
- **AND** the section SHALL cite `source.standard` and `source.section` exactly

#### Scenario: Section reference missing
- **WHEN** an audit report is generated for a view
- **AND** the view's pedigree has `source.standard` empty
- **THEN** the report SHALL include "Standard reference: NOT RECORDED" in the Standard Reference section
- **AND** SHALL list this as a trace gap in the project audit report

### Requirement: Audit report CLI integration
The audit commands SHALL be accessible via the existing CLI structure, following the same patterns as `dm2 view` and `dm2 validate`.

#### Scenario: Audit command help
- **WHEN** user runs `dm2 audit --help`
- **THEN** the system SHALL display usage information including required arguments and options
- **AND** SHALL show `--json`, `--output`, `--min-confidence` flags

#### Scenario: Audit requires dm2 project
- **WHEN** user runs `dm2 audit <view_id>` outside a dm2 project
- **THEN** the system SHALL output error "Not in a dm2 project" with code 1
- **AND** SHALL suggest running `dm2 init` first
