"""Instructions Engine — generates structured AI agent instructions."""

from dataclasses import dataclass, field
from typing import Optional

from dm2.core.artifacts.graph import ArtifactGraph
from dm2.core.knowledge.api import KnowledgeAPI
from dm2.kernel.formats import (
    default_format,
    format_extension,
    is_compatible,
    preferred_non_mermaid,
)

#: Diagram output channels for diagram-bearing views.
DIAGRAM_OUTPUT_MERMAID = "mermaid"
DIAGRAM_OUTPUT_SVG = "svg"


def _view_config(key: str, default):
    """Read a ``views.*`` config value, falling back to ``default``.

    The import is function-local on purpose: ``dm2.core`` shares a dependency
    level with ``dm2.config`` and must stay importable in isolation (see
    ``core/pedigree/completeness.py`` for the same pattern). Outside a dm2
    project — or with a broken config file — the documented defaults still
    apply, because instruction generation must never fail on config.
    """
    try:
        from dm2.config.manager import get
        return get(key, default)
    except Exception:
        return default


def _mermaid_enabled() -> bool:
    """`views.include_mermaid` — whether to inject an inline Mermaid section."""
    return bool(_view_config("views.include_mermaid", True))


def _diagram_output() -> str:
    """`views.diagram_output` (deprecated) — ``mermaid`` or ``svg``."""
    value = str(_view_config("views.diagram_output", DIAGRAM_OUTPUT_MERMAID)).strip().lower()
    return DIAGRAM_OUTPUT_SVG if value == DIAGRAM_OUTPUT_SVG else DIAGRAM_OUTPUT_MERMAID


def resolve_view_format(view_id: str, representation: Optional[str]) -> tuple[str, str]:
    """Resolve ``(format, source)`` for one view.

    A view's format is a project decision layered over a per-representation
    default; it is *not* derived from the representation alone. Order:

    1. ``views.formats.overrides.<view id>``
    2. ``views.formats.default``
    3. legacy ``views.diagram_output: svg``
    4. the representation's default format

    Incompatible values are skipped rather than applied, so a typo degrades to
    the default instead of producing a view dm2 cannot render.
    """
    overrides = _view_config("views.formats.overrides", {}) or {}
    if isinstance(overrides, dict):
        candidate = overrides.get(view_id)
        if candidate and is_compatible(representation, candidate):
            return str(candidate), "override"

    # A project-wide default shifts how *diagrams* are carried; prose views keep
    # their markdown form unless explicitly overridden. Without this guard,
    # `formats.default: svg` would drag every `table` view into a lossy SVG.
    project_default = _view_config("views.formats.default", None)
    if (
        project_default
        and default_format(representation) != "markdown"
        and is_compatible(representation, project_default)
    ):
        return str(project_default), "project_default"

    # Legacy switch: only a non-default value is honoured, and only for the
    # diagram representations it used to govern — otherwise `table` (which
    # tolerates SVG lossily) would be dragged along. The new pictorial→svg
    # default still applies when a project never set the key.
    if (
        _diagram_output() == DIAGRAM_OUTPUT_SVG
        and representation in REPRESENTATION_TO_MERMAID
        and is_compatible(representation, "svg")
    ):
        return "svg", "legacy_diagram_output"

    fmt = default_format(representation)

    # Legacy switch: `include_mermaid: false` means "anything but Mermaid".
    # Map it onto a native alternative rather than suppressing the diagram.
    if fmt == "mermaid" and not _mermaid_enabled():
        alternative = preferred_non_mermaid(representation)
        if alternative:
            return alternative, "legacy_include_mermaid"
    return fmt, "representation_default"


def _diagram_section(view_id: str, representation: Optional[str], fmt: str) -> Optional[str]:
    """The section that tells the agent how to carry the diagram, if any."""
    if fmt == "mermaid":
        mermaid_type = REPRESENTATION_TO_MERMAID.get(representation)
        return f"## Mermaid 图表 (```{mermaid_type})" if mermaid_type else None
    if fmt == "markdown":
        return None  # text / table content lives in the view's own sections
    if fmt == "svg":
        return (f"## 图示（独立 SVG 文件：{view_id}.svg，"
                f"Markdown 用 ![..]({view_id}.svg) 引用）")
    if fmt == "png":
        return f"## 图示（外部 PNG 文件：{view_id}.png，以图片引用嵌入）"
    if fmt == "html":
        return f"## 输出（HTML 文件：{view_id}.html）"
    ext = format_extension(fmt)
    return f"## 外部产物（{fmt} 文件：{view_id}.{ext}，在正文中引用并说明来源）"


def _format_rule(representation: Optional[str], fmt: str) -> Optional[str]:
    """The rule that states the carrier, unless the carrier is the default prose."""
    if fmt in ("mermaid", "markdown"):
        return None
    if fmt == "svg":
        return "图类内容以独立 SVG 绘制并以图片引用嵌入，不使用内联 Mermaid"
    if fmt == "png":
        return "图示以外部 PNG 图片引用嵌入，不使用内联 Mermaid"
    if fmt == "html":
        return "该视图以 HTML 文件交付"
    ext = format_extension(fmt)
    return f"该视图的 {fmt} 产物由外部提供（{ext} 文件），正文中须引用并说明来源"


@dataclass
class InstructionContext:
    project_description: str = ""
    dm2_terms: list[dict] = field(default_factory=list)
    dm2_concepts: list[dict] = field(default_factory=list)
    dependency_artifacts: list[dict] = field(default_factory=list)
    #: Provenance state of the view being generated: what the Agent must still
    #: declare through `dm2 trace record` before the view can reach `verified`.
    pedigree: dict = field(default_factory=dict)


@dataclass
class Instructions:
    context: InstructionContext
    rules: list[str]
    template: dict
    output_path: str
    # DM2 标准必要关联清单（源自怪物矩阵 × 元模型关联目录）
    association_manifest: list[dict] = field(default_factory=list)


# 关联清单条目上限（resolved 关联优先；超出时丢弃无端点定义的 label-only 条目）
MANIFEST_MAX_ENTRIES = 12


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

    def _build_association_manifest(self, view_id: str) -> list[dict]:
        """Necessary DM2 associations for the view (monster matrix × metamodel).

        Resolved associations (with endpoint types) come first; label-only
        entries are dropped once the section exceeds MANIFEST_MAX_ENTRIES.
        """
        content = self.knowledge.get_view_content(view_id)
        if not content:
            return []
        necessary = content.get("necessary_associations", [])
        resolved = [a for a in necessary if a.get("endpoint_types")]
        unresolved = [a for a in necessary if not a.get("endpoint_types")]
        manifest = [
            {
                "label": a["label"],
                "endpoint_types": a["endpoint_types"],
                "roles": a.get("roles", []),
            }
            for a in resolved
        ]
        if len(manifest) < MANIFEST_MAX_ENTRIES:
            manifest.extend({"label": a["label"]} for a in unresolved)
        return manifest[:MANIFEST_MAX_ENTRIES]

    def _build_rules_from_metadata(self, view) -> list[str]:
        """Generate compliance rules dynamically from view metadata."""
        rules = []

        # Representation rule
        rep = getattr(view, 'representation', None)
        if rep and rep in REPRESENTATION_LABELS:
            rules.append(f"该视图必须以{REPRESENTATION_LABELS[rep]}形式呈现")

        # Carrier rule (format axis), when it differs from the default prose
        fmt, _ = resolve_view_format(view.view_id, rep)
        format_rule = _format_rule(rep, fmt)
        if format_rule:
            rules.append(format_rule)

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
        """Generate template sections from view metadata, injecting the carrier section."""
        sections = list(getattr(view, 'sections', []) or [])

        representation = getattr(view, 'representation', None)
        fmt, source = resolve_view_format(view.view_id, representation)
        carrier = _diagram_section(view.view_id, representation, fmt)
        if carrier:
            sections.append(carrier)

        return {
            "view_id": view.view_id,
            "view_name": view.view_name,
            "viewpoint": view.viewpoint,
            "representation": representation,
            "format": fmt,
            "format_source": source,
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
                pedigree=self.knowledge.pedigree_summary(view_id),
            ),
            rules=rules,
            template=template,
            output_path=(f"dm2-changes/{change_name}/views/{view_id}.{fmt}"
                         if change_name else f"output/{view_id}.{fmt}"),
            association_manifest=self._build_association_manifest(view_id),
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
