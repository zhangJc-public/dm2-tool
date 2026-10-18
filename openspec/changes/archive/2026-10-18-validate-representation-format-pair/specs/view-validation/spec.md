# Spec Delta

## Purpose

Validation resolves each view's format and checks the evidence that carrier requires.

## MODIFIED Requirements

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
