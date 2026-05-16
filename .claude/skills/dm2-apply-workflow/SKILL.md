---
name: dm2-apply-workflow
description: Execute the implementation plan from /dm2:propose — read tasks.md and generate all DoDAF views in dependency order. Use after /dm2:propose to implement the planned views.
license: MIT
compatibility: Requires dm2-tool CLI and an active .dm2 project.
user-invocable: false
metadata:
  author: "dm2"
  version: "0.1.0"
  generatedBy: "dm2-tool/0.1.0"
---

Implement the architecture views planned in `/dm2:propose` by reading tasks.md and executing all pending view generation tasks.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `python3 -m dm2.cli.main change list-changes --json` and use the **AskUserQuestion tool** to let the user select

   Always announce which change is being worked on.

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose if ambiguous.

2. **Read the plan artifacts**

   Read the following files from `dm2-changes/<name>/`:
   - `proposal.md` — understand the system description, complexity, selected concerns, and scope
   - `design.md` — understand the technical approach, view dependency chain, and key decisions
   - `tasks.md` — the executable task list with checkboxes

   If `tasks.md` does not exist:
   > No implementation plan found. Run `/dm2:propose <system-description>` first to analyze the system and create a plan.

   Stop here if no tasks.md.

3. **Parse pending tasks**

   Scan tasks.md for unchecked view generation tasks:
   - `- [ ] Generate <View-ID>: <description>`

   Skip tasks that are already checked (`- [x]`). This makes apply resumable after interruption.

   If no pending tasks remain:
   > All tasks in tasks.md are complete. Run `/dm2:verify` to check consistency, then `/dm2:archive` to archive this change.

4. **Sort pending tasks by dependency order**

   ```bash
   python3 -m dm2.cli.main knowledge views --json
   ```

   Parse the dependency information. Sort pending view tasks so that dependency views are generated before dependent views. Tasks without explicit dependencies can be generated in any order.

5. **Generate views (loop through sorted pending tasks)**

   For each pending view generation task:

   a. **Get view instructions**:
      ```bash
      python3 -m dm2.cli.main instructions <view_id> --change "<name>" --json
      ```
      Returns `context`, `rules`, `template`, `output_path`.

   b. **Generate the view content** following the template and rules. Use the context from proposal.md and design.md to inform the content.

   c. **Save to the change directory**:
      Write the view to `dm2-changes/<name>/views/<View-ID>.<ext>`.
      Format (.md or .html) depends on what renders the diagrams best.

   d. **Register with view state**:
      ```bash
      python3 -m dm2.cli.main view register <view_id> --change "<name>" --path "dm2-changes/<name>/views/<View-ID>.<ext>"
      ```

   e. **Mark task complete** in tasks.md: change `- [ ]` to `- [x]` for this task.

   f. **If a view requires user input** (unclear from context):
      - Note the issue and continue with other views
      - Report skipped views at the end

6. **Show completion summary**

   Display:
   - Total views generated
   - Any skipped views and why
   - Output: "Run `/dm2:verify` to check consistency, then `/dm2:archive` to archive."

**Output During Generation**

```
## Applying: <change-name>

Generating view 3/7: SV-1 Systems Interface Description
[...generation happening...]
✓ SV-1 complete

Generating view 4/7: OV-2 Operational Resource Flow
[...generation happening...]
✓ OV-2 complete
```

**Output On Completion**

```
## Apply Complete: <change-name>

**Generated:** N/N views

### Generated Views
| View | Output Path |
|------|-------------|
| OV-1 | dm2-changes/<name>/views/OV-1.html |
| OV-2 | dm2-changes/<name>/views/OV-2.html |
...

### Next Steps
- `/dm2:verify` — Check view consistency
- `/dm2:archive` — Archive this change
```

**Output With Skips**

```
## Apply Complete (partial): <change-name>

**Generated:** N/M views

### Generated
| View | Output Path |
|------|-------------|
...

### Skipped
- <view_id>: <reason for skip>

Run `/dm2:apply` again to retry skipped views, or `/dm2:continue` for step-by-step generation.
```

**Guardrails**
- Read plan artifacts (proposal.md, design.md, tasks.md); do NOT re-run cynefin/analyze
- If tasks.md is missing, stop and suggest `/dm2:propose`
- Generate views in dependency order (respecting ArtifactGraph topology)
- Skip views that require user clarification; report at the end, continue with others
- Mark tasks.md checkboxes as each view is completed — this enables resuming after interruption
- If implementation reveals a design issue, flag it and suggest updating design.md — don't silently deviate
- Use `python3 -m dm2.cli.main` for all CLI calls
- Always pass `--json` for structured output
- Write generated views to `dm2-changes/<name>/views/<View-ID>.<ext>` (.md or .html, whichever renders best)
- After writing each view, register it: `python3 -m dm2.cli.main view register <view_id> --change "<name>" --path "dm2-changes/<name>/views/<View-ID>.<ext>"`
