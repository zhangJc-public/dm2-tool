---
name: dm2-ff-workflow
description: "Fast-forward through dm2 analysis and view generation. Use when the user wants to generate all recommended views in one shot without stepping through each one."
user-invocable: true
metadata:
  author: "dm2"
  version: "0.2.0"
  generatedBy: "dm2-tool/0.2.0"
---

Fast-forward through architecture analysis and view generation — run everything needed in one go.

**Input**: The user's request should include a system description OR a kebab-case name for the analysis.

**Steps**

1. **If no clear input provided, ask what they want to build**

   Use the **ask_user_question tool** (open-ended, no preset options) to ask:
   > "What system do you want to model? Describe what you're building."

   From their description, derive a kebab-case name.

   **IMPORTANT**: Do NOT proceed without understanding what the user wants to model.

2. **Create the change directory**
   ```bash
   dm2 change new "<name>"
   ```

3. **Run Cynefin heuristic prefill and adjudicate**
   ```bash
   dm2 cynefin -d "<description>" --json
   ```
   The result is `resolution: "heuristic"` until explicitly adjudicated. Read `signal_report`/`warnings` (excluded/weak crisis candidates such as 应急预案/中断风险 are not real crises; if the user confirms an ongoing event, re-run with `--domain Chaotic`), and re-run with explicit dimension options (or `--domain`) to lock the adjudicated result before committing to a view scope. Mark the domain as **未裁定** in the summary if you proceed without adjudication; if `needs_clarification` is true (Disorder), proceed cautiously with only the P0 core view set.

4. **Run 6W analysis to get recommended views**
   ```bash
   dm2 analyze -d "<description>" --json
   ```
   Parse `recommended_views` to get the list of views to generate.

5. **Generate all recommended views in dependency order**

   Use the artifact graph to determine generation order:
   ```bash
   dm2 knowledge views --json
   ```
   Parse to get view dependency information.

   Loop through views in dependency order:
   a. **Get instructions for each view**:
      ```bash
      dm2 instructions <view_id> --change "<name>" --json
      ```
      Returns `context`, `rules`, `template`, `output_path`.

   b. **Generate the view content** following the template and rules.

   c. **Save to the change directory**:
      Write the view to `dm2-changes/<name>/views/<View-ID>.<ext>`.
      Format (.md or .html) depends on what renders the diagrams best.

   d. **Register with view state**:
      ```bash
      dm2 view register <view_id> --change "<name>" --path "dm2-changes/<name>/views/<View-ID>.<ext>"
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
   - Prompt: "Run the `dm2-verify-workflow` skill to check consistency across all views."

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
- the `dm2-verify-workflow` skill — Check view consistency
- the `dm2-archive-workflow` skill — Archive this analysis
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

Run the `dm2-continue-workflow` skill to pick up remaining views.
```

**Guardrails**
- Generate views in dependency order (respecting ArtifactGraph)
- If a view fails, note it and continue — don't block the entire batch
- Skip views that require user clarification, report at the end
- Use `dm2` for all CLI calls
- Always pass `--json` for structured output
- Write generated views to `dm2-changes/<name>/views/<View-ID>.<ext>` (.md or .html, whichever renders best)
- After writing each view, register it: `dm2 view register <View-ID> --change "<name>" --path "dm2-changes/<name>/views/<View-ID>.<ext>"`
