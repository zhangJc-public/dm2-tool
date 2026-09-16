"""Generate AI tool skill and command files from workflow templates."""

from pathlib import Path

from dm2.core.adapters import ToolAdapter
from dm2.core.templates import WORKFLOWS


def generate_agent_config(
    target_dir: Path,
    version: str,
    adapter: ToolAdapter,
) -> int:
    """Generate skill (and optionally command) files for all registered workflows.

    Args:
        target_dir: Project root directory to generate files into.
        version: dm2-tool version string for `generatedBy` metadata.
        adapter: Tool-specific adapter (e.g. ClaudeCodeAdapter, DshAdapter).

    Returns:
        Number of files generated.
    """
    skills_dir = target_dir / adapter.get_skills_dir()
    skills_dir.mkdir(parents=True, exist_ok=True)

    commands_dir: Path | None = None
    if adapter.supports_commands and adapter.get_commands_dir() is not None:
        commands_dir = target_dir / adapter.get_commands_dir()
        commands_dir.mkdir(parents=True, exist_ok=True)

    count = 0

    for wf in WORKFLOWS:
        # Generate SKILL.md
        skill_dir = skills_dir / wf.skill_dir
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_body = adapter.render_skill_body(wf.skill.instructions)
        skill_content = (
            adapter.format_skill_frontmatter(wf.skill, version)
            + "\n"
            + skill_body
        )
        skill_file.write_text(skill_content, encoding="utf-8")
        count += 1

        # Adapters without a command convention (e.g. DSH) skip command files.
        if commands_dir is None:
            continue

        # Generate command .md
        cmd_file = commands_dir / wf.command_file
        cmd_body = wf.command.body
        if not cmd_body.strip():
            cmd_body = f"Invoke skill `{wf.skill.name}`."
        elif "Skill tool" not in cmd_body and "Skill:" not in cmd_body:
            cmd_body += f"\n\nWhen invoked, use the Skill tool with name `{wf.skill.name}` to load full instructions."
        cmd_content = (
            adapter.format_command_frontmatter(wf.command)
            + "\n"
            + cmd_body
        )
        cmd_file.write_text(cmd_content, encoding="utf-8")
        count += 1

    return count
