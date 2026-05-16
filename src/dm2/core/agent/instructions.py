"""Instructions Engine — generates structured AI agent instructions."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dm2.core.artifacts.graph import ArtifactGraph
from dm2.core.knowledge.api import KnowledgeAPI


@dataclass
class InstructionContext:
    project_description: str = ""
    dm2_terms: list[dict] = field(default_factory=list)
    dm2_concepts: list[dict] = field(default_factory=list)
    dependency_artifacts: list[dict] = field(default_factory=list)


@dataclass
class Instructions:
    context: InstructionContext
    rules: list[str]
    template: dict
    output_path: str


# DoDAF compliance rules per artifact type (fallback for old-format views)
VIEW_RULES = {
    "OV-1": [
        "OV-1 必须包含图形化描述（Mermaid diagram）",
        "OV-1 必须明确标注系统边界和主要作战节点",
        "OV-1 应使用简洁的图形语言，避免过多文字",
    ],
    "OV-2": [
        "OV-2 必须标注资源流的源节点和目标节点",
        "OV-2 必须包含资源流类型说明",
        "OV-2 必须与 OV-1 中定义的节点保持一致",
    ],
    "OV-4": [
        "OV-4 必须包含完整的组织层级关系",
        "OV-4 必须标注组织间的指挥/协作关系",
    ],
    "OV-5a": [
        "OV-5a 必须包含活动的层级分解结构",
        "OV-5a 每个活动必须有唯一标识符",
    ],
    "SV-4": [
        "SV-4 必须包含系统功能的层级分解",
        "SV-4 必须标注功能间的数据流关系",
    ],
    "DIV-1": [
        "DIV-1 必须定义核心实体及其关系",
        "DIV-1 必须包含实体属性说明",
    ],
    "CV-1": [
        "CV-1 必须描述能力的愿景和目标",
        "CV-1 必须包含能力的时间范围",
    ],
    "CV-2": [
        "CV-2 必须包含能力的层级分类",
        "CV-2 每个能力必须有唯一标识",
    ],
}

REPRESENTATION_TO_MERMAID = {
    "node-link": "graph",
    "tree": "graph",
    "org-chart": "graph",
    "flowchart": "flowchart",
    "state-diagram": "stateDiagram",
    "sequence-diagram": "sequenceDiagram",
    "er-diagram": "erDiagram",
    "pictorial": "graph",
    "gantt": "gantt",
    # table → None (no Mermaid)
    # text → None (no Mermaid)
}

MODEL_CATEGORY_LABELS = {
    "Structural": "结构模型 (Structural)，描述系统的静态结构、组成元素及其关系",
    "Behavioral": "行为模型 (Behavioral)，描述系统的动态过程、状态变迁和时序行为",
    "Tree": "层级分解模型 (Tree)，以树形结构展示分类或分解关系",
    "Mapping": "映射关系模型 (Mapping)，展示两个或多个维度之间的对应关系",
    "Tabular": "表格模型 (Tabular)，以表格形式组织结构化信息",
    "Pictorial": "图示模型 (Pictorial)，以图形化方式表达概念或场景",
    "Timeline": "时间线模型 (Timeline)，展示随时间变化的事件或里程碑",
    "Ontology": "本体模型 (Ontology)，定义领域内的核心概念及其语义关系",
}

REPRESENTATION_LABELS = {
    "node-link": "节点-连接图 (node-link diagram)",
    "tree": "树形图 (tree diagram)",
    "org-chart": "组织架构图 (organization chart)",
    "flowchart": "流程图 (flowchart)",
    "state-diagram": "状态图 (state diagram)",
    "sequence-diagram": "序列图 (sequence diagram)",
    "er-diagram": "实体关系图 (ER diagram)",
    "pictorial": "图形化图示 (pictorial)",
    "gantt": "甘特图 (Gantt chart)",
    "table": "表格 (table)",
    "text": "结构化文本 (structured text)",
}

STEP_TEMPLATES = {
    "step1-intent-scope": {
        "sections": ["意图澄清", "反向质问", "Cynefin 复杂度评估", "数据组选择", "上下文预算估算", "范围边界"],
        "output": ".dm2/steps/step1-intent-scope.md",
    },
    "step3-data-requirements": {
        "sections": ["6W 维度到数据组映射", "RAG 检索结果", "实体分类法", "数据缺口分析"],
        "output": ".dm2/steps/step3-data-requirements.md",
    },
    "step5-analysis": {
        "sections": ["溯因推理", "OODA 韧性分析", "TOC 瓶颈识别", "一致性检查", "改进建议"],
        "output": ".dm2/steps/step5-analysis.md",
    },
    "step6-documentation": {
        "sections": ["Composite View 生成", "单视图生成", "Wikilinks 关联", "知识增量", "迭代建议"],
        "output": ".dm2/steps/step6-documentation.md",
    },
}


class InstructionBuilder:
    """Assembles instructions for AI agents to generate DoDAF artifacts."""

    def __init__(self, knowledge_api: KnowledgeAPI, artifact_graph: Optional[ArtifactGraph] = None):
        self.knowledge = knowledge_api
        self.graph = artifact_graph

    def _has_metadata(self, view) -> bool:
        """Check if the view has new metadata fields populated."""
        return bool(view.representation) if hasattr(view, 'representation') else False

    def _build_rules_from_metadata(self, view) -> list[str]:
        """Generate compliance rules dynamically from view metadata."""
        rules = []

        # Representation rule
        rep = getattr(view, 'representation', None)
        if rep and rep in REPRESENTATION_LABELS:
            rules.append(f"该视图必须以{REPRESENTATION_LABELS[rep]}形式呈现")

        # Model category rule
        cat = getattr(view, 'model_category', None)
        if cat and cat in MODEL_CATEGORY_LABELS:
            rules.append(f"该视图属于{MODEL_CATEGORY_LABELS[cat]}")

        # Required fields rules
        for field_name in getattr(view, 'required_fields', []) or []:
            rules.append(f"必须包含: {field_name}")

        # Dependency consistency rules
        for dep_id in view.dependencies:
            rules.append(f"必须与 {dep_id} 保持一致")

        return rules

    def _build_template_from_metadata(self, view) -> dict:
        """Generate template sections from view metadata, with Mermaid injection for diagram views."""
        sections = list(getattr(view, 'sections', []) or [])

        # Inject Mermaid diagram section for views that need one
        rep = getattr(view, 'representation', None)
        mermaid_type = REPRESENTATION_TO_MERMAID.get(rep) if rep else None
        if mermaid_type:
            sections.append(f"## Mermaid 图表 (```{mermaid_type})")

        return {
            "view_id": view.view_id,
            "view_name": view.view_name,
            "viewpoint": view.viewpoint,
            "sections": sections,
            "required_fields": getattr(view, 'required_fields', []) or [],
        }

    def build_view_instructions(self, view_id: str, description: str,
                                  completed_views: Optional[set[str]] = None,
                                  change_name: str = "",
                                  fmt: str = "md") -> Instructions:
        view = self.knowledge.get_view(view_id)
        if not view:
            return Instructions(
                context=InstructionContext(project_description=description),
                rules=[],
                template={"sections": []},
                output_path=(f"dm2-changes/{change_name}/views/{view_id}.{fmt}"
                             if change_name else f"output/{view_id}.{fmt}"),
            )

        # Context: related DM2 terms
        terms = []
        for group in view.dm2_groups:
            results = self.knowledge.search_terms(group)
            terms.extend({"term": r.term, "definition": r.definition} for r in results[:5])

        # Context: dependency artifacts
        deps = []
        completed = completed_views or set()
        for dep_id in view.dependencies:
            deps.append({"id": dep_id, "status": "done" if dep_id in completed else "pending"})

        # Prefer metadata-driven rules and template, fall back to hardcoded
        if self._has_metadata(view):
            rules = self._build_rules_from_metadata(view)
            template = self._build_template_from_metadata(view)
        else:
            rules = VIEW_RULES.get(view_id, [
                f"{view_id} 必须符合 DoDAF DM2 规范",
                f"{view_id} 必须与依赖视图保持一致",
            ])
            template = {
                "view_id": view_id,
                "view_name": view.view_name,
                "viewpoint": view.viewpoint,
                "sections": ["## 概述", f"## {view.view_name}", "## 分析说明"],
                "required_fields": ["view_id", "view_name", "generated_at"],
            }

        return Instructions(
            context=InstructionContext(
                project_description=description,
                dm2_terms=terms,
                dependency_artifacts=deps,
            ),
            rules=rules,
            template=template,
            output_path=(f"dm2-changes/{change_name}/views/{view_id}.{fmt}"
                         if change_name else f"output/{view_id}.{fmt}"),
        )

    def build_step_instructions(self, step_id: str, description: str) -> Instructions:
        step_template = STEP_TEMPLATES.get(step_id, {
            "sections": ["分析", "输出"],
            "output": f".dm2/steps/{step_id}.md",
        })

        rules = [
            f"此步骤必须产出完整的 {step_id} 文档",
            "输出必须包含所有要求的章节",
            "必须引用 DM2 知识库中的相关概念",
        ]

        return Instructions(
            context=InstructionContext(project_description=description),
            rules=rules,
            template={
                "step_id": step_id,
                "sections": step_template["sections"],
                "required_fields": ["step_id", "completed_at"],
            },
            output_path=step_template["output"],
        )
