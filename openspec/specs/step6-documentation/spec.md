# Step 6: Documentation

## Purpose

文档化 + 知识回流，Composite View 生成 + wikilinks 双向关联 + 迭代反馈。

<!-- TBD: 详细架构文档。 -->

## Requirements

### Requirement: Composite view generation
The system SHALL generate Composite Views (multi-perspective architecture views) that combine multiple DoDAF viewpoints into integrated presentations, prioritizing composite views over single-viewpoint outputs.

#### Scenario: Composite view is generated
- **WHEN** Step 6 executes with a complete analysis from Step 5
- **THEN** the system SHALL generate at least one Composite View (e.g., OV-2+OV-5a combined, or SV-4+DIV-1 combined) in addition to any single views requested

### Requirement: Wikilinks bidirectional association
Generated view documents SHALL include Obsidian `[[wikilinks]]` linking back to the DM2 concepts, entities, and data sources used in their creation, establishing bidirectional traceability.

#### Scenario: View document contains wikilinks
- **WHEN** an OV-2 view is generated referencing Activity "A1" and Performer "P1"
- **THEN** the output SHALL contain `[[Activity-A1]]` and `[[Performer-P1]]` wikilinks to the corresponding DM2 knowledge base notes

### Requirement: Knowledge feedback to Step 1
Upon completion, the system SHALL summarize new knowledge generated during the pipeline (new entities, relationships, constraints) and present it as input for potential iteration back to Step 1.

#### Scenario: Knowledge feedback is presented
- **WHEN** Step 6 completes
- **THEN** the system SHALL list new entities/relationships discovered and ask whether to iterate with refined intent

### Requirement: Documentation output
Step 6 SHALL produce: generated DoDAF views (both single and composite) in `.dm2/output/`, a summary document listing all views with their wikilinks, and a knowledge delta for potential iteration.

#### Scenario: All documentation outputs are produced
- **WHEN** Step 6 completes
- **THEN** `.dm2/output/` SHALL contain generated view files and `.dm2/steps/step6-documentation.md` SHALL contain the summary

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
