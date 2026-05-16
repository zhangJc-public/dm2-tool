## MODIFIED Requirements

### Requirement: One-shot artifact generation
The dm2-propose-workflow SHALL create all architecture artifacts (proposal.md, design.md, tasks.md) in a single pass from a user-provided system description, using DM2 data group activation detection for view recommendations (not 6W-only).

#### Scenario: User describes a system
- **WHEN** user runs `/dm2:propose` with a system description
- **THEN** the workflow SHALL create a new change via `dm2 change new`
- **AND** SHALL run `dm2 cynefin` and `dm2 analyze --json` with the description
- **AND** SHALL generate proposal.md, design.md, and tasks.md
- **AND** SHALL present the generated artifacts and prompt the user to run `/dm2:apply` as the recommended next step, with `/dm2:continue` and `/dm2:ff` listed as alternatives
