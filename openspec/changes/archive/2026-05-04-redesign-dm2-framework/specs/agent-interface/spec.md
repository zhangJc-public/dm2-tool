## ADDED Requirements

### Requirement: --json flag on all commands
All CLI commands SHALL accept an optional `--json` flag that switches output from human-readable text to structured JSON. When `--json` is present, the output SHALL be valid JSON parsable by AI agents.

#### Scenario: Command outputs JSON
- **WHEN** user or AI agent executes `dm2 status --json`
- **THEN** the output SHALL be a valid JSON object with `status`, `data`, and optional `error` fields

#### Scenario: Command outputs human text by default
- **WHEN** user executes `dm2 status` without `--json`
- **THEN** the output SHALL be human-readable text in the original format

### Requirement: Unified JSON response structure
All `--json` responses SHALL conform to a unified structure: `{"status": "success"|"error", "data": {...}, "error": {"code": "...", "message": "..."}}`. The `error` field SHALL only be present when status is "error".

#### Scenario: Successful JSON response
- **WHEN** a command completes successfully with --json
- **THEN** the response SHALL contain `"status": "success"` and a `data` object with command-specific payload

#### Scenario: Error JSON response
- **WHEN** a command fails (e.g., missing required argument) with --json
- **THEN** the response SHALL contain `"status": "error"` and an `error` object with `code` and `message`

### Requirement: Command-specific JSON schemas
Each CLI command SHALL define and document the JSON schema of its `data` payload, enabling AI agents to reliably parse and act on the response.

#### Scenario: AI agent parses command output
- **WHEN** an AI agent calls `dm2 analyze --desc "..." --json`
- **THEN** the response `data` SHALL contain fields: `primary_6w`, `secondary_6ws`, `confidence`, `extracted_entities`, `recommended_views`

### Requirement: Backward compatibility with --json
The `--json` flag SHALL NOT change any existing command's default behavior. All existing scripts and workflows SHALL continue to work unchanged.

#### Scenario: Existing script continues to work
- **WHEN** an existing shell script calls `dm2 status` without --json
- **THEN** the output SHALL be identical to the pre-redesign format
