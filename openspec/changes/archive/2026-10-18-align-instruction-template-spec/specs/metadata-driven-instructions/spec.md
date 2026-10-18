# Spec Delta

## REMOVED Requirements

### Requirement: InstructionBuilder generates template sections from metadata
**Reason**: Four of its six scenarios described `views.include_mermaid` and `views.diagram_output`, which were removed in favour of `views.formats`. The requirement is re-added below under a name that does not cite removed switches, with its carrier scenarios restated in terms of the format axis.

## ADDED Requirements

### Requirement: InstructionBuilder generates template and carrier sections
The `InstructionBuilder` SHALL assemble the instruction template from the view's own `sections`, plus one carrier section selected by the view's resolved format.

#### Scenario: View-specific sections used in template
- **WHEN** `build_view_instructions` is called for a view whose `sections` field lists four sections
- **THEN** `template.sections` SHALL begin with exactly those sections
- **AND** no generic section SHALL replace them

#### Scenario: Mermaid section injected for diagram views only
- **WHEN** a view's resolved format is `mermaid`
- **THEN** `template.sections` SHALL include a Mermaid section naming the representation's diagram type
- **AND** a view whose resolved format is `markdown` SHALL NOT receive one

#### Scenario: Carrier follows the resolved format
- **WHEN** a view's resolved format is `svg`
- **THEN** `template.sections` SHALL include a section naming an independent SVG file for that view
- **AND** `template.sections` SHALL NOT include a Mermaid section
- **AND** `rules` SHALL state that diagram content is drawn as standalone SVG

#### Scenario: Template reports the resolution
- **WHEN** `build_view_instructions` returns a template
- **THEN** it SHALL report the view's `representation`, its resolved `format`, and the `format_source` that decided it

#### Scenario: External artefact carrier
- **WHEN** a view's resolved format is an externally produced artefact such as `xlsx` or `mp4`
- **THEN** `template.sections` SHALL include a section naming the expected artefact file
- **AND** `rules` SHALL state that the artefact is provided externally and must be referenced

#### Scenario: Diagram-free views receive no carrier section
- **WHEN** a view's resolved format is `markdown`
- **THEN** `template.sections` SHALL contain neither a Mermaid section nor a figure section

#### Scenario: Fallback when metadata is missing
- **WHEN** a view lacks the metadata fields this requirement relies on
- **THEN** the builder SHALL fall back to its hardcoded rules and generic template rather than failing
