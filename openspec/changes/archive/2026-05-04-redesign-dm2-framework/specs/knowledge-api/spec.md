## ADDED Requirements

### Requirement: Structured DM2 term search
The system SHALL provide `dm2 knowledge search <query> --json` that returns matching DM2 terms with definitions, aliases, source data groups, and associated file paths. Search SHALL match against term names, aliases, and definition text.

#### Scenario: Term search by keyword
- **WHEN** `dm2 knowledge search "Activity" --json` is executed
- **THEN** the response SHALL include the DM2 definition of Activity, its aliases, source data group (02-Activity), and related terms

#### Scenario: Chinese term search
- **WHEN** `dm2 knowledge search "作战活动" --json` is executed
- **THEN** the response SHALL return matching DM2 terms that have Chinese aliases or definitions containing the query

### Requirement: Concept detail lookup
The system SHALL provide `dm2 knowledge concept <name> --json` that returns the full concept record: DM2 type, layer, subtype, definition, synonyms, relationships (related concepts), tags, and wikilinks.

#### Scenario: Concept detail is retrieved
- **WHEN** `dm2 knowledge concept "Performer" --json` is executed
- **THEN** the response SHALL include Performer's DM2 type (Performer), layer (TYPE), related concepts (Person, Organization, System), and relationships

### Requirement: View listing by type
The system SHALL provide `dm2 knowledge views --type <viewpoint> --json` that returns all views for a given DoDAF viewpoint (AV/CV/DIV/OV/PV/SV/SvcV/StdV), with each view's ID, name, description, priority, and dependencies.

#### Scenario: List all operational views
- **WHEN** `dm2 knowledge views --type OV --json` is executed
- **THEN** the response SHALL return all 9 OV views with their metadata

### Requirement: Single view detail lookup
The system SHALL provide `dm2 knowledge view <id> --json` that returns the complete view definition: template structure, dependency list, downstream views, required DM2 data groups, priority, and description.

#### Scenario: View detail for generation planning
- **WHEN** `dm2 knowledge view OV-2 --json` is executed
- **THEN** the response SHALL include all fields from views.yaml for OV-2: dependencies, downstream views, required data groups, and template structure

### Requirement: Knowledge base statistics
The system SHALL provide `dm2 knowledge stats --json` that returns aggregate counts: total terms, total concepts, views by viewpoint, and data group coverage.

#### Scenario: Knowledge base stats are queried
- **WHEN** `dm2 knowledge stats --json` is executed
- **THEN** the response SHALL include `total_terms`, `total_concepts`, `total_views`, and a breakdown of views by viewpoint type
