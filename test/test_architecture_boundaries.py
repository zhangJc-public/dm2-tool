"""Guard the four-layer dependency direction.

Spec: openspec/specs/dm2-architecture-boundaries
Rationale and the measured baseline: docs/foundation.md §2.

The rule is that every package under ``src/dm2/`` imports only packages at the same
or a lower dependency level. The levels below are the enforceable form of the
conceptual four-layer model; keep them in sync with the spec.
"""

import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "dm2"

#: Dependency level per package. Lower levels must not import higher ones.
LEVELS = {
    "utils": 0,
    "config": 1,
    "kernel": 1,
    "cognitive": 2,
    "reasoning": 2,
    "core": 2,
    "engine": 3,
    "cli": 4,
}

_IMPORT = re.compile(r"^\s*(?:from\s+dm2\.([a-z_]+)|import\s+dm2\.([a-z_]+))", re.MULTILINE)


def _modules():
    """Yield ``(package, path)`` for every module inside a package directory."""
    for path in sorted(SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(SRC)
        if len(relative.parts) < 2:
            continue  # top-level modules such as src/dm2/__init__.py belong to no layer
        yield relative.parts[0], path


def _imported_packages(text: str):
    """Yield the dm2 sub-package names imported by ``text``."""
    for match in _IMPORT.finditer(text):
        yield match.group(1) or match.group(2)


def test_every_package_has_a_level():
    """A new package must be assigned a level rather than silently escaping the rule."""
    packages = {package for package, _ in _modules()}
    unknown = sorted(packages - set(LEVELS))
    assert not unknown, f"未分配层级的包: {unknown}（请更新 LEVELS 与 architecture-boundaries spec）"


def test_no_upward_imports():
    """No module may import a package from a higher level."""
    violations = []
    for package, path in _modules():
        source_level = LEVELS[package]
        for target in _imported_packages(path.read_text(encoding="utf-8")):
            if target not in LEVELS:
                continue
            target_level = LEVELS[target]
            if target_level > source_level:
                violations.append(
                    f"{path.relative_to(SRC.parent.parent)}: "
                    f"{package}(L{source_level}) -> {target}(L{target_level})"
                )
    assert not violations, "存在向上依赖:\n" + "\n".join(violations)


def test_utils_is_a_leaf():
    """`utils` sits at L0 and must not import any other dm2 sub-package."""
    offenders = []
    for package, path in _modules():
        if package != "utils":
            continue
        others = sorted(set(_imported_packages(path.read_text(encoding="utf-8"))))
        if others:
            offenders.append(f"{path.name}: {others}")
    assert not offenders, "utils 不再是叶子层:\n" + "\n".join(offenders)
