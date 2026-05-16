"""Propose workflow — full analysis + planning artifact generation."""

from dm2.core.templates import (
    WorkflowTemplate,
    SkillTemplate,
    CommandTemplate,
    WORKFLOWS,
)


PROPOSE_SKILL = SkillTemplate(
    name="dm2-propose-workflow",
    description="Run full DoDAF architecture analysis and generate planning artifacts (proposal, design, tasks) in one pass. Use when the user wants to analyze a system with DM2.",
    compatibility="Requires dm2-tool CLI and an active .dm2 project.",
    instructions="""Run a complete DoDAF architecture analysis and generate planning artifacts with concern-driven view focusing.

**Input**: The argument after `/dm2:propose` is a system description (what to analyze and model).

**Steps**

1. **Get input**

   If no system description is provided with the command, use the **AskUserQuestion tool** (open-ended, no preset options) to ask:
   > "What system do you want to model? Describe the system or problem you're working on."

   From their description, derive a kebab-case change name (e.g., "network security situational awareness system" → `network-security-situational-awareness`).

   **IMPORTANT**: Do NOT proceed without understanding what the user wants to model.

2. **Create the change directory**

   ```bash
   python3 -m dm2.cli.main change new "<name>"
   ```

   This creates a change at `dm2-changes/<name>/`.

3. **Run Cynefin complexity assessment**

   ```bash
   python3 -m dm2.cli.main cynefin --json -d "<system description>"
   ```

   Parse the JSON output to understand the complexity level (clear/complicated/complex/chaotic/disorder). This determines the scope of views to recommend.
   Optionally save your own rich Cynefin analysis to `dm2-changes/<name>/analysis/cynefin-assessment.md` for audit. Do NOT dump the raw CLI JSON — it is thin keyword-match output with little audit value. Capture your reasoning, not the CLI response.

4. **Run enhanced analysis with data group activation**

   ```bash
   python3 -m dm2.cli.main analyze --json -d "<system description>"
   ```
   ```bash
   python3 -m dm2.cli.main concern list --json
   ```

   Parse the analyze JSON to get:
   - `data_group_activation`: 17-dimensional activation vector
   - `data_group_keywords_matched`: keywords that triggered per group
   - `candidate_views`: all recommended DoDAF views (unsorted)
   - `group_to_views`: per-group mapping (name/label/activation/keywords/views)

   Parse the concern list JSON to get:
   - All 8 architecture concern templates with their `expected_data_groups` and `core_views` and `keywords`
   Optionally save your own rich analysis to `dm2-changes/<name>/analysis/` for audit (e.g., `data-group-activation.md`, `concern-match.md`). Do NOT dump raw CLI JSON — capture your reasoning, not the thin keyword-match output.

5. **Concern matching and Human selection**

   For each concern, compute a relevance score:

   ```
   concern_score = 0.6 × group_activation_overlap + 0.4 × keyword_match
     where:
       group_activation_overlap = |active_groups ∩ concern.expected_groups| / |concern.expected_groups|
       keyword_match = |description_words ∩ concern.keywords| / |concern.keywords|

       active_groups = {group_id for group_id, score in data_group_activation.items() if score > 0.0}
       description_words = set of normalized words from the system description
   ```

   **Rank** concerns by score descending. Present the top candidates with the AskUserQuestion tool:

   > "I've identified {N} relevant architecture concerns. Select the ones that match your focus:"

   Options should include at least the top 3 concerns (score ≥ 0.15) plus:
   - "全部视图（不做聚焦）" — skip concern filtering, use all candidate views
   - "再看一下" — let user review other concerns

   Each option label should show the concern name, score, and core view count:
   > "身份认证与访问控制 (0.58, 4 视图)"

   **IMPORTANT**: Let the Human make the final selection. Do NOT auto-select. The Human may pick 0, 1, or multiple concerns.

6. **Derive focused view set**

   From the Human-selected concerns:
   - **Focused views**: Union of `core_views` from all selected concerns
   - **Additional candidate views**: All views from `candidate_views` that are NOT in the focused set
   - **Separate into phases**:
     - **P1 (Core)**: Focused views that also appear in candidate_views
     - **P2 (Extended)**: Remaining focused views (concern core_views not in candidate_views)
     - **P3 (Additional)**: Additional candidate views (marked as supplementary)

   If Human picked "全部视图" (no concern filter), use all candidate_views as P1/P2/P3 based on relevance_score.

7. **Generate planning artifacts in the change directory**

   Create three files under `dm2-changes/<name>/`:

   a. **proposal.md** — why and scope
      - User's system description and conversation context
      - Cynefin complexity assessment result
      - Activated DM2 data groups overview (top activated groups)
      - **Selected concerns**: Which concerns the Human selected and why
      - **Focused views** (P1/P2): The concern-driven core view set
      - **Additional candidate views** (P3): Views not in any selected concern, for reference

   b. **design.md** — technical approach
      - Data group activation analysis (which groups scored highest)
      - Concern-driven view selection rationale
      - View dependency chain derived from ArtifactGraph
      - Phase rationale (P1=concern core, P2=concern extended, P3=supplementary)
      - Key decisions and trade-offs

   c. **tasks.md** — executable task list
      - View generation tasks ordered by dependency (use ArtifactGraph topological order)
      - Each task: `- [ ] Generate <View-ID>: <description>`
      - Phase-labelled: P1 (concern core), P2 (concern extended), P3 (supplementary)
      - Total view count should be focused (typically ≤ 12, vs unfocused 15+)

8. **Show results**

   ```
   ## Analysis Complete: <change-name>

   **Complexity**: <clear/complicated/complex/chaotic>
   **Selected Concerns**: <concern names>
   **Activated Data Groups**: <top 3-5 groups with scores>
   **Focused Views**: <N views (P1+P2)>

   ### Phase 1 (Concern Core)
   - <view-id>: <brief description>
   ...

   ### Phase 2 (Concern Extended)
   - <view-id>: <brief description>
   ...

   ### Phase 3 (Supplementary)
   - <view-id>: <brief description>
   ...

   Planning artifacts created at: dm2-changes/<name>/
     - proposal.md
     - design.md
     - tasks.md

   Ready to implement? Run `/dm2:apply` to execute the plan and generate all views.
   Step-by-step: `/dm2:continue`. One-shot (skip planning): `/dm2:ff`.
   ```

**Concern Matching Algorithm Reference**

```
For each concern in concerns.yaml:

  # Group activation overlap (0.0 to 1.0)
  active = set of group_ids with activation_score > 0.0
  group_overlap = len(active ∩ concern.expected_groups) / len(concern.expected_groups)

  # Keyword match (0.0 to 1.0)
  desc_lower = set of normalized words from system description
  kw_lower = set of normalized words from concern.keywords
  kw_match = len(desc_lower ∩ kw_lower) / max(len(kw_lower), 1)

  # Weighted score
  score = 0.6 * group_overlap + 0.4 * kw_match

Present concerns with score ≥ 0.10 to the Human (up to 5 options).
```

**Edge Cases**

- **No groups activated (all scores 0.0)**: Keyword match alone determines ranking. Present top 3 concerns, flag that activation is weak.
- **Single concern dominates (score > 2× second place)**: Highlight it as strongly recommended but still let Human choose.
- **All concerns below 0.10**: Present top 3 anyway with a note that confidence is low, and offer "全部视图" as the recommended option.
- **Human selects no concerns**: Treat the same as "全部视图" — use all candidate_views.

**Guardrails**
- Use `python3 -m dm2.cli.main` for all CLI calls
- Do NOT store priority rankings inside CLI output — the AI Agent decides priority
- Cynefin, analyze, and concern list use existing CLI commands, not new backend code
- Planning artifacts go into the change directory (dm2-changes/<name>/)
- Tasks must be ordered by view dependency (use ArtifactGraph topological order)
- Concern matching algorithm runs in the AI Agent (this SKILL), NOT in Python code
- The focused view set from selected concerns MUST be a subset/superset of candidate_views; use union logic
- If the user provides additional context during the conversation (compliance requirements, stakeholder roles, etc.), incorporate it into the artifacts and keyword matching
- Always let the Human make the final concern selection — never auto-select
- Focused view set target: ≤ 12 views (vs unfocused 15+)
""",
)

PROPOSE_COMMAND = CommandTemplate(
    name="DM2: Propose",
    description="Run full DoDAF architecture analysis and generate planning artifacts",
    tags=["dm2", "DoDAF", "architecture", "analysis", "propose"],
    body="""Run a complete DoDAF architecture analysis, including Cynefin complexity assessment, DM2 data group activation analysis, and view recommendation — then generate planning artifacts (proposal.md, design.md, tasks.md).

**Input**: `/dm2:propose <system-description>` — a description of the system to analyze.

This runs the full analysis pipeline and creates planning documents in the change directory. Run `/dm2:continue` or `/dm2:ff` afterwards to generate views.
""",
)


def get_workflow_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="propose",
        skill_dir="dm2-propose-workflow",
        command_file="propose.md",
        skill=PROPOSE_SKILL,
        command=PROPOSE_COMMAND,
    )
