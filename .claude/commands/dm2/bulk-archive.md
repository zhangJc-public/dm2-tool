---
name: "DM2: Bulk Archive"
description: Archive multiple completed dm2 architecture changes at once
category: Architecture
tags: [dm2, DoDAF, archive, batch]
---

Archive multiple completed dm2 architecture changes in a single operation.

**Input**: `/dm2:bulk-archive` — no arguments needed. The AI Agent shows you all active changes, you pick which to archive.

Handles view conflict detection, batch validation, and single-confirmation archive. Use after completing multiple parallel analyses.


When invoked, use the Skill tool with name `dm2-bulk-archive-workflow` to load full instructions.