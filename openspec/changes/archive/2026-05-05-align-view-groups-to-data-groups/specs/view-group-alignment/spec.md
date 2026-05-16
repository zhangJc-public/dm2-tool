## ADDED Requirements

### Requirement: View groups field uses DM2DataGroup-aligned names
All `groups` values in views.yaml SHALL use the exact short English names corresponding to `DM2DataGroup` enum members, ensuring `InstructionBuilder.search_terms(group)` can match against DM2 term group assignments.

#### Scenario: All group names are valid DM2DataGroup short names
- **WHEN** views.yaml is loaded by the indexer
- **THEN** every `groups` value SHALL be in the set {Foundation, Performer, Activity, Capability, Resource, Guidance, Measure, Location, Services, Project, Rules, ResourceFlow, InformationPedigree, OrganizationalStructure, InformationAndData}
- **AND** no view SHALL use non-standard names like `InfoAndData`, `OrgStructure`, or any ad-hoc abbreviation

#### Scenario: ResourceFlow group assigned to resource-flow-modeling views
- **WHEN** views.yaml is loaded
- **THEN** SV-2, SV-4, SV-6, OV-2, OV-3, DIV-2, DIV-3 SHALL include `ResourceFlow` in their `groups`
- **AND** ResourceFlow SHALL NOT appear in the groups of views that do not model resource flows

#### Scenario: InformationPedigree group assigned to data lineage views
- **WHEN** views.yaml is loaded
- **THEN** DIV-1, DIV-2 SHALL include `InformationPedigree` in their `groups`

#### Scenario: Foundation group assigned to foundational views
- **WHEN** views.yaml is loaded
- **THEN** AV-2, CV-1, DIV-1 SHALL include `Foundation` in their `groups`

#### Scenario: Pedigree and Reification do not appear in any view
- **WHEN** views.yaml is loaded
- **THEN** no view SHALL include `Pedigree` or `Reification` in their `groups`
- **AND** Pedigree and Reification SHALL remain available in the DM2DataGroup enum for ViewRecommender use

### Requirement: InstructionBuilder benefits from aligned group names
With aligned group names, `InstructionBuilder.build_view_instructions()` SHALL retrieve DM2 terms through `search_terms(group)` that match the group field in `_dm2_v202_extract.json`, providing more relevant context to the AI Agent.

#### Scenario: search_terms finds terms by matched group name
- **WHEN** InstructionBuilder searches for group `"ResourceFlow"` when building instructions for SV-4
- **THEN** the search SHALL return DM2 terms whose group field is `"Resource Flow"` (the DM2 term JSON uses space-separated naming)
- **AND** the number of matched terms SHALL be ≥ 5
