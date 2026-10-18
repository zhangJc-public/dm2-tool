## Purpose

InstructionBuilder generates DoDAF compliance rules and template sections dynamically from view metadata, eliminating hardcoded VIEW_RULES.

## Requirements

### Requirement: InstructionBuilder generates rules from view metadata
The `InstructionBuilder.build_view_instructions()` method SHALL generate DoDAF compliance rules dynamically from the view's metadata fields, prioritizing metadata over hardcoded rules.

#### Scenario: Representation rule generated for diagram view
- **WHEN** `build_view_instructions` is called for a view with `representation: node-link`
- **THEN** the returned `rules` SHALL include "该视图必须以节点-连接图 (node-link diagram) 形式呈现"
- **AND** the rule SHALL be generated from the `representation` field, not hardcoded

#### Scenario: Model category rule generated
- **WHEN** `build_view_instructions` is called for a view with `model_category: Behavioral`
- **THEN** the returned `rules` SHALL include a rule identifying the view as a Behavioral model describing dynamic process aspects

#### Scenario: Required field rules generated
- **WHEN** `build_view_instructions` is called for a view with `required_fields: [源活动, 目标活动, 资源类型]`
- **THEN** the returned `rules` SHALL include "必须包含: 源活动"
- **AND** the rules SHALL include "必须包含: 目标活动"
- **AND** the rules SHALL include "必须包含: 资源类型"

### Requirement: Fallback to hardcoded rules when metadata missing
When a view lacks the new metadata fields (e.g., loaded from an unenhanced views.yaml), the InstructionBuilder SHALL fall back to the existing VIEW_RULES hardcoded dictionary and generic template.

#### Scenario: Old-format view uses hardcoded rules
- **WHEN** `build_view_instructions` is called for OV-2
- **AND** the view's `representation` field is `None` or absent
- **THEN** the returned `rules` SHALL use the existing VIEW_RULES["OV-2"] hardcoded entries
- **AND** the returned `template.sections` SHALL use the generic `["## 概述", ...]` fallback

### Requirement: Knowledge API exposes new metadata fields
The `KnowledgeAPI.get_view()` method and `knowledge view <id> --json` command SHALL include the new metadata fields in the response.

#### Scenario: knowledge view output includes new fields
- **WHEN** `dm2 knowledge view OV-2 --json` is called
- **THEN** the response SHALL include `standard_name`, `model_category`, `representation`, `purpose`, `sections`, `required_fields` in the data object
- **AND** all existing fields (view_name, viewpoint, dependencies, etc.) SHALL still be present with unchanged values

### Requirement: Association manifest in view generation instructions
When generating instructions for a view, the InstructionBuilder SHALL include
a "DM2 关联清单" (DM2 association manifest) section listing the view's
necessary associations from `view-content-spec.json`, each with its endpoint
types and domain semantic roles.

#### Scenario: OV-5b instructions carry the necessary associations
- **WHEN** the AI agent receives instructions to generate OV-5b
- **THEN** the instructions SHALL list `activityPerformedByPerformer`
  (Performer ─▶ Activity), `activityConsumesResource` (Activity as consumer
  ─▶ Resource), and `activityProducesResource` (Activity as before ─▶
  Resource)
- **AND** each listed association SHALL show both endpoint types

#### Scenario: Manifest section is bounded
- **WHEN** a view's necessary association list is long or includes
  associations unresolved in the catalog
- **THEN** resolved associations with endpoint types SHALL appear first
- **AND** unresolved association labels MAY be truncated or omitted to keep
  the instruction section within size limits

#### Scenario: Manifest derived from index, not prose
- **WHEN** group templates and the content spec disagree about relationships
- **THEN** the association manifest SHALL use `view-content-spec.json` as the
  authoritative source

### Requirement: Knowledge API exposes view content spec
The Knowledge API SHALL expose necessary/optional terms and necessary
associations per view so AI agents can query view requirements directly
(see `dm2-metamodel-knowledge` capability).

#### Scenario: Agent queries what a view needs
- **WHEN** the AI agent queries the content spec for CV-2
- **THEN** the response SHALL include associations such as
  `activityPartOfCapability` (Activity ─▶ Capability) and
  `activityMapsToCapabilityType` (Activity ─▶ CapabilityType) with endpoint
  types

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
