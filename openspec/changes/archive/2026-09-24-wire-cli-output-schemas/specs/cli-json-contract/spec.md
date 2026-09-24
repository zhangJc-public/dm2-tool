# CLI JSON Contract (delta)

## ADDED Requirements

### Requirement: CLI output shapes are declared as JSON Schema and enforced
The machine-readable shape of each state-bearing command's JSON output SHALL be declared as a
JSON Schema under `schemas/`, and every declared shape SHALL be verified against real command
output by the test suite, so that a schema cannot drift from the implementation unnoticed.

#### Scenario: The envelope has a declared schema
- **WHEN** `schemas/common.json` is read
- **THEN** it SHALL declare the success shape (`status` plus `data`) and the error shape
  (`status` plus `error` carrying `code` and `message`)
- **AND** success and error output emitted by the CLI SHALL each satisfy it

#### Scenario: Declared payload shapes match real output
- **WHEN** the test suite runs a command whose payload has a schema
- **THEN** the emitted `data` SHALL satisfy that schema
- **AND** a divergence SHALL fail the test rather than be tolerated

#### Scenario: A schema is never silently under-validated
- **WHEN** a schema uses a keyword the test-time validator does not implement
- **THEN** validation SHALL fail explicitly
- **AND** it SHALL NOT skip that assertion and report success

#### Scenario: Schemas follow the capability they describe
- **WHEN** a command stops emitting a field, or a capability is removed
- **THEN** the corresponding schema SHALL be corrected or deleted in the same change
- **AND** a schema SHALL NOT remain describing behavior dm2 no longer has
