"""DM2 Knowledge API — structured query interface for AI agents."""

from dataclasses import dataclass, field
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
        # Indexer diagnostics are DM2_DEBUG-gated (indexer._diag), so stderr stays
        # clean for --json consumers piping 2>&1. No redirection needed here.
        self._indexer = DM2KnowledgeIndexer()
        self._indexer.load_all()
        self._metamodel = None

    @property
    def metamodel(self):
        """Lazy MetamodelIndex (derived associations/taxonomy/content-spec)."""
        if self._metamodel is None:
            from dm2.kernel.metamodel import MetamodelIndex
            self._metamodel = MetamodelIndex(self._indexer.reference_root).load()
        return self._metamodel

    # ── metamodel-grounded queries ───────────────────────────────────────
    def get_term_detail(self, name: str) -> Optional[dict]:
        """Term definition, aliases, groups, views marking it, association info."""
        t = self._indexer.get_term(name)
        if not t:
            # alias fallback
            for candidate in self._indexer._terms_cache.values():
                if name.lower() in [a.lower() for a in candidate.alias]:
                    t = candidate
                    break
        if not t:
            return None

        views_necessary, views_optional = self._views_for_term(t.term)
        detail = {
            "term": t.term,
            "id": t.curie_id,
            "definition": t.definition,
            "aliases": t.alias,
            "groups": t.groups,
            "association": t.association,
            "views_necessary": views_necessary,
            "views_optional": views_optional,
        }
        if t.association:
            assoc = self.metamodel.get_association(t.term)
            if assoc and assoc.get("endpoints"):
                detail["endpoints"] = [
                    {"type": e["type"], "ideas_role": e["ideas_role"], "domain_role": e["domain_role"]}
                    for e in assoc["endpoints"]
                ]
        return detail

    def _views_for_term(self, term: str):
        necessary, optional = [], []
        for view_id, spec in self.metamodel.all_view_specs().items():
            if term in spec.get("necessary_terms", []) or \
               any(a.get("label") == term for a in spec.get("necessary_associations", [])):
                necessary.append(view_id)
            elif term in spec.get("optional_terms", []):
                optional.append(view_id)
        return sorted(necessary), sorted(optional)

    def get_taxonomy(self, type_name: str) -> Optional[dict]:
        """Subtypes (direct and transitive) and powertype pair of a type."""
        mm = self.metamodel
        direct = mm.subtypes_of(type_name, transitive=False)
        if not direct and type_name not in mm._parents and type_name not in mm._children:
            # Still return empty for known powertype/individual names below
            pass
        transitive = mm.subtypes_of(type_name, transitive=True)
        parents = mm._parents.get(type_name, [])
        pair = next((p for p in mm.powertype_pairs()
                     if p["individual"] == type_name or p["powertype"] == type_name), None)
        if not direct and not transitive and not parents and not pair:
            return None
        return {
            "type": type_name,
            "parents": parents,
            "subtypes_direct": direct,
            "subtypes_transitive": transitive,
            "powertype_pair": pair,
        }

    def get_associations(self, type_name: str = "", group_id: str = "") -> list[dict]:
        """Association catalog filtered by endpoint type (subtype-aware) or group."""
        mm = self.metamodel
        if type_name:
            return [self._assoc_public(a) for a in mm.associations_for_type(type_name)]
        if group_id:
            group_types = [
                t.term for t in self._indexer._terms_cache.values()
                if group_id in t.groups and not t.association and t.term[:1].isupper()
            ]
            return [self._assoc_public(a)
                    for a in mm.associations_for_group(group_id, group_types)]
        return [self._assoc_public(a) for a in mm.all_associations() if len(a.get("endpoints") or []) == 2]

    def get_view_content(self, view_id: str) -> Optional[dict]:
        """View content specification: necessary/optional terms and associations."""
        spec = self.metamodel.get_view_spec(view_id)
        if not spec:
            return None
        tmpl = self._indexer.get_view_template(view_id)
        return {
            "view_id": view_id,
            "view_name": tmpl.view_name if tmpl else "",
            "necessary_terms": spec.get("necessary_terms", []),
            "optional_terms": spec.get("optional_terms", []),
            "necessary_associations": spec.get("necessary_associations", []),
        }

    @staticmethod
    def _assoc_public(a: dict) -> dict:
        return {
            "label": a["label"],
            "endpoints": [
                {"type": e["type"], "ideas_role": e["ideas_role"], "domain_role": e["domain_role"]}
                for e in (a.get("endpoints") or [])
            ],
            "homes": a.get("homes", []),
        }

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
