"""Tool adapter abstraction for mapping dm2 workflows to AI tool filesystems."""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from dm2.core.templates import CommandTemplate, SkillTemplate


class ToolAdapter(ABC):
    """Protocol for tool-specific skill/command generation.

    Each AI tool (Claude Code, DeepSeek Harness, etc.) implements this adapter
    to define where files go and how frontmatter is formatted.
    """

    @property
    @abstractmethod
    def tool_id(self) -> str:
        """Tool identifier, e.g. 'claude', 'dsh'."""

    def get_skills_dir(self) -> str:
        """Relative path to skills directory. Defaults to the Claude layout."""
        return ".claude/skills"

    def get_commands_dir(self) -> Optional[str]:
        """Relative path to commands directory, or None when unsupported.

        DSH has no project-level slash-command directory; adapters that only
        ship skills return None together with ``supports_commands = False``.
        """
        return ".claude/commands/dm2"

    @property
    def supports_commands(self) -> bool:
        """Whether this adapter emits slash-command files."""
        return True

    def render_skill_body(self, text: str) -> str:
        """Render raw skill instructions for the target tool.

        Adapters override this to rewrite tool-specific references (slash
        command syntax, tool names). Must be a pure function; the Claude
        adapter renders identity so raw template text stays byte-stable.
        """
        return text

    @abstractmethod
    def format_skill_frontmatter(self, template: SkillTemplate, version: str) -> str:
        """Render YAML frontmatter for a SKILL.md file."""

    @abstractmethod
    def format_command_frontmatter(self, template: CommandTemplate) -> str:
        """Render YAML frontmatter for a command .md file."""


def get_adapter(tool_id: str) -> ToolAdapter:
    """Return the adapter registered for a tool id.

    Raises ValueError for an unknown tool id. Imports live inside the
    function to avoid a circular import between the adapter modules and
    this package.
    """
    adapters = _build_adapter_registry()
    adapter = adapters.get(tool_id)
    if adapter is None:
        raise ValueError(f"未知 AI 工具: {tool_id}，可选: {', '.join(sorted(adapters))}")
    return adapter


def _build_adapter_registry() -> Dict[str, ToolAdapter]:
    """Instantiate every shipped adapter keyed by ``tool_id``."""
    from dm2.core.adapters.claude import ClaudeCodeAdapter
    from dm2.core.adapters.dsh import DshAdapter

    instances: Dict[str, ToolAdapter] = {}
    for adapter in (ClaudeCodeAdapter(), DshAdapter()):
        instances[adapter.tool_id] = adapter
    return instances
