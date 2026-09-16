# Add DeepSeek Harness adapter

## Why

The `ToolAdapter` protocol (`src/dm2/core/adapters/`) was introduced to distribute workflow
skills to more than one AI tool, but only `ClaudeCodeAdapter` has ever existed — so a
DeepSeek Harness (DSH) session cannot run any dm2 workflow at all:

- DSH discovers project skills in `<git-root>/.dsh/skills/<dir>/SKILL.md` and **never reads
  `.claude/skills/`**, so `dm2 init` currently produces nothing DSH can see.
- DSH has **no project-level slash-command directory**, so the protocol's assumption that
  every adapter emits command files is unsatisfiable.
- DSH ignores unknown frontmatter keys but requires a kebab-case `name` and a `description`,
  and it natively understands `user-invocable` — a field Claude Code's adapter already emits.
- The skill bodies are written for Claude Code (`/dm2:propose`, `AskUserQuestion tool`), which
  are meaningless or wrong in DSH.

Without this change, the DSH adaptation stops at "the CLI can be called from bash" and the
10 documented workflows never reach a DSH session.

## What Changes

- **New `DshAdapter`** writing 10 skills to `.dsh/skills/<skill>/SKILL.md`, emitting no command
  files, and producing DSH-valid frontmatter (`name`, `description`, `user-invocable: true`,
  `metadata.{author,version,generatedBy}`).
- **Skill-body rendering hook**: `ToolAdapter.render_skill_body(text)` rewrites tool-specific
  references before a skill file is written. Claude renders identity (byte-stable output);
  DSH rewrites `/dm2:<id>` → a `dm2-<id>-workflow` skill reference, `AskUserQuestion` →
  `ask_user_question`, and `python3 -m dm2.cli.main` → `dm2`.
- **Optional commands**: `get_commands_dir()` may return `None`, with a `supports_commands`
  property telling the generator whether to emit command files.
- **Adapter registry**: `get_adapter(tool_id)` returns the adapter for `claude` or `dsh` and
  raises `ValueError` otherwise.
- **`dm2 init --tool/-t claude|dsh`** (default `claude`, preserving current behavior).
- **BREAKING**: `dm2 init --json` replaces the boolean `claude_config` field with a structured
  `agent_config` object (`tool`, `files_generated`, `skills_dir`, `commands_dir`, `commands`).
  The pre-1.0 field was Claude-only and could not describe a second target.

## Capabilities

### New Capabilities
<!-- None: the DSH adapter is an implementation of the existing tool-adapter protocol,
     following the precedent that ClaudeCodeAdapter is specified under tool-command-adapter
     rather than as a capability of its own. -->

### Modified Capabilities

- `tool-command-adapter`: `get_commands_dir()` becomes optional, a `supports_commands`
  capability and a `render_skill_body()` hook join the protocol, skill frontmatter becomes
  tool-specific (only `name`/`description`/`metadata` are universal), the "generation logic
  remains unchanged" scenario is restated as "remains adapter-agnostic", and a DSH adapter
  requirement plus an adapter-registry requirement are added.
- `skill-template-generation`: generated instruction bodies become adapter-rendered, so the
  "functionally identical to `.claude/skills/`" scenario holds for the Claude adapter and is
  explicitly not a cross-adapter invariant.
- `dm2-project-init`: `dm2 init` gains `--tool/-t`, so generated skill/command locations and
  file counts depend on the selected tool; the stale "7 skills / 7 commands" scenario is
  corrected to the 10 workflows that exist.

## Impact

- **Code**: `src/dm2/core/adapters/__init__.py` (protocol + registry),
  `src/dm2/core/adapters/dsh.py` (new), `src/dm2/core/adapters/claude.py` (ordering only),
  `src/dm2/core/templates/generator.py` (optional commands + body rendering),
  `src/dm2/cli/main.py` (`init --tool`).
- **Tests**: `test/test_workflow_templates.py` (render mapping + DSH generation),
  `test/test_init_tool_option.py` (new CLI coverage). Suite 120 → 137.
- **CLI contract**: `dm2 init --json` field rename (`claude_config` → `agent_config`).
- **Docs**: `README.md`, `docs/readme.md`, `CLAUDE.md`, `CHANGELOG.md`.
- **Spec hygiene**: three touched specs are corrected from `### Requirements` to
  `## Requirements`, which had made every requirement in them invisible to
  `openspec validate`, `list`, and `archive`. The other seven specs with the same structural
  defect are explicitly out of scope for this change.
- **Unchanged**: Claude Code output is byte-identical; no `.dm2/` data, knowledge index, or
  workflow instruction text in the templates changes.
