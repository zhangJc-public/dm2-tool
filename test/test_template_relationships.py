"""Tests for group template relationship blocks against the association catalog.

Group template `relationships:` frontmatter slots AND prose relationship
headings must be projections of associations.json (regenerated via
`scripts/build_knowledge_indexes.py --fix-templates`), not hand-authored
vernacular slots.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent
CORE = ROOT / "dm2-reference" / "core"
GROUPS = CORE / "groups"


@pytest.fixture(scope="module")
def builder():
    spec = importlib.util.spec_from_file_location(
        "build_knowledge_indexes", ROOT / "scripts" / "build_knowledge_indexes.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_knowledge_indexes"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def catalog():
    assocs = json.loads((CORE / "associations.json").read_text(encoding="utf-8"))
    taxonomy = json.loads((CORE / "taxonomy.json").read_text(encoding="utf-8"))
    return {a["label"]: a for a in assocs if len(a.get("endpoints") or []) == 2}, taxonomy


def _template_relationship_slots(path):
    text = path.read_text(encoding="utf-8")
    # frontmatter is the first --- ... --- block
    parts = text.split("---", 2)
    fm = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
    rel = (fm or {}).get("relationships") or {}
    return list(rel.keys())


class TestTemplateRelationships:
    def test_all_slots_resolve_in_catalog(self, catalog):
        labels, _ = catalog
        unresolved = []
        for tpl in GROUPS.glob("*/*Template.md"):
            for slot in _template_relationship_slots(tpl):
                if slot not in labels:
                    unresolved.append((tpl.parent.name, slot))
        assert unresolved == [], f"Slots without catalog association: {unresolved}"

    def test_blocks_match_catalog_projection(self, builder, catalog):
        _, taxonomy = catalog
        assocs = json.loads((CORE / "associations.json").read_text(encoding="utf-8"))
        projection = builder.project_group_associations(assocs, taxonomy)
        drift = builder.reconcile_group_templates(projection, assocs, taxonomy, fix=False)
        assert drift == [], (
            "Template relationship blocks drift from catalog — run "
            "`python3 scripts/build_knowledge_indexes.py --fix-templates`: "
            f"{[(g, n) for g, n, *_ in drift]}"
        )

    def test_performer_template_uses_authoritative_slots(self):
        slots = _template_relationship_slots(GROUPS / "01-performer" / "Performer-Template.md")
        # formerly hand-authored, now catalog-backed
        assert "activityPerformedByPerformer" in slots
        assert "materielPartOfPerformer" in slots
        assert "personRoleTypePartOfPerformer" in slots
        # slots without metamodel basis were removed
        assert "measuredByOrg" not in slots
        # misattributed Activity association removed from Performer
        assert "consumesResource" not in slots

    def test_every_slot_endpoint_touches_group_family(self, builder, catalog):
        """Each projected slot's endpoints must include a type attributed to the group."""
        labels, taxonomy = catalog
        assocs = json.loads((CORE / "associations.json").read_text(encoding="utf-8"))
        terms = json.loads((CORE / "terms.json").read_text(encoding="utf-8"))
        type_groups = {t["term"]: t["groups"] for t in terms if not t["association"]}

        projection = builder.project_group_associations(assocs, taxonomy)
        for gid, slot_labels in projection.items():
            for label in slot_labels:
                assoc = labels[label]
                endpoint_types = [e["type"] for e in assoc["endpoints"]]
                # the association must be modeled in a submodel mapped to this
                # group, or touch a type whose submodel attribution includes it
                homes = assoc.get("homes", [])
                modeled_here = any(
                    builder.SUBMODEL_HOME_GROUP.get(h) == gid
                    or (h == "rules")
                    or builder.FOUNDATION_HOME_GROUP.get(h) == gid
                    for h in homes
                )
                type_here = any(gid in type_groups.get(t, []) for t in endpoint_types)
                assert modeled_here or type_here, f"{gid}: {label} not grounded"


class TestProseProjection:
    """正文土话关系标题已替换为权威关联名（VERNACULAR_TO_CATALOG 映射）。"""

    @pytest.mark.parametrize("gid,vernacular", [
        ("01-performer", "performs"),
        ("01-performer", "providesService"),
        ("02-activity", "prerequisite"),
        ("03-capability", "composedOf"),
        ("04-resource", "consumedBy"),
        ("05-guidance", "derivedFrom"),
        ("07-location", "hosts"),
    ])
    def test_prose_has_no_vernacular_headings(self, gid, vernacular):
        tpl = next(GROUPS.glob(f"{gid}/*Template.md"))
        text = tpl.read_text(encoding="utf-8")
        assert re.search(rf"^### {vernacular}（", text, re.M) is None, \
            f"[{gid}] 正文仍含土话标题: {vernacular}"
        assert re.search(rf"^- \*\*{vernacular}\*\*", text, re.M) is None, \
            f"[{gid}] 正文仍含土话粗体: {vernacular}"

    def test_authoritative_block_injected(self):
        tpl = next(GROUPS.glob("01-performer/*Template.md"))
        text = tpl.read_text(encoding="utf-8")
        assert "## DM2 关联清单（元模型权威）" in text
        assert "activityPerformedByPerformer: Performer ─▶ Activity" in text

    def test_authoritative_block_matches_frontmatter(self):
        """注入清单与 frontmatter relationships 槽位一致（同集合）。"""
        for tpl in GROUPS.glob("*/*Template.md"):
            text = tpl.read_text(encoding="utf-8")
            if "## DM2 关联清单（元模型权威）" not in text:
                continue
            fm = yaml.safe_load(text.split("---", 2)[1])
            slots = set((fm.get("relationships") or {}).keys())
            block = text.split("## DM2 关联清单（元模型权威）", 1)[1].split("##", 1)[0]
            block_labels = set(
                re.findall(r"^> - ([A-Za-z]+)", block, re.M)
            )
            assert block_labels == slots, \
                f"[{tpl.parent.name}] 权威清单与 frontmatter 槽位不一致: {block_labels ^ slots}"

    def test_performer_subtype_synced_from_taxonomy(self):
        tpl = next(GROUPS.glob("01-performer/*Template.md"))
        text = tpl.read_text(encoding="utf-8")
        assert "dm2-subtype: OrganizationType | PersonRoleType | Port | Service | System" in text
        assert "| 子类型 | OrganizationType | PersonRoleType | Port | Service | System |" in text

    def test_physical_logical_virtual_not_touched(self):
        """07-location 的位置分类标题（非关系）不得被替换。"""
        tpl = next(GROUPS.glob("07-location/*Template.md"))
        text = tpl.read_text(encoding="utf-8")
        assert "### Physical（物理位置）" in text
        assert "### Logical（逻辑位置）" in text
