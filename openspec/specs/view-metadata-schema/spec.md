## Purpose

Define the enhanced metadata schema for views.yaml, driving AI agent instruction generation from DoDAF V2.02 standard-derived fields.

## Requirements

### Requirement: View definition includes standard-derived metadata
Each view in `views.yaml` SHALL include six new metadata fields derived from the DoDAF V2.02 standard: `standard_name`, `model_category`, `representation`, `purpose`, `sections`, and `required_fields`.

The `groups` field SHALL use names from the DM2DataGroup short-name set: {Foundation, Performer, Activity, Capability, Resource, Guidance, Measure, Location, Services, Project, Rules, ResourceFlow, InformationPedigree, OrganizationalStructure, InformationAndData}.

#### Scenario: All 52 views have complete metadata
- **WHEN** `views.yaml` is loaded by the indexer
- **THEN** every view entry SHALL have a non-empty `standard_name`
- **AND** every view entry SHALL have a valid `model_category` from the set {Structural, Behavioral, Tree, Mapping, Tabular, Pictorial, Timeline, Ontology}
- **AND** every view entry SHALL have a valid `representation` from the set {node-link, tree, org-chart, flowchart, state-diagram, sequence-diagram, er-diagram, pictorial, gantt, table, text}
- **AND** every view entry SHALL have a non-empty `purpose` string
- **AND** every view entry SHALL have a non-empty `sections` list (2-6 items)
- **AND** every view entry SHALL have a non-empty `required_fields` list
- **AND** every view entry SHALL have a non-empty `groups` list with values from the valid DM2DataGroup short-name set

#### Scenario: Table/text views do not require Mermaid diagrams
- **WHEN** a view has `representation: table` or `representation: text`
- **THEN** its `sections` SHALL NOT contain entries equivalent to "Mermaid 图表"
- **AND** the InstructionBuilder SHALL NOT generate a Mermaid diagram block for this view

#### Scenario: Diagram views include appropriate Mermaid type
- **WHEN** a view has `representation` in {node-link, tree, org-chart, pictorial}
- **THEN** the InstructionBuilder SHALL generate a `graph` Mermaid block
- **WHEN** a view has `representation: flowchart`
- **THEN** the InstructionBuilder SHALL generate a `flowchart` Mermaid block
- **WHEN** a view has `representation: state-diagram`
- **THEN** the InstructionBuilder SHALL generate a `stateDiagram` Mermaid block
- **WHEN** a view has `representation: sequence-diagram`
- **THEN** the InstructionBuilder SHALL generate a `sequenceDiagram` Mermaid block
- **WHEN** a view has `representation: er-diagram`
- **THEN** the InstructionBuilder SHALL generate an `erDiagram` Mermaid block
- **WHEN** a view has `representation: gantt`
- **THEN** the InstructionBuilder SHALL generate a `gantt` Mermaid block

### Requirement: Metadata validation on load
When `views.yaml` is loaded, the indexer SHALL validate each view's metadata fields and report errors for invalid values without blocking the load.

#### Scenario: Invalid model_category produces warning
- **WHEN** a view has `model_category: "InvalidType"`
- **THEN** the indexer SHALL emit a warning listing the invalid value and the valid options
- **AND** the view SHALL still be loaded with the invalid value preserved

#### Scenario: Missing required new field produces warning
- **WHEN** a view lacks the `representation` field entirely
- **THEN** the indexer SHALL emit a warning
- **AND** the field SHALL default to `None` in the ViewTemplate

### Requirement: Existing fields preserved unchanged
All existing fields (id, name, viewpoint, groups, description, priority, dependencies, required_data, downstream) SHALL remain unchanged in name, type, and meaning.

#### Scenario: Old code reads enhanced views.yaml
- **WHEN** code reads only existing fields (e.g., `view["description"]`)
- **THEN** the returned values SHALL be identical to before the enhancement
- **AND** code that does not reference new fields SHALL function without modification
