---
name: "DM2: Fast-Forward"
description: Generate all recommended DoDAF views in one shot
category: Architecture
tags: [dm2, DoDAF, architecture, generate, batch]
---

Fast-forward through dm2 analysis and view generation — everything in one shot.

**Input**: `/dm2:ff <system-description>` — what system to model and generate views for.

This runs Cynefin analysis, 6W analysis, and generates ALL recommended DoDAF views in dependency order. No step-by-step — just results. Run `/dm2:verify` afterwards to check consistency.


When invoked, use the Skill tool with name `dm2-ff-workflow` to load full instructions.