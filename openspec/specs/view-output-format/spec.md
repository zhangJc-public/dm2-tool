# view-output-format Specification

## Purpose
A view's `representation` (what structure it conveys) and its `format` (how that structure is carried) are independent; the format is resolved from project configuration layered over per-representation defaults.

## Requirements

### Requirement: Representation and format are independent axes
The system SHALL treat a view's format as independent of its representation, relating them through a compatibility matrix rather than a one-to-one mapping, so that one representation may be carried by several formats and one format may carry several representations.

#### Scenario: A concept graphic is not forced into a node-link carrier
- **WHEN** a view declares `representation: pictorial`
- **THEN** its default format SHALL be `svg`
- **AND** the default SHALL NOT be an inline Mermaid node-link diagram

#### Scenario: An incompatible pair is rejected
- **WHEN** a requested format is not compatible with the view's representation
- **THEN** the resolver SHALL ignore that request and continue down the resolution order

#### Scenario: Video is a carrier rather than a representation
- **WHEN** a `pictorial` view is configured with format `mp4`
- **THEN** the format SHALL be accepted as an external artefact carrier
- **AND** a `table` view configured with `mp4` SHALL be rejected

### Requirement: Format resolution order
The system SHALL resolve a view's format from, in order: a per-view override, the project default, and the representation's own default.

#### Scenario: Per-view override wins
- **WHEN** `views.formats.overrides` names the view
- **THEN** that format SHALL be used, and reported with `format_source: override`

#### Scenario: Project default applies to diagram views only
- **WHEN** `views.formats.default` is set
- **THEN** it SHALL apply to views whose representation is carried by a diagram
- **AND** it SHALL NOT change a `table` or `text` view away from markdown

#### Scenario: Unset configuration falls back to the representation default
- **WHEN** no override or project default is configured
- **THEN** the format SHALL be the representation's default, reported with `format_source: representation_default`

### Requirement: The resolved format is reported in generated instructions
Instruction generation SHALL report the view's `representation`, its resolved `format` and the `format_source` that decided it, and SHALL emit a carrier section and rule matching that format.

#### Scenario: Standalone figure carrier
- **WHEN** the resolved format is `svg`
- **THEN** the template SHALL include a section naming an independent SVG file for the view
- **AND** the rules SHALL state that diagram content is drawn as standalone SVG rather than inline Mermaid

#### Scenario: External artefact carrier
- **WHEN** the resolved format is an externally produced artefact such as `xlsx` or `mp4`
- **THEN** the template SHALL include a section naming the expected artefact file
- **AND** the rules SHALL state that the artefact is provided externally and must be referenced

#### Scenario: Prose carriers add no carrier section
- **WHEN** the resolved format is `markdown` or `mermaid`
- **THEN** the template SHALL use the view's own sections, adding only the Mermaid section for `mermaid`
