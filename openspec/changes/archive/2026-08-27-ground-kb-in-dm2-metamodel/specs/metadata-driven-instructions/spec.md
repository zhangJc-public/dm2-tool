# Metadata-driven Instructions (delta)

## ADDED Requirements

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
