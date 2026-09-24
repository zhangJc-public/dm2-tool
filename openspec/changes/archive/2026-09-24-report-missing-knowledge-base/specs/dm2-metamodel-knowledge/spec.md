# DM2 Metamodel Knowledge (delta)

## ADDED Requirements

### Requirement: An unresolvable knowledge base is a reported failure
When neither the project-local reference copy nor the packaged reference copy can be located,
dm2 SHALL fail with a non-zero exit code and report the condition, and SHALL NOT continue with an
empty knowledge base. The same applies to any other runtime knowledge asset resolved the same
way (`concerns.yaml`).

#### Scenario: Resolution raises instead of returning a phantom path
- **WHEN** `get_reference_path()` is called and neither `.dm2/reference/` nor the packaged
  `dm2-reference/core/` exists
- **THEN** it SHALL raise `KnowledgeBaseNotFound` rather than return a path that does not exist
- **AND** a caller SHALL NOT receive an empty result set as a success

#### Scenario: JSON mode reports the condition as an envelope
- **WHEN** a knowledge-dependent command runs with `--json` (or `-j`) and the knowledge base
  cannot be resolved
- **THEN** stdout SHALL contain the JSON envelope with `status` equal to `"error"`
- **AND** `error.code` SHALL be `KB_NOT_FOUND`
- **AND** the exit code SHALL be non-zero

#### Scenario: Human mode reports an actionable message
- **WHEN** the same condition occurs without a JSON flag
- **THEN** dm2 SHALL print a message naming what was not found and how to fix it
- **AND** the exit code SHALL be non-zero

#### Scenario: Both entry points behave identically
- **WHEN** the CLI is invoked as the `dm2` console script
- **THEN** it SHALL report the condition exactly as when invoked as `python -m dm2.cli.main`

#### Scenario: A missing concerns file is reported, not silently empty
- **WHEN** `dm2 concern list` runs and `concerns.yaml` cannot be located
- **THEN** it SHALL report the missing knowledge base rather than an empty template list

#### Scenario: Developer debugging still gets the traceback
- **WHEN** `DM2_DEBUG` is set and the knowledge base cannot be resolved
- **THEN** the underlying exception SHALL propagate instead of being converted into a message
