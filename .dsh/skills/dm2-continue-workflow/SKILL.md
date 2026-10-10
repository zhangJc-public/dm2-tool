---
name: dm2-continue-workflow
description: "Continue an in-progress dm2 architecture analysis or view generation. Use when the user wants to pick up where they left off."
user-invocable: true
metadata:
  author: "dm2"
  version: "0.1.0"
  generatedBy: "dm2-tool/0.1.0"
---

Continue working on a dm2 architecture analysis or view generation session.

**Input**: Optionally specify a change name. If omitted, auto-detect from project state.

**Steps**

1. **If no change name provided, prompt for selection**

   Run `dm2 change list-changes --json` to get available changes. Then use the **ask_user_question tool** to let the user select which change to work on.

   Present the top 3-4 most recently modified changes, showing:
   - Change name
   - Status (from `.change.yaml`)
   - View generation progress (generated vs pending)

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose.

2. **Check current state**
   ```bash
   dm2 change status --json
   ```
   Also check project status:
   ```bash
   dm2 status --json
   ```
   Parse to understand:
   - Which views have been generated (from `.dm2/view-state.yaml` if available)
   - Which views are pending
   - If a pipeline is in progress (`dm2 run --status --json`)

3. **Act based on state**

   **If pipeline is in progress:**
   ```bash
   dm2 run --status --json
   ```
   - Get `current_step` and `status`
   - Get step instructions: `dm2 run --instructions <current_step> --json`
   - Complete the current step
   - Advance to next step: `dm2 run --complete-step <step_id> --json`
   - Continue pipeline until complete or user pauses

   **If views are pending (no active pipeline):**
   - Find the first pending view (from analysis recommendations or view state)
   - Get its instructions: `dm2 instructions <view_id> --change "<name>" --json`
   - Generate the view content
   - Write to `dm2-changes/<name>/views/<View-ID>.<ext>` (.md or .html)
   - Register with view state:
     ```bash
     dm2 view register <View-ID> --change "<name>" --path "dm2-changes/<name>/views/<View-ID>.<ext>"
     ```

   **If all views generated and no pipeline:**
   - Suggest: "All recommended views have been generated."
   - Offer: "Run the `dm2-verify-workflow` skill to check consistency, or the `dm2-archive-workflow` skill to archive this change."

   **If nothing to continue:**
   - "No active analysis found. Start a new one with the `dm2-new-workflow` skill."

4. **After advancing, show progress**

   Display:
   - What was just completed
   - Current overall progress (views generated / total recommended)
   - What's next

**Output On Progress**

```
## Continuing: <change-name>

**Just completed:** <view_id or step>
**Progress:** 3/7 views generated

### Next
- [ ] <next_view_id>: <description>

Ready to continue? Say "continue" or run the `dm2-continue-workflow` skill.
```

**Output When Done**

```
## Analysis Complete: <change-name>

All recommended views generated ✓

### What's Next
- the `dm2-verify-workflow` skill — Check consistency across all views
- the `dm2-archive-workflow` skill — Archive the completed analysis
```

**Guardrails**
- Always prompt for change selection if multiple exist
- Create exactly ONE view or complete ONE step per invocation
- Do not skip dependency views (views with prerequisites should be generated first)
- If a view fails to generate, stop and report the issue
- Use `dm2` for all CLI calls
- Always pass `--json` for structured output
- Write each generated view to `dm2-changes/<name>/views/<View-ID>.<ext>` and register with `dm2 view register`
