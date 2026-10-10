---
name: dm2-new-workflow
description: "Start a new DoDAF architecture analysis using dm2. Use when the user wants to model a system architecture with DM2."
user-invocable: true
metadata:
  author: "dm2"
  version: "0.1.0"
  generatedBy: "dm2-tool/0.1.0"
---

Start a new dm2 architecture analysis session.

**Input**: The argument after the `dm2-new-workflow` skill is a system description OR a kebab-case name for the analysis.

**Steps**

1. **If no clear input provided, ask what they want to model**

   Use the **ask_user_question tool** (open-ended, no preset options) to ask:
   > "What system do you want to model? Describe the system or problem you're working on."

   From their description, derive a kebab-case name (e.g., "logistics tracking system" → `logistics-tracking`).

   **IMPORTANT**: Do NOT proceed without understanding what the user wants to model.

2. **Create the change directory**
   ```bash
   dm2 change new "<name>"
   ```
   This creates a change at `dm2-changes/<name>/`.

3. **Show change info and prompt for next step**

   ```
   ## Architecture Analysis: <name>

   Change created at: dm2-changes/<name>/

   Ready for full analysis? Run the `dm2-propose-workflow` skill or describe the system you want to analyze.
   ```

**Guardrails**
- Do NOT run cynefin, 6W analysis, or view generation — that belongs to the `dm2-propose-workflow` skill
- Use `dm2` for all CLI calls (dm2 may not be in PATH)
