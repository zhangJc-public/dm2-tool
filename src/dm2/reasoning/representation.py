"""Representation conformance checks for generated DoDAF views.

``views.yaml`` declares a ``representation`` per view and
``instructions.REPRESENTATION_TO_MERMAID`` decides which Mermaid diagram (if
any) the instruction template asks for. Nothing verified that a *generated*
view actually honours that declaration: a `table` view could ship a Mermaid
graph, and a `state-diagram` view could ship no diagram at all, while
``dm2 validate`` stayed silent.

This module closes that gap. It is deliberately narrow — it reasons only about
the Mermaid convention and about externally referenced figures (``.svg`` /
``.png`` / ``.jpg``), so it never has to know which image tooling a project
prefers.

Severity follows ``consistency.strict_mode``: warnings by default (so existing
projects are not broken by a stricter checker), errors when a project opts in.
"""

from __future__ import annotations

import re
from typing import Iterable, Optional

from dm2.reasoning.consistency import ConsistencyIssue, IssueSeverity

#: ``graph`` and ``flowchart`` are the same family — both are directed graphs and
#: the Mermaid distinction between them is cosmetic, so either satisfies the other.
_GRAPH_FAMILY = {"graph", "flowchart"}

_MERMAID_BLOCK = re.compile(r"```mermaid\s*\n\s*(\w+)")
_FIGURE_REF = re.compile(r"!\[[^\]]*\]\(([^)]+\.(?:svg|png|jpg|jpeg))\)", re.IGNORECASE)

#: Representations that carry no diagram at all.
_DIAGRAM_FREE = {"table", "text"}


def _strict() -> bool:
    """``consistency.strict_mode`` promotes warnings to errors."""
    try:
        from dm2.config.manager import get
        return bool(get("consistency.strict_mode", False))
    except Exception:  # non-dm2 cwd or broken config — stay non-fatal
        return False


def _mermaid_map() -> dict:
    """The representation→Mermaid map declared by the instruction builder.

    Imported lazily: ``dm2.reasoning`` and ``dm2.core`` sit at the same
    dependency level, and a function-local import keeps module load order free.
    """
    from dm2.core.agent.instructions import REPRESENTATION_TO_MERMAID
    return REPRESENTATION_TO_MERMAID


def _allowed_mermaid_types(representation: str) -> Optional[set[str]]:
    """Mermaid types that satisfy ``representation``.

    Returns ``set()`` when the representation carries no diagram, or ``None``
    when the representation is unknown (not this checker's business).
    """
    if representation in _DIAGRAM_FREE:
        return set()
    expected = _mermaid_map().get(representation)
    if not expected:
        return None
    if expected in _GRAPH_FAMILY:
        return set(_GRAPH_FAMILY)
    return {expected}


class RepresentationChecker:
    """Compare a view's declared representation with what the file contains."""

    def __init__(self, knowledge=None):
        #: Optional ``KnowledgeAPI``; built on demand so callers stay simple.
        self._knowledge = knowledge

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
            allowed = _allowed_mermaid_types(representation)
            if allowed is None:
                continue

            mermaid = set(_MERMAID_BLOCK.findall(content))
            figures = _FIGURE_REF.findall(content)

            if allowed:
                issues.extend(self._check_diagram_expected(
                    view_id, representation, allowed, mermaid, figures, severity))
            elif mermaid:
                issues.append(ConsistencyIssue(
                    issue_type="representation_unexpected_diagram",
                    severity=severity,
                    view_id=view_id,
                    message=(f"视图 {view_id} 的 representation={representation} "
                             f"不应包含 Mermaid 图"),
                    suggestion="改为表格 / 结构化文本，或把图示移到图类视图",
                ))
        return issues

    @staticmethod
    def _check_diagram_expected(view_id, representation, allowed, mermaid, figures, severity):
        if mermaid:
            stray = mermaid - allowed
            if stray:
                return [ConsistencyIssue(
                    issue_type="representation_mismatch",
                    severity=severity,
                    view_id=view_id,
                    message=(f"视图 {view_id} 的图型 {sorted(stray)} 与 "
                             f"representation={representation} 不符"),
                    suggestion=f"改用 {sorted(allowed)} 之一，或引用独立图文件",
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
        if figures:
            # An externally generated figure satisfies the diagram requirement.
            return []
        return [ConsistencyIssue(
            issue_type="representation_missing_diagram",
            severity=severity,
            view_id=view_id,
            message=(f"视图 {view_id} 的 representation={representation} 需要图示，"
                     f"但文件中既无 Mermaid 也无外部图引用"),
            suggestion=f"补充 ```mermaid {sorted(allowed)} 区块，或引用独立图文件",
        )]

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
