"""Path Utilities - 项目路径解析"""

import os
from pathlib import Path
from typing import Optional


def get_reference_path() -> Path:
    """获取 DM2 参考知识库路径。

    优先检测当前项目 .dm2/reference/（项目本地副本），
    如不存在则回退到包内置的 dm2-reference/core/。
    """
    # 1. 项目本地副本优先（由 dm2 init 复制）
    try:
        project_root = get_project_root()
        project_ref = project_root / ".dm2" / "reference"
        if project_ref.exists():
            return project_ref
    except Exception:
        pass

    # 2. 回退到包内置的参考知识库
    base = Path(__file__).parent.parent.parent.parent / "dm2-reference"
    core = base / "core"
    if core.exists():
        return core
    return base


def get_vault_path() -> Optional[Path]:
    """获取可选的 Obsidian vault 路径（通过环境变量）"""
    vault = os.environ.get("DM2_VAULT_PATH")
    if vault:
        return Path(vault).expanduser().resolve()
    return None


def get_project_root(cwd: Optional[str] = None) -> Path:
    """从当前目录向上查找 .dm2 项目根目录"""
    start = Path(cwd or os.getcwd()).resolve()
    for current in (start, *start.parents):
        if (current / ".dm2" / "config.yaml").exists():
            return current
    return start


def is_dm2_project(cwd: Optional[str] = None) -> bool:
    """检查当前目录是否在 .dm2 项目中（向上遍历目录树）"""
    start = Path(cwd or os.getcwd()).resolve()
    for current in (start, *start.parents):
        if (current / ".dm2" / "config.yaml").exists():
            return True
    return False
