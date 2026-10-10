"""Pedigree completeness and the ``trace.enabled`` escape hatch.

Shared by the view lifecycle (``verified`` gating), ``dm2 view list`` and the
audit commands, so all three agree on what "incomplete" means.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from dm2.core.pedigree.model import CORE_FIELDS, Pedigree

#: ``pedigree_status`` values persisted in ``.dm2/view-state.yaml``.
COMPLETE = "complete"
INCOMPLETE = "incomplete"
ABSENT = "absent"


def missing_core_fields(pedigree: Optional[Pedigree]) -> list[str]:
    """Missing core fields; every core field is missing when there is no record."""
    if pedigree is None:
        return list(CORE_FIELDS)
    return pedigree.missing_core_fields()


def status(pedigree: Optional[Pedigree]) -> str:
    """Classify a record (or its absence) into a ``pedigree_status`` value."""
    if pedigree is None:
        return ABSENT
    return COMPLETE if not pedigree.missing_core_fields() else INCOMPLETE


def trace_enabled(project_root: Optional[Path] = None) -> bool:
    """Whether pedigree writes and ``verified`` gating are active.

    Convention over configuration: on by default, with ``trace.enabled: false``
    in ``.dm2/config.yaml`` as the documented escape hatch for legacy projects.
    """
    from dm2.config.manager import get

    return bool(get("trace.enabled", True, project_root))
