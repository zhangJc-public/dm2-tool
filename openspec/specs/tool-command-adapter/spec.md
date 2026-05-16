## Tool Command Adapter Spec

### Purpose
Define the `ToolAdapter` protocol — an abstract interface for mapping workflow templates to tool-specific filesystem locations and frontmatter formats, enabling support for multiple AI coding tools through the same template system.

### Requirements

### Requirement: Tool adapter protocol
dm2 SHALL define a `ToolAdapter` protocol in `src/dm2/core/adapters/` specifying the interface for mapping workflow templates to tool-specific filesystem locations and frontmatter formats.

#### Scenario: Adapter defines target directories
- **WHEN** any `ToolAdapter` implementation is used
- **THEN** it SHALL provide `get_skills_dir()` returning the skills directory path (e.g., `.claude/skills/`)
- **AND** it SHALL provide `get_commands_dir()` returning the commands directory path (e.g., `.claude/commands/dm2/`)
- **AND** both paths SHALL be relative to the project root

#### Scenario: Adapter formats skill frontmatter
- **WHEN** `format_skill_frontmatter(template, version)` is called
- **THEN** it SHALL return a complete YAML frontmatter string with `name`, `description`, `license`, `compatibility`, and `metadata` fields
- **AND** the `metadata` SHALL include `author`, `version`, and `generatedBy` keys

#### Scenario: Adapter formats command frontmatter
- **WHEN** `format_command_frontmatter(template)` is called
- **THEN** it SHALL return a complete YAML frontmatter string with `name`, `description`, `category`, and `tags` fields
- **AND** the body SHALL follow the closing `---` of the frontmatter

### Requirement: Claude Code adapter implementation
dm2 SHALL provide a `ClaudeCodeAdapter` implementing `ToolAdapter` for Claude Code, writing skills to `.claude/skills/` and commands to `.claude/commands/dm2/`.

#### Scenario: Claude adapter produces valid skill file
- **WHEN** `ClaudeCodeAdapter` generates a SKILL.md from the propose workflow template
- **THEN** the file path SHALL be `.claude/skills/dm2-propose-workflow/SKILL.md`
- **AND** the frontmatter SHALL include `name: dm2-propose-workflow`
- **AND** the file SHALL be valid YAML frontmatter followed by markdown instructions

#### Scenario: Claude adapter produces valid command file
- **WHEN** `ClaudeCodeAdapter` generates a command from the propose workflow template
- **THEN** the file path SHALL be `.claude/commands/dm2/propose.md`
- **AND** the frontmatter SHALL include `name: "DM2: Propose"` and `category: Architecture`
- **AND** the tags SHALL include `dm2`, `DoDAF`, `architecture`, `analysis`, `propose`

#### Scenario: Future adapter uses same interface
- **WHEN** a future tool adapter is implemented (e.g., for Cursor or CodeBuddy)
- **THEN** it SHALL implement the same `ToolAdapter` protocol
- **AND** the `dm2 init` generation logic SHALL remain unchanged (adapter-agnostic)
