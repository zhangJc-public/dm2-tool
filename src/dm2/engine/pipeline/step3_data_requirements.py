from __future__ import annotations
"""
Step 3+4: Data Definition + Knowledge Accumulation (数据定义 + 知识沉淀)

融合流程:
  1. 接收 Step 1+2 的范围定义
  2. 6W 矩阵分析 → 数据需求
  3. DM2 数据组 → 实体类型映射
  4. RAG 检索 DM2 知识库
  5. 数据缺口检测
  6. 输出数据需求文档
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from dm2.cognitive.six_w_analyzer import SixW, SIX_W_TO_DM2_GROUPS
from dm2.kernel.indexer import DM2KnowledgeIndexer
from dm2.kernel.rag import ObsidianRAGEngine


DM2_GROUP_TO_ENTITY_TYPES: dict[str, list[str]] = {
    "Resource": ["resource", "information", "data", "material"],
    "Information": ["information", "data", "knowledge"],
    "Project": ["project", "milestone", "phase"],
    "Capability": ["capability", "function", "ability"],
    "Activity": ["activity", "process", "task", "operation"],
    "Service": ["service", "endpoint", "interface"],
    "Measure": ["measure", "metric", "KPI", "indicator"],
    "Location": ["location", "site", "facility", "environment"],
    "Performer": ["performer", "system", "organization", "role"],
    "Organization": ["organization", "department", "team", "unit"],
    "Rules": ["rule", "constraint", "policy", "standard"],
    "Guidance": ["guidance", "directive", "strategy", "goal"],
}


@dataclass
class DataRequirement:
    dimension: str
    entity_types: list[str]
    dm2_groups: list[str]
    required_concepts: list[str]


@dataclass
class DataRequirementsResult:
    requirements: list[DataRequirement]
    retrieved_concepts: list[dict]
    retrieved_terms: list[dict]
    organized_taxonomy: dict[str, list[str]]
    gaps: list[str]


class Step3DataRequirements:
    """Step 3+4：数据定义 + 知识沉淀"""

    def __init__(self, indexer: DM2KnowledgeIndexer = None, knowledge_api=None):
        if knowledge_api is not None:
            self.api = knowledge_api
            self.indexer = knowledge_api._indexer
        else:
            from dm2.core.knowledge.api import KnowledgeAPI
            self.api = KnowledgeAPI()
            self.indexer = self.api._indexer
        self.rag = ObsidianRAGEngine(self.indexer)

    def execute(
        self, description: str, selected_groups: list[str],
        primary_w: str, secondary_ws: list[str],
    ) -> DataRequirementsResult:
        # 1. 建立 6W 维度到数据组的映射
        requirements = self._build_requirements(primary_w, secondary_ws, selected_groups)

        # 2. RAG 检索
        retrieved_concepts = []
        retrieved_terms = []
        for req in requirements:
            query = f"{req.dimension} {' '.join(req.entity_types)} {' '.join(req.dm2_groups)}"
            context = self.rag.retrieve(query, max_results=3)
            for r in context.results:
                if r.chunk_type in ("frontmatter", "body"):
                    retrieved_concepts.append({
                        "source": r.source,
                        "content": r.content[:200],
                        "relevance": r.relevance_score,
                    })
                elif r.chunk_type == "term_definition":
                    retrieved_terms.append({
                        "source": r.source,
                        "content": r.content[:200],
                        "relevance": r.relevance_score,
                    })

        # 3. 组织分类
        taxonomy = self._build_taxonomy(requirements, retrieved_concepts)

        # 4. 缺口检测
        gaps = self._detect_gaps(requirements, retrieved_concepts, retrieved_terms)

        return DataRequirementsResult(
            requirements=requirements,
            retrieved_concepts=retrieved_concepts,
            retrieved_terms=retrieved_terms,
            organized_taxonomy=taxonomy,
            gaps=gaps,
        )

    def _build_requirements(
        self, primary_w_str: str, secondary_ws: list[str], selected_groups: list[str]
    ) -> list[DataRequirement]:
        requirements = []

        all_ws = [primary_w_str]
        if secondary_ws:
            all_ws.extend(secondary_ws[:2])

        for w_str in all_ws:
            try:
                w = SixW(w_str)
            except ValueError:
                continue

            groups = SIX_W_TO_DM2_GROUPS.get(w, [])
            # 与选定数据组取交集
            matched_groups = [g for g in groups if g in selected_groups] or groups

            entity_types = []
            for g in matched_groups:
                g_short = g.split("-")[-1] if "-" in g else g
                types = DM2_GROUP_TO_ENTITY_TYPES.get(g_short, [])
                entity_types.extend(types)

            if not entity_types:
                entity_types = ["entity"]

            requirements.append(DataRequirement(
                dimension=w.value,
                entity_types=list(set(entity_types)),
                dm2_groups=matched_groups,
                required_concepts=[],
            ))

        return requirements

    def _build_taxonomy(
        self, requirements: list[DataRequirement], concepts: list[dict]
    ) -> dict[str, list[str]]:
        taxonomy: dict[str, list[str]] = {}
        for req in requirements:
            key = f"6W-{req.dimension}"
            taxonomy[key] = []
            for et in req.entity_types:
                taxonomy[key].append(f"entity:{et}")
            for g in req.dm2_groups:
                taxonomy[key].append(f"group:{g}")
        return taxonomy

    def _detect_gaps(
        self,
        requirements: list[DataRequirement],
        concepts: list[dict],
        terms: list[dict],
    ) -> list[str]:
        gaps = []

        total_retrieved = len(concepts) + len(terms)
        if total_retrieved == 0:
            gaps.append("DM2 知识库中未检索到任何相关概念。建议补充相关知识笔记或扩展 vault_path。")

        for req in requirements:
            found = False
            for c in concepts:
                content_lower = c["content"].lower()
                for et in req.entity_types:
                    if et.lower() in content_lower:
                        found = True
                        break
                if found:
                    break
            if not found and req.entity_types:
                gaps.append(
                    f"{req.dimension} 维度：未找到 '{', '.join(req.entity_types[:3])}' 相关概念，"
                    f"建议补充 DM2 数据组 {req.dm2_groups} 的实例数据。"
                )

        return gaps

    def format_output(self, result: DataRequirementsResult) -> str:
        req_lines = []
        for i, req in enumerate(result.requirements, 1):
            req_lines.append(f"### {i}. 维度: {req.dimension}")
            req_lines.append(f"- **实体类型**: {', '.join(req.entity_types)}")
            req_lines.append(f"- **DM2 数据组**: {', '.join(req.dm2_groups)}")
            req_lines.append("")

        concepts_lines = []
        for i, c in enumerate(result.retrieved_concepts[:10], 1):
            src = Path(c["source"]).name
            concepts_lines.append(f"{i}. [{c['relevance']:.2f}] **{src}**: {c['content'][:100]}...")
        if not concepts_lines:
            concepts_lines.append("（无检索结果）")

        terms_lines = []
        for i, t in enumerate(result.retrieved_terms[:10], 1):
            src = Path(t["source"]).name
            terms_lines.append(f"{i}. [{t['relevance']:.2f}] **{src}**: {t['content'][:100]}...")
        if not terms_lines:
            terms_lines.append("（无检索结果）")

        taxonomy_lines = []
        for key, items in result.organized_taxonomy.items():
            taxonomy_lines.append(f"- **{key}**: {', '.join(items)}")

        gaps_lines = []
        for g in result.gaps:
            gaps_lines.append(f"- ⚠️ {g}")
        if not gaps_lines:
            gaps_lines.append("- ✅ 未检测到明显数据缺口")

        return f"""# Step 3+4：数据定义 + 知识沉淀

## 数据需求（6W 矩阵驱动）

{chr(10).join(req_lines)}

## 检索到的 DM2 概念

### 概念匹配

{chr(10).join(concepts_lines)}

### 术语定义

{chr(10).join(terms_lines)}

## 数据组织分类

{chr(10).join(taxonomy_lines)}

## 数据缺口

{chr(10).join(gaps_lines)}

---
*生成时间: 由 Pipeline Step 3+4 自动生成*
"""
