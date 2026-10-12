"""Tests for the metamodel-grounded Knowledge API (dm2 knowledge ...)."""
import json

import pytest

from dm2.core.knowledge.api import KnowledgeAPI
from test._cli import run_cli


@pytest.fixture(scope="module")
def api():
    return KnowledgeAPI()


class TestTermDetail:
    def test_entity_term(self, api):
        d = api.get_term_detail("Performer")
        assert d["term"] == "Performer"
        assert d["id"] == "dodaf:Performer"
        assert d["association"] is False
        assert "01-performer" in d["groups"]
        assert d["definition"]

    def test_association_term_has_endpoints(self, api):
        d = api.get_term_detail("activityConsumesResource")
        assert d["association"] is True
        types = [e["type"] for e in d["endpoints"]]
        assert types == ["Activity", "Resource"]

    def test_alias_lookup(self, api):
        # Performer's aliases include Actor
        d = api.get_term_detail("Actor")
        assert d is not None
        assert d["term"] == "Performer"

    def test_unknown_term(self, api):
        assert api.get_term_detail("NonexistentThing") is None


class TestTaxonomy:
    def test_performer_subtypes(self, api):
        t = api.get_taxonomy("Performer")
        assert set(t["subtypes_direct"]) == {"System", "Service", "OrganizationType", "PersonRoleType", "Port"}
        assert "ServicePort" in t["subtypes_transitive"]

    def test_guidance_hierarchy(self, api):
        t = api.get_taxonomy("Guidance")
        assert "Rule" in t["subtypes_direct"]
        assert "TechnicalStandard" in t["subtypes_transitive"]

    def test_unknown_type(self, api):
        assert api.get_taxonomy("NonexistentThing") is None


class TestAssociations:
    def test_filter_by_type_is_subtype_aware(self, api):
        # System is-a Performer: querying Performer surfaces associations
        # whose endpoint is System/Service/Port...
        labels = {a["label"] for a in api.get_associations(type_name="Performer")}
        assert "activityPerformedByPerformer" in labels
        assert "partiesToAnAgreement" in labels

    def test_all_binary_associations_have_two_endpoints(self, api):
        for a in api.get_associations():
            assert len(a["endpoints"]) == 2

    def test_filter_by_group(self, api):
        labels = {a["label"] for a in api.get_associations(group_id="01-performer")}
        assert "activityPerformedByPerformer" in labels


class TestViewContent:
    def test_ov5b_content_spec(self, api):
        c = api.get_view_content("OV-5b")
        assert "Activity" in c["necessary_terms"]
        labels = {a["label"] for a in c["necessary_associations"]}
        assert {"activityConsumesResource", "activityPerformedByPerformer",
                "activityProducesResource"} <= labels

    def test_cv2_content_spec_endpoints(self, api):
        c = api.get_view_content("CV-2")
        mapping = {a["label"]: a for a in c["necessary_associations"]}
        assert mapping["activityPartOfCapability"]["endpoint_types"] == ["Activity", "Capability"]

    def test_unknown_view(self, api):
        assert api.get_view_content("NOPE-9") is None


class TestCliJsonEnvelope:
    """End-to-end: the CLI emits the standard {status, data} envelope."""

    def _run(self, *args):
        proc = run_cli(
            ["knowledge", *args, "--json"],
            capture_output=True, text=True,
        )
        assert proc.returncode == 0, proc.stderr
        # stderr must be silent (indexer diagnostics are DM2_DEBUG-gated) so that
        # `2>&1` merged streams stay parseable JSON
        assert proc.stderr == "", f"stderr not clean: {proc.stderr!r}"
        return json.loads(proc.stdout)

    def test_term_envelope(self):
        out = self._run("term", "Activity")
        assert out["status"] == "success"
        assert out["data"]["term"] == "Activity"

    def test_taxonomy_envelope(self):
        out = self._run("taxonomy", "Performer")
        assert "System" in out["data"]["subtypes_direct"]

    def test_content_envelope(self):
        out = self._run("content", "OV-5b")
        labels = {a["label"] for a in out["data"]["necessary_associations"]}
        assert "activityPerformedByPerformer" in labels

    def test_not_found_envelope(self):
        proc = run_cli(
            ["knowledge", "term", "Nope", "--json"],
            capture_output=True, text=True,
        )
        assert proc.returncode == 1
        out = json.loads(proc.stdout)
        assert out["status"] == "error"


class TestPedigreeQueries:
    """`KnowledgeAPI.get_pedigree` / `list_pedigrees` (view provenance)."""

    @staticmethod
    def _project(tmp_path):
        (tmp_path / ".dm2").mkdir()
        (tmp_path / ".dm2" / "config.yaml").write_text("trace:\n  enabled: true\n", encoding="utf-8")
        return tmp_path

    def test_absent_record(self, tmp_path):
        api = KnowledgeAPI(project_root=self._project(tmp_path))
        assert api.get_pedigree("CV-1") is None
        assert api.list_pedigrees() == []

        summary = api.pedigree_summary("CV-1")
        assert summary["pedigree_status"] == "absent"
        assert summary["pedigree_missing"] == ["author", "creation_date", "source"]
        assert summary["confidence"] is None

    def test_get_pedigree_and_summary(self, tmp_path):
        from dm2.core.pedigree import Author, Pedigree, Source
        from dm2.core.pedigree.store import PedigreeStore

        project = self._project(tmp_path)
        PedigreeStore(project).save(Pedigree.new(
            "CV-1",
            author=Author(type="agent-assisted", model="deepseek-v3"),
            source=Source(standard="DoDAF V2.02 Vol 2"),
            reliability="medium",
            confidence=0.8,
        ))

        api = KnowledgeAPI(project_root=project)
        record = api.get_pedigree("CV-1")
        assert record is not None and record.view_id == "CV-1"

        summary = api.pedigree_summary("CV-1")
        assert summary["pedigree_status"] == "complete"
        assert summary["author_type"] == "agent-assisted"
        assert summary["creation_date"]
        assert summary["confidence"] == 0.8

    def test_list_pedigrees_filters_by_author_type(self, tmp_path):
        from dm2.core.pedigree import Author, Pedigree, Source
        from dm2.core.pedigree.store import PedigreeStore

        project = self._project(tmp_path)
        store = PedigreeStore(project)
        store.save(Pedigree.new(
            "CV-1",
            author=Author(type="agent-autonomous"),
            source=Source(standard="DoDAF V2.02 Vol 2"),
            confidence=0.9,
        ))
        store.save(Pedigree.new(
            "OV-2",
            author=Author(type="human"),
            source=Source(standard="DoDAF V2.02 Vol 2"),
        ))

        api = KnowledgeAPI(project_root=project)
        assert sorted(entry["view_id"] for entry in api.list_pedigrees()) == ["CV-1", "OV-2"]

        autonomous = api.list_pedigrees(author_type="agent-autonomous")
        assert [entry["view_id"] for entry in autonomous] == ["CV-1"]
        assert autonomous[0]["confidence"] == 0.9
        assert autonomous[0]["pedigree_status"] == "complete"
        assert autonomous[0]["creation_date"]


class TestChineseSearchRecall:
    """D9: Chinese and multi-token queries must recall the right terms."""

    @pytest.mark.parametrize("query,expected", [
        ("能力", "Capability"),
        ("执行者", "Performer"),
        ("活动", "Activity"),
        ("度量", "Measure"),
        ("项目", "Project"),
        ("系统", "System"),
        ("愿景", "Vision"),
    ])
    def test_exact_chinese_alias_ranks_first(self, api, query, expected):
        results = api.search_terms(query)
        assert results, f"{query} 应至少命中一个术语"
        assert results[0].term == expected

    def test_result_exposes_the_curated_alias(self, api):
        capability = next(r for r in api.search_terms("能力") if r.term == "Capability")
        assert "能力" in capability.zh_aliases
        # standard aliases stay separate from the curated overlay
        assert "能力" not in capability.aliases

    def test_association_reachable_by_chinese_alias(self, api):
        results = api.search_terms("活动属于能力")
        assert results
        assert results[0].term == "activityPartOfCapability"

    def test_group_alias_recalls_group_members(self, api):
        results = api.search_terms("资源流")
        assert results
        assert all("11-resource-flow" in r.groups for r in results)

    def test_multi_token_requires_every_token(self, api):
        both = api.search_terms("能力 活动")
        assert any(r.term == "activityPartOfCapability" for r in both)

        assert api.search_terms("能力 zzzznope") == []

    def test_english_behaviour_is_unchanged(self, api):
        assert any(r.term == "Performer" for r in api.search_terms("Performer"))
        assert api.search_terms("Actor")[0].term == "Performer"
        assert api.search_terms("01-performer")

    def test_cli_envelope_reports_chinese_hits(self):
        from test._cli import run_cli

        proc = run_cli(["knowledge", "search", "资源流", "--json"], capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        assert proc.stderr == "", f"stderr not clean: {proc.stderr!r}"
        out = json.loads(proc.stdout)
        assert out["status"] == "success"
        assert out["data"]["count"] > 0
        # Group-level recall is attributable: every hit belongs to the 资源流 group.
        assert all("11-resource-flow" in r["groups"] for r in out["data"]["results"])
        assert any(r["zh_aliases"] for r in out["data"]["results"])


class TestElementNormalizedSearch:
    """P2: query segments normalize through the data element vocabulary."""

    def test_structural_match_outranks_substring_match(self, api):
        results = api.search_terms("能力 活动")
        terms = [r.term for r in results]
        # 关系术语由词元（capability + activity）命中，应领先纯文本命中
        assert terms[:2] == ["activityMapsToCapabilityType", "activityPartOfCapability"]
        assert terms.index("Activity") > 1

    def test_english_multi_token_gets_the_same_treatment(self, api):
        terms = [r.term for r in api.search_terms("activity capability")]
        assert terms[:2] == ["activityMapsToCapabilityType", "activityPartOfCapability"]

    def test_single_token_alias_still_ranks_first(self, api):
        assert api.search_terms("能力")[0].term == "Capability"
        assert api.search_terms("执行者")[0].term == "Performer"
        assert api.search_terms("类型")[0].term == "Type"

    def test_canonical_name_is_searchable(self, api):
        assert api.search_terms("结束边界类型的度量")[0].term == "measureOfTypeEndBoundaryType"
        assert api.search_terms("国家类型的类型")[0].term == "CountryTypeType"

    def test_result_exposes_the_canonical_name(self, api):
        capability = next(r for r in api.search_terms("能力") if r.term == "Capability")
        assert capability.canonical_zh == "能力"

    def test_segment_without_vocabulary_entry_falls_back_to_substring(self, api):
        # 「资源流」不是词元，走子串兜底 → 召回不回退
        results = api.search_terms("资源流")
        assert results
        assert all("11-resource-flow" in r.groups for r in results)

    def test_cli_envelope_carries_canonical_zh(self):
        from test._cli import run_cli

        proc = run_cli(["knowledge", "search", "能力", "--json"], capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        out = json.loads(proc.stdout)
        assert out["status"] == "success"
        top = out["data"]["results"][0]
        assert top["term"] == "Capability"
        assert top["canonical_zh"] == "能力"


class TestSearchExplanation:
    """P3: order-sensitive pattern matching and explainable hits."""

    def test_pattern_match_beats_structural_match(self, api):
        results = api.search_terms("活动 属于 能力", explain=True)
        assert results
        top = results[0]
        assert top.term == "activityPartOfCapability"
        assert top.match["kind"] == "pattern"
        assert top.match["tier"] == 1
        assert top.match["pattern"] == ["activity", "part", "capability"]

    def test_reversed_query_is_not_a_pattern_match(self, api):
        top = api.search_terms("能力 属于 活动", explain=True)[0]
        assert top.term == "activityPartOfCapability"
        assert top.match["kind"] == "structural"
        assert top.match["pattern"] == []

    def test_every_query_segment_is_explained(self, api):
        top = api.search_terms("活动 属于 能力", explain=True)[0]
        segments = top.match["segments"]
        assert [s["segment"] for s in segments] == ["活动", "属于", "能力"]
        assert all(s["route"] == "token" for s in segments)
        assert [s["matched"] for s in segments] == ["activity", "part", "capability"]

    def test_match_kind_is_from_the_closed_set(self, api):
        allowed = {"exact", "pattern", "structural", "substring", "text"}
        for query in ["能力", "活动 属于 能力", "能力 活动", "资源流", "zzznope"]:
            for result in api.search_terms(query, explain=True):
                assert result.match["kind"] in allowed

    def test_unrecognized_segment_is_routed_to_text(self, api):
        top = api.search_terms("资源流", explain=True)[0]
        assert top.match["kind"] == "text"
        assert top.match["segments"][0]["route"] == "text"

    def test_explanation_is_opt_in(self, api):
        assert api.search_terms("能力")[0].match is None
        assert api.search_terms("能力", explain=True)[0].match is not None

    def test_cli_json_omits_match_without_explain(self):
        from test._cli import run_cli

        proc = run_cli(["knowledge", "search", "能力", "--json"], capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        assert "match" not in json.loads(proc.stdout)["data"]["results"][0]

    def test_cli_explain_json_carries_the_reason(self):
        from test._cli import run_cli

        proc = run_cli(
            ["knowledge", "search", "活动 属于 能力", "--explain", "--json"],
            capture_output=True, text=True,
        )
        assert proc.returncode == 0, proc.stderr
        assert proc.stderr == "", f"stderr not clean: {proc.stderr!r}"
        top = json.loads(proc.stdout)["data"]["results"][0]
        assert top["term"] == "activityPartOfCapability"
        assert top["match"]["kind"] == "pattern"

    def test_cli_explain_human_output_contains_the_reason(self):
        from test._cli import run_cli

        proc = run_cli(
            ["knowledge", "search", "活动 消耗 资源", "--explain"],
            capture_output=True, text=True,
        )
        assert proc.returncode == 0, proc.stderr
        assert "命中理由" in proc.stdout
        assert "activity·consumes·resource" in proc.stdout


class TestAutoNamedNewTerm:
    """P4: a new term with no curated alias is searchable by its composed name."""

    @staticmethod
    def _index(tmp_path, term, canonical_zh, zh_aliases=()):
        entry = {
            "id": f"dodaf:{term}",
            "term": term,
            "definition": "synthetic term used to exercise auto-naming",
            "aliases": [],
            "zh_aliases": list(zh_aliases),
            "groups": [],
            "zh_groups": [],
            "canonical_zh": canonical_zh,
            "association": True,
            "status": "",
            "erd": False,
        }
        (tmp_path / "terms.json").write_text(
            json.dumps([entry], ensure_ascii=False), encoding="utf-8"
        )
        from dm2.kernel.indexer import DM2KnowledgeIndexer

        indexer = DM2KnowledgeIndexer(reference_kb_path=str(tmp_path))
        indexer.load_all()
        return indexer

    def test_searchable_by_its_composed_name(self, tmp_path):
        from dm2.kernel.elements import ElementVocabulary

        vocab = ElementVocabulary.load()
        name = "CapabilityPartOfProject"
        indexer = self._index(tmp_path, name, vocab.compose(name))

        assert [t.term for t in indexer.search_terms("能力属于项目")] == [name]

    def test_searchable_by_a_pattern_query(self, tmp_path):
        from dm2.kernel.elements import ElementVocabulary

        vocab = ElementVocabulary.load()
        name = "CapabilityPartOfProject"
        indexer = self._index(tmp_path, name, vocab.compose(name))

        matches = indexer.match_terms("能力 属于 项目")
        assert [m.term.term for m in matches] == [name]
        assert matches[0].explanation.kind == "pattern"

    def test_compose_cli_reports_the_name_and_the_gap(self):
        proc = run_cli(["knowledge", "compose", "CapabilityType", "--json"],
                       capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        data = json.loads(proc.stdout)["data"]
        assert data["composed"] == "能力类型"
        assert data["composable"] is True

        gap = run_cli(["knowledge", "compose", "ZzzThing", "--json"],
                      capture_output=True, text=True)
        assert gap.returncode == 0, "无法组合是诊断答案，不是命令失败"
        gap_data = json.loads(gap.stdout)["data"]
        assert gap_data["composed"] == ""
        assert gap_data["unregistered"] == ["zzz"]

    def test_compose_cli_human_output_names_the_missing_tokens(self):
        proc = run_cli(["knowledge", "compose", "ZzzThing"],
                       capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        assert "未登记词元" in proc.stdout
        assert "zzz" in proc.stdout
