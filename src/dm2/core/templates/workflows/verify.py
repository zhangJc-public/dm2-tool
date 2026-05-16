"""Verify workflow — validate generated DoDAF views for completeness, correctness, and coherence."""

from dm2.core.templates import WorkflowTemplate, SkillTemplate, CommandTemplate

VERIFY_SKILL = SkillTemplate(
    name="dm2-verify-workflow",
    description="Verify generated DoDAF views for completeness, correctness, and coherence. Use when the user wants to validate their architecture views before archiving.",
    instructions="""Verify that generated DoDAF views are complete, correct, and coherent.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **If no change name provided, prompt for selection**

   Run `python3 -m dm2.cli.main change list-changes --json` to get available changes. Use the **AskUserQuestion tool** to let the user select.

   Show changes that have generated views.
   Mark changes with view generation progress.

   **IMPORTANT**: Do NOT guess or auto-select a change. Always let the user choose.

2. **Check status to understand the state**
   ```bash
   python3 -m dm2.cli.main change status --json
   python3 -m dm2.cli.main status --json
   ```
   Parse to understand:
   - Which views exist and their paths
   - Analysis results (Cynefin domain, recommended views)

3. **Read generated view contents**

   Read views from the change directory: `dm2-changes/<name>/views/`.
   Look for files named `<View-ID>.<ext>` (ext may be .md or .html).
   Also check `dm2 view list --json` for registered view paths.

4. **Initialize verification report structure**

   Create a report with three dimensions:
   - **Completeness**: Are all recommended views generated? Are any views missing required sections?
   - **Correctness**: Does each view follow DM2 rules? Are templates properly filled?
   - **Coherence**: Are views consistent with each other? (use `ConsistencyChecker`)

   Each dimension can have CRITICAL, WARNING, or SUGGESTION issues.

5. **Verify Completeness**

   **View Coverage**:
   - Compare recommended views (from analysis) against generated views
   - If recommended views are not generated:
     - Add CRITICAL issue: "Recommended view not generated: <view_id>"
     - Recommendation: "Generate <view_id> using `/dm2:continue`"

   **Section Coverage**:
   - For each generated view, check if required sections exist
   - DM2 views have defined structures — check against `dm2 knowledge view <view_id> --json` for expected sections

6. **Verify Correctness**

   **DM2 Rule Compliance**:
   - For each generated view, get the expected template:
     ```bash
     python3 -m dm2.cli.main instructions <view_id> --json
     ```
   - Compare generated content against the rules in the instructions
   - Flag missing required elements or format violations

   **Terminology Accuracy**:
   - Search for DM2 terms used in the views
   - Verify against knowledge base: `python3 -m dm2.cli.main knowledge search "<term>" --json`
   - Flag terms used incorrectly or inconsistently

7. **Verify Coherence**

   **Cross-View Consistency**:
   - If `dm2 validate` command is available:
     ```bash
     python3 -m dm2.cli.main validate --all --change "<name>" --json
     ```
   - Otherwise, manually check common consistency rules:
     - Activity-Performer binding (OV-5a activities must map to OV-4 performers)
     - Resource Flow integrity (OV-2 resources need producers and consumers)
     - Capability-Activity mapping (CV-2 capabilities should link to OV-5a activities)

   **Terminology Consistency**:
   - Check that the same concepts are named consistently across views
   - Flag inconsistencies as WARNING

8. **Generate Verification Report**

   **Summary Scorecard**:
   ```
   ## Verification Report: <change-name>

   ### Summary
   | Dimension    | Status           |
   |--------------|------------------|
   | Completeness | N/M views, K issues |
   | Correctness  | X/Y rules passed |
   | Coherence    | Z issues found  |
   ```

   **Issues by Priority**:

   1. **CRITICAL** (Must fix before archive):
      - Missing recommended views
      - Missing required view sections
      - Each with specific, actionable recommendation

   2. **WARNING** (Should fix):
      - DM2 rule deviations
      - Cross-view inconsistencies
      - Each with specific recommendation

   3. **SUGGESTION** (Nice to fix):
      - Terminology improvements
      - Format refinements
      - Each with specific recommendation

   **Final Assessment**:
   - If CRITICAL issues: "X critical issue(s) found. Fix before archiving."
   - If only warnings: "No critical issues. Y warning(s) to consider. Ready for archive."
   - If all clear: "All checks passed. Ready for archive."

**Verification Heuristics**

- **Completeness**: Focus on objective coverage (all recommended views done?)
- **Correctness**: Use DM2 knowledge base as the source of truth
- **Coherence**: Cross-reference views for consistency, don't nitpick formatting
- **False Positives**: When uncertain, prefer SUGGESTION over WARNING, WARNING over CRITICAL
- **Actionability**: Every issue must have a specific recommendation

**Output Format**

Use clear markdown with:
- Table for summary scorecard
- Grouped lists for issues (CRITICAL/WARNING/SUGGESTION)
- Code references in format: `view_id::section_name`
- Specific, actionable recommendations

Save the report to `dm2-changes/<name>/reports/verify.md`.
""",
)

VERIFY_COMMAND = CommandTemplate(
    name="DM2: Verify",
    description="Verify generated DoDAF views for consistency and completeness",
    tags=["dm2", "DoDAF", "architecture", "verify", "validate"],
    body="""Verify generated DoDAF views for completeness, correctness, and cross-view coherence.

**Input**: `/dm2:verify [change-name]` — optionally specify which change to verify. If omitted, the AI Agent prompts for selection.

Checks view coverage against recommendations, DM2 rule compliance, and cross-view consistency. Produces a verification report with CRITICAL/WARNING/SUGGESTION issues. Run before `/dm2:archive`.
""",
)


def get_workflow_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="verify",
        skill_dir="dm2-verify-workflow",
        command_file="verify.md",
        skill=VERIFY_SKILL,
        command=VERIFY_COMMAND,
    )
