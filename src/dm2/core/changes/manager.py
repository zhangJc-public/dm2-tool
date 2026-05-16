"""Change Manager — architecture change lifecycle management."""

import os
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml


class ChangeStatus(str, Enum):
    OPEN = "open"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    VERIFYING = "verifying"
    COMPLETE = "complete"


@dataclass
class ChangeInfo:
    name: str
    status: ChangeStatus
    created_at: str
    modified_at: str
    artifact_count: int = 0
    artifact_done: int = 0


class ChangeManager:
    """Manages lifecycle of architecture changes."""

    def __init__(self, project_root: Optional[Path] = None):
        self._root = project_root or Path.cwd()

    def _changes_dir(self) -> Path:
        return self._root / "dm2-changes"

    def _archive_dir(self) -> Path:
        return self._root / "dm2-archive"

    def create(self, name: str) -> Path:
        change_dir = self._changes_dir() / name
        change_dir.mkdir(parents=True, exist_ok=True)

        # Create standard subdirectories per spec
        for sub in ["analysis", "views", "delta-specs"]:
            (change_dir / sub).mkdir(parents=True, exist_ok=True)

        state = {
            "change": {
                "name": name,
                "status": ChangeStatus.OPEN.value,
                "created_at": datetime.now().isoformat(),
            },
            "artifacts": {},
        }

        with open(change_dir / ".change.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(state, f, allow_unicode=True, default_flow_style=False)

        return change_dir

    def load_state(self, name: str) -> Optional[dict]:
        state_file = self._changes_dir() / name / ".change.yaml"
        if not state_file.exists():
            return None
        with open(state_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def save_state(self, name: str, state: dict) -> None:
        state_file = self._changes_dir() / name / ".change.yaml"
        with open(state_file, 'w', encoding='utf-8') as f:
            yaml.dump(state, f, allow_unicode=True, default_flow_style=False)

    def update_status(self, name: str, status: ChangeStatus) -> None:
        state = self.load_state(name)
        if state:
            state["change"]["status"] = status.value
            state["change"]["modified_at"] = datetime.now().isoformat()
            self.save_state(name, state)

    def list_changes(self) -> list[ChangeInfo]:
        changes_dir = self._changes_dir()
        if not changes_dir.exists():
            return []

        result = []
        for d in sorted(changes_dir.iterdir()):
            if d.is_dir():
                state = self.load_state(d.name)
                if state:
                    ch = state["change"]
                    artifacts = state.get("artifacts", {})
                    done = sum(1 for a in artifacts.values()
                               if isinstance(a, dict) and a.get("status") == "done")
                    result.append(ChangeInfo(
                        name=ch["name"],
                        status=ChangeStatus(ch.get("status", "open")),
                        created_at=ch.get("created_at", ""),
                        modified_at=ch.get("modified_at", ""),
                        artifact_count=len(artifacts),
                        artifact_done=done,
                    ))
                else:
                    result.append(ChangeInfo(
                        name=d.name,
                        status=ChangeStatus.OPEN,
                        created_at="",
                        modified_at="",
                    ))
        return result

    def archive(self, name: str) -> Path:
        src = self._changes_dir() / name
        dst = self._archive_dir() / f"{date.today()}-{name}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return dst

    def is_change_dir(self) -> bool:
        return (self._changes_dir()).exists()
