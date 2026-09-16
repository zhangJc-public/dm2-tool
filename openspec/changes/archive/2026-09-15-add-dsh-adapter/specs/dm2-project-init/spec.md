# DM2 Project Init (delta)

## MODIFIED Requirements

### Requirement: Init provisions local reference knowledge base
The `dm2 init` command SHALL copy the DM2 reference knowledge base (views.yaml, _dm2_v202_extract.json, group-to-views.yaml, and 17 data group templates) into `.dm2/reference/` when creating a project, making the project self-contained.

#### Scenario: Reference files present after init
- **WHEN** `dm2 init <project-name>` completes successfully
- **THEN** `.dm2/reference/views.yaml` SHALL exist with all 52 view definitions
- **AND** `.dm2/reference/_dm2_v202_extract.json` SHALL exist with ~277 DM2 terms
- **AND** `.dm2/reference/group-to-views.yaml` SHALL exist with data group to view mappings
- **AND** `.dm2/reference/groups/` SHALL contain 17 data group subdirectories with templates

#### Scenario: Existing reference not overwritten on re-init
- **WHEN** `dm2 init` is run in a directory that already has `.dm2/reference/`
- **THEN** the command SHALL NOT overwrite the existing reference files
- **AND** the project SHALL continue to use its existing local reference data

#### Scenario: Workflow skills generated for the selected tool, not copied
- **WHEN** `dm2 init <project-name>` completes successfully
- **THEN** the selected tool's skills directory SHALL contain only dm2 skill directories, one per registered workflow (currently 10: propose, continue, new, ff, verify, onboard, bulk-archive, explore, apply, archive)
- **AND** for the `claude` tool `.claude/commands/dm2/` SHALL contain only dm2 command files, one per registered workflow
- **AND** for the `dsh` tool no command directory SHALL be created
- **AND** NO OpenSpec (openspec-* or opsx) files SHALL be present in the generated directories
- **AND** each generated SKILL.md SHALL include `generatedBy: "dm2-tool/<version>"` in metadata

#### Scenario: Skills regenerated on re-init
- **WHEN** `dm2 init` is run in a directory that already has the selected tool's skills directory
- **THEN** existing dm2 skill directories SHALL be overwritten with freshly generated content
- **AND** non-dm2 skill directories SHALL NOT be touched (e.g., openspec-* from a separate `openspec init`)

### Requirement: Template-based skill generation
`dm2 init` SHALL generate skill and command files for the selected tool from Python template dataclasses rather than copying from the developer's `.claude/` directory. The developer's `.claude/` SHALL be ignored by `dm2 init`.

#### Scenario: Init works without dev .claude/
- **WHEN** dm2-tool is installed via `pip install` (non-editable, no `.claude/` at package root)
- **THEN** `dm2 init` SHALL generate a skill for every registered workflow, plus command files when the selected tool has a command convention
- **AND** the generation SHALL NOT rely on `Path(__file__).parent.parent.parent.parent` to locate template files

#### Scenario: Dev's .claude/ is ignored
- **WHEN** `dm2 init` runs in a dm2-tool development checkout (where `.claude/` exists with OpenSpec content)
- **THEN** the generated project SHALL NOT contain OpenSpec skills or commands
- **AND** the copy source SHALL be the Python template dataclasses, not any directory on the filesystem

## ADDED Requirements

### Requirement: Init targets a selectable AI tool
`dm2 init` SHALL accept `--tool/-t` with the values `claude` and `dsh`, selecting the adapter that generates the project's AI Agent files.

#### Scenario: Tool selects the output layout
- **WHEN** `dm2 init <project-name>` runs without `--tool`
- **THEN** it SHALL behave as `--tool claude`, generating `.claude/skills/` and `.claude/commands/dm2/`
- **AND** `--tool dsh` SHALL generate `.dsh/skills/` and no command directory
- **AND** the generated layout SHALL be determined solely by the selected adapter, not by the tool name in the command

#### Scenario: JSON reports the generated configuration
- **WHEN** `dm2 init --json` completes
- **THEN** `data.agent_config` SHALL contain `tool`, `files_generated`, `skills_dir`, `commands_dir`, and `commands`
- **AND** `commands` SHALL be `false` for a tool without a command convention
- **AND** `files_generated` SHALL equal the number of files actually written

#### Scenario: Unknown tool is rejected without side effects
- **WHEN** `dm2 init --tool <unknown>` runs
- **THEN** it SHALL fail with error code `INVALID_TOOL` and a non-zero exit code
- **AND** it SHALL NOT create the project directory or any generated file, because the adapter is resolved before any filesystem write

#### Scenario: Re-init is idempotent for either tool
- **WHEN** `dm2 init` is re-run in an existing project with either `--tool` value
- **THEN** the selected tool's generated files SHALL be refreshed
- **AND** the pre-existing reference knowledge base and any other tool's generated directory SHALL NOT be modified
