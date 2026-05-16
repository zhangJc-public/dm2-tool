## Why

`dm2 init` currently copies skills and commands by `shutil.copytree()` from the developer's `.claude/` directory — which contains both dm2 AND OpenSpec content. This pollutes user projects with irrelevant OpenSpec files. More fundamentally, path resolution via `Path(__file__).parent.parent.parent.parent` only works in editable install mode (`pip install -e`), breaking `dm2 init` when installed as a regular pip package.

OpenSpec solved this with a "generated, not copied" architecture: workflow content lives as template functions, tool adapters know where to write files. We adopt the same pattern for dm2, scoped to Claude Code initially.

## What Changes

- Extract 7 SKILL.md and 7 command .md contents into Python template classes (not file copies)
- Create a `ClaudeCodeAdapter` that maps workflows to `.claude/` paths (skills + commands)
- Rewrite `dm2 init` to generate skill/command files from templates instead of copying from `.claude/`
- Fix path resolution: use package-relative resources (no more `Path(__file__).parent.parent...`)
- The developer's `.claude/` returns to being developer-only config, not a distribution source

## Capabilities

### New Capabilities

- `skill-template-generation`: Python template classes that hold SKILL.md and command .md content for each dm2 workflow (7 workflows: propose, continue, new, ff, verify, onboard, bulk-archive). Templates are versioned and include `generatedBy` metadata.
- `tool-command-adapter`: Abstraction for mapping workflow templates to tool-specific paths. Initial implementation: `ClaudeCodeAdapter` only. Interface designed for future Cursor/CodeBuddy/etc support.

### Modified Capabilities

- `dm2-project-init`: `dm2 init` SHALL use the template generation system instead of copying from `.claude/`. The project-local `.claude/` (skills + commands) SHALL be generated, not copied. Reference knowledge base provisioning (`dm2-reference/` → `.dm2/reference/`) is unchanged.

## Impact

- `src/dm2/cli/main.py` — init command rewritten (lines 79–92)
- `src/dm2/core/templates/` — NEW: workflow template classes (7 workflows)
- `src/dm2/core/adapters/` — NEW: tool adapter abstraction + `claude.py`
- `.claude/` — developer's directory, no longer read by dm2 init
- `pyproject.toml` — may need package-data update for templates
- **BREAKING**: Previously initialized projects that relied on OpenSpec skills being present will need to run `openspec init` separately (correct behavior — dm2 should not distribute OpenSpec)
