## Skill Template Generation Spec

### Purpose
Define the workflow template system — each dm2 workflow (propose, continue, new, ff, verify, onboard, bulk-archive) is defined as a Python `WorkflowTemplate` dataclass containing both skill and command content, replacing file-copy distribution.

### Requirements

### Requirement: Workflow templates as Python dataclasses
dm2 SHALL define each workflow (propose, continue, new, ff, verify, onboard, bulk-archive, explore, apply, archive) as a `WorkflowTemplate` dataclass in `src/dm2/core/templates/workflows/`, containing both `SkillTemplate` (SKILL.md content) and `CommandTemplate` (slash command .md content).

#### Scenario: Each workflow has both skill and command
- **WHEN** a `WorkflowTemplate` is instantiated for any workflow
- **THEN** it SHALL contain a `SkillTemplate` with `name`, `description`, and `instructions` fields
- **AND** it SHALL contain a `CommandTemplate` with `name`, `description`, `category`, `tags`, and `body` fields
- **AND** the `instructions` field SHALL be the complete SKILL.md body (without frontmatter, which is generated separately)

#### Scenario: Skill content matches current SKILL.md
- **WHEN** the template-generated SKILL.md is compared with the current `.claude/skills/dm2-*-workflow/SKILL.md`
- **THEN** the generated file SHALL have functionally identical instructions content to the current file
- **AND** the generated file SHALL include `generatedBy: "dm2-tool/<version>"` in frontmatter metadata

#### Scenario: All 10 workflows are registered
- **WHEN** `WORKFLOWS` is imported from `dm2.core.templates`
- **THEN** it SHALL contain exactly 10 entries: propose, continue, new, ff, verify, onboard, bulk-archive, explore, apply, archive
- **AND** each entry SHALL be a `WorkflowTemplate` with both skill and command defined

### Requirement: Templates are versioned
Generated SKILL.md files SHALL include a `generatedBy` metadata field containing the dm2-tool version, enabling consumers to detect stale generated content.

#### Scenario: Generated skill has version metadata
- **WHEN** a SKILL.md is generated from a template via any adapter
- **THEN** the YAML frontmatter SHALL include `metadata.generatedBy` set to `"dm2-tool/<version>"`
- **AND** `<version>` SHALL match `dm2.__version__`
