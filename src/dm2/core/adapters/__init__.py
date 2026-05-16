"""Tool adapter abstraction for mapping dm2 workflows to AI tool filesystems."""

from abc import ABC, abstractmethod
from dm2.core.templates import SkillTemplate, CommandTemplate


class ToolAdapter(ABC):
    """Protocol for tool-specific skill/command generation.

    Each AI tool (Claude Code, Cursor, etc.) implements this adapter
    to define where files go and how frontmatter is formatted.
    """

    @property
    @abstractmethod
    def tool_id(self) -> str:
        """Tool identifier, e.g. 'claude', 'cursor'."""

    @abstractmethod
    def get_skills_dir(self) -> str:
        """Relative path to skills directory, e.g. '.claude/skills/'."""

    @abstractmethod
    def get_commands_dir(self) -> str:
        """Relative path to commands directory, e.g. '.claude/commands/dm2/'."""

    @abstractmethod
    def format_skill_frontmatter(self, template: SkillTemplate, version: str) -> str:
        """Render YAML frontmatter for a SKILL.md file."""

    @abstractmethod
    def format_command_frontmatter(self, template: CommandTemplate) -> str:
        """Render YAML frontmatter for a command .md file."""
