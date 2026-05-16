---
name: "DM2: Continue"
description: Continue an in-progress dm2 architecture analysis
category: Architecture
tags: [dm2, DoDAF, architecture, continue]
---

Continue working on an in-progress dm2 architecture analysis or view generation session.

**Input**: `/dm2:continue [change-name]` — optionally specify which change to continue. If omitted, the AI Agent prompts for selection.

This picks up where you left off — continuing pipeline steps or generating the next pending view. Run after `/dm2:propose` or `/dm2:new` to start generating views.


When invoked, use the Skill tool with name `dm2-continue-workflow` to load full instructions.