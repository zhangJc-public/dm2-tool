from __future__ import annotations
"""
Step 6: Documentation + Knowledge Feedback (文档化 + 知识回流)

融合流程:
  1. 基于 Step 5 分析结果生成 Composite Views
  2. Composite View 组合: OV-2+OV-5a, SV-4+DIV-1
  3. 复用 view_generator.py 填充视图模板
  4. wikilinks 生成（DM2 概念 [[wikilinks]]）
  5. 知识回流摘要
  6. 输出视图文件到 .dm2/output/
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from dm2.cognitive.six_w_analyzer import SixWAnalyzer, SixW
from dm2.core.agent.instructions import InstructionBuilder
from dm2.core.knowledge.api import KnowledgeAPI
from dm2.engine.view_generator import (
    ArchitectureInput,
    ViewTemplateFiller,
)
from dm2.kernel.indexer import DM2KnowledgeIndexer


@dataclass
class KnowledgeDelta:
    new_entities: list[str]
    new_relationships: list[str]
    iteration_suggestions: list[str]


@dataclass
class DocumentationResult:
    views: dict[str, str]
    composite_view: str
    wikilinks_map: dict[str, list[str]]
    knowledge_delta: KnowledgeDelta
    output_dir: str


class Step6Documentation:
    """Step 6：文档化 + 知识回流"""

    COMPOSITE_COMBINATIONS = [
        {
            "name": "OV-2+OV-5a 复合视图",
            "views": ["OV-2", "OV-5a"],
            "description": "资源流 + 活动分解的组合视图，展示活动与资源之间的关系",
        },
        {
            "name": "SV-4+DIV-1 复合视图",
            "views": ["SV-4", "DIV-1"],
            "description": "系统功能 + 数据概念的组合视图，展示功能与数据的映射",
        },
    ]

    def __init__(self, indexer: DM2KnowledgeIndexer = None, knowledge_api=None):
        self.indexer = indexer or DM2KnowledgeIndexer()
        if not self.indexer._view_templates:
            self.indexer.load_all()
        if knowledge_api is not None:
            self.api = knowledge_api
        else:
            self.api = KnowledgeAPI()
        self.six_w_analyzer = SixWAnalyzer()
        self.filler = ViewTemplateFiller(self.indexer)
        self._instruction_builder = InstructionBuilder(self.api)

    def execute(
        self,
        description: str,
        analysis_text: str = "",
        data_text: str = "",
        scope_text: str = "",
    ) -> DocumentationResult:
        # 1. 提取架构中涉及的实体和关系
        entities = self._extract_entities(description, analysis_text, data_text)
        relationships = self._extract_relationships(analysis_text)

        # 2. 生成 wikilinks 映射
        wikilinks_map = self._build_wikilinks(entities)

        # 3. 生成 Composite View
        composite = self._generate_composite_view(
            description, analysis_text, entities, relationships, wikilinks_map
        )

        # 4. 生成各个独立视图的草稿
        views = {}
        view_data = {
            "overview": description[:500],
            "details": analysis_text[:500] if analysis_text else description[:500],
            "interfaces": "\n".join(f"- {e}" for e in entities[:5]),
            "functions": "\n".join(f"- {r}" for r in relationships[:5]),
            "concepts": "\n".join(f"- {e}" for e in entities[:5]),
            "relationships": "\n".join(f"- {r}" for r in relationships[:5]),
        }
        for view_id in ["OV-1", "OV-2", "OV-5a"]:
            try:
                filled = self.filler.fill(view_id, view_data)
                filled = self._add_wikilinks(filled, wikilinks_map)
                views[view_id] = filled
            except Exception:
                views[view_id] = f"# {view_id}\n\n视图生成待 LLM 填充"

        # 5. 知识回流摘要
        knowledge_delta = self._build_knowledge_delta(entities, relationships, analysis_text)

        return DocumentationResult(
            views=views,
            composite_view=composite,
            wikilinks_map=wikilinks_map,
            knowledge_delta=knowledge_delta,
            output_dir=".dm2/output/",
        )

    def _extract_entities(
        self, *texts: str
    ) -> list[str]:
        entities: list[str] = []
        seen = set()

        patterns = [
            r"[一-龥]+(?:系统|平台|引擎|模块|组件|服务|探针|网关|防火墙|数据库|中心)",
            r"[A-Z][A-Za-z]+(?:\s*[A-Z][a-z]+){0,2}",
        ]

        for text in texts:
            for p in patterns:
                matches = re.findall(p, text)
                for m in matches:
                    m = m.strip()
                    if len(m) > 2 and m.lower() not in seen:
                        seen.add(m.lower())
                        entities.append(m)

        return entities[:20]

    def _extract_relationships(self, analysis_text: str) -> list[str]:
        relations: list[str] = []
        seen = set()

        rel_patterns = [
            r"(?:检测|监控|采集|分析|处理|转发|存储|展示|下发|同步|通知|阻断|隔离)",
            r"\b(?:detect|monitor|collect|analyze|process|forward|store|display|notify)\b",
        ]

        for p in rel_patterns:
            matches = re.findall(p, analysis_text, re.IGNORECASE)
            for m in matches:
                if m.lower() not in seen:
                    seen.add(m.lower())
                    relations.append(m)

        return relations[:15]

    def _build_wikilinks(self, entities: list[str]) -> dict[str, list[str]]:
        """构建实体到 wikilinks 的映射"""
        wikilinks_map: dict[str, list[str]] = {}

        for entity in entities:
            links = []
            concept = self.indexer.get_concept(entity)
            if concept:
                links.append(entity)
                for link in concept.related_links[:3]:
                    link_name = Path(link).stem if "/" in link else link
                    links.append(link_name)
            else:
                links.append(entity)
            wikilinks_map[entity] = list(set(links))[:5]

        return wikilinks_map

    def _generate_composite_view(
        self,
        description: str,
        analysis_text: str,
        entities: list[str],
        relationships: list[str],
        wikilinks_map: dict[str, list[str]],
    ) -> str:
        """生成 Composite View"""
        entities_list = "\n".join(
            f"- [[{e}]]" for e in entities[:10]
        )
        relations_list = "\n".join(
            f"- {r}" for r in relationships[:8]
        )

        return f"""# Composite View：架构全景

## 系统概览

{description[:500]}

## 架构实体

{entities_list}

## 关键关系

{relations_list}

## 组合视点

### OV-2+OV-5a（资源流 + 活动分解）

该组合视图整合资源流图（OV-2）和活动分解树（OV-5a），
展示活动之间的资源交换关系。

### SV-4+DIV-1（系统功能 + 数据概念）

该组合视图整合系统功能描述（SV-4）和概念数据模型（DIV-1），
展示功能与数据实体的映射关系。

## 分析摘要

{analysis_text[:300] if analysis_text else '（待分析完成）'}

---
*Composite View 由 Pipeline Step 6 自动生成*
"""

    def build_view_instructions(self, description: str, view_ids: list[str]) -> list[dict]:
        """使用 Instructions Engine 生成视图生成指令（供 AI Agent 消费）"""
        instructions = []
        for view_id in view_ids:
            instr = self._instruction_builder.build_view_instructions(view_id, description)
            instructions.append({
                "view_id": view_id,
                "context": {
                    "dm2_terms": instr.context.dm2_terms,
                    "dependency_artifacts": instr.context.dependency_artifacts,
                },
                "rules": instr.rules,
                "template": instr.template,
                "output_path": instr.output_path,
            })
        return instructions

    @staticmethod
    def to_json(result: DocumentationResult) -> dict:
        """将文档化结果序列化为 AI Agent 可消费的 JSON"""
        return {
            "views": {vid: content[:500] for vid, content in result.views.items()},
            "composite_view_preview": result.composite_view[:500],
            "wikilinks": {
                entity: links
                for entity, links in list(result.wikilinks_map.items())[:20]
            },
            "knowledge_delta": {
                "new_entities": result.knowledge_delta.new_entities,
                "new_relationships": result.knowledge_delta.new_relationships,
                "iteration_suggestions": result.knowledge_delta.iteration_suggestions,
            },
            "output_dir": result.output_dir,
        }

    def _add_wikilinks(self, content: str, wikilinks_map: dict[str, list[str]]) -> str:
        """在内容中追加 wikilinks 章节"""
        links_section = "\n\n## 关联知识\n\n"
        for entity, links in list(wikilinks_map.items())[:10]:
            link_str = " ".join(f"[[{l}]]" for l in links)
            links_section += f"- **{entity}**: {link_str}\n"

        return content.rstrip() + links_section

    def _build_knowledge_delta(
        self, entities: list[str], relationships: list[str], analysis_text: str
    ) -> KnowledgeDelta:
        """构建知识回流摘要"""
        suggestions = []
        if len(entities) < 3:
            suggestions.append("建议补充更多架构实体信息（系统、组织、资源等）")
        if len(relationships) < 3:
            suggestions.append("建议细化活动流程和资源交换关系")
        if "gap" in analysis_text.lower() or "缺失" in analysis_text:
            suggestions.append("分析中发现数据缺口，建议在迭代中补充")

        if not suggestions:
            suggestions.append("当前架构描述已覆盖主要实体和关系，可进一步细化细节")

        return KnowledgeDelta(
            new_entities=entities,
            new_relationships=relationships,
            iteration_suggestions=suggestions,
        )

    def format_output(self, result: DocumentationResult) -> str:
        entities_list = "\n".join(
            f"- {e}" for e in result.knowledge_delta.new_entities[:10]
        )
        rel_list = "\n".join(
            f"- {r}" for r in result.knowledge_delta.new_relationships[:8]
        )
        suggestions_list = "\n".join(
            f"{i}. {s}" for i, s in enumerate(
                result.knowledge_delta.iteration_suggestions, 1
            )
        )

        views_summary = "\n".join(
            f"- **{vid}**: {len(content)} 字符"
            for vid, content in result.views.items()
        )

        wikilinks_summary = "\n".join(
            f"- **{entity}**: {' '.join(f'[[{l}]]' for l in links[:3])}"
            for entity, links in list(result.wikilinks_map.items())[:10]
        )

        return f"""# Step 6：文档化 + 知识回流

## 生成视图

{views_summary}

### Composite View

{result.composite_view[:1500]}...

## Wikilinks 关联

{wikilinks_summary}

## 知识回流

### 新增实体

{entities_list if entities_list else '（无）'}

### 新增关系

{rel_list if rel_list else '（无）'}

### 迭代建议

{suggestions_list}

---
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    def save_views(self, result: DocumentationResult, output_dir: Path):
        """保存视图文件到输出目录"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存 Composite View
        composite_path = output_dir / "composite-view.md"
        composite_path.write_text(result.composite_view, encoding='utf-8')

        # 保存各独立视图
        for vid, content in result.views.items():
            view_path = output_dir / f"{vid}.md"
            view_path.write_text(content, encoding='utf-8')

        # Register generated views with ViewManager
        from dm2.core.views.manager import ViewManager
        vm = ViewManager(project_root=output_dir.parent)
        for vid in result.views:
            vm.register_view(vid)

        return output_dir
