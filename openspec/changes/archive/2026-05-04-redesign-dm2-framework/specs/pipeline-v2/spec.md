## ADDED Requirements

### Requirement: Agent-driven pipeline loop
The Pipeline V2 SHALL operate as an AI-Agent-driven loop: CLI manages step state and generates instructions, AI Agent executes each step based on instructions, CLI validates results and advances state. The CLI SHALL NOT hardcode execution logic within Python functions.

#### Scenario: Pipeline step is driven by AI Agent
- **WHEN** pipeline starts Step 3
- **THEN** the CLI SHALL output structured instructions for Step 3 (context, rules, template) and wait for AI Agent to produce the step output, rather than executing Step 3 logic itself

### Requirement: Structured step status
The `dm2 run --status --json` command SHALL return the current pipeline state: which step is active, what steps are complete, each step's output file path, and the iteration count.

#### Scenario: AI Agent queries pipeline status
- **WHEN** `dm2 run --status --json` is executed mid-pipeline
- **THEN** the response SHALL show Step 1+2=done, Step 3+4=ready, Step 5=pending, Step 6=pending, with output file paths for completed steps

### Requirement: Step instructions for AI
The `dm2 run --instructions <step-id> --json` command SHALL return step-specific instructions: context (previous step outputs + DM2 knowledge), rules (step execution constraints), and expected output format.

#### Scenario: AI Agent requests step instructions
- **WHEN** `dm2 run --instructions step5-analysis --json` is executed
- **THEN** the response SHALL include: context from Steps 1-4 outputs, DM2 analysis rules, OODA/TOC framework templates, and the expected output format for step5-analysis.md

### Requirement: Step completion handoff
The system SHALL provide `dm2 run --complete-step <step-id> --json` that marks a step as done after AI Agent has produced its output, advances to the next step, and returns the pipeline's new state.

#### Scenario: AI Agent completes a step
- **WHEN** AI Agent has written step output to `.dm2/steps/step3-data-requirements.md` and calls `dm2 run --complete-step step3-data-requirements --json`
- **THEN** the step SHALL be marked done, Step 5 SHALL become ready, and the response SHALL indicate "next_step: step5-analysis"

### Requirement: V1 backward compatibility
The existing `dm2 run` command (non-Agent mode) SHALL continue to function as before. Agent-driven mode SHALL be an additive capability.

#### Scenario: Legacy dm2 run still works
- **WHEN** user executes `dm2 run -d "系统描述"` without Agent mode
- **THEN** the pipeline SHALL execute all 6 steps as hardcoded Python functions, producing identical output to pre-redesign behavior
