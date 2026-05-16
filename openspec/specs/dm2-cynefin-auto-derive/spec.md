## DM2 Cynefin Auto-Derive Spec

### Purpose
Enable `dm2 cynefin` to auto-derive Cynefin complexity parameters from a natural language description using keyword counting, eliminating the need for manual parameter input.

### Requirements

### Requirement: Auto-derive Cynefin parameters from description
The `dm2 cynefin` command SHALL support automatic derivation of Cynefin complexity parameters (systems, stakeholders, uncertainty, rules) from a natural language description.

#### Scenario: Derive with --desc flag
- **WHEN** user runs `dm2 cynefin --desc "..."` or `dm2 cynefin -d "..."`
- **THEN** the command SHALL analyze the description text using keyword counting
- **AND** SHALL output the derived Cynefin parameters in the same JSON structure as manual input

#### Scenario: Combined with --json output
- **WHEN** user runs `dm2 cynefin -d "..." --json`
- **THEN** the JSON output SHALL include all 4 Cynefin parameter values

#### Scenario: Manual parameters still work
- **WHEN** user runs `dm2 cynefin --systems 5 --stakeholders 3`
- **THEN** the command SHALL use the provided manual parameters (no auto-derivation)
- **AND** SHALL work exactly as before

#### Scenario: Override auto-derived values
- **WHEN** user runs `dm2 cynefin -d "..." --systems 8`
- **THEN** the explicit `--systems` value SHALL override the auto-derived system count
