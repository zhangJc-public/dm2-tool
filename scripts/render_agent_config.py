#!/usr/bin/env python3
"""Render the committed agent artifacts for every supported tool adapter.

The committed trees under ``.claude/`` and ``.dsh/`` are dm2's own product
surface: ``dm2 init`` produces exactly these files in a user's project, so the
repository keeps copies for byte-consistency guarding
(``test/test_generated_agent_config.py``).

Works from a plain checkout as well as from an editable install: ``src/`` is
put on ``sys.path`` the same way pytest's ``pythonpath`` option does it.

Run after editing ``src/dm2/core/templates/workflows/``:
    python3 scripts/render_agent_config.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

#: Every adapter whose output is committed and guarded.
TOOLS = ("claude", "dsh")


def main() -> int:
    from dm2 import __version__
    from dm2.core.adapters import get_adapter
    from dm2.core.templates.generator import generate_agent_config

    for tool_id in TOOLS:
        count = generate_agent_config(ROOT, __version__, get_adapter(tool_id))
        print(f"{tool_id}: {count} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
