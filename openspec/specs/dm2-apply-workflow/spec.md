## DM2 Apply Workflow Spec

### Purpose
Define the `/dm2:apply` workflow — task-driven view generation that reads tasks.md and executes the implementation plan from `/dm2:propose`.

### Requirements

### Requirement: Task-driven view generation
The dm2-apply-workflow SHALL generate DoDAF views by reading and executing the tasks.md plan file produced by `/dm2:propose`, rather than re-running analysis.

#### Scenario: Apply reads tasks.md and generates views
- **WHEN** user runs `/dm2:apply` with a valid change name
- **THEN** the workflow SHALL read `dm2-changes/<name>/tasks.md`
- **AND** SHALL parse pending tasks matching `- [ ] Generate <View-ID>: <description>`
- **AND** SHALL read `dm2-changes/<name>/proposal.md` and `design.md` for context
- **AND** SHALL sort pending views by dependency order using `dm2 knowledge views --json`
- **AND** SHALL generate each view in order, save to `dm2-changes/<name>/views/<View-ID>.<ext>`, and register with `dm2 view register`
- **AND** SHALL mark each completed task with `- [x]` in tasks.md

#### Scenario: Apply with missing tasks.md
- **WHEN** user runs `/dm2:apply` but `dm2-changes/<name>/tasks.md` does not exist
- **THEN** the workflow SHALL inform the user that no plan exists
- **AND** SHALL suggest running `/dm2:propose` first

#### Scenario: Apply resumes after interruption
- **WHEN** user runs `/dm2:apply` on a change with some tasks already checked `[x]`
- **THEN** the workflow SHALL skip already-completed tasks
- **AND** SHALL continue from the first unchecked task

### Requirement: Apply differs from continue and ff
The dm2-apply-workflow SHALL be task-driven (reading tasks.md), distinguishing it from `/dm2:continue` (state-file-driven, one view per invocation) and `/dm2:ff` (analysis-driven, re-runs cynefin/analyze).

#### Scenario: Apply vs continue vs ff
- **WHEN** a user has completed `/dm2:propose` and wants to generate views
- **THEN** `/dm2:apply` SHALL be the recommended next step (task-driven batch)
- **AND** `/dm2:continue` SHALL remain available for step-by-step generation
- **AND** `/dm2:ff` SHALL remain available for analysis-driven batch generation without a plan
