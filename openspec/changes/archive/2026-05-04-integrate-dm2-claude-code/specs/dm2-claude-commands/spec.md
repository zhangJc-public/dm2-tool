## ADDED Requirements

### Requirement: Slash commands for dm2 CLI groups
The system SHALL provide Claude Code slash commands under `/dm2:` prefix that allow users to manually invoke dm2 functionality.

#### Scenario: Knowledge query command
- **WHEN** user types `/dm2:knowledge search OV-2`
- **THEN** Claude Code SHALL execute `python3 -m dm2.cli.main knowledge search OV-2 --json`

#### Scenario: Analysis command
- **WHEN** user types `/dm2:analyze <description>`
- **THEN** Claude Code SHALL execute `python3 -m dm2.cli.main analyze "<description>" --json`

#### Scenario: Pipeline command
- **WHEN** user types `/dm2:pipeline --status`
- **THEN** Claude Code SHALL execute `python3 -m dm2.cli.main run --status --json`

#### Scenario: Change command
- **WHEN** user types `/dm2:change list`
- **THEN** Claude Code SHALL execute `python3 -m dm2.cli.main change list-changes --json`

### Requirement: Command definitions in .claude/commands/dm2
The system SHALL store dm2 slash command definitions as Markdown files in `.claude/commands/dm2/` directory, following Claude Code command definition format.

#### Scenario: Command file structure
- **WHEN** a command file `knowledge.md` is created
- **THEN** it SHALL include frontmatter with `name`, `description`, `category`, `tags` fields
- **AND** the body SHALL describe the command's purpose and usage

### Requirement: Commands installable to target projects
The system SHALL support installing dm2 commands into target project directories.

#### Scenario: Install with dm2 init
- **WHEN** user creates a new dm2 project
- **THEN** the project's `.claude/commands/dm2/` SHALL contain dm2 command files

#### Scenario: Install to existing project
- **WHEN** user runs install script in an existing project
- **THEN** dm2 command files SHALL appear in the project's `.claude/commands/dm2/`
