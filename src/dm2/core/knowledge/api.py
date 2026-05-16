"""DM2 Knowledge API — structured query interface for AI agents."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dm2.kernel.indexer import DM2KnowledgeIndexer


@dataclass
class KnowledgeSearchResult:
    term: str
    definition: str
    aliases: list[str]
    groups: list[str]
    source: str


@dataclass
class ConceptResult:
    name: str
    dm2_type: str
    layer: str
    subtype: str
    definition: str
    relationships: dict[str, list[str]]
    tags: list[str]
    synonyms: list[str]


@dataclass
class ViewResult:
    view_id: str
    view_name: str
    viewpoint: str
    description: str
    dependencies: list[str]
    downstream: list[str]
    dm2_groups: list[str]
    priority: int
    required_data: list[str]
    standard_name: str = ""
    model_category: str = ""
    representation: Optional[str] = None
    purpose: str = ""
    sections: list[str] = field(default_factory=list)
    required_fields: list[str] = field(default_factory=list)


class KnowledgeAPI:
    """Public API for querying DM2 knowledge base."""

    def __init__(self):
        import io
        import sys
        self._indexer = DM2KnowledgeIndexer()
        # Suppress indexer log output to keep JSON stdout clean
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            self._indexer.load_all()
        finally:
            sys.stdout = old_stdout

    def search_terms(self, query: str) -> list[KnowledgeSearchResult]:
        results = self._indexer.search_terms(query)
        return [
            KnowledgeSearchResult(
                term=r.term,
                definition=r.definition,
                aliases=r.alias,
                groups=r.groups,
                source=r.file_path,
            )
            for r in results
        ]

    def get_concept(self, name: str) -> Optional[ConceptResult]:
        c = self._indexer.get_concept(name)
        if not c:
            return None
        return ConceptResult(
            name=c.name,
            dm2_type=c.dm2_type,
            layer=c.layer,
            subtype=c.subtype,
            definition=c.definition,
            relationships=c.relationships,
            tags=c.tags,
            synonyms=c.synonyms,
        )

    def get_views_by_viewpoint(self, viewpoint: str) -> list[ViewResult]:
        all_views = self._indexer.get_all_views()
        filtered = [v for v in all_views if v.viewpoint.upper() == viewpoint.upper()]
        return [self._view_to_result(v) for v in filtered]

    def get_view(self, view_id: str) -> Optional[ViewResult]:
        v = self._indexer.get_view_template(view_id)
        if not v:
            return None
        return self._view_to_result(v)

    def get_all_views(self) -> list[ViewResult]:
        return [self._view_to_result(v) for v in self._indexer.get_all_views()]

    def get_statistics(self) -> dict:
        return self._indexer.get_statistics()

    def _view_to_result(self, v) -> ViewResult:
        return ViewResult(
            view_id=v.view_id,
            view_name=v.view_name,
            viewpoint=v.viewpoint,
            description=v.description,
            dependencies=v.dependencies,
            downstream=v.downstream,
            dm2_groups=v.dm2_groups,
            priority=v.priority,
            required_data=v.required_data,
            standard_name=v.standard_name,
            model_category=v.model_category,
            representation=v.representation,
            purpose=v.purpose,
            sections=v.sections,
            required_fields=v.required_fields,
        )
