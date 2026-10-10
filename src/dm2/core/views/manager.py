"""View Manager — DoDAF view lifecycle state management.

The lifecycle owns the ``verified`` gate: a view may only reach that state when
its pedigree carries the core fields (``author``, ``creation_date``, ``source``),
unless the project switches tracing off or an operator forces the transition.
Pedigree records themselves are read/written through :mod:`dm2.core.pedigree`;
this module never owns their content.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml

from dm2.core.pedigree.completeness import (
    ABSENT,
    missing_core_fields,
    trace_enabled,
)
from dm2.core.pedigree.completeness import status as pedigree_status
from dm2.core.pedigree.store import PedigreeStore


class ViewStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    GENERATED = "generated"
    VERIFIED = "verified"


@dataclass
class ViewInfo:
    id: str
    status: ViewStatus
    generated_at: str = ""
    verified_at: str = ""
    output_path: str = ""
    change_name: str = ""
    pedigree_status: str = ABSENT
    pedigree_missing: list[str] = field(default_factory=list)


@dataclass
class VerifyDecision:
    """Outcome of a pedigree-gated attempt to reach ``verified``."""

    allowed: bool
    missing: list[str] = field(default_factory=list)
    forced: bool = False


class ViewManager:
    """Manages lifecycle state of DoDAF views within a dm2 project."""

    def __init__(self, project_root: Optional[Path] = None,
                 pedigree_store: Optional[PedigreeStore] = None):
        self._root = project_root or Path.cwd()
        self._state: dict = {}
        self._pedigree_store = pedigree_store
        self._load()

    def _state_file(self) -> Path:
        return self._root / ".dm2" / "view-state.yaml"

    def _load(self) -> None:
        sf = self._state_file()
        if sf.exists():
            with open(sf, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self._state = data.get("views", {}) if data else {}
        else:
            self._state = {}

    def _save(self) -> None:
        sf = self._state_file()
        sf.parent.mkdir(parents=True, exist_ok=True)
        with open(sf, 'w', encoding='utf-8') as f:
            yaml.dump({"views": self._state}, f, allow_unicode=True, default_flow_style=False)

    # ── pedigree state ───────────────────────────────────────────────────

    @property
    def pedigree_store(self) -> PedigreeStore:
        if self._pedigree_store is None:
            self._pedigree_store = PedigreeStore(self._root)
        return self._pedigree_store

    def _pedigree_state(self, view_id: str) -> tuple[str, list[str]]:
        """Freshly computed ``(pedigree_status, missing fields)`` for one view."""
        record = self.pedigree_store.load(view_id)
        return pedigree_status(record), missing_core_fields(record)

    def _persist_pedigree_state(self, view_id: str) -> None:
        state, missing = self._pedigree_state(view_id)
        entry = self._state.setdefault(view_id, {})
        entry["pedigree_status"] = state
        if missing:
            entry["pedigree_missing"] = missing
        else:
            entry.pop("pedigree_missing", None)

    # ── lifecycle transitions ────────────────────────────────────────────

    def update_status(self, view_id: str, status: ViewStatus) -> None:
        if view_id not in self._state:
            self._state[view_id] = {}
        self._state[view_id]["status"] = status.value
        if status == ViewStatus.GENERATED:
            self._state[view_id]["generated_at"] = datetime.now().isoformat()
        elif status == ViewStatus.VERIFIED:
            self._state[view_id]["verified_at"] = datetime.now().isoformat()
        self._persist_pedigree_state(view_id)
        self._save()

    def try_verify(self, view_id: str, *, force: bool = False) -> VerifyDecision:
        """Attempt the ``verified`` transition, gated on pedigree completeness.

        Facts observed here are appended to the pedigree when a record exists; a
        missing record cannot be annotated and is reported via ``missing``.

        Args:
            view_id: View to promote.
            force: Operator override (``dm2 validate --force-pedigree``).
        """
        record = self.pedigree_store.load(view_id)
        missing = missing_core_fields(record)

        if not trace_enabled(self._root):
            self.update_status(view_id, ViewStatus.VERIFIED)
            return VerifyDecision(allowed=True)

        if missing and not force:
            if record is not None:
                record.append_modification("cli", "verified blocked: pedigree incomplete")
                self.pedigree_store.save(record)
            return VerifyDecision(allowed=False, missing=missing)

        if force and missing:
            if record is not None:
                record.append_modification("operator", "verified via --force-pedigree override")
                self.pedigree_store.save(record)
            self.update_status(view_id, ViewStatus.VERIFIED)
            return VerifyDecision(allowed=True, missing=missing, forced=True)

        if record is not None:
            record.append_modification("cli", "verified: validation passed")
            self.pedigree_store.save(record)
        self.update_status(view_id, ViewStatus.VERIFIED)
        return VerifyDecision(allowed=True)

    def register_view(self, view_id: str, output_path: str = "",
                       change_name: str = "") -> None:
        if view_id not in self._state:
            self._state[view_id] = {"status": ViewStatus.GENERATED.value,
                                     "generated_at": datetime.now().isoformat()}
        else:
            self._state[view_id]["status"] = ViewStatus.GENERATED.value
            self._state[view_id]["generated_at"] = datetime.now().isoformat()
        self._state[view_id]["output_path"] = output_path
        self._state[view_id]["change"] = change_name
        self._persist_pedigree_state(view_id)
        self._save()

    def sync_pedigree_state(self) -> dict[str, str]:
        """Persist the freshly computed pedigree status for every known view.

        ``dm2 trace migrate`` uses this to stamp ``absent``/``incomplete``/
        ``complete`` onto a legacy ``view-state.yaml`` without inventing records.
        """
        statuses = {}
        for view_id in self._state:
            self._persist_pedigree_state(view_id)
            statuses[view_id] = self._state[view_id].get("pedigree_status", ABSENT)
        self._save()
        return statuses

    # ── queries ──────────────────────────────────────────────────────────

    def _view_info(self, view_id: str, data: dict) -> ViewInfo:
        state, missing = self._pedigree_state(view_id)
        return ViewInfo(
            id=view_id,
            status=ViewStatus(data.get("status", "pending")),
            generated_at=data.get("generated_at", ""),
            verified_at=data.get("verified_at", ""),
            output_path=data.get("output_path", ""),
            change_name=data.get("change", ""),
            pedigree_status=state,
            pedigree_missing=missing,
        )

    def list_views(self, status_filter: Optional[ViewStatus] = None,
                   pedigree_status_filter: Optional[str] = None) -> list[ViewInfo]:
        result = []
        for vid, data in self._state.items():
            if not isinstance(data, dict):
                continue
            info = self._view_info(vid, data)
            if status_filter and info.status != status_filter:
                continue
            if pedigree_status_filter and info.pedigree_status != pedigree_status_filter:
                continue
            result.append(info)
        return result

    def get_progress(self) -> dict:
        counts = {s.value: 0 for s in ViewStatus}
        for data in self._state.values():
            if isinstance(data, dict):
                s = data.get("status", "pending")
                counts[s] = counts.get(s, 0) + 1
        return counts

    def get_view(self, view_id: str) -> Optional[ViewInfo]:
        data = self._state.get(view_id)
        if not data or not isinstance(data, dict):
            return None
        return self._view_info(view_id, data)
