"""Metamodel index — runtime access to the derived DM2 metamodel indexes.

Loads the compact build artifacts (produced by
scripts/build_knowledge_indexes.py) from the reference knowledge base:

  associations.json       — binary associations (label, endpoint types, roles)
  taxonomy.json           — super-subtype hierarchy + powertype (Type/Individual) pairs
  view-content-spec.json  — per-view necessary/optional terms and associations

Runtime never parses the 840 KB source YAMLs.
"""

import json
from pathlib import Path
from typing import Optional

from dm2.kernel.indexer import _diag
from dm2.utils.paths import get_reference_path


class MetamodelIndex:
    """Query interface over the derived metamodel indexes."""

    def __init__(self, reference_root: Optional[Path] = None):
        self.reference_root = Path(reference_root) if reference_root else get_reference_path()
        self._associations: dict[str, dict] = {}
        self._parents: dict[str, list[str]] = {}
        self._children: dict[str, list[str]] = {}
        self._powertype_pairs: list[dict] = []
        self._view_specs: dict[str, dict] = {}
        self._loaded = False

    def load(self) -> "MetamodelIndex":
        if self._loaded:
            return self
        self._associations = {a["label"]: a for a in self._read_json("associations.json", [])}
        taxonomy = self._read_json("taxonomy.json", {})
        self._parents = taxonomy.get("parents", {})
        self._children = taxonomy.get("children", {})
        self._powertype_pairs = taxonomy.get("powertype_pairs", [])
        self._view_specs = self._read_json("view-content-spec.json", {})
        self._loaded = True
        return self

    def _read_json(self, name: str, default):
        path = self.reference_root / name
        if not path.exists():
            _diag(f"[MetamodelIndex] Warning: {path} not found")
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ── associations ─────────────────────────────────────────────────────
    def get_association(self, label: str) -> Optional[dict]:
        self.load()
        return self._associations.get(label)

    def all_associations(self) -> list[dict]:
        self.load()
        return sorted(self._associations.values(), key=lambda a: a["label"])

    def associations_for_type(self, type_name: str) -> list[dict]:
        """Binary associations whose endpoint accepts `type_name`.

        Subtype-aware: an endpoint expecting Performer also matches System.
        """
        self.load()
        accepted = self._type_closure(type_name)
        result = []
        for assoc in self._associations.values():
            endpoints = assoc.get("endpoints") or []
            if len(endpoints) != 2:
                continue
            if any(e["type"] in accepted for e in endpoints):
                result.append(assoc)
        return sorted(result, key=lambda a: a["label"])

    def associations_for_group(self, group_id: str, group_types: list[str]) -> list[dict]:
        """Associations touching any of the given types (used by group templates)."""
        self.load()
        accepted = set()
        for t in group_types:
            accepted |= self._type_closure(t)
        result = []
        for assoc in self._associations.values():
            endpoints = assoc.get("endpoints") or []
            if len(endpoints) == 2 and any(e["type"] in accepted for e in endpoints):
                result.append(assoc)
        return sorted(result, key=lambda a: a["label"])

    # ── taxonomy ─────────────────────────────────────────────────────────
    def subtypes_of(self, type_name: str, transitive: bool = True) -> list[str]:
        self.load()
        if not transitive:
            return list(self._children.get(type_name, []))
        return sorted(self._type_closure(type_name) - {type_name})

    def is_subtype(self, maybe_subtype: str, supertype: str) -> bool:
        """True if maybe_subtype is supertype itself or a (transitive) subtype."""
        self.load()
        return maybe_subtype in self._type_closure(supertype)

    def powertype_pairs(self) -> list[dict]:
        self.load()
        return list(self._powertype_pairs)

    def _type_closure(self, type_name: str) -> set:
        """Transitive closure: the type itself plus all its descendants."""
        self.load()
        result = {type_name}
        stack = [type_name]
        while stack:
            current = stack.pop()
            for child in self._children.get(current, []):
                if child not in result:
                    result.add(child)
                    stack.append(child)
        return result

    # ── view content spec ────────────────────────────────────────────────
    def get_view_spec(self, view_id: str) -> Optional[dict]:
        self.load()
        return self._view_specs.get(view_id)

    def all_view_specs(self) -> dict:
        self.load()
        return dict(self._view_specs)
