---
name: "DM2: Apply"
description: Execute the implementation plan — read tasks.md and generate all DoDAF views in dependency order
category: Architecture
tags: [dm2, DoDAF, architecture, implement, generate]
---

Execute the implementation plan created by `/dm2:propose`. Reads tasks.md and generates all planned DoDAF views in dependency order.

**Input**: `/dm2:apply [change-name]` — optionally specify which change to implement. If omitted, the AI Agent prompts for selection.

This is the standard implementation step after `/dm2:propose`. It is task-driven (reads tasks.md), unlike `/dm2:continue` (step-by-step, analysis-driven) or `/dm2:ff` (batch, analysis-driven). Run `/dm2:verify` afterwards to check consistency, then `/dm2:archive` to complete.


When invoked, use the Skill tool with name `dm2-apply-workflow` to load full instructions.