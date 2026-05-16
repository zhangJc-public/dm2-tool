"""Artifact Graph — DoDAF view dependency management."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml


class ArtifactStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclass
class ArtifactInfo:
    artifact_id: str
    name: str
    viewpoint: str
    status: ArtifactStatus
    dependencies: list[str] = field(default_factory=list)
    downstream: list[str] = field(default_factory=list)
    priority: int = 3
    output_path: str = ""


class ArtifactGraph:
    """Manages DoDAF view dependency graph from views.yaml."""

    def __init__(self, views_yaml_path: str):
        with open(views_yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        self._views: dict[str, dict] = {}
        for entry in data.get("views", []):
            self._views[entry["id"]] = entry

    def get_dependencies(self, view_id: str) -> list[str]:
        view = self._views.get(view_id, {})
        return view.get("dependencies", [])

    def get_downstream(self, view_id: str) -> list[str]:
        view = self._views.get(view_id, {})
        return view.get("downstream", [])

    def get_all_view_ids(self) -> list[str]:
        return list(self._views.keys())

    def get_view_info(self, view_id: str) -> Optional[dict]:
        return self._views.get(view_id)

    def compute_status(self, view_id: str, completed: set[str]) -> ArtifactStatus:
        if view_id in completed:
            return ArtifactStatus.DONE
        deps = self.get_dependencies(view_id)
        if all(d in completed for d in deps):
            return ArtifactStatus.READY
        return ArtifactStatus.PENDING

    def get_ready_views(self, completed: set[str]) -> list[str]:
        return [
            vid for vid in self._views
            if self.compute_status(vid, completed) == ArtifactStatus.READY
        ]

    def get_generation_order(self) -> list[str]:
        """Topological sort of views by dependencies."""
        in_degree = {vid: len(self.get_dependencies(vid)) for vid in self._views}
        ready = [vid for vid, deg in in_degree.items() if deg == 0]
        result = []

        while ready:
            vid = ready.pop(0)
            result.append(vid)
            for downstream in self.get_downstream(vid):
                if downstream in in_degree:
                    in_degree[downstream] -= 1
                    if in_degree[downstream] == 0:
                        ready.append(downstream)

        return result
