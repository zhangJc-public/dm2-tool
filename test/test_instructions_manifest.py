"""Tests for the DM2 association manifest in view-generation instructions."""
import pytest

from dm2.core.agent.instructions import MANIFEST_MAX_ENTRIES, InstructionBuilder
from dm2.core.knowledge.api import KnowledgeAPI


@pytest.fixture(scope="module")
def builder():
    return InstructionBuilder(KnowledgeAPI())


class TestAssociationManifest:
    def test_ov5b_manifest_has_performer_and_resource_flows(self, builder):
        instr = builder.build_view_instructions("OV-5b", "测试系统")
        labels = {a["label"] for a in instr.association_manifest}
        assert {
            "activityPerformedByPerformer",
            "activityConsumesResource",
            "activityProducesResource",
        } <= labels
        # endpoint types present
        by_label = {a["label"]: a for a in instr.association_manifest}
        assert by_label["activityPerformedByPerformer"]["endpoint_types"] == ["Performer", "Activity"]

    def test_cv2_manifest_has_capability_mapping(self, builder):
        instr = builder.build_view_instructions("CV-2", "能力体系")
        labels = {a["label"] for a in instr.association_manifest}
        assert "activityPartOfCapability" in labels

    def test_manifest_is_bounded(self, builder):
        for vid in ("OV-3", "PV-3", "CV-5"):
            instr = builder.build_view_instructions(vid, "测试")
            assert len(instr.association_manifest) <= MANIFEST_MAX_ENTRIES

    def test_manifest_resolved_entries_carry_endpoints(self, builder):
        instr = builder.build_view_instructions("OV-5b", "测试系统")
        for entry in instr.association_manifest:
            if "endpoint_types" in entry:
                assert len(entry["endpoint_types"]) == 2

    def test_unknown_view_has_empty_manifest(self, builder):
        instr = builder.build_view_instructions("NOPE-9", "测试")
        assert instr.association_manifest == []
