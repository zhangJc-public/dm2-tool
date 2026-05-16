## ADDED Requirements

### Requirement: Auto-generate .claude/ on project init
The system SHALL automatically create `.claude/skills/` and `.claude/commands/dm2/` directories when a new dm2 project is initialized.

#### Scenario: dm2 init creates Claude Code config
- **WHEN** user runs `dm2 init my-project`
- **THEN** the project SHALL contain `.claude/skills/dm2-explore/SKILL.md`
- **AND** `.claude/skills/dm2-generate/SKILL.md`
- **AND** `.claude/skills/dm2-pipeline/SKILL.md`
- **AND** `.claude/commands/dm2/explore.md`
- **AND** `.claude/commands/dm2/generate.md`
- **AND** `.claude/commands/dm2/pipeline.md`
- **AND** `.claude/commands/dm2/status.md`

#### Scenario: Init does not overwrite existing .claude/
- **WHEN** user runs `dm2 init` in a directory that already has `.claude/`
- **THEN** the system SHALL preserve existing files and only add missing dm2 files

### Requirement: Install Claude Code config to existing project
The system SHALL provide a `dm2 setup-claude` command that installs dm2 skills and commands into an existing dm2 project.

#### Scenario: Setup claude in existing project
- **WHEN** user runs `dm2 setup-claude` in a dm2 project directory
- **THEN** the system SHALL create `.claude/skills/dm2-*/` with current skill files
- **AND** SHALL create `.claude/commands/dm2/` with current command files

#### Scenario: Setup claude outside a dm2 project
- **WHEN** user runs `dm2 setup-claude` outside a dm2 project
- **THEN** the system SHALL report an error with message "Not a dm2 project directory"

### Requirement: Skill and command files stored as templates
The system SHALL store dm2 skill and command files as reusable templates within the dm2-tool package.

#### Scenario: Template source location
- **WHEN** dm2-tool is installed
- **THEN** skill templates SHALL be available at `<package>/templates/init/.claude/skills/`
- **AND** command templates SHALL be available at `<package>/templates/init/.claude/commands/dm2/`
