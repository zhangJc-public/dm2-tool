---
name: dm2-bulk-archive-workflow
description: Archive multiple completed dm2 architecture changes at once. Use when archiving several parallel analyses.
license: MIT
compatibility: Requires dm2-tool CLI.
user-invocable: false
metadata:
  author: "dm2"
  version: "0.1.0"
  generatedBy: "dm2-tool/0.1.0"
---

Archive multiple completed dm2 architecture changes in a single operation.

**Input**: None required (prompts for selection)

**Steps**

1. **Get active changes**

   Run `python3 -m dm2.cli.main change list-changes --json` to get all active changes.

   If no active changes exist, inform user and stop.

2. **Prompt for change selection**

   Use **AskUserQuestion tool** with multi-select to let user choose changes:
   - Show each change with its status
   - Include an option for "All changes"
   - Allow any number of selections (1+ works, 2+ is the typical use case)

   **IMPORTANT**: Do NOT auto-select. Always let the user choose.

3. **Batch validation — gather status for all selected changes**

   For each selected change, collect:

   a. **Change status** — Run `python3 -m dm2.cli.main change status --json`
      - Parse the state file for artifact completion

   b. **View generation status** — Check `.dm2/view-state.yaml` if available
      - Count generated vs pending views
      - Note which views exist

   c. **View conflicts** — Build a map of `view_type -> [changes that generated it]`:
      ```
      OV-2 -> [change-a, change-b]  <- CONFLICT (2+ changes generated same view type)
      OV-1 -> [change-c]            <- OK (only 1 change)
      ```

4. **Detect view conflicts**

   A conflict exists when 2+ selected changes have generated the same view type. This matters because:
   - Views represent the same architecture aspect
   - The latest version should be the authoritative one

5. **Show consolidated status table**

   Display a table summarizing all changes:

   ```
   | Change            | Status | Views Generated | Conflicts | Ready |
   |-------------------|--------|-----------------|-----------|-------|
   | logistics-system  | open   | 5/7             | None      | Ready |
   | security-model    | open   | 3/3             | OV-2 (!)  | Ready*|
   ```

   For conflicts, show:
   ```
   * Conflict resolution:
     - OV-2: Both logistics-system and security-model have OV-2.
       Check which is more recent/authoritative.
   ```

   For incomplete changes, show warnings:
   ```
   Warnings:
   - logistics-system: 2 pending views (OV-6c, SV-1)
   ```

6. **Confirm batch operation**

   Use **AskUserQuestion tool** with a single confirmation:
   - Options:
     - "Archive all N changes"
     - "Archive only ready changes (skip those with warnings)"
     - "Cancel"

   If there are incomplete changes, make clear they'll be archived with warnings.

7. **Execute archive for each confirmed change**

   For each change:
   ```bash
   python3 -m dm2.cli.main change archive-change "<name>"
   ```

   Track outcome for each:
   - Success: archived successfully
   - Failed: error during archive (record error)
   - Skipped: user chose not to archive

8. **Display summary**

   ```
   ## Bulk Archive Complete

   Archived N changes:
   - logistics-system → dm2-archive/2026-05-04-logistics-system/
   - security-model → dm2-archive/2026-05-04-security-model/

   Skipped M changes:
   - Some other change (user chose not to archive)

   View conflict summary:
   - 1 conflict detected (OV-2): both changes archived, review for authoritative version
   ```

**Output On Success**

```
## Bulk Archive Complete

Archived N changes:
- <change-1> → dm2-archive/YYYY-MM-DD-<change-1>/
- <change-2> → dm2-archive/YYYY-MM-DD-<change-2>/

No conflicts (or: M conflicts resolved)
```

**Output When No Changes**

```
## No Changes to Archive

No active changes found. Start a new analysis with `/dm2:new`.
```

**Guardrails**
- Allow any number of changes (1+ is fine, 2+ is the typical use case)
- Always prompt for selection, never auto-select
- Detect view type conflicts early and warn user
- Show clear per-change status before confirming
- Use single confirmation for entire batch
- Track and report all outcomes (success/skip/fail)
- Archive directory uses dm2's standard archive path (`dm2-archive/`)
- Use `python3 -m dm2.cli.main` for all CLI calls
