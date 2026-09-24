"""Run the dm2 CLI in a subprocess without depending on an editable install.

``pytest``'s ``pythonpath`` setting only affects the in-process interpreter. A
subprocess launched as ``sys.executable -m dm2.cli.main`` therefore cannot see
``src/`` unless dm2-tool happens to be pip-installed into that exact interpreter
— a hidden coupling that makes the suite pass on a developer machine and fail
anywhere the install is absent.

Putting the repository's ``src/`` on the subprocess ``PYTHONPATH`` removes that
coupling: these tests exercise the CLI the same way regardless of how (or
whether) the package is installed.
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"


def cli_env(**overrides: str | None) -> dict[str, str]:
    """Environment for a CLI subprocess, with ``src/`` on ``PYTHONPATH``.

    Each keyword override sets a variable; passing ``None`` removes it.
    """
    env = dict(os.environ)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{SRC}{os.pathsep}{existing}" if existing else str(SRC)
    for key, value in overrides.items():
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    return env


def run_cli(args, **kwargs):
    """Run ``python -m dm2.cli.main <args>`` in a subprocess.

    Extra keyword arguments are forwarded to ``subprocess.run``; a caller that
    supplies its own ``env`` keeps it.
    """
    kwargs.setdefault("env", cli_env())
    return subprocess.run([sys.executable, "-m", "dm2.cli.main", *args], **kwargs)
