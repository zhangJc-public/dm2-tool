## MODIFIED Requirements

### Requirement: DM2 knowledge base retrieval
The system SHALL query the DM2 reference knowledge base (built-in + optional Obsidian vault) to retrieve relevant concepts, associations, and view templates for the identified data requirements. The retrieval SHALL be exposed via the Knowledge API (`dm2 knowledge search/concept --json`) so AI Agents can independently query beyond what the pipeline step retrieves.

#### Scenario: Knowledge retrieval returns relevant concepts
- **WHEN** data requirements include "Activity" and "Performer" entities
- **THEN** the RAG engine SHALL return DM2 concepts for Activity, Performer, and their association type (Activity-Performer) from the knowledge base

#### Scenario: AI Agent supplements retrieval independently
- **WHEN** AI Agent determines the pipeline retrieval missed a concept
- **THEN** the Agent SHALL be able to call `dm2 knowledge concept <name> --json` to perform targeted retrieval without re-running the pipeline step
