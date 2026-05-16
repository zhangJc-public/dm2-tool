"""Onboard workflow — guided walkthrough of the complete dm2 DoDAF architecture modeling cycle."""

from dm2.core.templates import WorkflowTemplate, SkillTemplate, CommandTemplate

ONBOARD_SKILL = SkillTemplate(
    name="dm2-onboard-workflow",
    description="Guided onboarding for dm2 — walk through a complete DoDAF architecture modeling cycle with narration and real system description.",
    instructions="""Guide the user through their first complete dm2 architecture modeling cycle. This is a teaching experience — you'll do real DoDAF modeling work while explaining each step.

---

## Preflight

Before starting, check if dm2 is installed:

```bash
python3 -m dm2.cli.main version 2>&1 || echo "CLI_NOT_INSTALLED"
```

**If CLI not installed:**
> dm2-tool is not installed. Install it with `pip install -e .` from the dm2-tool directory, then come back to `/dm2:onboard`.

Stop here if not installed.

---

## Phase 1: Welcome

Display:

```
## Welcome to dm2-tool!

I'll walk you through a complete DoDAF architecture modeling cycle — from system description to generated views — using dm2.

**What we'll do:**
1. Describe a system you want to model
2. Assess complexity with Cynefin
3. Run 6W analysis to find the right views
4. Generate a DoDAF view
5. Verify consistency
6. Archive the analysis

**Time:** ~10-15 minutes

Let's start with your system description.
```

---

## Phase 2: System Description

Ask the user to describe the system they want to model:

```
## What System Are You Modeling?

Describe your system in a few sentences. For example:

> "A logistics tracking platform that monitors shipments across multiple warehouses and transportation modes, with real-time alerts for delays."

Or pick something simple for learning:
- A library management system
- An online ordering platform
- A healthcare appointment system

What system would you like to model?
```

**PAUSE** — Wait for user's description.

---

## Phase 3: Cynefin Assessment

**EXPLAIN:**
```
## Cynefin Complexity Assessment

Cynefin helps us understand how complex your system is. This determines which DoDAF views are most appropriate.

- **简单（Clear）**: Simple, well-understood systems → fewer views needed
- **繁杂（Complicated）**: Requires expert analysis → moderate view count
- **复杂（Complex）**: Emergent behavior, many interdependencies → comprehensive view set
- **混沌（Chaotic）**: Highly unstable → start with high-level views first
```

**DO:**
```bash
python3 -m dm2.cli.main cynefin "<description>" --json
```

**SHOW:**
Parse and display the result:
```
**Domain:** <domain>
**Confidence:** <confidence>%
**Recommended Views:** <recommended_view_count>

**Reasoning:** <brief explanation>

This tells us how to approach the modeling.
```

**PAUSE** — Wait for acknowledgment.

---

## Phase 4: 6W Analysis

**EXPLAIN:**
```
## 6W Analysis

6W analysis breaks down your system across six dimensions:
- **What** — Activities and functions
- **Who** — Performers and organizations
- **Where** — Locations and nodes
- **When** — Timing and events
- **Why** — Rules and constraints
- **hoW** — Resources and flows

Each dimension maps to specific DoDAF views.
```

**DO:**
```bash
python3 -m dm2.cli.main analyze "<description>" --json
```

**SHOW:**
Parse and present:
- Primary 6W dimensions
- Secondary dimensions
- Data groups involved
- Recommended views

```
**Primary Focus:** <dimensions>
**Secondary:** <dimensions>

**Recommended Views:**
| View | Type | Why |
|------|------|-----|
| OV-1 | Overview | High-level concept |
| OV-2 | Resource Flow | Shows data flows |
...
```

**PAUSE** — Wait for acknowledgment.

---

## Phase 5: Generate a View

**EXPLAIN:**
```
## View Generation

Let's generate one view to see how it works. dm2 provides structured instructions for each view — context (what DM2 concepts are relevant), rules (what constraints to follow), and a template (how to structure the output).

Let's start with <first recommended view>.
```

**DO:**
```bash
python3 -m dm2.cli.main instructions <view_id> --json
```

Explain what the returned template and rules mean, then generate the view content.

Write the content to the output path.

**SHOW:**
```
## Generated: <view_id>

**Output:** `dm2-changes/<name>/views/<view_id>.md`

[Show a brief excerpt of the generated content]

Each DoDAF view follows a specific structure. The template ensures compliance with DM2 standards.
```

**PAUSE** — Wait for acknowledgment.

---

## Phase 6: Verify and Recap

**EXPLAIN:**
```
## Verification

dm2 can check your views for consistency — ensuring activities have performers, resources have flows, and views don't contradict each other.
```

**DO:**
If `dm2 validate` is available:
```bash
python3 -m dm2.cli.main validate <view_id> --json
```

Otherwise, explain what consistency checks would look like.

---

## Phase 7: Recap & Next Steps

```
## Congratulations!

You just completed a dm2 architecture modeling cycle:

1. **System Description** — What you're modeling
2. **Cynefin** — How complex is it?
3. **6W Analysis** — What dimensions matter?
4. **View Generation** — Create structured DoDAF views
5. **Verification** — Check consistency

---

## Command Reference

**Core workflow:**

 | Command            | What it does                               |
 |--------------------|--------------------------------------------|
 | `/dm2:new`       | Start a new architecture analysis          |
 | `/dm2:continue`  | Continue an in-progress analysis           |
 | `/dm2:ff`        | Fast-forward: generate all views at once   |
 | `/dm2:verify`    | Verify view completeness and consistency   |
 | `/dm2:archive`   | Archive a completed analysis               |

**Knowledge queries:**

 | Command                       | What it does                    |
 |-------------------------------|---------------------------------|
 | `/dm2:knowledge search <q>` | Search DM2 terms                |
 | `/dm2:knowledge views`      | List all 52 DoDAF views         |
 | `/dm2:knowledge view <id>`  | View metadata and dependencies  |

---

## What's Next?

Try `/dm2:new` on a system you actually need to model. You've got the rhythm now!
```

---

## Guardrails

- **Follow the EXPLAIN → DO → SHOW → PAUSE pattern** at key transitions
- **Keep narration light** — teach without lecturing
- **Don't skip phases** even if the system is simple — the goal is teaching
- **Pause for acknowledgment** at marked points
- **Handle exits gracefully** — never pressure the user to continue
- **Use real system descriptions** — don't simulate or use fake examples
- **Use `python3 -m dm2.cli.main` for all CLI calls**
- **Always pass `--json` for structured output**
""",
)

ONBOARD_COMMAND = CommandTemplate(
    name="DM2: Onboard",
    description="Guided walkthrough of the complete dm2 DoDAF architecture modeling workflow",
    tags=["dm2", "DoDAF", "tutorial", "onboarding"],
    body="""Guided onboarding — walk through your first complete dm2 architecture modeling cycle with narration and real system description.

**Input**: `/dm2:onboard` — no arguments needed, the AI Agent guides you through each step interactively.

This is a teaching experience (~10-15 minutes). You'll do real DoDAF modeling work while the AI Agent explains each step: Cynefin assessment, 6W analysis, view generation, and verification.
""",
)


def get_workflow_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        workflow_id="onboard",
        skill_dir="dm2-onboard-workflow",
        command_file="onboard.md",
        skill=ONBOARD_SKILL,
        command=ONBOARD_COMMAND,
    )
