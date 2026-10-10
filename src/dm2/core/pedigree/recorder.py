"""Fact-layer capture: turn observed lifecycle events into pedigree records.

The recorder writes only what dm2 can observe itself — registration, state
transitions, content edits. Agent-stated reasoning is never touched here; it is
persisted by ``dm2 trace record`` and always marked as unverified in reports.

Everything is a no-op when the project switches tracing off
(``trace.enabled: false``), which is the documented escape hatch.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

from dm2.core.pedigree.completeness import trace_enabled
from dm2.core.pedigree.model import Pedigree
from dm2.core.pedigree.store import PedigreeStore
from dm2.core.views.events import ViewEvent


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class PedigreeRecorder:
    """Appends fact-layer records for one dm2 project."""

    def __init__(self, store: PedigreeStore):
        self._store = store

    @property
    def store(self) -> PedigreeStore:
        return self._store

    # ── observer entry point ─────────────────────────────────────────────

    def handle_event(self, event: ViewEvent) -> None:
        """Record one lifecycle event (``ViewManager`` observer callback)."""
        if not trace_enabled(self._store.root):
            return
        record = self._store.load(event.view_id) or Pedigree.stub(
            event.view_id, change=event.change_name
        )
        if not record.creation_date:
            record.creation_date = event.at
        record.append_modification(event.actor, self._description(event), date=event.at)
        if event.output_path:
            # Registration (re)establishes the generation baseline; a human edit
            # afterwards is detected by detect_content_change().
            self._sync_hash(record, event.output_path, annotate=False)
        self._store.save(record)

    @staticmethod
    def _description(event: ViewEvent) -> str:
        if event.description:
            return event.description
        if event.kind == "register":
            return "view registered"
        if event.previous_status and event.previous_status != event.status:
            return f"state: {event.previous_status} → {event.status}"
        return f"state: {event.status}"

    # ── explicit fact recording ──────────────────────────────────────────

    def record_modification(
        self, view_id: str, actor: str, change_description: str
    ) -> Optional[Path]:
        """Append one observed modification; returns the written path or ``None``."""
        if not trace_enabled(self._store.root):
            return None
        record = self._store.load(view_id) or Pedigree.stub(view_id)
        record.append_modification(actor, change_description)
        return self._store.save(record)

    def detect_content_change(self, view_id: str, view_path: str) -> bool:
        """Log a human edit when a view file no longer matches the stored hash.

        Called on registration/validation. The first observation stores the
        baseline without logging anything; a later difference is recorded as
        ``human`` / ``content modified post-generation`` and rebaselines.
        """
        if not trace_enabled(self._store.root):
            return False
        record = self._store.load(view_id)
        if record is None:
            return False
        before = len(record.modification_history)
        if self._sync_hash(record, view_path, annotate=True):
            self._store.save(record)
        return len(record.modification_history) > before

    # ── helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _sync_hash(record: Pedigree, view_path: str, *, annotate: bool) -> bool:
        """Sync ``content_hash`` with the file; returns whether the record changed."""
        path = Path(view_path)
        if not path.is_file():
            return False
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not record.content_hash:
            record.content_hash = digest
            return True
        if record.content_hash == digest:
            return False
        if annotate:
            record.append_modification("human", "content modified post-generation")
        record.content_hash = digest
        return True
