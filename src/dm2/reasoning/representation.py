"""Representation-and-format conformance checks for generated DoDAF views.

A view declares a ``representation`` (what structure it conveys) in
``views.yaml``, and its ``format`` (how that structure is carried) is resolved
from project configuration. Nothing verified that a generated view actually
honoured that pair: a `table` view could ship a Mermaid graph, a `state-diagram`
view could ship nothing, and a view declared as ``svg`` could quietly contain
inline Mermaid.

This module closes that gap. For each view it resolves the expected format, then
checks the view's content for the corresponding evidence:

===================  ================================================
format               accepted evidence
===================  ================================================
``markdown``         no Mermaid block (the view's sections carry the content)
``mermaid``          a Mermaid block whose type matches the representation
``svg`` / ``png``    a reference to an artefact with that extension
``html`` / ``xlsx``  a reference to an artefact with that extension
``csv`` / ``mp4``    a reference to an artefact with that extension
===================  ================================================

Severity follows ``consistency.strict_mode``: warnings by default (so existing
projects are not broken by a stricter checker), errors when a project opts in.
"""

from __future__ import annotations

import re
from typing import Iterable, Optional

from dm2.kernel.formats import (
    ARTEFACT_EXTENSIONS,
    MERMAID_TYPE_BY_REPRESENTATION,
    resolve_view_format,
)
from dm2.reasoning.consistency import ConsistencyIssue, IssueSeverity

#: ``graph`` and ``flowchart`` are the same family — both are directed graphs and
#: the Mermaid distinction between them is cosmetic, so either satisfies the other.
_GRAPH_FAMILY = {"graph", "flowchart"}

_MERMAID_BLOCK = re.compile(r"```mermaid\s*\n\s*(\w+)")
_FIGURE_REF = re.compile(r"!\[[^\]]*\]\(([^)]+\.(?:svg|png|jpg|jpeg))\)", re.IGNORECASE)

#: Representations whose format carries no diagram at all.
_DIAGRAM_FREE = {"table", "text"}


def _strict() -> bool:
    """``consistency.strict_mode`` promotes warnings to errors."""
    try:
        from dm2.config.manager import get
        return bool(get("consistency.strict_mode", False))
    except Exception:  # non-dm2 cwd or broken config — stay non-fatal
        return False


def _allowed_mermaid_types(representation: str) -> Optional[set[str]]:
    """Mermaid types that satisfy ``representation``.

    Returns ``set()`` when the representation carries no diagram, or ``None``
    when the representation is unknown (not this checker's business).
    """
    if representation in _DIAGRAM_FREE:
        return set()
    expected = MERMAID_TYPE_BY_REPRESENTATION.get(representation)
    if not expected:
        return None
    if expected in _GRAPH_FAMILY:
        return set(_GRAPH_FAMILY)
    return {expected}


def _artefact_refs(content: str, extensions: tuple[str, ...]) -> list[str]:
    """Files referenced by name with one of ``extensions``."""
    pattern = r"[\w./-]+\.(?:" + "|".join(extensions) + r")\b"
    return re.findall(pattern, content, re.IGNORECASE)


class RepresentationChecker:
    """Compare a view's representation and resolved format with its content."""

    def __init__(self, knowledge=None, format_resolver=None):
        #: Optional ``KnowledgeAPI``; built on demand so callers stay simple.
        self._knowledge = knowledge
        #: Injectable for tests; defaults to the shared resolver.
        self._resolve_format = format_resolver or resolve_view_format

    def check(self, views_data: dict[str, str],
              view_ids: Optional[Iterable[str]] = None) -> list[ConsistencyIssue]:
        issues: list[ConsistencyIssue] = []
        severity = IssueSeverity.ERROR if _strict() else IssueSeverity.WARNING

        for view_id in (view_ids if view_ids is not None else views_data.keys()):
            content = views_data.get(view_id)
            if content is None:
                continue

            representation = self._representation(view_id)
            if not representation:
                continue

            fmt, source = self._resolve_format(view_id, representation)
            issues.extend(
                self._check_view(view_id, representation, fmt, source, content, severity)
            )
        return issues

    def _check_view(self, view_id, representation, fmt, source, content, severity):
        mermaid = set(_MERMAID_BLOCK.findall(content))
        figures = _FIGURE_REF.findall(content)
        origin = f"（载体 {fmt}，来源 {source}）"

        if fmt == "markdown":
            if mermaid:
                return [ConsistencyIssue(
                    issue_type="representation_unexpected_diagram",
                    severity=severity,
                    view_id=view_id,
                    message=(f"视图 {view_id} 的载体为 markdown（{representation}），"
                             f"却包含 Mermaid 图"),
                    suggestion="改为表格 / 结构化文本，或把图示移到图类视图",
                )]
            return []

        if fmt == "mermaid":
            return self._check_mermaid(
                view_id, representation, mermaid, figures, origin, severity)

        # Artefact carriers: svg / png / html / xlsx / csv / mp4
        extensions = ARTEFACT_EXTENSIONS.get(fmt, (fmt,))
        if mermaid:
            return [ConsistencyIssue(
                issue_type="representation_mismatch",
                severity=severity,
                view_id=view_id,
                message=(f"视图 {view_id} 声明载体为 {fmt}{origin}，内容却包含 Mermaid 图"),
                suggestion=f"改为引用 .{extensions[0]} 产物，或把载体改回 mermaid",
            )]
        if not _artefact_refs(content, extensions):
            return [ConsistencyIssue(
                issue_type="representation_missing_artifact",
                severity=severity,
                view_id=view_id,
                message=(f"视图 {view_id} 声明载体为 {fmt}{origin}，"
                         f"但正文未引用任何 .{extensions[0]} 文件"),
                suggestion=f"提供 {view_id}.{extensions[0]} 并在视图中引用",
            )]
        return []

    @staticmethod
    def _check_mermaid(view_id, representation, mermaid, figures, origin, severity):
        allowed = _allowed_mermaid_types(representation)
        if allowed is None:
            return []

        if not mermaid:
            if figures:
                return [ConsistencyIssue(
                    issue_type="representation_mismatch",
                    severity=severity,
                    view_id=view_id,
                    message=(f"视图 {view_id} 声明载体为 mermaid{origin}，"
                             f"内容却使用独立图文件"),
                    suggestion=f"补充 ```mermaid {sorted(allowed)} 区块，或把载体改为 svg",
                )]
            return [ConsistencyIssue(
                issue_type="representation_missing_diagram",
                severity=severity,
                view_id=view_id,
                message=(f"视图 {view_id} 的 representation={representation} 需要图示{origin}，"
                         f"但文件中既无 Mermaid 也无外部图引用"),
                suggestion=f"补充 ```mermaid {sorted(allowed)} 区块，或把载体改为 svg",
            )]

        stray = mermaid - allowed
        if stray:
            return [ConsistencyIssue(
                issue_type="representation_mismatch",
                severity=severity,
                view_id=view_id,
                message=(f"视图 {view_id} 的图型 {sorted(stray)} 与 "
                         f"representation={representation} 不符"),
                suggestion=f"改用 {sorted(allowed)} 之一",
            )]
        if figures:
            return [ConsistencyIssue(
                issue_type="representation_mixed",
                severity=IssueSeverity.INFO,
                view_id=view_id,
                message=f"视图 {view_id} 同时包含 Mermaid 图与外部图引用",
                suggestion="通常只需保留一种图示载体",
            )]
        return []

    def _representation(self, view_id: str) -> str:
        knowledge = self._knowledge
        if knowledge is None:
            try:
                from dm2.core.knowledge.api import KnowledgeAPI
                knowledge = KnowledgeAPI()
                self._knowledge = knowledge
            except Exception:
                return ""
        try:
            view = knowledge.get_view(view_id)
        except Exception:
            return ""
        return getattr(view, "representation", "") or ""
