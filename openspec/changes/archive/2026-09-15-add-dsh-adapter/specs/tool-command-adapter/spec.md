# Tool Command Adapter (delta)

## MODIFIED Requirements

### Requirement: Tool adapter protocol
dm2 SHALL define a `ToolAdapter` protocol in `src/dm2/core/adapters/` specifying the interface for mapping workflow templates to tool-specific filesystem locations and frontmatter formats.

#### Scenario: Adapter defines target directories
- **WHEN** any `ToolAdapter` implementation is used
- **THEN** it SHALL provide `get_skills_dir()` returning the skills directory path (e.g., `.claude/skills/`)
- **AND** it SHALL provide `get_commands_dir()` returning the commands directory path relative to the project root, or `None` when the target tool has no project-level command convention
- **AND** it SHALL expose a `supports_commands` property that is `True` only when the adapter emits command files
- **AND** every returned path SHALL be relative to the project root

#### Scenario: Adapter formats skill frontmatter
- **WHEN** `format_skill_frontmatter(template, version)` is called
- **THEN** it SHALL return a complete YAML frontmatter string containing `name`, `description`, and a `metadata` object with `author`, `version`, and `generatedBy` keys
- **AND** it SHALL include the additional fields its target tool requires (for example `license` and `compatibility` for Claude Code, or `user-invocable` for DeepSeek Harness)
- **AND** fields the target tool does not read SHALL be omitted rather than emitted unconditionally

#### Scenario: Adapter renders skill bodies for its target
- **WHEN** `render_skill_body(text)` is called
- **THEN** it SHALL return the instruction text as the target tool should receive it
- **AND** an adapter whose template text already matches its target SHALL return the text unchanged
- **AND** the transformation SHALL be pure, so identical input yields identical output

#### Scenario: Adapter formats command frontmatter
- **WHEN** `format_command_frontmatter(template)` is called on an adapter whose `supports_commands` is `True`
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

#### Scenario: Generation remains adapter-agnostic
- **WHEN** a new tool adapter is implemented
- **THEN** `dm2 init` SHALL select it through the adapter registry without a target-specific branch in the generation logic
- **AND** generation SHALL express differences only through protocol members (`get_skills_dir`, `get_commands_dir`, `supports_commands`, `render_skill_body`, and the frontmatter formatters)
- **AND** the Claude adapter's generated output SHALL remain byte-identical to its pre-change output

## ADDED Requirements

### Requirement: DeepSeek Harness adapter implementation
dm2 SHALL provide a `DshAdapter` implementing `ToolAdapter` for DeepSeek Harness, writing skills to `.dsh/skills/` and emitting no command files.

#### Scenario: DSH adapter writes discoverable project skills
- **WHEN** `DshAdapter` generates files for all registered workflows
- **THEN** each skill SHALL be written to `.dsh/skills/<skill-dir>/SKILL.md`
- **AND** no `.claude/` directory and no command file SHALL be created
- **AND** the number of files written SHALL equal the number of registered workflows

#### Scenario: DSH frontmatter satisfies the harness parser
- **WHEN** a generated DSH SKILL.md is parsed by DeepSeek Harness
- **THEN** `name` SHALL match the harness kebab-case skill-name grammar
- **AND** `description` SHALL be present and non-empty
- **AND** `user-invocable` SHALL be `true`, so each workflow keeps a user-facing entry point after command files are dropped
- **AND** `metadata.generatedBy` SHALL be `"dm2-tool/<version>"`

#### Scenario: Claude-specific references are rewritten
- **WHEN** a generated DSH skill is inspected
- **THEN** no `/dm2:` slash reference SHALL remain; each SHALL become a reference to the corresponding `dm2-<id>-workflow` skill
- **AND** a reference carrying an angle argument SHALL preserve it as `(input: <args>)`
- **AND** `AskUserQuestion` SHALL be rewritten to `ask_user_question`
- **AND** `/dm2:knowledge` and `python3 -m dm2.cli.main` SHALL be rewritten to the `dm2` CLI entry point
- **AND** a slash reference whose id matches no registered workflow SHALL be left unchanged

### Requirement: Adapter registry
dm2 SHALL expose `get_adapter(tool_id)` from `src/dm2/core/adapters/`, resolving a tool id to its adapter implementation.

#### Scenario: Known tool ids resolve
- **WHEN** `get_adapter("claude")` or `get_adapter("dsh")` is called
- **THEN** it SHALL return the corresponding adapter instance

#### Scenario: Unknown tool id is rejected
- **WHEN** `get_adapter()` is called with an unregistered id
- **THEN** it SHALL raise `ValueError` naming the available ids
- **AND** `dm2 init --tool <unknown>` SHALL report `INVALID_TOOL` and exit non-zero without writing files
