"""Unit tests for the Pedigree data model.

Spec: openspec/specs/view-provenance (Pedigree data model / required fields)
"""

from pathlib import Path

import pytest

from dm2.core.pedigree import (
    ABSENT,
    COMPLETE,
    INCOMPLETE,
    Alternative,
    Author,
    DecisionFactor,
    Pedigree,
    PedigreeValidationError,
    Reasoning,
    Source,
    TermReference,
    ValidationIssue,
    ValidationRecord,
    missing_core_fields,
    status,
    trace_enabled,
)


def minimal_pedigree(**overrides) -> Pedigree:
    base = {
        "view_id": "OV-1",
        "pedigree_id": "pid-1",
        "author": Author(type="human"),
        "creation_date": "2026-01-01T00:00:00",
        "source": Source(standard="DoDAF V2.02 Vol 2"),
    }
    base.update(overrides)
    return Pedigree(**base)


def complete_pedigree() -> Pedigree:
    return Pedigree.new(
        "CV-1",
        author=Author(type="agent-assisted", model="deepseek-v3", operator="vano"),
        source=Source(
            standard="DoDAF V2.02 Vol 2",
            section="CV-1 Capability Taxonomy",
            dm2_terms_used=[TermReference(term="Capability", definition_ref="terms.json#Capability")],
        ),
        reasoning=Reasoning(
            summary="Taxonomy derived from the capability data group.",
            decision_factors=[
                DecisionFactor(
                    factor="data group activation: 03-capability",
                    score=0.85,
                    source="dm2 analyze --json",
                )
            ],
            alternatives_considered=[
                Alternative(
                    option="Generate OV-5a instead",
                    rejected_because="the description is capability-centric",
                )
            ],
        ),
        reliability="medium",
        confidence=0.8,
        change="add-view-provenance",
    )


def test_new_populates_required_fields():
    record = complete_pedigree()
    assert record.view_id == "CV-1"
    assert record.pedigree_id
    assert record.creation_date
    assert record.missing_core_fields() == []


def test_yaml_round_trip_is_lossless():
    original = complete_pedigree()
    restored = Pedigree.from_yaml(original.to_yaml())
    assert restored == original
    assert restored.missing_core_fields() == []


def test_strict_flag_is_not_serialized():
    assert "strict" not in complete_pedigree().to_dict()


@pytest.mark.parametrize(
    "overrides, field_name",
    [
        ({"author": None}, "author"),
        ({"creation_date": ""}, "creation_date"),
        ({"source": None}, "source"),
    ],
)
def test_constructor_rejects_missing_core_fields(overrides, field_name):
    with pytest.raises(PedigreeValidationError) as excinfo:
        minimal_pedigree(**overrides)
    assert excinfo.value.field_name == field_name
    assert "OV-1" in str(excinfo.value)


def test_lenient_load_keeps_incomplete_record():
    record = Pedigree.from_dict({"view_id": "SV-1", "reasoning": {"summary": "draft"}})
    assert record.missing_core_fields() == ["author", "creation_date", "source"]
    assert status(record) == INCOMPLETE


def test_incomplete_record_round_trips_without_gaining_fields():
    record = Pedigree.from_dict({"view_id": "SV-1", "reasoning": {"summary": "draft"}})
    restored = Pedigree.from_yaml(record.to_yaml())
    assert restored.missing_core_fields() == ["author", "creation_date", "source"]


def test_status_distinguishes_absent_incomplete_and_complete():
    assert status(None) == ABSENT
    assert missing_core_fields(None) == ["author", "creation_date", "source"]
    assert status(Pedigree.from_dict({"view_id": "X"})) == INCOMPLETE
    assert status(complete_pedigree()) == COMPLETE


@pytest.mark.parametrize("value", [-0.1, 1.5, "high", True])
def test_confidence_must_be_a_fraction(value):
    with pytest.raises(PedigreeValidationError) as excinfo:
        minimal_pedigree(confidence=value)
    assert excinfo.value.field_name == "confidence"


def test_confidence_bool_is_rejected_when_loading():
    with pytest.raises(PedigreeValidationError):
        Pedigree.from_dict({"view_id": "OV-1", "confidence": True})


def test_reliability_is_an_enum():
    with pytest.raises(PedigreeValidationError) as excinfo:
        minimal_pedigree(reliability="certain")
    assert excinfo.value.field_name == "reliability"


def test_author_type_is_an_enum():
    with pytest.raises(PedigreeValidationError) as excinfo:
        minimal_pedigree(author=Author(type="robot"))
    assert excinfo.value.field_name == "author.type"


def test_decision_factor_requires_factor_and_source():
    with pytest.raises(PedigreeValidationError) as excinfo:
        minimal_pedigree(reasoning=Reasoning(decision_factors=[DecisionFactor(factor="", source="dm2 analyze")]))
    assert excinfo.value.field_name == "reasoning.decision_factors[0].factor"

    with pytest.raises(PedigreeValidationError) as excinfo:
        minimal_pedigree(reasoning=Reasoning(decision_factors=[DecisionFactor(factor="f", source="")]))
    assert excinfo.value.field_name == "reasoning.decision_factors[0].source"


def test_alternative_requires_option_and_reason():
    with pytest.raises(PedigreeValidationError) as excinfo:
        minimal_pedigree(reasoning=Reasoning(alternatives_considered=[Alternative(option="", rejected_because="x")]))
    assert excinfo.value.field_name == "reasoning.alternatives_considered[0].option"

    with pytest.raises(PedigreeValidationError):
        minimal_pedigree(reasoning=Reasoning(alternatives_considered=[Alternative(option="x", rejected_because="")]))


def test_validation_issue_severity_is_an_enum():
    with pytest.raises(PedigreeValidationError) as excinfo:
        minimal_pedigree(
            validation=ValidationRecord(issues=[ValidationIssue(rule="R1", severity="fatal", message="m")])
        )
    assert excinfo.value.field_name == "validation.issues[0].severity"


def test_source_term_requires_a_term_name():
    with pytest.raises(PedigreeValidationError) as excinfo:
        minimal_pedigree(source=Source(dm2_terms_used=[TermReference(term="", definition_ref="x")]))
    assert excinfo.value.field_name == "source.dm2_terms_used[0].term"


def test_append_modification_records_date_and_actor():
    record = minimal_pedigree()
    entry = record.append_modification("cli", "view registered")
    assert record.modification_history == [entry]
    assert entry.actor == "cli"
    assert entry.date
    assert entry.change_description == "view registered"


def test_frontmatter_block_is_minimal_and_human_readable():
    record = complete_pedigree()
    block = record.frontmatter_block()
    assert set(block) == {"pedigree_id", "author", "creation_date", "source"}
    assert set(block["source"]) == {"standard", "section", "dm2_terms_used"}
    assert block["pedigree_id"] == record.pedigree_id
    assert block["source"]["dm2_terms_used"][0]["term"] == "Capability"
    assert "reasoning" not in block
    assert "validation" not in block


def test_from_yaml_rejects_a_non_mapping_document():
    with pytest.raises(PedigreeValidationError):
        Pedigree.from_yaml("- just\n- a list\n")


def test_trace_enabled_reads_the_project_switch(tmp_path):
    (tmp_path / ".dm2").mkdir()
    config = tmp_path / ".dm2" / "config.yaml"

    config.write_text("trace:\n  enabled: false\n", encoding="utf-8")
    assert trace_enabled(tmp_path) is False

    config.write_text("trace:\n  enabled: true\n", encoding="utf-8")
    assert trace_enabled(tmp_path) is True


def test_from_yaml_rejects_a_record_without_a_view_id():
    with pytest.raises(PedigreeValidationError) as excinfo:
        Pedigree.from_yaml("")
    assert excinfo.value.field_name == "view_id"


SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent / "src" / "dm2" / "core" / "pedigree" / "schema.yaml"
)
EXAMPLE_PATH = Path(__file__).resolve().parent.parent / "docs" / "examples" / "pedigree-example.yaml"


def test_schema_yaml_documents_every_model_field():
    import dataclasses

    from dm2.core.pedigree import model

    text = SCHEMA_PATH.read_text(encoding="utf-8")
    for name, obj in vars(model).items():
        if name.startswith("_") or not dataclasses.is_dataclass(obj):
            continue
        for field_info in dataclasses.fields(obj):
            if field_info.name == "strict":
                continue  # internal loading flag, never persisted
            assert f"{field_info.name}:" in text, f"{name}.{field_info.name} missing from schema.yaml"


def test_example_pedigree_parses_as_a_complete_record():
    record = Pedigree.from_yaml(EXAMPLE_PATH.read_text(encoding="utf-8"))
    assert record.view_id == "CV-1"
    assert record.missing_core_fields() == []
    assert record.source.dm2_terms_used[0].term == "Capability"
    assert record.validation.ran_R5 is True
