"""Metamodel-grounded conformance checks.

Validates structured instance data (note frontmatter `dm2-type`,
`dm2-layer`, typed `relationships` slots) against the derived metamodel
indexes (associations.json / taxonomy.json / view-content-spec.json).

Distinct from the prose-level regex heuristics in
`dm2.reasoning.consistency.ConsistencyChecker`: this module checks
standard conformance with the DM2 association catalog, not text patterns.
"""

import difflib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dm2.kernel.metamodel import MetamodelIndex
from dm2.utils.frontmatter import FrontmatterParser
from dm2.utils.paths import get_reference_path

from .consistency import IssueSeverity


@dataclass
class ConformanceIssue:
    """标准符合性问题（元模型层）"""
    issue_type: str
    severity: IssueSeverity
    message: str
    note_id: str = ""
    view_id: str = ""
    suggestion: str = ""
    source: str = "metamodel-conformance"
    related: list = field(default_factory=list)
    related_views: list = field(default_factory=list)


class MetamodelConformanceChecker:
    """基于派生元模型索引的符合性检查器。

    规则集（输入为结构化 frontmatter，纯散文跳过）：
    - unknown-term        dm2-type 不在术语库        WARNING
    - type-layer          dm2-layer 与 powertype 配对矛盾 INFO
    - unknown-relation    关系槽不在关联目录          WARNING + 最近邻建议
    - endpoint-type       端点类型与目录不兼容        ERROR
    - required-association 视图必要关联缺失           WARNING
    """

    def __init__(self, index: Optional[MetamodelIndex] = None,
                 reference_root: Optional[Path] = None):
        self.index = index or MetamodelIndex(reference_root).load()
        self._term_names: set = set()
        self._load_term_names(reference_root)

    def _load_term_names(self, reference_root: Optional[Path]):
        root = Path(reference_root) if reference_root else get_reference_path()
        path = root / "terms.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                for t in json.load(f):
                    self._term_names.add(t.get("term", ""))

    # ── note collection ──────────────────────────────────────────────────
    @staticmethod
    def collect_note_frontmatters(paths) -> dict[str, dict]:
        """Parse markdown files' frontmatter; returns {note_id: fm_dict}.

        Files without frontmatter or without `dm2-type` are skipped.
        """
        notes = {}
        for p in paths:
            path = Path(p)
            if not path.exists() or path.suffix != ".md":
                continue
            fm = FrontmatterParser.parse(path.read_text(encoding="utf-8"))
            if fm and fm.get("dm2-type"):
                notes[path.stem] = fm
        return notes

    # ── note-level checks ────────────────────────────────────────────────
    def check_notes(self, notes: dict[str, dict]) -> list[ConformanceIssue]:
        """Run unknown-term / type-layer / unknown-relation / endpoint-type.

        Args:
            notes: {note_id: frontmatter dict}; each frontmatter carries
                `dm2-type`, optional `dm2-layer`, and `relationships`
                (slot label -> [target note names or free text]).
        """
        issues: list[ConformanceIssue] = []
        type_map = {nid: str(fm.get("dm2-type", "")) for nid, fm in notes.items()}

        for note_id, fm in notes.items():
            dm2_type = str(fm.get("dm2-type", ""))
            issues.extend(self._check_unknown_term(note_id, dm2_type))
            issues.extend(self._check_type_layer(note_id, dm2_type, str(fm.get("dm2-layer", ""))))
            issues.extend(
                self._check_relationships(note_id, dm2_type, fm.get("relationships") or {}, type_map)
            )
        return issues

    def _check_unknown_term(self, note_id: str, dm2_type: str) -> list[ConformanceIssue]:
        if not dm2_type or dm2_type in self._term_names:
            return []
        known = sorted(self._term_names)
        close = difflib.get_close_matches(dm2_type, known, n=1, cutoff=0.6)
        return [ConformanceIssue(
            issue_type="unknown-term",
            severity=IssueSeverity.WARNING,
            message=f"笔记 {note_id} 的 dm2-type '{dm2_type}' 不在 DM2 术语库中",
            note_id=note_id,
            suggestion=f"最接近的标准术语: {close[0]}" if close else "",
        )]

    def _check_type_layer(self, note_id: str, dm2_type: str, layer: str) -> list[ConformanceIssue]:
        if not layer:
            return []
        individuals, powertypes = set(), set()
        for pair in self.index.powertype_pairs():
            individuals.add(pair["individual"])
            powertypes.add(pair["powertype"])
        # 循环配对（Organization↔OrganizationType 等双向 powertypeInstance）
        # 两侧都出现的名称层归属有歧义，不判定。
        if dm2_type in powertypes and dm2_type not in individuals and layer == "Individual":
            counterpart = next(p["individual"] for p in self.index.powertype_pairs()
                               if p["powertype"] == dm2_type)
            return [ConformanceIssue(
                issue_type="type-layer",
                severity=IssueSeverity.INFO,
                message=(f"笔记 {note_id} 类型 '{dm2_type}' 是 powertype "
                         f"(Type 层)，但 dm2-layer 标为 Individual"),
                note_id=note_id,
                suggestion=f"Individual 层对应类型为 '{counterpart}'",
            )]
        if dm2_type in individuals and dm2_type not in powertypes and layer == "Type":
            counterpart = next(p["powertype"] for p in self.index.powertype_pairs()
                               if p["individual"] == dm2_type)
            return [ConformanceIssue(
                issue_type="type-layer",
                severity=IssueSeverity.INFO,
                message=(f"笔记 {note_id} 类型 '{dm2_type}' 是 individual 层概念，"
                         f"但 dm2-layer 标为 Type"),
                note_id=note_id,
                suggestion=f"Type 层对应类型为 '{counterpart}'",
            )]
        return []

    def _check_relationships(self, note_id: str, dm2_type: str,
                             relationships: dict, type_map: dict) -> list[ConformanceIssue]:
        issues: list[ConformanceIssue] = []
        for slot, targets in relationships.items():
            assoc = self.index.get_association(slot)
            if not assoc or not assoc.get("endpoints"):
                # label-only tuple or unknown slot
                known = [a["label"] for a in self.index.all_associations()]
                close = difflib.get_close_matches(slot, known, n=1, cutoff=0.7)
                issues.append(ConformanceIssue(
                    issue_type="unknown-relation",
                    severity=IssueSeverity.WARNING,
                    message=f"笔记 {note_id} 的关系槽 '{slot}' 不在 DM2 关联目录中",
                    note_id=note_id,
                    suggestion=f"最接近的标准关联: {close[0]}" if close else "",
                ))
                continue
            issues.extend(self._check_endpoint_types(note_id, dm2_type, slot, assoc, targets, type_map))
        return issues

    def _check_endpoint_types(self, note_id: str, dm2_type: str, slot: str,
                              assoc: dict, targets, type_map: dict) -> list[ConformanceIssue]:
        """Subtype-aware endpoint conformance for one relationship slot."""
        endpoints = assoc["endpoints"]
        if len(endpoints) != 2:
            return []
        expected = [e["type"] for e in endpoints]
        issues: list[ConformanceIssue] = []

        # The note itself must fit one endpoint slot...
        if not any(self.index.is_subtype(dm2_type, e) for e in expected):
            issues.append(ConformanceIssue(
                issue_type="endpoint-type",
                severity=IssueSeverity.ERROR,
                message=(f"笔记 {note_id}({dm2_type}) 不满足关联 '{slot}' "
                         f"的端点类型 {expected}"),
                note_id=note_id,
                suggestion=f"该关联合法端点: {expected[0]} ─▶ {expected[1]}",
            ))
            return issues

        # ...and the other endpoint is filled by each target note.
        # note fits endpoints[i]; targets must fit the opposite one.
        target_expected = [e for e in expected if not self.index.is_subtype(dm2_type, e)] or expected
        for target in self._iter_targets(targets):
            target_type = type_map.get(target)
            if not target_type:
                continue  # unresolvable (free text / note not in batch) - skip
            if not any(self.index.is_subtype(target_type, e) for e in target_expected):
                issues.append(ConformanceIssue(
                    issue_type="endpoint-type",
                    severity=IssueSeverity.ERROR,
                    message=(f"关联 '{slot}' 端点类型不匹配: {note_id}({dm2_type}) "
                             f"─▶ {target}({target_type})，期望 {target_expected}"),
                    note_id=note_id,
                    suggestion=f"'{slot}' 的合法端点: {expected[0]} ─▶ {expected[1]}",
                    related=[target],
                ))
        return issues

    @staticmethod
    def _iter_targets(targets):
        if targets is None:
            return
        if isinstance(targets, list):
            for t in targets:
                if isinstance(t, str):
                    yield t.strip()
        elif isinstance(targets, str):
            yield targets.strip()

    # ── view-level check ─────────────────────────────────────────────────
    def check_view_required(self, view_id: str, notes: dict[str, dict]) -> list[ConformanceIssue]:
        """Necessary associations of a view absent from the structured data."""
        spec = self.index.get_view_spec(view_id)
        if not spec:
            return []
        necessary = {a.get("label") for a in spec.get("necessary_associations", []) if a.get("label")}
        if not necessary:
            return []
        present = set()
        for fm in notes.values():
            for slot in (fm.get("relationships") or {}):
                present.add(slot)
        missing = sorted(necessary - present)
        if not missing:
            return []
        return [ConformanceIssue(
            issue_type="required-association",
            severity=IssueSeverity.WARNING,
            message=f"视图 {view_id} 缺少 {len(missing)} 个标准必要关联",
            view_id=view_id,
            suggestion=f"缺失关联: {', '.join(missing)}",
        )]
