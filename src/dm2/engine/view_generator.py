"""
DoDAF View Generator - DoDAF 视图模板填充器
依据 views.yaml 的视图元数据生成符合 DM2 规范的视图文档（不依赖 LLM）
"""

from dm2.kernel.indexer import DM2KnowledgeIndexer


class ViewTemplateFiller:
    """视图模板填充器（不依赖 LLM 的模板填充）"""

    def __init__(self, indexer: DM2KnowledgeIndexer):
        self.indexer = indexer

    def fill(self, view_id: str, data: dict) -> str:
        """填充视图模板。

        文档结构完全来自索引器中的视图元数据（views.yaml）。dm2-reference 里
        没有按视图存放的模板文件——它只提供权威源与派生索引，任何「找模板文件」
        的路径都找不到东西。
        """
        template = self.indexer.get_view_template(view_id)
        if not template:
            return f"# Error: Unknown view {view_id}"

        return self._fill_from_scratch(view_id, data)

    def _fill_from_scratch(self, view_id: str, data: dict) -> str:
        """从视图元数据生成文档骨架"""
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
