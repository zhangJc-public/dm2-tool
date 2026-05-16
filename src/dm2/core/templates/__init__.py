"""Workflow template system — generates SKILL.md and slash command files for AI agents."""

from dataclasses import dataclass, field


@dataclass
class SkillTemplate:
    name: str
    description: str
    instructions: str
    license: str = "MIT"
    compatibility: str = "Requires dm2-tool CLI."


@dataclass
class CommandTemplate:
    name: str
    description: str
    category: str = "Architecture"
    tags: list[str] = field(default_factory=list)
    body: str = ""


@dataclass
class WorkflowTemplate:
    workflow_id: str
    skill_dir: str
    command_file: str
    skill: SkillTemplate
    command: CommandTemplate


WORKFLOWS: list[WorkflowTemplate] = []
"""All registered workflow templates. Populated by workflow modules in `workflows/`."""

# Eagerly import all workflow modules so WORKFLOWS is populated on first access.
from dm2.core.templates import workflows  # noqa: E402, F401 — side-effect import
