## ADDED Requirements

### Requirement: View instructions accept optional --desc
When `dm2 instructions` is called for a view-type artifact (e.g., `StdV-1`, `view/OV-2`, bare view ID like `OV-5a`), the `--desc` parameter SHALL be optional. If not provided, the response SHALL include a guidance prompt in `project_description` encouraging the Agent to interact with the user.

#### Scenario: View instruction without --desc returns guidance
- **WHEN** `dm2 instructions StdV-1 --json` is called without `--desc`
- **THEN** the response SHALL have `status: "success"`
- **AND** `data.context.project_description` SHALL contain a guidance prompt suggesting the Agent use AskUserQuestion tool to discuss direction with the user
- **AND** `data.context.dm2_terms` SHALL be populated from DM2 knowledge base
- **AND** `data.rules` SHALL contain DoDAF compliance rules for the view

#### Scenario: View instruction with --desc preserves normal behavior
- **WHEN** `dm2 instructions StdV-1 -d "安全态势感知平台" --json` is called
- **THEN** `data.context.project_description` SHALL be `"安全态势感知平台"` (unchanged behavior)

### Requirement: Step instructions require --desc after type resolution
When `dm2 instructions` is called for a step-type artifact (e.g., `step1-intent-scope`), the `--desc` parameter SHALL remain required. The validation SHALL occur AFTER artifact type resolution, not at command entry.

#### Scenario: Step instruction without --desc errors after type check
- **WHEN** `dm2 instructions step1-intent-scope --json` is called without `--desc`
- **THEN** the response SHALL have `status: "error"` with `error.code: "MISSING_ARG"`
- **AND** the error message SHALL reference the step type requirement

#### Scenario: Step instruction with --desc works normally
- **WHEN** `dm2 instructions step1-intent-scope -d "系统描述" --json` is called
- **THEN** the response SHALL return step instructions with project description and template sections
