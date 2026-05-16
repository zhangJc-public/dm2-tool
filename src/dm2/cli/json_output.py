"""Unified JSON response helper for AI Agent interface."""

import json
from typing import Any


def json_success(data: Any) -> None:
    """Output a successful JSON response."""
    print(json.dumps({"status": "success", "data": data}, ensure_ascii=False, indent=2))


def json_error(code: str, message: str) -> None:
    """Output an error JSON response."""
    print(json.dumps({
        "status": "error",
        "error": {"code": code, "message": message}
    }, ensure_ascii=False, indent=2))
