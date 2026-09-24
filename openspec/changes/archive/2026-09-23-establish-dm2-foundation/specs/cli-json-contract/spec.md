# CLI JSON Contract (delta)

## ADDED Requirements

### Requirement: dm2 emits one documented JSON envelope
Every dm2 command that reads or mutates project or architecture state SHALL be able to emit a
single JSON envelope, and that envelope SHALL have exactly one of two shapes:

- success: `{"status": "success", "data": <object>}`
- error: `{"status": "error", "error": {"code": "<UPPER_SNAKE>", "message": "<human text>"}}`

#### Scenario: Success envelope
- **WHEN** a command completes successfully in JSON mode
- **THEN** stdout SHALL contain a single JSON object with `status` equal to `"success"`
- **AND** it SHALL contain a `data` member

#### Scenario: Error envelope
- **WHEN** a command fails in JSON mode
- **THEN** stdout SHALL contain a single JSON object with `status` equal to `"error"`
- **AND** it SHALL contain `error.code` and `error.message`
- **AND** it SHALL NOT emit a success envelope

#### Scenario: Non-JSON mode is unaffected
- **WHEN** a command runs without `--json` and it has a human-readable mode
- **THEN** it SHALL print its human-facing output
- **AND** this requirement SHALL NOT change that output

### Requirement: JSON mode keeps stdout machine-parseable
In JSON mode stdout SHALL contain only the envelope; diagnostics, progress, and warnings SHALL go
to stderr.

#### Scenario: Guard failures still produce an envelope
- **WHEN** a state-bearing command runs with `--json` outside a `.dm2` project
- **THEN** stdout SHALL be parseable JSON with `status` equal to `"error"`
- **AND** `error.code` SHALL identify the missing project rather than a parse failure
- **AND** the exit code SHALL be non-zero

#### Scenario: Success stdout contains nothing but the envelope
- **WHEN** a state-bearing command succeeds in JSON mode
- **THEN** `json.loads(stdout)` SHALL succeed without stripping non-JSON preamble

### Requirement: Exit codes distinguish success from failure
A command SHALL exit `0` when its envelope reports success and non-zero when its envelope reports
an error.

#### Scenario: Exit code matches the envelope
- **WHEN** a command emits `status: "success"`
- **THEN** it SHALL exit `0`
- **AND** when it emits `status: "error"` it SHALL exit non-zero

### Requirement: `--json` is accepted by state-bearing commands
Every dm2 command that reads or mutates project or architecture state SHALL accept `--json` and
`-j`, including commands that emit the envelope unconditionally and therefore have no
human-readable mode.

#### Scenario: Agent-facing commands accept the documented flag
- **WHEN** an agent follows the documented convention of appending `--json` to a CLI call
- **THEN** the command SHALL accept the flag
- **AND** `dm2 view register` SHALL accept `--json` even though it always emits the envelope

#### Scenario: The convention holds for the whole state-bearing surface
- **WHEN** every non-exempt command is invoked with `--json`
- **THEN** the flag SHALL be recognized by each of them

### Requirement: Error codes are stable and consistent
Envelope error codes SHALL be `UPPER_SNAKE_CASE` and SHALL carry the same meaning wherever they
appear.

#### Scenario: Codes are machine-comparable
- **WHEN** a command reports a missing project
- **THEN** it SHALL use the shared code for that condition rather than a command-specific synonym
- **AND** the same condition SHALL NOT be reported under two different codes

### Requirement: Exemptions are enumerated, not incidental
Commands that cannot honour the JSON contract SHALL be listed as explicit exemptions with a
reason, so that an unlisted command failing the contract is a defect rather than an accepted gap.

#### Scenario: Documented exemptions
- **WHEN** the exempt commands are considered
- **THEN** `completion` SHALL be exempt because it prints a shell completion script
- **AND** the hidden `__complete` helper SHALL be exempt because it is an internal shell protocol
- **AND** `uninstall` SHALL be exempt because it is an interactive human maintenance command with
  a confirmation prompt, and granting an agent unattended uninstall runs counter to dm2's role

#### Scenario: An unlisted command failing the contract is a defect
- **WHEN** a state-bearing command that is not on the exemption list rejects `--json`
- **THEN** the contract test SHALL fail
