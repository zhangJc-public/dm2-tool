"""View Manager — DoDAF view lifecycle state management."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml


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


class ViewManager:
    """Manages lifecycle state of DoDAF views within a dm2 project."""

    def __init__(self, project_root: Optional[Path] = None):
        self._root = project_root or Path.cwd()
        self._state: dict = {}
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

    def update_status(self, view_id: str, status: ViewStatus) -> None:
        if view_id not in self._state:
            self._state[view_id] = {}
        self._state[view_id]["status"] = status.value
        if status == ViewStatus.GENERATED:
            self._state[view_id]["generated_at"] = datetime.now().isoformat()
        elif status == ViewStatus.VERIFIED:
            self._state[view_id]["verified_at"] = datetime.now().isoformat()
        self._save()

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
        self._save()

    def list_views(self, status_filter: Optional[ViewStatus] = None) -> list[ViewInfo]:
        result = []
        for vid, data in self._state.items():
            if isinstance(data, dict):
                s = ViewStatus(data.get("status", "pending"))
                if status_filter and s != status_filter:
                    continue
                result.append(ViewInfo(
                    id=vid,
                    status=s,
                    generated_at=data.get("generated_at", ""),
                    verified_at=data.get("verified_at", ""),
                    output_path=data.get("output_path", ""),
                    change_name=data.get("change", ""),
                ))
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
        return ViewInfo(
            id=view_id,
            status=ViewStatus(data.get("status", "pending")),
            generated_at=data.get("generated_at", ""),
            verified_at=data.get("verified_at", ""),
            output_path=data.get("output_path", ""),
            change_name=data.get("change", ""),
        )
