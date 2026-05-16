---
name: "DM2: Verify"
description: Verify generated DoDAF views for consistency and completeness
category: Architecture
tags: [dm2, DoDAF, architecture, verify, validate]
---

Verify generated DoDAF views for completeness, correctness, and cross-view coherence.

**Input**: `/dm2:verify [change-name]` — optionally specify which change to verify. If omitted, the AI Agent prompts for selection.

Checks view coverage against recommendations, DM2 rule compliance, and cross-view consistency. Produces a verification report with CRITICAL/WARNING/SUGGESTION issues. Run before `/dm2:archive`.


When invoked, use the Skill tool with name `dm2-verify-workflow` to load full instructions.