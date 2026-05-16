"""Claude Code adapter — maps dm2 workflows to .claude/skills/ and .claude/commands/dm2/."""

from dm2.core.adapters import ToolAdapter
from dm2.core.templates import SkillTemplate, CommandTemplate


class ClaudeCodeAdapter(ToolAdapter):
    """Adapter for Claude Code's skills and slash commands convention."""

    @property
    def tool_id(self) -> str:
        return "claude"

    def get_skills_dir(self) -> str:
        return ".claude/skills"

    def get_commands_dir(self) -> str:
        return ".claude/commands/dm2"

    def format_skill_frontmatter(self, template: SkillTemplate, version: str) -> str:
        return (
            "---\n"
            f"name: {template.name}\n"
            f"description: {template.description}\n"
            f"license: {template.license}\n"
            f"compatibility: {template.compatibility}\n"
            "user-invocable: false\n"
            "metadata:\n"
            f'  author: "dm2"\n'
            f'  version: "{version}"\n'
            f'  generatedBy: "dm2-tool/{version}"\n'
            "---\n"
        )

    def format_command_frontmatter(self, template: CommandTemplate) -> str:
        tags_str = ", ".join(template.tags)
        return (
            "---\n"
            f'name: "{template.name}"\n'
            f"description: {template.description}\n"
            f"category: {template.category}\n"
            f"tags: [{tags_str}]\n"
            "---\n"
        )
