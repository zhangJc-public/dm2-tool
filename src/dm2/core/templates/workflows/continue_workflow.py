"""Continue workflow — resume in-progress dm2 analysis or view generation."""

from dm2.core.templates import WorkflowTemplate, SkillTemplate, CommandTemplate, WORKFLOWS

CONTINUE_SKILL = SkillTemplate(
    name="dm2-continue-workflow",
    description="Continue an in-progress dm2 architecture analysis or view generation. Use when the user wants to pick up where they left off.",
    instructions="""Continue working on a dm2 architecture analysis or view generation session.

**Input**: Optionally specify a change name. If omitted, auto-detect from project state.

**Steps**

1. **If no change name provided, prompt for selection**

   Run `python3 -m dm2.cli.main change list-changes --json` to get available changes. Then use the **AskUserQuestion tool** to let the user select which change to work on.

   Present the top 3-4 most recently modified changes, showing:
   - Change name
   - Status (from `.change.yaml`)
   - View generation progress (generated vs pending)

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose.

2. **Check current state**
   ```bash
   python3 -m dm2.cli.main change status --json
   ```
   Also check project status:
   ```bash
   python3 -m dm2.cli.main status --json
   ```
   Parse to understand:
   - Which views have been generated (from `.dm2/view-state.yaml` if available)
   - Which views are pending
   - If a pipeline is in progress (`dm2 run --status --json`)

3. **Act based on state**

   **If pipeline is in progress:**
   ```bash
   python3 -m dm2.cli.main run --status --json
   ```
   - Get `current_step` and `status`
   - Get step instructions: `python3 -m dm2.cli.main run --instructions <current_step> --json`
   - Complete the current step
   - Advance to next step: `python3 -m dm2.cli.main run --complete-step <step_id> --json`
   - Continue pipeline until complete or user pauses

   **If views are pending (no active pipeline):**
   - Find the first pending view (from analysis recommendations or view state)
   - Get its instructions: `python3 -m dm2.cli.main instructions <view_id> --change "<name>" --json`
   - Generate the view content
   - Write to `dm2-changes/<name>/views/<View-ID>.<ext>` (.md or .html)
   - Register with view state:
     ```bash
     python3 -m dm2.cli.main view register <View-ID> --change "<name>" --path "dm2-changes/<name>/views/<View-ID>.<ext>"
     ```

   **If all views generated and no pipeline:**
   - Suggest: "All recommended views have been generated."
   - Offer: "Run `/dm2:verify` to check consistency, or `/dm2:archive` to archive this change."

   **If nothing to continue:**
   - "No active analysis found. Start a new one with `/dm2:new`."

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

Ready to continue? Say "continue" or run `/dm2:continue`.
```

**Output When Done**

```
## Analysis Complete: <change-name>

All recommended views generated ✓

### What's Next
- `/dm2:verify` — Check consistency across all views
- `/dm2:archive` — Archive the completed analysis
```

**Guardrails**
- Always prompt for change selection if multiple exist
- Create exactly ONE view or complete ONE step per invocation
- Do not skip dependency views (views with prerequisites should be generated first)
- If a view fails to generate, stop and report the issue
- Use `python3 -m dm2.cli.main` for all CLI calls
- Always pass `--json` for structured output
- Write each generated view to `dm2-changes/<name>/views/<View-ID>.<ext>` and register with `dm2 view register`
""",
)

CONTINUE_COMMAND = CommandTemplate(
    name="DM2: Continue",
    description="Continue an in-progress dm2 architecture analysis",
    tags=["dm2", "DoDAF", "architecture", "continue"],
    body="""Continue working on an in-progress dm2 architecture analysis or view generation session.

**Input**: `/dm2:continue [change-name]` — optionally specify which change to continue. If omitted, the AI Agent prompts for selection.

This picks up where you left off — continuing pipeline steps or generating the next pending view. Run after `/dm2:propose` or `/dm2:new` to start generating views.
""",
)


def get_workflow_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="continue",
        skill_dir="dm2-continue-workflow",
        command_file="continue.md",
        skill=CONTINUE_SKILL,
        command=CONTINUE_COMMAND,
    )
