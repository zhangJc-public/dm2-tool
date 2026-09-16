"""Tests for MetamodelConformanceChecker rules (fixture notes per rule)."""
import pytest

from dm2.reasoning.conformance import MetamodelConformanceChecker
from dm2.reasoning.consistency import IssueSeverity


@pytest.fixture(scope="module")
def checker():
    return MetamodelConformanceChecker()


def _by_type(issues):
    return {i.issue_type: i for i in issues}


class TestUnknownTerm:
    def test_unknown_dm2_type_flagged_with_suggestion(self, checker):
        issues = checker.check_notes({"note1": {"dm2-type": "Performr"}})
        d = _by_type(issues)
        assert "unknown-term" in d
        assert d["unknown-term"].severity == IssueSeverity.WARNING
        assert d["unknown-term"].suggestion == "最接近的标准术语: Performer"

    def test_known_term_passes(self, checker):
        issues = checker.check_notes({"note1": {"dm2-type": "System"}})
        assert "unknown-term" not in _by_type(issues)

    def test_note_without_dm2_type_is_skipped(self, checker):
        issues = checker.check_notes({"note1": {"name": "x"}})
        assert issues == []


class TestTypeLayer:
    def test_individual_layer_on_unambiguous_powertype(self, checker):
        # CapabilityType only ever appears as powertype
        issues = checker.check_notes({"note2": {"dm2-type": "CapabilityType", "dm2-layer": "Individual"}})
        d = _by_type(issues)
        assert d["type-layer"].severity == IssueSeverity.INFO
        assert "Capability" in d["type-layer"].suggestion

    def test_type_layer_on_unambiguous_individual(self, checker):
        # Capability only ever appears as individual
        issues = checker.check_notes({"note2": {"dm2-type": "Capability", "dm2-layer": "Type"}})
        assert "type-layer" in _by_type(issues)

    def test_consistent_layer_passes(self, checker):
        issues = checker.check_notes({"note2": {"dm2-type": "Capability", "dm2-layer": "Individual"}})
        assert "type-layer" not in _by_type(issues)

    def test_cyclic_pair_names_are_ambiguous(self, checker):
        # Organization↔OrganizationType pairs exist in both directions:
        # neither layer is a contradiction
        issues = checker.check_notes({"note2": {"dm2-type": "Organization", "dm2-layer": "Individual"}})
        assert "type-layer" not in _by_type(issues)
        issues = checker.check_notes({"note2": {"dm2-type": "OrganizationType", "dm2-layer": "Individual"}})
        assert "type-layer" not in _by_type(issues)


class TestUnknownRelation:
    def test_unknown_slot_suggests_closest_catalog_label(self, checker):
        issues = checker.check_notes({
            "note3": {"dm2-type": "Performer",
                      "relationships": {"activityPerformedByPerformr": []}},
        })
        d = _by_type(issues)
        assert d["unknown-relation"].severity == IssueSeverity.WARNING
        assert "activityPerformedByPerformer" in d["unknown-relation"].suggestion

    def test_catalog_slot_passes(self, checker):
        issues = checker.check_notes({
            "note3": {"dm2-type": "Performer",
                      "relationships": {"activityPerformedByPerformer": []}},
        })
        assert "unknown-relation" not in _by_type(issues)


class TestEndpointType:
    def test_subtype_endpoint_is_legal(self, checker):
        # System is-a Performer: legal in activityPerformedByPerformer
        notes = {
            "sys": {"dm2-type": "System",
                    "relationships": {"activityPerformedByPerformer": ["act1"]}},
            "act1": {"dm2-type": "Activity"},
        }
        issues = checker.check_notes(notes)
        assert "endpoint-type" not in _by_type(issues)

    def test_endpoint_mismatch_is_error(self, checker):
        # Organization cannot consume resources: activityConsumesResource
        # expects Activity on the consumer endpoint
        notes = {
            "org": {"dm2-type": "Organization",
                    "relationships": {"activityConsumesResource": ["res1"]}},
            "res1": {"dm2-type": "Resource"},
        }
        issues = checker.check_notes(notes)
        d = _by_type(issues)
        assert d["endpoint-type"].severity == IssueSeverity.ERROR
        assert "activityConsumesResource" in d["endpoint-type"].message

    def test_target_mismatch_is_error(self, checker):
        # Performer performs Activity; linking to a Resource note is an error
        notes = {
            "perf": {"dm2-type": "Performer",
                     "relationships": {"activityPerformedByPerformer": ["res1"]}},
            "res1": {"dm2-type": "Resource"},
        }
        issues = checker.check_notes(notes)
        assert "endpoint-type" in _by_type(issues)

    def test_unresolvable_target_is_skipped(self, checker):
        notes = {
            "perf": {"dm2-type": "Performer",
                     "relationships": {"activityPerformedByPerformer": ["free text"]}},
        }
        issues = checker.check_notes(notes)
        assert "endpoint-type" not in _by_type(issues)


class TestViewRequired:
    def test_ov5b_missing_associations_warned(self, checker):
        notes = {
            "act": {"dm2-type": "Activity",
                    "relationships": {"activityConsumesResource": []}},
        }
        issues = checker.check_view_required("OV-5b", notes)
        d = _by_type(issues)
        assert d["required-association"].severity == IssueSeverity.WARNING
        for label in ("activityPerformedByPerformer", "activityProducesResource"):
            assert label in d["required-association"].suggestion

    def test_complete_data_passes(self, checker):
        notes = {
            "act": {"dm2-type": "Activity",
                    "relationships": {"activityConsumesResource": [],
                                      "activityPerformedByPerformer": [],
                                      "activityProducesResource": []}},
        }
        assert checker.check_view_required("OV-5b", notes) == []

    def test_unknown_view(self, checker):
        assert checker.check_view_required("NOPE-9", {}) == []


class TestCollectFrontmatters:
    def test_collect_from_markdown_files(self, checker, tmp_path):
        (tmp_path / "note.md").write_text(
            "---\ndm2-type: System\ndm2-layer: Individual\nrelationships:\n"
            "  activityPerformedByPerformer: []\n---\nbody\n",
            encoding="utf-8",
        )
        (tmp_path / "plain.md").write_text("# no frontmatter\n", encoding="utf-8")
        notes = checker.collect_note_frontmatters([tmp_path / "note.md", tmp_path / "plain.md"])
        assert set(notes) == {"note"}
        assert notes["note"]["dm2-type"] == "System"
