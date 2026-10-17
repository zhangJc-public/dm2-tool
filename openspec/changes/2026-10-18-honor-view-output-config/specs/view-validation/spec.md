# Spec Delta

## Purpose

Validation reports when a generated view does not honour the `representation` it declares in `views.yaml`.

## ADDED Requirements

### Requirement: Representation conformance check
`dm2 validate` SHALL compare every generated view's declared `representation` with the evidence in the view's content — a Mermaid block, an external figure reference, or neither — and report each mismatch as a consistency issue.

#### Scenario: Diagram-bearing view ships no diagram
- **WHEN** a view declares `representation: state-diagram`
- **AND** its content contains neither a Mermaid block nor a figure reference
- **THEN** validation SHALL report a `representation_missing_diagram` warning for that view

#### Scenario: Mermaid type does not match the declaration
- **WHEN** a view declares `representation: state-diagram`
- **AND** its content contains a `graph` Mermaid block
- **THEN** validation SHALL report a `representation_mismatch` warning naming the found and the allowed types

#### Scenario: External figure satisfies the requirement
- **WHEN** a view declares a diagram representation
- **AND** its content references an `.svg`, `.png` or `.jpg` figure instead of Mermaid
- **THEN** validation SHALL NOT report a representation issue for that view

#### Scenario: Diagram appears in a tabular view
- **WHEN** a view declares `representation: table` or `text`
- **AND** its content contains a Mermaid block
- **THEN** validation SHALL report a `representation_unexpected_diagram` warning for that view

#### Scenario: Strict mode promotes representation issues
- **WHEN** the project config sets `consistency.strict_mode: true`
- **THEN** representation issues SHALL be reported at ERROR severity instead of WARNING

#### Scenario: Unknown view metadata is skipped
- **WHEN** a view has no `representation` in `views.yaml`
- **THEN** the representation check SHALL skip it without reporting an issue
