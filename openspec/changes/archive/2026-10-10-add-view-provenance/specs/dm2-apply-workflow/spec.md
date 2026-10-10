# DM2 Apply Workflow (delta)

This delta modifies `/dm2:apply` to require pedigree updates during view generation, capturing the actual generation event and any human modifications.

## MODIFIED Requirements

### Requirement: Task-driven view generation
The dm2-apply-workflow SHALL generate DoDAF views by reading and executing the tasks.md plan file produced by `/dm2:propose`. For each view generated, the workflow SHALL update the view's pedigree with generation event metadata.

#### Scenario: Apply reads tasks.md and generates views
- **WHEN** user runs `/dm2:apply` with a valid change name
- **THEN** the workflow SHALL read `dm2-changes/<name>/tasks.md`
- **AND** SHALL parse pending tasks matching `- [ ] Generate <View-ID>: <description>`
- **AND** SHALL read `dm2-changes/<name>/proposal.md` and `design.md` for context
- **AND** SHALL sort pending views by dependency order using `dm2 knowledge views --json`
- **AND** SHALL generate each view in order, save to `dm2-changes/<name>/views/<View-ID>.<ext>`, and register with `dm2 view register`
- **AND** for each view, SHALL call `dm2 trace record <view_id>` with the AI Agent's generation reasoning
- **AND** SHALL mark each completed task with `- [x]` in tasks.md

#### Scenario: Apply with missing tasks.md
- **WHEN** user runs `/dm2:apply` but `dm2-changes/<name>/tasks.md` does not exist
- **THEN** the workflow SHALL inform the user that no plan exists
- **AND** SHALL suggest running `/dm2:propose` first

#### Scenario: Apply resumes after interruption
- **WHEN** user runs `/dm2:apply` on a change with some tasks already checked `[x]`
- **THEN** the workflow SHALL skip already-completed tasks
- **AND** SHALL continue from the first unchecked task

## ADDED Requirements

### Requirement: Apply requires agent-supplied generation reasoning
The SKILL.md for `/dm2:apply` SHALL instruct the AI Agent to record generation reasoning when producing each view.

#### Scenario: Generation reasoning recorded per view
- **WHEN** the AI Agent finishes generating a view file
- **THEN** the SKILL.md SHALL require the Agent to call `dm2 trace record <view_id>` before moving to the next view
- **AND** the call SHALL include:
  - `--summary` describing the view's content approach
  - `--reasoning-file` with YAML containing:
    - `decision_factors` referencing input data, analysis results, and DM2 terms
    - `alternatives_considered` listing content approach options and why each was rejected
    - `known_limitations` listing any aspects the Agent is uncertain about

#### Scenario: Generation reasoning captures sources
- **WHEN** the Agent records generation reasoning
- **THEN** the `source.dm2_terms_used` field SHALL be populated with every DM2 term referenced in the view content
- **AND** each term SHALL include a `definition_ref` pointing to the canonical definition location
- **AND** `source.standard` SHALL be set to "DoDAF V2.02 Vol 2"
- **AND** `source.section` SHALL be set to the section name from `views.yaml`

#### Scenario: Apply pauses on trace failure
- **WHEN** a `dm2 trace record` call fails during view generation
- **THEN** the SKILL.md SHALL instruct the Agent to halt generation for that view
- **AND** the Agent SHALL report the trace failure to the human
- **AND** the corresponding task in tasks.md SHALL remain unchecked with a note "trace record failed"

### Requirement: Apply captures human modifications
The apply workflow SHALL record any post-generation human edits to a view as a ModificationRecord in the pedigree.

#### Scenario: Manual edit detected and recorded
- **WHEN** a view file is modified after its initial generation
- **AND** the modification is detected on the next `dm2 view register` or `dm2 validate` invocation
- **THEN** the system SHALL compare the current content hash to the stored generation hash
- **AND** if they differ, SHALL append a ModificationRecord with `actor=human`, `change_description="content modified post-generation"`
- **AND** SHALL NOT overwrite the original generation metadata

#### Scenario: Modification history preserved
- **WHEN** multiple human edits occur over time
- **THEN** the pedigree's `modification_history` SHALL grow with one entry per detected edit
- **AND** the original generation entry SHALL remain as the first record
