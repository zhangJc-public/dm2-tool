# View Register (delta)

## MODIFIED Requirements

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
