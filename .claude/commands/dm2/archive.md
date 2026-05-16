---
name: "DM2: Archive"
description: Archive a single completed dm2 architecture change
category: Architecture
tags: [dm2, DoDAF, archive, finalize]
---

Archive a completed dm2 architecture change — finalize it and move to the archive directory.

**Input**: `/dm2:archive [change-name]` — optionally specify which change to archive. If omitted, the AI Agent prompts for selection.

Checks artifact and task completion, optionally runs verification, confirms with you, then archives the change. For batch archiving of multiple changes, use `/dm2:bulk-archive`.


When invoked, use the Skill tool with name `dm2-archive-workflow` to load full instructions.