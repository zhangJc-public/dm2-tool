---
name: dm2-archive-workflow
description: Archive a single completed dm2 architecture change. Use after /dm2:apply and /dm2:verify to finalize a change.
license: MIT
compatibility: Requires dm2-tool CLI and an active .dm2 project.
user-invocable: false
metadata:
  author: "dm2"
  version: "0.1.0"
  generatedBy: "dm2-tool/0.1.0"
---

Archive a completed dm2 architecture change — finalize it and move it to the archive directory.

**Input**: Optionally specify a change name. If omitted, prompt for selection.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `python3 -m dm2.cli.main change list-changes --json` and use the **AskUserQuestion tool** to let the user select

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose if ambiguous.

2. **Check change status**

   ```bash
   python3 -m dm2.cli.main change status --json
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
   > "Run `/dm2:verify` to check view consistency before archiving?"

   If user wants to verify:
   ```bash
   python3 -m dm2.cli.main validate --all --change "<name>" --json
   ```
   Parse and display verification results. Warnings don't block archive.

5. **Show archive summary and confirm**

   Display what will be archived:
   - Change name
   - Artifact status (proposal.md, design.md, tasks.md)
   - View generation progress (N/M views generated)
   - Task completion (N/M tasks complete)

   Use **AskUserQuestion tool** with:
   - "Archive this change" — proceed
   - "Cancel" — stop

   **IMPORTANT**: Always confirm before archiving. Archiving moves the change and cannot be easily undone.

6. **Execute archive**

   ```bash
   python3 -m dm2.cli.main archive "<name>" --json
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
- Cancel (finish remaining tasks first with /dm2:apply)
```

**Output When No Changes**

```
No active changes found. Start a new analysis with `/dm2:new` or `/dm2:propose`.
```

**Guardrails**
- Always confirm before archiving — this is a destructive operation (moves the change)
- Warn about incomplete tasks but don't block — user may have valid reasons
- Offer to run `/dm2:verify` before archiving
- Use `python3 -m dm2.cli.main` for all CLI calls
- Always pass `--json` for structured output
- Single change only — for batch archiving, use `/dm2:bulk-archive`
