## MODIFIED Requirements

### Requirement: Documentation output
Step 6 SHALL produce: generated DoDAF views (both single and composite) in `.dm2/output/`, a summary document listing all views with their wikilinks, and a knowledge delta for potential iteration. Each generated view SHALL be structured according to the template from the Instructions Engine, ensuring consistency between what the AI was instructed to produce and what was actually generated.

#### Scenario: All documentation outputs are produced
- **WHEN** Step 6 completes
- **THEN** `.dm2/output/` SHALL contain generated view files and `.dm2/steps/step6-documentation.md` SHALL contain the summary

#### Scenario: Generated views match instruction templates
- **WHEN** AI Agent generates a view using instructions from `dm2 instructions OV-2 --json`
- **THEN** the resulting `output/OV-2.md` SHALL contain all template-required sections from the instructions
