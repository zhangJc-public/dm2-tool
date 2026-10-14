# Spec Delta

## ADDED Requirements

### Requirement: Per-view documents carry generated content
Each view file Step 6 writes to the output directory SHALL contain content generated from the architecture description and the analysis, not placeholder text. A view document whose body is a fixed notice that generation is outstanding SHALL be treated as a failure to produce the view.

#### Scenario: Per-view document has generated content
- **WHEN** Step 6 completes and writes a view file
- **THEN** the file SHALL contain the view's heading together with populated sections derived from the description and analysis
- **AND** SHALL NOT consist of a fixed notice that the view awaits generation

#### Scenario: Wikilinks reach the per-view documents
- **WHEN** entities were identified for the architecture
- **THEN** each per-view document SHALL include the `[[wikilinks]]` for those entities, as required by the wikilinks requirement in this capability

### Requirement: Generated documents do not name an LLM dependency
dm2 is a zero-LLM tool. Text that dm2 writes into a generated document SHALL NOT instruct a reader to supply an LLM, nor name an LLM as the means by which outstanding content will be produced.

#### Scenario: No generated file names an LLM
- **WHEN** Step 6 has written every view file it produces
- **THEN** no generated document SHALL contain a notice naming an LLM
- **AND** no generated document SHALL defer its content to LLM filling
