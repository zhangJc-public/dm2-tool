## 1. Documentation

- [ ] 1.1 Add architecture section to CLAUDE.md explaining DM2 (Python) and OpenSpec (TypeScript) independence
- [ ] 1.2 Update README.md with clear runtime requirements (Python required, Node.js optional for OpenSpec workflow)
- [ ] 1.3 Document the Claude Code orchestration model: how `/opsx:*` commands, `.claude/skills/`, and DM2 CLI relate

## 2. Validation

- [ ] 2.1 Verify all `dm2` CLI commands work without Node.js installed (only `openspec` commands need Node)
- [ ] 2.2 Verify `.claude/commands/opsx/*.md` and `.claude/skills/openspec-*/SKILL.md` are static files that work without `openspec` installed
- [ ] 2.3 Confirm `openspec update` is the only command requiring Node.js at runtime

## 3. Decision Record

- [ ] 3.1 Create decision record in project docs confirming Python as the permanent implementation language
- [ ] 3.2 Document the alternatives considered and rationale for rejection
