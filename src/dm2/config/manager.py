"""
Configuration resolver —— 三层配置解析（用户 → 项目 → 内置默认值）
支持字段级容错：部分字段出错仍返回有效配置
"""

import os
import platform
from pathlib import Path
from typing import Any, Optional

# ── 内置默认配置 ──
DEFAULTS: dict[str, Any] = {
    "views": {
        "include_mermaid": True,
        "include_timestamps": True,
    },
    "consistency": {
        "check_enabled": True,
        "strict_mode": False,
    },
    "dm2": {
        "language": "zh",
    },
}


def _get_user_config_dir() -> Path:
    """获取用户配置目录（遵循 XDG 规范）"""
    if platform.system() == "Darwin":
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    elif platform.system() == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "dm2"


def _load_yaml(path: Path) -> Optional[dict]:
    """安全加载 YAML 文件"""
    import yaml
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _merge_configs(base: dict, override: dict) -> dict:
    """深度合并配置，override 覆盖 base"""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_configs(result[key], value)
        else:
            result[key] = value
    return result


def _safe_get_nested(data: dict, path: str, default: Any = None) -> Any:
    """安全获取嵌套键值（dot notation），单个字段出错返回 default"""
    keys = path.split(".")
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def get_project_config(project_root: Optional[Path] = None) -> dict:
    """读取 .dm2 项目的配置（从 .dm2/config.yaml）"""
    if project_root is None:
        from dm2.utils.paths import get_project_root
        project_root = get_project_root()
    return _load_yaml(project_root / ".dm2" / "config.yaml") or {}


def get_user_config() -> dict:
    """读取用户级配置（~/.config/dm2/config.yaml）"""
    return _load_yaml(_get_user_config_dir() / "config.yaml") or {}


def resolve_config(project_root: Optional[Path] = None) -> dict:
    """
    三层配置解析：用户级 → 项目级 → 内置默认值
    项目覆盖用户，用户覆盖默认。每层独立解析，字段级容错。
    """
    config = dict(DEFAULTS)
    user_config = get_user_config()
    project_config = get_project_config(project_root)

    config = _merge_configs(config, user_config)
    config = _merge_configs(config, project_config)
    return config


def get(path: str, default: Any = None, project_root: Optional[Path] = None) -> Any:
    """获取配置项（支持 dot notation，如 'llm.model'）"""
    config = resolve_config(project_root)
    return _safe_get_nested(config, path, default)


def set_user_config(updates: dict) -> Path:
    """更新用户级配置（创建目录和文件如需要）"""
    config_dir = _get_user_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.yaml"

    import yaml
    existing = _load_yaml(config_path) or {}
    merged = _merge_configs(existing, updates)

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(merged, f, allow_unicode=True, default_flow_style=False)

    return config_path
