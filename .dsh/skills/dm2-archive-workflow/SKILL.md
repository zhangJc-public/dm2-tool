---
name: dm2-archive-workflow
description: "Archive a single completed dm2 architecture change. Use after the dm2-apply-workflow skill and the dm2-verify-workflow skill to finalize a change."
user-invocable: true
metadata:
  author: "dm2"
  version: "0.2.0"
  generatedBy: "dm2-tool/0.2.0"
---

Archive a completed dm2 architecture change — finalize it and move it to the archive directory.

**Input**: Optionally specify a change name. If omitted, prompt for selection.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `dm2 change list-changes --json` and use the **ask_user_question tool** to let the user select

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose if ambiguous.

2. **Check change status**

   ```bash
   dm2 change status --json
   ```

   Parse to understand:
   - Artifact completion status
   - View generation progress (from view-state.yaml)

3. **Read tasks.md for completion summary**

   Check `dm2-changes/<name>/tasks.md` for task completion status.
   Count completed vs pending tasks.

   If tasks are incomplete, show a warning but allow the user to proceed.

4. **Optional: Run verification**

   Offer to verify before archiving:
   > "Run the `dm2-verify-workflow` skill to check view consistency before archiving?"

   If user wants to verify:
   ```bash
   dm2 validate --all --change "<name>" --json
   ```
   Parse and display verification results. Warnings don't block archive.

5. **Show archive summary and confirm**

   Display what will be archived:
   - Change name
   - Artifact status (proposal.md, design.md, tasks.md)
   - View generation progress (N/M views generated)
   - Task completion (N/M tasks complete)

   Use **ask_user_question tool** with:
   - "Archive this change" — proceed
   - "Cancel" — stop

   **IMPORTANT**: Always confirm before archiving. Archiving moves the change and cannot be easily undone.

6. **Execute archive**

   ```bash
   dm2 archive "<name>" --json
   ```

   Parse the result to get the archive location.

7. **Show result**

   ```
   ## Archived: <change-name>

   **Archived to:** dm2-archive/<date>-<name>/

   Change finalized and moved to archive. All artifacts preserved for audit.
   ```

**Output With Incomplete Tasks**

```
⚠ Warning: <change-name> has incomplete tasks (3/7 complete).

Incomplete tasks won't be preserved. Archive anyway?

Options:
- Archive anyway
- Cancel (finish remaining tasks first with the dm2-apply-workflow skill)
```

**Output When No Changes**

```
No active changes found. Start a new analysis with the `dm2-new-workflow` skill or the `dm2-propose-workflow` skill.
```

**Guardrails**
- Always confirm before archiving — this is a destructive operation (moves the change)
- Warn about incomplete tasks but don't block — user may have valid reasons
- Offer to run the `dm2-verify-workflow` skill before archiving
- Use `dm2` for all CLI calls
- Always pass `--json` for structured output
- Single change only — for batch archiving, use the `dm2-bulk-archive-workflow` skill
