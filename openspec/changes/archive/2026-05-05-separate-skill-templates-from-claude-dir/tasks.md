## 1. Core infrastructure — template dataclasses + adapter protocol

- [x] 1.1 Create `src/dm2/core/templates/__init__.py` with `WorkflowTemplate`, `SkillTemplate`, `CommandTemplate` dataclasses and `WORKFLOWS` registry list
- [x] 1.2 Create `src/dm2/core/adapters/__init__.py` with `ToolAdapter` protocol class (ABC with `tool_id`, `get_skills_dir()`, `get_commands_dir()`, `format_skill_frontmatter()`, `format_command_frontmatter()`)
- [x] 1.3 Create `src/dm2/core/adapters/claude.py` — `ClaudeCodeAdapter` implementing `ToolAdapter` for Claude Code (skills → `.claude/skills/`, commands → `.claude/commands/dm2/`)

## 2. Workflow templates — extract 7 workflows into Python

- [x] 2.1 Create propose workflow template (extract from `.claude/skills/dm2-propose-workflow/SKILL.md` + `.claude/commands/dm2/propose.md`)
- [x] 2.2 Create continue workflow template (extract from `.claude/skills/dm2-continue-workflow/SKILL.md` + `.claude/commands/dm2/continue.md`)
- [x] 2.3 Create new workflow template (extract from `.claude/skills/dm2-new-workflow/SKILL.md` + `.claude/commands/dm2/new.md`)
- [x] 2.4 Create ff workflow template (extract from `.claude/skills/dm2-ff-workflow/SKILL.md` + `.claude/commands/dm2/ff.md`)
- [x] 2.5 Create verify workflow template (extract from `.claude/skills/dm2-verify-workflow/SKILL.md` + `.claude/commands/dm2/verify.md`)
- [x] 2.6 Create onboard workflow template (extract from `.claude/skills/dm2-onboard-workflow/SKILL.md` + `.claude/commands/dm2/onboard.md`)
- [x] 2.7 Create bulk-archive workflow template (extract from `.claude/skills/dm2-bulk-archive-workflow/SKILL.md` + `.claude/commands/dm2/bulk-archive.md`)
- [x] 2.8 Register all 7 workflows in `WORKFLOWS` list

## 3. Rewrite dm2 init — generate, not copy

- [x] 3.1 Implement `generate_claude_config(target_dir, version, adapter)` in `src/dm2/core/templates/` — iterates WORKFLOWS, calls adapter to write SKILL.md and command .md for each
- [x] 3.2 Rewrite `dm2 init` in `src/dm2/cli/main.py`: remove `.claude/` copy block (lines 79-92), replace with call to `generate_claude_config()`
- [x] 3.3 Ensure init does NOT import or reference `.claude/` from the dm2-tool package root

## 4. Verification

- [x] 4.1 Run `dm2 init /tmp/dm2-test-proj` and verify `.claude/skills/` contains only 7 dm2-* directories
- [x] 4.2 Run `dm2 init /tmp/dm2-test-proj` and verify `.claude/commands/` contains only `dm2/` (no `opsx/`)
- [x] 4.3 Verify each generated SKILL.md has `generatedBy: "dm2-tool/<version>"` in frontmatter
- [x] 4.4 Verify `dm2 init` works when dm2-tool was installed via `pip install` (not editable mode) — no `.claude/` source directory needed
- [x] 4.5 Verify existing `.claude/skills/dm2-*-workflow/SKILL.md` content matches generated output (instructions body)
