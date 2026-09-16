"""DeepSeek Harness adapter — maps dm2 workflows to .dsh/skills/SKILL.md files.

DSH discovers project skills under ``<project-root>/.dsh/skills/<dir>/SKILL.md``
(see packages/skill/skill-filesystem in the DSH checkout). It has no
project-level slash-command directory, so this adapter emits skills only and
rewrites Claude-specific references in the instruction bodies:

- `` `/dm2:<id>` ``        -> `` the `dm2-<id>-workflow` skill ``
- `` `/dm2:<id> <args>` `` -> `` the `dm2-<id>-workflow` skill (input: <args>) ``
- bare `` /dm2:<id> `` in prose/code fences -> `` the dm2-<id>-workflow skill ``
- `` `/dm2:knowledge ...` `` -> `` `dm2 knowledge ...` `` (CLI invocation)
- `` AskUserQuestion tool `` -> `` ask_user_question tool ``
- `` `python3 -m dm2.cli.main ...` `` -> `` `dm2 ...` ``
"""

import re
from typing import Dict

from dm2.core.adapters import ToolAdapter
from dm2.core.templates import WORKFLOWS, CommandTemplate, SkillTemplate

# Backticked slash reference with an optional single <angle-arg>:
#   `/dm2:propose` or `/dm2:propose <system-description>`
_BACKTICKED_SLASH = re.compile(r"`/dm2:([a-z-]+)(\s+<[^`>]+>)?`")

# Bare slash reference in prose / fenced example blocks. Matched after the
# backticked pass, so backtick-adjacent characters bound the token.
_BARE_SLASH = re.compile(r"(?<![\w`/])/dm2:([a-z-]+)(?!\w)")

# `/dm2:knowledge search <q>` -> `dm2 knowledge search <q>` (CLI command form)
_KNOWLEDGE = re.compile(r"`/dm2:knowledge\b")

_ASK_USER = re.compile(r"AskUserQuestion")
_MODULE_INVOCATION = re.compile(r"python3 -m dm2\.cli\.main\b")


def _yaml_quote(value: str) -> str:
    """Render a value as a YAML double-quoted scalar (DSH parses YAML)."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


class DshAdapter(ToolAdapter):
    """Adapter for DeepSeek Harness project skills (``.dsh/skills``)."""

    def __init__(self) -> None:
        # workflow_id -> skill directory, built from the registered templates
        # so new workflows need no change here.
        self._skill_names: Dict[str, str] = {
            wf.workflow_id: wf.skill_dir for wf in WORKFLOWS
        }

    @property
    def tool_id(self) -> str:
        return "dsh"

    def get_skills_dir(self) -> str:
        return ".dsh/skills"

    def get_commands_dir(self) -> None:
        return None

    @property
    def supports_commands(self) -> bool:
        return False

    def format_skill_frontmatter(self, template: SkillTemplate, version: str) -> str:
        # Every dm2 workflow was a user-facing slash command under Claude; DSH
        # has no command files, so skills stay user-invocable to preserve the
        # explicit entry point. Model invocation stays enabled by default.
        # Descriptions may reference slash commands (e.g. apply/archive);
        # rewrite them with the same mapping used for instruction bodies.
        description = self.render_skill_body(template.description)
        return (
            "---\n"
            f"name: {template.name}\n"
            f"description: {_yaml_quote(description)}\n"
            "user-invocable: true\n"
            "metadata:\n"
            '  author: "dm2"\n'
            f'  version: "{version}"\n'
            f'  generatedBy: "dm2-tool/{version}"\n'
            "---\n"
        )

    def format_command_frontmatter(self, template: CommandTemplate) -> str:
        # Dead path: the generator skips command files when supports_commands
        # is False. Implemented to satisfy the ToolAdapter contract.
        raise NotImplementedError("DSH adapter does not emit command files")

    def render_skill_body(self, text: str) -> str:
        # 1. Pseudo-command `/dm2:knowledge ...` -> the real CLI invocation.
        text = _KNOWLEDGE.sub("`dm2 knowledge", text)
        # 2. Module invocation -> installed entry point.
        text = _MODULE_INVOCATION.sub("dm2", text)
        # 3. Claude tool name -> DSH tool name.
        text = _ASK_USER.sub("ask_user_question", text)
        # 4. Backticked workflow references (may carry an <angle-arg>).
        text = _BACKTICKED_SLASH.sub(self._replace_backticked, text)
        # 5. Bare workflow references in prose / fenced blocks.
        text = _BARE_SLASH.sub(self._replace_bare, text)
        return text

    def _replace_backticked(self, match: re.Match) -> str:
        workflow_id = match.group(1)
        args = match.group(2)
        skill_name = self._skill_names.get(workflow_id)
        if skill_name is None:
            return match.group(0)
        rendered = f"the `{skill_name}` skill"
        if args:
            rendered += f" (input: {args.strip()})"
        return rendered

    def _replace_bare(self, match: re.Match) -> str:
        workflow_id = match.group(1)
        skill_name = self._skill_names.get(workflow_id)
        if skill_name is None:
            return match.group(0)
        return f"the {skill_name} skill"
