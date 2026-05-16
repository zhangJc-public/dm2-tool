## 1. Apply Workflow

- [x] 1.1 Create `src/dm2/core/templates/workflows/apply.py` with `APPLY_SKILL` (SkillTemplate) containing task-driven view generation instructions: select change, read proposal/design/tasks.md, parse pending tasks, sort by dependency, generate views, mark checkboxes
- [x] 1.2 Create `APPLY_COMMAND` (CommandTemplate) with name "DM2: Apply", description, tags, and body text
- [x] 1.3 Implement `get_workflow_template()` returning `WorkflowTemplate` with workflow_id="apply", skill_dir="dm2-apply-workflow", command_file="apply.md"

## 2. Archive Workflow

- [x] 2.1 Create `src/dm2/core/templates/workflows/archive.py` with `ARCHIVE_SKILL` (SkillTemplate) containing single-change archive instructions: select change, check status, optionally verify, confirm, execute archive
- [x] 2.2 Create `ARCHIVE_COMMAND` (CommandTemplate) with name "DM2: Archive", description, tags, and body text
- [x] 2.3 Implement `get_workflow_template()` returning `WorkflowTemplate` with workflow_id="archive", skill_dir="dm2-archive-workflow", command_file="archive.md"

## 3. Register New Workflows

- [x] 3.1 Update `src/dm2/core/templates/workflows/__init__.py`: add `apply` and `archive` to imports and `_all_workflows` list

## 4. Update Propose Output

- [x] 4.1 Update `src/dm2/core/templates/workflows/propose.py` step 8 output: change primary recommendation from `/dm2:continue`/`dm2:ff` to `/dm2:apply`, with continue/ff listed as alternatives

## 5. Regenerate Agent Config

- [x] 5.1 Run `generate_agent_config()` to generate `.claude/skills/dm2-apply-workflow/SKILL.md`, `.claude/skills/dm2-archive-workflow/SKILL.md`, `.claude/commands/dm2/apply.md`, `.claude/commands/dm2/archive.md`
- [x] 5.2 Verify all generated files exist and have correct content
