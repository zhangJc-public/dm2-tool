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
    outputs = builder.build_all(dd_terms, mm, builder.data_group_ids())
    outputs.pop("_zh_aliases")
    outputs.pop("_zh_group_aliases")
    outputs.pop("_canonical")
    return outputs


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


class TestChineseAliases:
    """The curated Chinese overlay must be complete and consistent (D9)."""

    def test_every_term_carries_a_chinese_alias(self, regenerated):
        missing = [t["term"] for t in regenerated["terms.json"] if not t.get("zh_aliases")]
        assert missing == [], f"缺中文别名的术语（中文查询将 0 命中）: {missing}"

    def test_every_data_group_carries_chinese_aliases(self, builder, regenerated):
        source = yaml.safe_load(builder.ZH_ALIAS_PATH.read_text(encoding="utf-8"))
        assert set(source["groups"]) == builder.data_group_ids()

    def test_group_aliases_flow_into_their_terms(self, regenerated):
        members = [t for t in regenerated["terms.json"] if "11-resource-flow" in t["groups"]]
        assert members, "resource-flow group has no terms"
        assert all("资源流" in t["zh_groups"] for t in members)

    def test_every_term_carries_a_composed_canonical_name(self, regenerated):
        missing = [t["term"] for t in regenerated["terms.json"] if not t.get("canonical_zh")]
        assert missing == [], f"缺 canonical_zh 的术语: {missing}"

    def test_canonical_name_matches_the_composer(self, regenerated):
        from dm2.kernel.elements import ElementVocabulary

        vocab = ElementVocabulary.load()
        for term in regenerated["terms.json"]:
            assert term["canonical_zh"] == vocab.compose(term["term"])

    @staticmethod
    def _source(tmp_path, data):
        path = tmp_path / "zh.yaml"
        path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return path

    def test_complete_source_passes(self, builder, tmp_path):
        path = self._source(tmp_path, {
            "aliases": {"Activity": ["活动"]},
            "groups": {"02-activity": ["活动"]},
        })
        terms, groups = builder.load_zh_aliases(path, {"Activity"}, {"02-activity"})
        assert terms == {"Activity": ["活动"]}
        assert groups == {"02-activity": ["活动"]}

    def test_unknown_term_key_fails_the_build(self, builder, tmp_path):
        path = self._source(tmp_path, {"aliases": {"Nope": ["无"]}})
        with pytest.raises(SystemExit):
            builder.load_zh_aliases(path, {"Activity"}, {"02-activity"})

    def test_missing_alias_for_a_term_fails_the_build(self, builder, tmp_path):
        path = self._source(tmp_path, {"aliases": {"Activity": ["活动"]}})
        with pytest.raises(SystemExit):
            builder.load_zh_aliases(path, {"Activity", "Capability"}, {"02-activity"})

    def test_empty_alias_fails_the_build(self, builder, tmp_path):
        path = self._source(tmp_path, {"aliases": {"Activity": ["   "]}})
        with pytest.raises(SystemExit):
            builder.load_zh_aliases(path, {"Activity"}, {"02-activity"})

    def test_duplicate_alias_fails_the_build(self, builder, tmp_path):
        path = self._source(tmp_path, {"aliases": {"Activity": ["活动", "活动"]}})
        with pytest.raises(SystemExit):
            builder.load_zh_aliases(path, {"Activity"}, {"02-activity"})

    def test_unknown_group_key_fails_the_build(self, builder, tmp_path):
        path = self._source(tmp_path, {
            "aliases": {"Activity": ["活动"]},
            "groups": {"99-nope": ["无"]},
        })
        with pytest.raises(SystemExit):
            builder.load_zh_aliases(path, {"Activity"}, {"02-activity"})

    def test_missing_group_fails_the_build(self, builder, tmp_path):
        path = self._source(tmp_path, {
            "aliases": {"Activity": ["活动"]},
            "groups": {"02-activity": ["活动"]},
        })
        with pytest.raises(SystemExit):
            builder.load_zh_aliases(path, {"Activity"}, {"02-activity", "03-capability"})
