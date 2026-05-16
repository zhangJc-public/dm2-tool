## DM2 Project Init Spec

### Purpose
Define the `dm2 init` command behavior — creating a self-contained `.dm2/` project with all necessary configuration, reference knowledge base, and AI Agent collaboration files.

### Requirements

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

#### Scenario: Claude Code skills generated, not copied
- **WHEN** `dm2 init <project-name>` completes successfully
- **THEN** `.claude/skills/` SHALL contain only dm2 skill directories (dm2-propose-workflow, dm2-continue-workflow, dm2-new-workflow, dm2-ff-workflow, dm2-verify-workflow, dm2-onboard-workflow, dm2-bulk-archive-workflow)
- **AND** `.claude/commands/dm2/` SHALL contain only dm2 command files (propose.md, continue.md, new.md, ff.md, verify.md, onboard.md, bulk-archive.md)
- **AND** NO OpenSpec (openspec-* or opsx) files SHALL be present in `.claude/`
- **AND** each generated SKILL.md SHALL include `generatedBy: "dm2-tool/<version>"` in metadata

#### Scenario: Skills regenerated on re-init
- **WHEN** `dm2 init` is run in a directory that already has `.claude/skills/`
- **THEN** existing dm2 skill directories SHALL be overwritten with freshly generated content
- **AND** non-dm2 skill directories SHALL NOT be touched (e.g., openspec-* from a separate `openspec init`)

### Requirement: Reference path resolution prefers project-local
The `get_reference_path()` function SHALL check for a project-local `.dm2/reference/` directory first, falling back to the built-in package `dm2-reference/core/` if no project-local copy exists.

#### Scenario: Project-local reference used when present
- **WHEN** a dm2 command runs within a project that has `.dm2/reference/`
- **THEN** `get_reference_path()` SHALL return the project-local `.dm2/reference/` path
- **AND** all knowledge loading (terms, concepts, views, groups) SHALL use the project-local data

#### Scenario: Package reference used as fallback
- **WHEN** a dm2 command runs outside a dm2 project, or within a project without `.dm2/reference/`
- **THEN** `get_reference_path()` SHALL return the built-in package `dm2-reference/core/` path
- **AND** commands SHALL function identically to before this change

### Requirement: Template-based skill generation
`dm2 init` SHALL generate Claude Code skill and command files from Python template dataclasses rather than copying from the developer's `.claude/` directory. The developer's `.claude/` SHALL be ignored by `dm2 init`.

#### Scenario: Init works without dev .claude/
- **WHEN** dm2-tool is installed via `pip install` (non-editable, no `.claude/` at package root)
- **THEN** `dm2 init` SHALL still generate all 7 skills and 7 commands successfully
- **AND** the generation SHALL NOT rely on `Path(__file__).parent.parent.parent.parent` to locate template files

#### Scenario: Dev's .claude/ is ignored
- **WHEN** `dm2 init` runs in a dm2-tool development checkout (where `.claude/` exists with OpenSpec content)
- **THEN** the generated project SHALL NOT contain OpenSpec skills or commands
- **AND** the copy source SHALL be the Python template dataclasses, not any directory on the filesystem
