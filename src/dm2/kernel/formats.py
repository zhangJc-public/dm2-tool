"""View output formats — the carrier axis, kept separate from ``representation``.

A DoDAF view has two independent properties:

``representation``
    What information structure it conveys (``text``, ``table``, ``node-link``,
    ``state-diagram``, ``pictorial`` …). Fixed by the view's definition.

``format``
    How that structure is carried (``markdown``, ``mermaid``, ``svg``, ``xlsx``,
    ``mp4`` …). A project decision.

Treating format as a function of representation is what forced every concept
graph to be drawn as a Mermaid node-link diagram; the relationship is a
compatibility relation, not a mapping. This module holds that relation and is
deliberately dependency-free so both ``dm2.core`` and ``dm2.reasoning`` can use it.
"""

from __future__ import annotations

from typing import Optional

#: dm2 produces or instructs this format directly.
NATIVE = "native"
#: The format can carry the representation only by losing structure it conveys.
LOSSY = "lossy"
#: The artefact is produced outside dm2 and referenced from the view.
EXTERNAL = "external"

#: representation → {format: capability}
COMPATIBLE_FORMATS: dict[str, dict[str, str]] = {
    "text": {
        "markdown": NATIVE,
        "html": EXTERNAL,
    },
    "table": {
        "markdown": NATIVE,
        "html": EXTERNAL,
        "xlsx": EXTERNAL,
        "csv": EXTERNAL,
        "svg": LOSSY,
        "png": LOSSY,
    },
    "node-link": {
        "mermaid": NATIVE,
        "svg": NATIVE,
        "png": EXTERNAL,
        "html": EXTERNAL,
    },
    "tree": {
        "mermaid": NATIVE,
        "svg": NATIVE,
        "png": EXTERNAL,
        "html": EXTERNAL,
    },
    "org-chart": {
        "mermaid": NATIVE,
        "svg": NATIVE,
        "png": EXTERNAL,
        "html": EXTERNAL,
    },
    "flowchart": {
        "mermaid": NATIVE,
        "svg": NATIVE,
        "png": EXTERNAL,
        "html": EXTERNAL,
    },
    "state-diagram": {
        "mermaid": NATIVE,
        "svg": NATIVE,
        "png": EXTERNAL,
        "html": EXTERNAL,
    },
    "sequence-diagram": {
        "mermaid": NATIVE,
        "svg": NATIVE,
        "png": EXTERNAL,
        "html": EXTERNAL,
        "mp4": EXTERNAL,
    },
    "er-diagram": {
        "mermaid": NATIVE,
        "svg": NATIVE,
        "png": EXTERNAL,
        "html": EXTERNAL,
    },
    "pictorial": {
        "svg": NATIVE,
        # A concept graphic is positional; a node-link graph is a lossy stand-in.
        "mermaid": LOSSY,
        "png": EXTERNAL,
        "html": EXTERNAL,
        "mp4": EXTERNAL,
    },
    "gantt": {
        "mermaid": NATIVE,
        "svg": NATIVE,
        "png": EXTERNAL,
        "html": EXTERNAL,
        "xlsx": EXTERNAL,
    },
}

#: The format a view gets when nothing overrides it.
#:
#: ``pictorial`` defaults to ``svg`` because its semantics *are* the layout: a
#: concept graphic carries meaning in where things sit, which a Mermaid node-link
#: graph flattens. The other diagram representations have no such claim, so they
#: keep the cheap, diffable Mermaid default.
DEFAULT_FORMAT: dict[str, str] = {
    "text": "markdown",
    "table": "markdown",
    "node-link": "mermaid",
    "tree": "mermaid",
    "org-chart": "mermaid",
    "flowchart": "mermaid",
    "state-diagram": "mermaid",
    "sequence-diagram": "mermaid",
    "er-diagram": "mermaid",
    "gantt": "mermaid",
    "pictorial": "svg",
}

#: Formats whose artefact is a separate file referenced from the view.
FIGURE_FORMATS = {"svg", "png"}


def capabilities(representation: Optional[str]) -> dict[str, str]:
    """Format → capability for ``representation``; empty when unknown."""
    if not representation:
        return {}
    return dict(COMPATIBLE_FORMATS.get(representation, {}))


def compatible_formats(representation: Optional[str]) -> set[str]:
    """Every format that may carry ``representation``."""
    return set(capabilities(representation))


def capability(representation: Optional[str], fmt: Optional[str]) -> Optional[str]:
    """``NATIVE`` / ``LOSSY`` / ``EXTERNAL``, or ``None`` when incompatible."""
    if not fmt:
        return None
    return capabilities(representation).get(fmt)


def is_compatible(representation: Optional[str], fmt: Optional[str]) -> bool:
    return capability(representation, fmt) is not None


def default_format(representation: Optional[str]) -> str:
    """The format used when no configuration overrides it."""
    if representation in DEFAULT_FORMAT:
        return DEFAULT_FORMAT[representation]
    # Unknown representation: keep the view readable rather than guessing a
    # carrier it may not support.
    return "markdown"


def format_extension(fmt: str) -> str:
    """File extension for an artefact of ``fmt``."""
    return {
        "markdown": "md",
        "mermaid": "md",
        "html": "html",
        "xlsx": "xlsx",
        "csv": "csv",
        "mp4": "mp4",
    }.get(fmt, fmt)


#: Mermaid diagram type per representation. Only consulted when the resolved
#: format *is* Mermaid; it is a detail of that carrier, not of the representation.
MERMAID_TYPE_BY_REPRESENTATION: dict[str, str] = {
    "node-link": "graph",
    "tree": "graph",
    "org-chart": "graph",
    "flowchart": "flowchart",
    "state-diagram": "stateDiagram",
    "sequence-diagram": "sequenceDiagram",
    "er-diagram": "erDiagram",
    "pictorial": "graph",
    "gantt": "gantt",
}

#: File extensions that satisfy each artefact format.
ARTEFACT_EXTENSIONS: dict[str, tuple[str, ...]] = {
    "svg": ("svg",),
    "png": ("png", "jpg", "jpeg"),
    "html": ("html",),
    "xlsx": ("xlsx",),
    "csv": ("csv",),
    "mp4": ("mp4",),
}


def _view_config(key: str, default):
    """Read a ``views.*`` config value, falling back to ``default``.

    The import is function-local: ``dm2.kernel`` and ``dm2.config`` share a
    dependency level and this module must stay importable in isolation. Outside
    a dm2 project — or with a broken config — defaults still apply.
    """
    try:
        from dm2.config.manager import get
        return get(key, default)
    except Exception:
        return default


def resolve_view_format(view_id: str, representation: Optional[str]) -> tuple[str, str]:
    """Resolve ``(format, source)`` for one view.

    A view's format is a project decision layered over a per-representation
    default; it is *not* derived from the representation alone. Order:

    1. ``views.formats.overrides.<view id>``
    2. ``views.formats.default`` (diagram views only)
    3. the representation's default format

    Incompatible values are skipped rather than applied, so a typo degrades to
    the default instead of producing a view dm2 cannot render.
    """
    overrides = _view_config("views.formats.overrides", {}) or {}
    if isinstance(overrides, dict):
        candidate = overrides.get(view_id)
        if candidate and is_compatible(representation, candidate):
            return str(candidate), "override"

    derived = default_format(representation)
    is_diagram = derived != "markdown"

    # A project-wide default shifts how *diagrams* are carried; prose views keep
    # their markdown form unless explicitly overridden. Without this guard,
    # `formats.default: svg` would drag every `table` view into a lossy SVG.
    project_default = _view_config("views.formats.default", None)
    if project_default and is_diagram and is_compatible(representation, project_default):
        return str(project_default), "project_default"

    return derived, "representation_default"
