"""Snapshot/regeneration tests for derived knowledge indexes.

Asserts that the committed indexes under dm2-reference/core/ are up-to-date
with the authoritative sources (dm2-data-dictionary.yaml,
dm2-metamodel-2.02.yaml) and meet expected content counts.

If these fail, regenerate with:  python3 scripts/build_knowledge_indexes.py
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "build_knowledge_indexes.py"
CORE = ROOT / "dm2-reference" / "core"


@pytest.fixture(scope="module")
def builder():
    spec = importlib.util.spec_from_file_location("build_knowledge_indexes", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["build_knowledge_indexes"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def regenerated(builder):
    dd = yaml.safe_load((builder.REF / "dm2-data-dictionary.yaml").read_text(encoding="utf-8"))
    dd_terms = dd if isinstance(dd, list) else dd.get("terms", [])
    mm = yaml.safe_load((builder.REF / "dm2-metamodel-2.02.yaml").read_text(encoding="utf-8"))
    terms = builder.build_terms(dd_terms)
    associations = builder.build_associations(mm)
    taxonomy = builder.build_taxonomy(mm)
    content_spec = builder.build_view_content_spec(dd_terms, associations)
    return {
        "terms.json": terms,
        "associations.json": associations,
        "taxonomy.json": taxonomy,
        "view-content-spec.json": content_spec,
    }


def _committed(name):
    return json.loads((CORE / name).read_text(encoding="utf-8"))


class TestCounts:
    def test_terms_count(self, regenerated):
        assert len(regenerated["terms.json"]) == 279

    def test_binary_associations_at_least_60(self, regenerated):
        binary = [a for a in regenerated["associations.json"] if len(a["endpoints"]) == 2]
        assert len(binary) >= 60

    def test_powertype_pairs(self, regenerated):
        assert len(regenerated["taxonomy.json"]["powertype_pairs"]) == 26

    def test_content_spec_covers_all_views(self, regenerated):
        assert len(regenerated["view-content-spec.json"]) == 52


class TestContentShape:
    def test_performer_subtypes(self, regenerated):
        children = regenerated["taxonomy.json"]["children"]
        assert set(children["Performer"]) == {"System", "Service", "OrganizationType", "PersonRoleType", "Port"}

    def test_ov5b_necessary_associations(self, regenerated):
        labels = {a["label"] for a in regenerated["view-content-spec.json"]["OV-5b"]["necessary_associations"]}
        assert {"activityConsumesResource", "activityPerformedByPerformer", "activityProducesResource"} <= labels

    def test_terms_carry_reconciled_groups(self, regenerated):
        activity = next(t for t in regenerated["terms.json"] if t["term"] == "Activity")
        assert "02-activity" in activity["groups"]
        assert activity["aliases"]  # dictionary aliases preserved

    def test_rules_name_split(self, regenerated):
        terms = {t["term"]: t for t in regenerated["terms.json"]}
        assert "05-guidance" in terms["TechnicalStandard"]["groups"]
        assert "10-rules" in terms["Condition"]["groups"]
        assert "05-guidance" not in terms["Condition"]["groups"]


class TestSnapshotFreshness:
    @pytest.mark.parametrize("name", ["terms.json", "associations.json", "taxonomy.json", "view-content-spec.json"])
    def test_committed_matches_sources(self, regenerated, name):
        assert _committed(name) == regenerated[name], (
            f"{name} is stale — run: python3 scripts/build_knowledge_indexes.py"
        )
