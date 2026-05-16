## ADDED Requirements

### Requirement: 6W matrix-driven data identification
The system SHALL use the 6W matrix (What/How/Who/Where/When/Why) to identify required data entities, mapping each dimension to relevant DM2 data groups.

#### Scenario: 6W analysis drives data selection
- **WHEN** Step 3 executes with a scope definition from Step 2
- **THEN** each 6W dimension SHALL produce a list of required DM2 data groups and entity types

### Requirement: DM2 knowledge base retrieval
The system SHALL query the DM2 reference knowledge base (built-in + optional Obsidian vault) to retrieve relevant concepts, associations, and view templates for the identified data requirements.

#### Scenario: Knowledge retrieval returns relevant concepts
- **WHEN** data requirements include "Activity" and "Performer" entities
- **THEN** the RAG engine SHALL return DM2 concepts for Activity, Performer, and their association type (Activity-Performer) from the knowledge base

### Requirement: Data organization and gap identification
The system SHALL organize identified data into a taxonomy based on DM2 data groups and identify gaps where required data is not yet available in the knowledge base.

#### Scenario: Data gap is identified
- **WHEN** the scope requires a concept type not present in the DM2 reference
- **THEN** the system SHALL flag it as a gap and suggest the user provide additional data sources

### Requirement: Data requirements output
Step 3+4 SHALL produce a data requirements document containing: 6W dimension-to-data mapping, retrieved DM2 concepts, organized taxonomy, and identified gaps.

#### Scenario: Data requirements document is produced
- **WHEN** Step 3+4 completes
- **THEN** `.dm2/steps/step3-data-requirements.md` SHALL contain all four sections
