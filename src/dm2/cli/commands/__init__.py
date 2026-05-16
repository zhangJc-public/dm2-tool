"""CLI command modules — one file per functional area."""

from dm2.cli.commands.knowledge import register_knowledge_commands
from dm2.cli.commands.change import register_change_commands

__all__ = ["register_knowledge_commands", "register_change_commands"]
