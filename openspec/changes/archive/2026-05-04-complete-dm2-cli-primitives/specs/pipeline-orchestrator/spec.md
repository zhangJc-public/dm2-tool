## MODIFIED Requirements

### Requirement: Step state persistence
Each step's output SHALL be persisted to `.dm2/steps/step<N>-<name>.md`, and pipeline state SHALL be tracked in `.dm2/state.yaml` to support resumption from any step. When step6-documentation completes successfully and generates DoDAF view files, the corresponding views SHALL be registered in ViewManager with status `generated`.

#### Scenario: Pipeline resumes after interruption
- **WHEN** a previous run completed Step 1+2 and Step 3+4 but was interrupted before Step 5
- **THEN** `dm2 run --resume` SHALL continue from Step 5 using previously stored state

#### Scenario: View registration on documentation completion
- **WHEN** Step 6 (documentation) completes and writes view files to the output directory
- **THEN** each generated view SHALL be registered in `.dm2/view-state.yaml` with status `generated`
