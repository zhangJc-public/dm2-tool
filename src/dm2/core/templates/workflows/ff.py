"""Fast-forward workflow — generate all recommended views in one shot."""

from dm2.core.templates import WorkflowTemplate, SkillTemplate, CommandTemplate

FF_SKILL = SkillTemplate(
    name="dm2-ff-workflow",
    description="Fast-forward through dm2 analysis and view generation. Use when the user wants to generate all recommended views in one shot without stepping through each one.",
    instructions="""Fast-forward through architecture analysis and view generation — run everything needed in one go.

**Input**: The user's request should include a system description OR a kebab-case name for the analysis.

**Steps**

1. **If no clear input provided, ask what they want to build**

   Use the **AskUserQuestion tool** (open-ended, no preset options) to ask:
   > "What system do you want to model? Describe what you're building."

   From their description, derive a kebab-case name.

   **IMPORTANT**: Do NOT proceed without understanding what the user wants to model.

2. **Create the change directory**
   ```bash
   python3 -m dm2.cli.main change new "<name>"
   ```

3. **Run Cynefin assessment**
   ```bash
   python3 -m dm2.cli.main cynefin "<description>" --json
   ```
   Parse the domain and confidence for the summary.

4. **Run 6W analysis to get recommended views**
   ```bash
   python3 -m dm2.cli.main analyze "<description>" --json
   ```
   Parse `recommended_views` to get the list of views to generate.

5. **Generate all recommended views in dependency order**

   Use the artifact graph to determine generation order:
   ```bash
   python3 -m dm2.cli.main knowledge views --json
   ```
   Parse to get view dependency information.

   Loop through views in dependency order:
   a. **Get instructions for each view**:
      ```bash
      python3 -m dm2.cli.main instructions <view_id> --change "<name>" --json
      ```
      Returns `context`, `rules`, `template`, `output_path`.

   b. **Generate the view content** following the template and rules.

   c. **Save to the change directory**:
      Write the view to `dm2-changes/<name>/views/<View-ID>.<ext>`.
      Format (.md or .html) depends on what renders the diagrams best.

   d. **Register with view state**:
      ```bash
      python3 -m dm2.cli.main view register <view_id> --change "<name>" --path "dm2-changes/<name>/views/<View-ID>.<ext>"
      ```

   e. **Continue** to the next view.

   f. **If a view requires user input** (unclear from context):
      - Note the issue and continue with other views
      - Report skipped views at the end

6. **Show final summary**

   Display:
   - Cynefin domain and confidence
   - All views generated with their output paths
   - Any views that were skipped
   - Prompt: "Run `/dm2:verify` to check consistency across all views."

**Output On Success**

```
## Fast-Forward Complete: <change-name>

**Domain:** <Cynefin domain> (confidence: <confidence>)
**Generated:** N/N views

### Generated Views
| View | Output Path |
|------|-------------|
| OV-1 | dm2-changes/<name>/views/OV-1.html |
| OV-2 | dm2-changes/<name>/views/OV-2.html |
...

### Next Steps
- `/dm2:verify` — Check view consistency
- `/dm2:archive` — Archive this analysis
```

**Output With Skips**

```
## Fast-Forward Complete (partial): <change-name>

**Generated:** N/M views

### Generated
| View | Output Path |
|------|-------------|
...

### Skipped
- <view_id>: <reason for skip>

Run `/dm2:continue` to pick up remaining views.
```

**Guardrails**
- Generate views in dependency order (respecting ArtifactGraph)
- If a view fails, note it and continue — don't block the entire batch
- Skip views that require user clarification, report at the end
- Use `python3 -m dm2.cli.main` for all CLI calls
- Always pass `--json` for structured output
- Write generated views to `dm2-changes/<name>/views/<View-ID>.<ext>` (.md or .html, whichever renders best)
- After writing each view, register it: `python3 -m dm2.cli.main view register <View-ID> --change "<name>" --path "dm2-changes/<name>/views/<View-ID>.<ext>"`
""",
)

FF_COMMAND = CommandTemplate(
    name="DM2: Fast-Forward",
    description="Generate all recommended DoDAF views in one shot",
    tags=["dm2", "DoDAF", "architecture", "generate", "batch"],
    body="""Fast-forward through dm2 analysis and view generation — everything in one shot.

**Input**: `/dm2:ff <system-description>` — what system to model and generate views for.

This runs Cynefin analysis, 6W analysis, and generates ALL recommended DoDAF views in dependency order. No step-by-step — just results. Run `/dm2:verify` afterwards to check consistency.
""",
)


def get_workflow_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="ff",
        skill_dir="dm2-ff-workflow",
        command_file="ff.md",
        skill=FF_SKILL,
        command=FF_COMMAND,
    )
