"""Lifecycle events emitted by :class:`~dm2.core.views.manager.ViewManager`.

Kept in a leaf module so the manager and the pedigree recorder can both import
it without a cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ViewEvent:
    """One observed lifecycle fact about a view.

    ``actor``/``description`` let the emitter supply the outcome text (a
    verification result, an operator override); when ``description`` is empty the
    recorder writes a generic ``state: <old> → <new>`` entry.
    """

    view_id: str
    kind: str  # "register" | "status"
    status: str = ""
    previous_status: str = ""
    output_path: str = ""
    change_name: str = ""
    actor: str = "cli"
    description: str = ""
    at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
