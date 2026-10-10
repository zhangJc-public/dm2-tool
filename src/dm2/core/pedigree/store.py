"""Atomic, YAML-backed pedigree storage at ``.dm2/pedigree/<view_id>.yaml``.

The store never creates the project directory on a read, and writes go through a
same-directory temp file plus ``os.replace`` so an interrupted write can never
leave a half-parsed record behind.

Corrupt files are reported on stderr (``DM2_DEBUG`` gated) and treated as absent:
stdout has to stay a single JSON envelope for ``--json`` consumers, and a broken
file must not take down ``dm2 audit``/``dm2 validate``.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

import yaml

from dm2.core.pedigree.model import Pedigree, PedigreeValidationError


def _diag(message: str) -> None:
    """Diagnostics go to stderr, and only when DM2_DEBUG is set."""
    if os.environ.get("DM2_DEBUG"):
        print(message, file=sys.stderr)


def _atomic_write(path: Path, text: str) -> None:
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


class PedigreeStore:
    """Read and write pedigree records within one dm2 project."""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            from dm2.utils.paths import get_project_root

            project_root = get_project_root()
        self._root = Path(project_root)

    @property
    def root(self) -> Path:
        """The dm2 project root this store reads and writes under."""
        return self._root

    @property
    def directory(self) -> Path:
        return self._root / ".dm2" / "pedigree"

    def path_for(self, view_id: str) -> Path:
        return self.directory / f"{view_id}.yaml"

    def exists(self, view_id: str) -> bool:
        return self.path_for(view_id).exists()

    def load(self, view_id: str) -> Optional[Pedigree]:
        """Load a record, or ``None`` when the file is missing or unreadable."""
        path = self.path_for(view_id)
        if not path.exists():
            return None
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as error:
            _diag(f"[dm2 pedigree] 忽略无法解析的记录 {path}: {error}")
            return None
        if data is not None and not isinstance(data, dict):
            _diag(f"[dm2 pedigree] 忽略非映射记录 {path}")
            return None
        try:
            # The filename is the key; a drifted embedded view_id must not win.
            return Pedigree.from_dict({**(data or {}), "view_id": view_id})
        except PedigreeValidationError as error:
            _diag(f"[dm2 pedigree] 忽略不合规的记录 {path}: {error}")
            return None

    def save(self, pedigree: Pedigree) -> Path:
        """Atomically write a record and return its path."""
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.path_for(pedigree.view_id)
        _atomic_write(path, pedigree.to_yaml())
        return path

    def list_all(self) -> list[str]:
        """Every ``view_id`` that has a pedigree file, sorted."""
        if not self.directory.exists():
            return []
        return sorted(path.stem for path in self.directory.glob("*.yaml"))

    def delete(self, view_id: str) -> bool:
        """Remove a record; returns whether a file was removed."""
        path = self.path_for(view_id)
        if not path.exists():
            return False
        path.unlink()
        return True
