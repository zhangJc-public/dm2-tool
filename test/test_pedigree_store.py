"""Integration tests for PedigreeStore — atomic YAML storage under .dm2/pedigree/."""

import pytest

from dm2.core.pedigree import Author, Pedigree, Source
from dm2.core.pedigree.store import PedigreeStore


def _project(tmp_path):
    (tmp_path / ".dm2").mkdir()
    (tmp_path / ".dm2" / "config.yaml").write_text("trace:\n  enabled: true\n", encoding="utf-8")
    return tmp_path


def _pedigree(view_id: str = "CV-1") -> Pedigree:
    return Pedigree.new(
        view_id,
        author=Author(type="agent-assisted", model="deepseek-v3"),
        source=Source(standard="DoDAF V2.02 Vol 2", section="CV-1"),
    )


def test_load_returns_none_without_creating_directories(tmp_path):
    store = PedigreeStore(_project(tmp_path))
    assert store.load("CV-1") is None
    assert not store.directory.exists()
    assert store.list_all() == []


def test_save_then_load_round_trips(tmp_path):
    store = PedigreeStore(_project(tmp_path))
    record = _pedigree()
    path = store.save(record)
    assert path == store.path_for("CV-1")
    assert path.exists()
    assert store.exists("CV-1")
    assert store.load("CV-1") == record


def test_save_overwrites_the_previous_record(tmp_path):
    store = PedigreeStore(_project(tmp_path))
    record = _pedigree()
    store.save(record)
    record.confidence = 0.4
    record.append_modification("cli", "view registered")
    store.save(record)
    loaded = store.load("CV-1")
    assert loaded.confidence == 0.4
    assert [entry.actor for entry in loaded.modification_history] == ["cli"]


def test_save_leaves_no_temporary_files_behind(tmp_path):
    store = PedigreeStore(_project(tmp_path))
    store.save(_pedigree())
    assert [path.name for path in store.directory.iterdir()] == ["CV-1.yaml"]


def test_list_all_is_sorted(tmp_path):
    store = PedigreeStore(_project(tmp_path))
    store.save(_pedigree("OV-1"))
    store.save(_pedigree("CV-1"))
    assert store.list_all() == ["CV-1", "OV-1"]


def test_delete_reports_whether_a_file_was_removed(tmp_path):
    store = PedigreeStore(_project(tmp_path))
    store.save(_pedigree())
    assert store.delete("CV-1") is True
    assert store.delete("CV-1") is False
    assert store.load("CV-1") is None


def test_corrupt_yaml_is_treated_as_absent(tmp_path):
    store = PedigreeStore(_project(tmp_path))
    store.directory.mkdir(parents=True)
    store.path_for("CV-1").write_text("view_id: [unclosed\n", encoding="utf-8")
    assert store.load("CV-1") is None


def test_non_mapping_record_is_treated_as_absent(tmp_path):
    store = PedigreeStore(_project(tmp_path))
    store.directory.mkdir(parents=True)
    store.path_for("CV-1").write_text("- just\n- a list\n", encoding="utf-8")
    assert store.load("CV-1") is None


def test_incomplete_record_loads_as_incomplete(tmp_path):
    store = PedigreeStore(_project(tmp_path))
    store.directory.mkdir(parents=True)
    store.path_for("SV-1").write_text("reasoning:\n  summary: draft\n", encoding="utf-8")
    record = store.load("SV-1")
    assert record is not None
    assert record.view_id == "SV-1"
    assert record.missing_core_fields() == ["author", "creation_date", "source"]


def test_filename_is_the_authoritative_view_id(tmp_path):
    store = PedigreeStore(_project(tmp_path))
    store.directory.mkdir(parents=True)
    store.path_for("OV-1").write_text(
        "view_id: WRONG\nauthor:\n  type: human\ncreation_date: '2026-01-01'\n"
        "source:\n  standard: DoDAF V2.02 Vol 2\n",
        encoding="utf-8",
    )
    record = store.load("OV-1")
    assert record.view_id == "OV-1"


def test_corrupt_record_diagnostic_is_debug_gated(tmp_path, capsys, monkeypatch):
    store = PedigreeStore(_project(tmp_path))
    store.directory.mkdir(parents=True)
    store.path_for("CV-1").write_text("- just\n- a list\n", encoding="utf-8")

    monkeypatch.delenv("DM2_DEBUG", raising=False)
    assert store.load("CV-1") is None
    assert capsys.readouterr().err == ""

    monkeypatch.setenv("DM2_DEBUG", "1")
    assert store.load("CV-1") is None
    assert "CV-1" in capsys.readouterr().err


@pytest.mark.parametrize("view_id", ["CV-1", "OV-5b", "SvcV-4"])
def test_path_for_uses_the_view_id_as_filename(tmp_path, view_id):
    store = PedigreeStore(_project(tmp_path))
    assert store.path_for(view_id).name == f"{view_id}.yaml"
