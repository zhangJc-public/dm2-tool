"""
DoDAF View Generator - DoDAF 视图模板填充器
基于模板生成符合 DM2 规范的视图文档（不依赖 LLM）
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dm2.kernel.indexer import DM2KnowledgeIndexer


@dataclass
class GenerationResult:
    """生成结果"""
    view_id: str
    content: str
    success: bool
    error: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class ArchitectureInput:
    """架构输入"""
    description: str  # 纯文本描述
    image_paths: list[str] = field(default_factory=list)  # 图片路径列表
    metadata: dict = field(default_factory=dict)  # 额外元数据


class ViewTemplateFiller:
    """视图模板填充器（不依赖 LLM 的模板填充）"""

    def __init__(self, indexer: DM2KnowledgeIndexer):
        self.indexer = indexer

    def fill(self, view_id: str, data: dict) -> str:
        """填充视图模板"""
        template = self.indexer.get_view_template(view_id)
        if not template:
            return f"# Error: Unknown view {view_id}"

        # 获取对应模板文件
        template_path = self._find_template_file(view_id)
        if template_path and template_path.exists():
            return self._fill_from_file(template_path, data)
        else:
            return self._fill_from_scratch(view_id, data)

    def _find_template_file(self, view_id: str) -> Optional[Path]:
        """查找模板文件"""
        dm2_root = self.indexer.reference_root

        patterns = [
            dm2_root / "详细分析" / f"*{view_id}*",
            dm2_root / "**" / f"*{view_id}*Template*",
        ]

        for pattern in patterns:
            matches = list(dm2_root.glob(str(pattern)))
            if matches:
                return matches[0]

        return None

    def _fill_from_file(self, template_path: Path, data: dict) -> str:
        """从模板文件填充"""
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 简单占位符替换
        for key, value in data.items():
            placeholder = "{" + key + "}"
            content = content.replace(placeholder, str(value))

        return content

    def _fill_from_scratch(self, view_id: str, data: dict) -> str:
        """从零生成视图"""
        template = self.indexer.get_view_template(view_id)

        lines = [
            f"# {view_id} {template.view_name}",
            "",
            f"**视图类型**: {template.viewpoint}",
            f"**涉及数据组**: {', '.join(template.dm2_groups)}",
            "",
            "---",
            "",
        ]

        # 根据视图类型添加基本结构
        if view_id.startswith("OV-"):
            lines.extend([
                "## 1. 概览",
                data.get("overview", ""),
                "",
                "## 2. 详细描述",
                data.get("details", ""),
                "",
                "## 3. 关系图",
                "```mermaid",
                "graph LR",
                "    A[活动] --> B[结果]",
                "```",
            ])
        elif view_id.startswith("SV-"):
            lines.extend([
                "## 1. 系统概览",
                data.get("overview", ""),
                "",
                "## 2. 接口描述",
                data.get("interfaces", ""),
                "",
                "## 3. 功能分解",
                data.get("functions", ""),
            ])
        elif view_id.startswith("DIV-"):
            lines.extend([
                "## 1. 数据概念",
                data.get("concepts", ""),
                "",
                "## 2. 概念关系",
                data.get("relationships", ""),
                "",
                "## 3. ER 图",
                "```mermaid",
                "erDiagram",
                "    A ||--o| B : relation",
                "```",
            ])

        return "\n".join(lines)

