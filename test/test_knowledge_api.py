"""Tests for the metamodel-grounded Knowledge API (dm2 knowledge ...)."""
import json
import subprocess
import sys

import pytest

from dm2.core.knowledge.api import KnowledgeAPI


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
        proc = subprocess.run(
            [sys.executable, "-m", "dm2.cli.main", "knowledge", *args, "--json"],
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
        proc = subprocess.run(
            [sys.executable, "-m", "dm2.cli.main", "knowledge", "term", "Nope", "--json"],
            capture_output=True, text=True,
        )
        assert proc.returncode == 1
        out = json.loads(proc.stdout)
        assert out["status"] == "error"
