"""
DM2 Knowledge Base Indexer
从文件系统加载 DM2 术语、概念和视图模板
"""

import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from dm2.utils.frontmatter import FrontmatterParser
from dm2.utils.paths import get_reference_path, get_vault_path

VALID_MODEL_CATEGORIES = {
    "Structural", "Behavioral", "Tree", "Mapping",
    "Tabular", "Pictorial", "Timeline", "Ontology",
}

VALID_REPRESENTATIONS = {
    "node-link", "tree", "org-chart", "flowchart",
    "state-diagram", "sequence-diagram", "er-diagram",
    "pictorial", "gantt", "table", "text",
}


class DM2Layer(str, Enum):
    TYPE = "Type"
    INDIVIDUAL = "Individual"
    TYPE_TYPE = "TypeType"


class DM2DataGroup(str, Enum):
    FOUNDATION = "00-基础模式"
    PERFORMER = "01-Performer"
    ACTIVITY = "02-Activity"
    CAPABILITY = "03-Capability"
    RESOURCE = "04-Resource"
    GUIDANCE = "05-Guidance"
    MEASURE = "06-Measure"
    LOCATION = "07-Location"
    SERVICES = "08-Services"
    PROJECT = "09-Project"
    RULES = "10-Rules"
    RESOURCE_FLOW = "11-ResourceFlow"
    PEDIGREE = "12-Pedigree"
    INFO_PEDIGREE = "13-InformationPedigree"
    ORG_STRUCTURE = "14-OrganizationalStructure"
    REIFICATION = "15-ReificationLevels"
    INFO_AND_DATA = "16-InformationAndData"


@dataclass
class DM2Term:
    """DM2 术语条目"""
    term: str
    definition: str
    alias: list[str] = field(default_factory=list)
    source: str = ""
    groups: list[str] = field(default_factory=list)
    file_path: str = ""


@dataclass
class DM2Concept:
    """DM2 概念（从 frontmatter 解析）"""
    name: str
    dm2_type: str
    layer: str
    subtype: str = ""
    definition: str = ""
    file_path: str = ""
    synonyms: list[str] = field(default_factory=list)
    relationships: dict[str, list[str]] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    related_links: list[str] = field(default_factory=list)


@dataclass
class ViewTemplate:
    """DoDAF 视图模板"""
    view_id: str
    view_name: str
    viewpoint: str
    dm2_groups: list[str]
    template_path: str
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    priority: int = 3
    required_data: list[str] = field(default_factory=list)
    downstream: list[str] = field(default_factory=list)
    # New metadata fields from DoDAF V2.02 standard
    standard_name: str = ""
    model_category: str = ""
    representation: Optional[str] = None
    purpose: str = ""
    sections: list[str] = field(default_factory=list)
    required_fields: list[str] = field(default_factory=list)


class DM2KnowledgeIndexer:
    """DM2 知识库索引器"""

    def __init__(self, reference_kb_path: Optional[str] = None):
        self.reference_root = Path(reference_kb_path or get_reference_path())
        self._terms_cache: dict[str, DM2Term] = {}
        self._concepts_cache: dict[str, DM2Concept] = {}
        self._view_templates: dict[str, ViewTemplate] = {}

    def load_all(self):
        """加载所有 DM2 知识"""
        self._load_terms_from_json()
        self._load_concepts_from_markdown(self.reference_root)

        # 可选：从 vault 补充加载
        vault = get_vault_path()
        if vault:
            vault_kb = vault / "文学" / "领域知识" / "DM2"
            if vault_kb.exists():
                self._load_concepts_from_markdown(vault_kb, overwrite=False)

        self._load_view_templates()

        # DAG 环检测
        in_degree = {vid: len(t.dependencies) for vid, t in self._view_templates.items()}
        queue = [vid for vid, deg in in_degree.items() if deg == 0]
        order = []
        while queue:
            vid = queue.pop(0)
            order.append(vid)
            for downstream_vid in self._view_templates[vid].downstream:
                if downstream_vid in in_degree:
                    in_degree[downstream_vid] -= 1
                    if in_degree[downstream_vid] == 0:
                        queue.append(downstream_vid)
        if len(order) != len(self._view_templates):
            missing = set(self._view_templates.keys()) - set(order)
            raise ValueError(f"Circular dependency detected involving: {missing}")

        print(f"[DM2 Indexer] Loaded: {len(self._terms_cache)} terms, {len(self._concepts_cache)} concepts", file=sys.stderr)

    def _load_terms_from_json(self):
        """从 _dm2_v202_extract.json 加载术语"""
        json_path = self.reference_root / "_dm2_v202_extract.json"
        if not json_path.exists():
            print(f"[DM2 Indexer] Warning: {json_path} not found", file=sys.stderr)
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            term = DM2Term(
                term=item.get("term", ""),
                definition=item.get("definition", ""),
                alias=item.get("alias", "").split(", ") if item.get("alias") else [],
                source=item.get("source", ""),
                groups=item.get("groups", []),
                file_path=str(json_path)
            )
            self._terms_cache[term.term] = term

    def _load_concepts_from_markdown(self, root: Path, overwrite: bool = True):
        """从 Markdown 文件加载 DM2 概念"""
        if not root.exists():
            return

        for md_file in root.rglob("*.md"):
            if "详细分析" in md_file.parts:
                continue
            concept = self._parse_markdown_concept(md_file)
            if concept:
                if overwrite or concept.name not in self._concepts_cache:
                    self._concepts_cache[concept.name] = concept

    def _parse_markdown_concept(self, file_path: Path) -> Optional[DM2Concept]:
        """解析单个 Markdown 文件的 frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            frontmatter = FrontmatterParser.parse(content)
            if not frontmatter:
                return None

            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            name = frontmatter.get('name', '') or frontmatter.get('title', '')
            if not name:
                name = file_path.stem

            return DM2Concept(
                name=name,
                dm2_type=frontmatter.get('dm2-type', frontmatter.get('type', '')),
                layer=frontmatter.get('dm2-layer', ''),
                subtype=frontmatter.get('dm2-subtype', ''),
                definition=frontmatter.get('definition', ''),
                file_path=str(file_path),
                synonyms=frontmatter.get('synonyms', []),
                relationships={k: v for k, v in frontmatter.items()
                              if k.startswith(('performs', 'partOf', 'hasPart', 'providesService',
                                            'consumes', 'produces', 'locatedAt', 'measuredBy',
                                            'directedBy', 'underCondition', 'mapsToCapability'))},
                tags=frontmatter.get('tags', []),
                related_links=links
            )
        except Exception as e:
            print(f"[DM2 Indexer] Error parsing {file_path}: {e}", file=sys.stderr)
            return None

    def _validate_view(self, entry: dict) -> list[str]:
        """Validate new metadata fields for a single view entry. Returns warning messages."""
        warnings = []
        vid = entry.get("id", "?")

        if not entry.get("standard_name"):
            warnings.append(f"[{vid}] standard_name is empty")
        if entry.get("model_category") not in VALID_MODEL_CATEGORIES:
            warnings.append(
                f"[{vid}] model_category '{entry.get('model_category')}' "
                f"not in {sorted(VALID_MODEL_CATEGORIES)}"
            )
        rep = entry.get("representation")
        if rep is not None and rep not in VALID_REPRESENTATIONS:
            warnings.append(
                f"[{vid}] representation '{rep}' not in {sorted(VALID_REPRESENTATIONS)}"
            )
        if rep is None:
            warnings.append(f"[{vid}] representation field missing")
        sections = entry.get("sections", [])
        if not sections:
            warnings.append(f"[{vid}] sections is empty")
        if not entry.get("required_fields", []):
            warnings.append(f"[{vid}] required_fields is empty")
        if rep in ("table", "text") and any("Mermaid" in s for s in sections):
            warnings.append(
                f"[{vid}] representation={rep} but sections contain Mermaid entry"
            )
        return warnings

    def _load_view_templates(self):
        """从 views.yaml 加载 DoDAF 视图模板"""
        import yaml

        views_yaml = self.reference_root / "views.yaml"
        if not views_yaml.exists():
            # 回退到包内置的 views.yaml（兼容新旧目录结构）
            base = Path(__file__).parent.parent.parent.parent / "dm2-reference"
            views_yaml = base / "core" / "views.yaml"
            if not views_yaml.exists():
                views_yaml = base / "views.yaml"

        if not views_yaml.exists():
            return

        with open(views_yaml, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        for entry in data.get("views", []):
            vid = entry["id"]

            # Validate new metadata fields (warnings only, non-blocking)
            for w in self._validate_view(entry):
                print(f"[DM2 Indexer] Warning: {w}", file=sys.stderr)

            self._view_templates[vid] = ViewTemplate(
                view_id=vid,
                view_name=entry.get("name", ""),
                viewpoint=entry.get("viewpoint", ""),
                dm2_groups=entry.get("groups", []),
                template_path=entry.get("template_path", ""),
                description=entry.get("description", ""),
                dependencies=entry.get("dependencies", []),
                priority=entry.get("priority", 3),
                required_data=entry.get("required_data", []),
                downstream=entry.get("downstream", []),
                standard_name=entry.get("standard_name", ""),
                model_category=entry.get("model_category", ""),
                representation=entry.get("representation"),
                purpose=entry.get("purpose", ""),
                sections=entry.get("sections", []),
                required_fields=entry.get("required_fields", []),
            )

        # 自动推导 downstream (从 dependencies 反向), YAML 显式声明优先
        for vid, template in self._view_templates.items():
            for dep in template.dependencies:
                if dep in self._view_templates:
                    ds = self._view_templates[dep].downstream
                    if vid not in ds:
                        ds.append(vid)

    def get_term(self, term_name: str) -> Optional[DM2Term]:
        return self._terms_cache.get(term_name)

    def search_terms(self, query: str) -> list[DM2Term]:
        q = query.lower()
        q_nospace = q.replace(" ", "")
        results = []
        for t in self._terms_cache.values():
            if q in t.term.lower() or q in t.definition.lower():
                results.append(t)
            elif any(q_nospace in g.lower().replace(" ", "") for g in t.groups):
                results.append(t)
        return results

    def get_concept(self, name: str) -> Optional[DM2Concept]:
        return self._concepts_cache.get(name)

    def search_concepts(self, dm2_type: str = None, layer: str = None,
                       tags: list[str] = None) -> list[DM2Concept]:
        results = list(self._concepts_cache.values())
        if dm2_type:
            results = [c for c in results if c.dm2_type == dm2_type]
        if layer:
            results = [c for c in results if c.layer == layer]
        if tags:
            results = [c for c in results if any(tag in c.tags for tag in tags)]
        return results

    def get_view_template(self, view_id: str) -> Optional[ViewTemplate]:
        return self._view_templates.get(view_id)

    def get_all_views(self) -> list[ViewTemplate]:
        return list(self._view_templates.values())

    def get_views_by_viewpoint(self, viewpoint: str) -> list[ViewTemplate]:
        return [v for v in self._view_templates.values() if v.viewpoint == viewpoint]

    def get_related_concepts(self, concept_name: str) -> list[DM2Concept]:
        concept = self._concepts_cache.get(concept_name)
        if not concept:
            return []
        related = []
        for link in concept.related_links:
            link_name = Path(link).stem if '/' in link else link
            related_concept = self._concepts_cache.get(link_name)
            if related_concept:
                related.append(related_concept)
        return related

    def get_concepts_by_data_group(self, data_group: str) -> list[DM2Concept]:
        return [c for c in self._concepts_cache.values()
                if data_group in c.file_path]

    def get_statistics(self) -> dict:
        by_type = {}
        for c in self._concepts_cache.values():
            by_type[c.dm2_type] = by_type.get(c.dm2_type, 0) + 1
        return {
            "total_terms": len(self._terms_cache),
            "total_concepts": len(self._concepts_cache),
            "total_views": len(self._view_templates),
            "concepts_by_type": by_type,
        }
