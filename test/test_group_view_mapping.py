"""Regression tests for dm2-reference/group-to-views.yaml

Validates the data-group → DoDAF view mapping against views.yaml and the
evidence-basis conventions established in change `repair-group-view-mapping`
(derived from the DoDAF 2.02 DM2 Data Dictionary monster matrix analysis).
"""
from pathlib import Path

import pytest
import yaml

REFERENCE_ROOT = Path(__file__).parent.parent / "dm2-reference"
MAPPING_PATH = REFERENCE_ROOT / "group-to-views.yaml"
VIEWS_PATH = REFERENCE_ROOT / "core" / "views.yaml"

# Meta views delivered through the view dependency graph, not activation.
META_VIEWS = {"AV-1", "AV-2"}
# Entries kept by practitioner judgment without monster-matrix support.
PRACTICE_ALLOWLIST = {
    ("07-location", "OV-1"),
    ("07-location", "OV-2"),
}


@pytest.fixture(scope="module")
def mapping():
    return yaml.safe_load(MAPPING_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def view_ids():
    data = yaml.safe_load(VIEWS_PATH.read_text(encoding="utf-8"))
    return {v["id"] for v in data["views"]}


def _entries(mapping):
    """Yield (group_id, view_id, basis) for every concrete mapping entry."""
    for group in mapping["groups"]:
        for entry in group.get("group_views", []):
            yield group["id"], entry["id"], entry.get("basis")


class TestMappingIdsExist:
    def test_every_mapping_id_exists_in_views_yaml(self, mapping, view_ids):
        """Dead IDs (e.g. the former 'SvcV-3') must not exist."""
        dead = [
            (gid, vid)
            for gid, vid, _ in _entries(mapping)
            if vid != "All" and vid not in view_ids
        ]
        assert dead == [], f"Mapping entries reference unknown view IDs: {dead}"

    def test_svcv3_split_into_3a_3b(self, mapping, view_ids):
        """The dead 'SvcV-3' ID is replaced by the real SvcV-3a / SvcV-3b."""
        entries = {(gid, vid) for gid, vid, _ in _entries(mapping)}
        assert ("08-services", "SvcV-3") not in entries
        assert ("08-services", "SvcV-3a") in entries
        assert ("08-services", "SvcV-3b") in entries


class TestCoverage:
    def test_every_non_meta_view_is_claimed(self, mapping, view_ids):
        """No DoDAF view may be invisible to data-group activation."""
        claimed = {vid for _, vid, _ in _entries(mapping) if vid != "All"}
        unclaimed = (view_ids - META_VIEWS) - claimed
        assert unclaimed == set(), f"Views claimed by no data group: {sorted(unclaimed)}"

    def test_former_blind_spots_are_covered(self, mapping):
        """Views that were unclaimed before the repair must now be claimed."""
        claimed = {vid for _, vid, _ in _entries(mapping) if vid != "All"}
        former_blind_spots = {
            "OV-6b", "OV-6c",
            "SV-1", "SV-3", "SV-5a", "SV-5b", "SV-8", "SV-9", "SV-10b", "SV-10c",
            "SvcV-3a", "SvcV-3b", "StdV-2",
        }
        missing = former_blind_spots - claimed
        assert missing == set(), f"Former blind spots still unclaimed: {sorted(missing)}"


class TestEvidenceBasis:
    def test_every_entry_has_valid_basis(self, mapping):
        missing = [
            (gid, vid)
            for gid, vid, basis in _entries(mapping)
            if vid != "All" and basis not in ("matrix", "practice")
        ]
        assert missing == [], f"Entries missing a valid basis field: {missing}"

    def test_practice_entries_match_allowlist(self, mapping):
        practice = {
            (gid, vid) for gid, vid, basis in _entries(mapping) if basis == "practice"
        }
        assert practice == PRACTICE_ALLOWLIST, (
            f"practice entries differ from documented allow-list: "
            f"unexpected={sorted(practice - PRACTICE_ALLOWLIST)}, "
            f"missing={sorted(PRACTICE_ALLOWLIST - practice)}"
        )


class TestRulesModelAttribution:
    def test_ov6a_belongs_to_rules_not_guidance(self, mapping):
        entries = {(gid, vid) for gid, vid, _ in _entries(mapping)}
        assert ("10-rules", "OV-6a") in entries
        assert ("05-guidance", "OV-6a") not in entries

    def test_rules_model_views_together(self, mapping):
        """The three rules-model views share the Rules group."""
        rules_views = {
            vid for gid, vid, _ in _entries(mapping) if gid == "10-rules"
        }
        assert {"OV-6a", "SV-10a", "SvcV-10a"} <= rules_views
