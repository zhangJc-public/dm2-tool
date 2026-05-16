---
name: "DM2: Propose"
description: Run full DoDAF architecture analysis and generate planning artifacts
category: Architecture
tags: [dm2, DoDAF, architecture, analysis, propose]
---

Run a complete DoDAF architecture analysis, including Cynefin complexity assessment, DM2 data group activation analysis, and view recommendation — then generate planning artifacts (proposal.md, design.md, tasks.md).

**Input**: `/dm2:propose <system-description>` — a description of the system to analyze.

This runs the full analysis pipeline and creates planning documents in the change directory. Run `/dm2:continue` or `/dm2:ff` afterwards to generate views.


When invoked, use the Skill tool with name `dm2-propose-workflow` to load full instructions.