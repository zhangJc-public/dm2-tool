"""Path Utilities - 项目路径解析"""

import os
from pathlib import Path
from typing import Optional


class KnowledgeBaseNotFound(RuntimeError):
    """运行时可解析的知识库资产缺失。

    这与「知识库为空」是两件事：前者是安装或项目状态损坏，后者是合法状态。
    两者混同正是静默给空答案的根源，因此调用方必须显式处理本异常。
    """


def get_reference_path() -> Path:
    """获取 DM2 参考知识库路径。

    优先检测当前项目 .dm2/reference/（项目本地副本），
    如不存在则回退到包内置的 dm2-reference/core/。

    Raises:
        KnowledgeBaseNotFound: 两条候选都不存在时。此处**绝不返回不存在的路径**——
            静默返回幻觉路径会让上层 glob 到空集合、进而报成功
            （见 openspec/specs/dm2-metamodel-knowledge 的
            「An unresolvable knowledge base is a reported failure」）。
    """
    # 1. 项目本地副本优先（由 dm2 init 复制）
    project_ref: Optional[Path] = None
    try:
        project_root = get_project_root()
        project_ref = project_root / ".dm2" / "reference"
        if project_ref.exists():
            return project_ref
    except Exception:
        project_ref = None

    # 2. 回退到包内置的参考知识库
    base = Path(__file__).parent.parent.parent.parent / "dm2-reference"
    core = base / "core"
    if core.exists():
        return core

    raise KnowledgeBaseNotFound(
        "未找到 DM2 知识库。已检查：\n"
        f"  - 项目本地副本：{project_ref or '(无法确定项目根)'}\n"
        f"  - 包内置副本：  {core}\n"
        "请运行 dm2 init 创建项目本地副本，或改用 editable 安装（pip install -e .）。"
    )


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
