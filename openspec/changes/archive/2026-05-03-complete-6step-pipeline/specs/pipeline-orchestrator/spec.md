## ADDED Requirements

### Requirement: dm2 run command
The system SHALL provide a `dm2 run` command that executes the complete 6-step DODAF architecture development pipeline from a user-provided architecture description.

#### Scenario: User starts a new pipeline run
- **WHEN** user executes `dm2 run -d "描述某个系统的架构意图"`
- **THEN** the system SHALL execute Step 1+2 through Step 6 sequentially and output progress at each step

### Requirement: Step state persistence
Each step's output SHALL be persisted to `.dm2/steps/step<N>-<name>.md`, and pipeline state SHALL be tracked in `.dm2/state.yaml` to support resumption from any step.

#### Scenario: Pipeline resumes after interruption
- **WHEN** a previous run completed Step 1+2 and Step 3+4 but was interrupted before Step 5
- **THEN** `dm2 run --resume` SHALL continue from Step 5 using previously stored state

### Requirement: Iteration loop
After Step 6 completes, the system SHALL prompt the user whether to iterate back to Step 1 with refined intent, supporting the document's iterative philosophy.

#### Scenario: User chooses to iterate
- **WHEN** Step 6 completes and the system asks "是否基于当前结果迭代优化?"
- **THEN** answering yes SHALL restart the pipeline at Step 1 with the previous Step 6 outputs as additional context

### Requirement: Step skipping
The system SHALL support `dm2 run --step <N>` to execute only a specific step, using existing intermediate outputs from prior steps.

#### Scenario: User runs a single step
- **WHEN** user executes `dm2 run --step 5 --resume`
- **THEN** only Step 5 SHALL execute, using outputs from Steps 1-4 stored in `.dm2/steps/`
