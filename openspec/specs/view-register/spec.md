# view-register Specification

## Purpose
Define the view-registration contract: after generating a view the agent registers it through `dm2 view register`, which records the view's lifecycle state against its change and returns a JSON envelope the agent can consume.

## Requirements

### Requirement: Agent registers view after generation

After generating a DoDAF view file, the AI Agent SHALL call the view register CLI command to record the artifact in project state.

#### Scenario: Register generated view

- **WHEN** the AI Agent has written a view file (e.g., `dm2-changes/boundary-security/views/OV-1.html`)
- **AND** the agent calls `dm2 view register OV-1 --change boundary-security --path dm2-changes/boundary-security/views/OV-1.html`
- **THEN** the system SHALL update `.dm2/view-state.yaml`:
  - Create entry for `OV-1` if not present
  - Set `status` to `generated`
  - Set `generated_at` to current timestamp
  - Set `output_path` to the provided path
  - Set `change` to the provided change name

#### Scenario: Register view without change name

- **WHEN** the AI Agent calls `dm2 view register OV-1` without `--change` argument
- **THEN** the system SHALL return error code `MISSING_ARG` with message "请提供 --change 参数"

#### Scenario: Register already-registered view

- **WHEN** `dm2 view register OV-1 --change boundary-security --path ...` is called
- **AND** the view `OV-1` already exists in `view-state.yaml`
- **THEN** the system SHALL update the existing entry (overwrite change, output_path, refresh timestamp)
- **AND** NOT create a duplicate entry

### Requirement: view register outputs JSON for agent consumption
The `dm2 view register` command SHALL always output `{"status": "success", "data": {"view_id": "...", "change": "...", "output_path": "..."}}` for machine consumption by AI Agent, and SHALL accept the documented `--json`/`-j` flag so that the project-wide convention of appending `--json` applies to it as well.

#### Scenario: Successful JSON response
- **WHEN** the agent calls `dm2 view register OV-1 --change test --path dm2-changes/test/views/OV-1.html`
- **THEN** the command outputs `{"status":"success","data":{"view_id":"OV-1","change":"test","output_path":"dm2-changes/test/views/OV-1.html"}}`

#### Scenario: The documented `--json` flag is accepted
- **WHEN** the agent appends `--json` as every skill template instructs
- **THEN** the command SHALL accept the flag rather than failing with an unknown-option error
- **AND** the output SHALL be the same envelope as without the flag

#### Scenario: Outside a project the command reports a missing project
- **WHEN** `dm2 view register OV-1 --change test` runs outside a `.dm2` project
- **THEN** it SHALL emit the `NOT_IN_PROJECT` error envelope
- **AND** it SHALL NOT create a `.dm2/` directory in the current working directory or register the view
