## MODIFIED Requirements

### Requirement: Init provisions local reference knowledge base
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

## ADDED Requirements

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
