# Tasks

## 1. Generalize the adapter protocol

- [x] 1.1 In `src/dm2/core/adapters/__init__.py`, change `get_commands_dir()` to return `Optional[str]` and give it a concrete default of `.claude/commands/dm2`
- [x] 1.2 Add the `supports_commands` property (default `True`) so the generator can decide whether command files are emitted
- [x] 1.3 Add the `render_skill_body(text: str) -> str` hook with an identity default, documenting that implementations must be pure
- [x] 1.4 Add `get_adapter(tool_id)` with lazy imports inside the function body to avoid a circular import, raising `ValueError` listing the known ids

## 2. DshAdapter

- [x] 2.1 Create `src/dm2/core/adapters/dsh.py` with `tool_id = "dsh"`, `get_skills_dir() -> ".dsh/skills"`, `get_commands_dir() -> None`, `supports_commands = False`
- [x] 2.2 Emit DSH frontmatter: `name`, YAML double-quoted `description`, `user-invocable: true`, `metadata.{author,version,generatedBy}`; route the description through the renderer so sibling references resolve
- [x] 2.3 Build the workflow-id → skill-directory map from `WORKFLOWS` so a newly registered workflow needs no adapter edit
- [x] 2.4 Implement `render_skill_body` in order: `/dm2:knowledge` → `dm2 knowledge`, `python3 -m dm2.cli.main` → `dm2`, `AskUserQuestion` → `ask_user_question`, backticked slash refs (with optional `<angle-arg>`), bare slash refs; leave unknown ids untouched
- [x] 2.5 Make `format_command_frontmatter` raise `NotImplementedError` as an explicit dead path
- [x] 2.6 Verify the two residual reference shapes found during implementation: `` `/dm2:new`. `` (period outside the token) and fenced `python3 -m dm2.cli.main ...` lines in `apply`

## 3. Generator

- [x] 3.1 In `src/dm2/core/templates/generator.py`, create the commands directory only when `supports_commands` is true and `get_commands_dir()` is not `None`
- [x] 3.2 Skip command-file writes for adapters without a command convention and keep the returned count meaning "files written" (Claude 20, DSH 10)
- [x] 3.3 Pass skill bodies through `adapter.render_skill_body()` before concatenating frontmatter

## 4. CLI

- [x] 4.1 Add `--tool/-t` (default `claude`) to `init` in `src/dm2/cli/main.py` and resolve it via `get_adapter()`
- [x] 4.2 Return `INVALID_TOOL` as JSON (exit 1) for `--json`, and a plain error otherwise
- [x] 4.3 Parameterize the human-readable directory echo for both targets
- [x] 4.4 Replace the `claude_config` boolean in the `--json` payload with structured `agent_config` (`tool`, `files_generated`, `skills_dir`, `commands_dir`, `commands`)

## 5. Tests

- [x] 5.1 `test/test_workflow_templates.py`: unit tests for every rewrite rule, including the angle-argument form, unknown-id passthrough, and an identity case for unrelated prose
- [x] 5.2 `test/test_workflow_templates.py`: DSH generation test group — 10 files, no `.claude/` and no `.dsh/commands/`, PyYAML-parsed frontmatter per skill, DSH kebab-case name grammar, and a hygiene assertion that no skill retains `/dm2:`, `AskUserQuestion`, or the module invocation
- [x] 5.3 `test/test_init_tool_option.py` (new): `init -t dsh --json`, default `init --json`, explicit `-t claude`, `INVALID_TOOL` for an unknown tool, and registry coverage
- [x] 5.4 Confirm the existing Claude generation test still asserts 20 files and that the committed `.claude/skills/` output is byte-identical after the change
- [x] 5.5 Verify with the real harness loader, not only the PyYAML emulation: instantiate `FileSystemSkillProvider` from the DSH checkout against a generated project and confirm 10 `project-dsh` candidates whose bodies parse with `userInvocable`/`modelInvocable` true and no residual tokens

## 6. Documentation

- [x] 6.1 `docs/readme.md`: `--tool` comparison table, `.dsh/` project structure, DSH discovery rule, `init -t dsh` usage, and the PATH fallback note
- [x] 6.2 `README.md`: quick-start example, capability table, and a target-tool table replacing the now-incomplete "10 Claude Code slash commands" sentence
- [x] 6.3 `CLAUDE.md`: skill-distribution section, adapter row in the source map, and the `.dm2/` project-mode entry
- [x] 6.4 `CHANGELOG.md`: the new option and the `claude_config` → `agent_config` contract change

## 7. Spec hygiene (touched specs only)

- [x] 7.1 Correct `### Requirements` to `## Requirements` in `openspec/specs/tool-command-adapter/spec.md`, `skill-template-generation/spec.md`, and `dm2-project-init/spec.md`, which currently make every requirement invisible to `validate`/`list`/`archive`
- [x] 7.2 Note the remaining seven structurally broken specs as a separate follow-up rather than folding them into this change

## 8. Verification

- [x] 8.1 `pytest test/` green (137 passed, up from 120)
- [x] 8.2 `ruff check` clean on every added or modified file; the touched-file set introduced no new errors and reduced `main.py` by one
- [x] 8.3 Manual `dm2 init . -t dsh` and `dm2 init .` runs in scratch projects: 10 skills and 0 commands for DSH, 10 skills plus 10 commands for Claude
- [x] 8.4 `openspec validate add-dsh-adapter` passes
