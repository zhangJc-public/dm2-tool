"""View-lifecycle integration with the pedigree gate.

Spec: openspec/changes/add-view-provenance (view-lifecycle delta, view-provenance)
"""

import json

import yaml
from typer.testing import CliRunner

from dm2.cli.main import app
from dm2.core.pedigree import Author, Pedigree, Source
from dm2.core.pedigree.store import PedigreeStore
from dm2.core.views.manager import ViewManager, ViewStatus


def _project(tmp_path, *, trace: bool = True):
    (tmp_path / ".dm2").mkdir(exist_ok=True)
    (tmp_path / ".dm2" / "config.yaml").write_text(
        f"trace:\n  enabled: {'true' if trace else 'false'}\n", encoding="utf-8"
    )
    return tmp_path


def _register(tmp_path, view_id: str = "CV-1") -> ViewManager:
    vm = ViewManager(tmp_path)
    vm.register_view(view_id, output_path="", change_name="demo")
    return vm


def _complete_record(tmp_path, view_id: str = "CV-1") -> Pedigree:
    record = Pedigree.new(
        view_id,
        author=Author(type="agent-assisted"),
        source=Source(standard="DoDAF V2.02 Vol 2"),
    )
    PedigreeStore(tmp_path).save(record)
    return record


def test_registered_view_without_a_record_is_absent(tmp_path):
    _project(tmp_path)
    info = _register(tmp_path).get_view("CV-1")
    assert info.pedigree_status == "absent"
    assert info.pedigree_missing == ["author", "creation_date", "source"]

    state = yaml.safe_load((tmp_path / ".dm2" / "view-state.yaml").read_text(encoding="utf-8"))
    assert state["views"]["CV-1"]["pedigree_status"] == "absent"
    assert state["views"]["CV-1"]["pedigree_missing"] == ["author", "creation_date", "source"]


def test_incomplete_record_reports_only_the_missing_fields(tmp_path):
    _project(tmp_path)
    PedigreeStore(tmp_path).save(Pedigree.from_dict({"view_id": "CV-1", "author": {"type": "human"}}))
    info = _register(tmp_path).get_view("CV-1")
    assert info.pedigree_status == "incomplete"
    assert info.pedigree_missing == ["creation_date", "source"]


def test_try_verify_blocks_an_incomplete_pedigree(tmp_path):
    _project(tmp_path)
    vm = _register(tmp_path)
    decision = vm.try_verify("CV-1")
    assert decision.allowed is False
    assert decision.missing == ["author", "creation_date", "source"]
    assert vm.get_view("CV-1").status == ViewStatus.GENERATED


def test_blocked_transition_is_recorded_on_an_existing_record(tmp_path):
    _project(tmp_path)
    store = PedigreeStore(tmp_path)
    store.save(Pedigree.from_dict({"view_id": "CV-1", "author": {"type": "human"}}))
    vm = _register(tmp_path)

    assert vm.try_verify("CV-1").allowed is False
    record = store.load("CV-1")
    assert [entry.change_description for entry in record.modification_history] == [
        "verified blocked: pedigree incomplete"
    ]


def test_complete_pedigree_promotes_and_records_the_pass(tmp_path):
    _project(tmp_path)
    _complete_record(tmp_path)
    vm = _register(tmp_path)

    decision = vm.try_verify("CV-1")
    assert decision.allowed is True
    assert decision.missing == []
    info = vm.get_view("CV-1")
    assert info.status == ViewStatus.VERIFIED
    assert info.pedigree_status == "complete"

    record = PedigreeStore(tmp_path).load("CV-1")
    assert [entry.change_description for entry in record.modification_history] == [
        "verified: validation passed"
    ]


def test_force_override_promotes_and_leaves_a_trail(tmp_path):
    _project(tmp_path)
    store = PedigreeStore(tmp_path)
    store.save(Pedigree.from_dict({"view_id": "CV-1", "author": {"type": "human"}}))
    vm = _register(tmp_path)

    decision = vm.try_verify("CV-1", force=True)
    assert decision.allowed is True
    assert decision.forced is True
    assert vm.get_view("CV-1").status == ViewStatus.VERIFIED

    record = store.load("CV-1")
    assert record.modification_history[-1].actor == "operator"
    assert record.modification_history[-1].change_description == "verified via --force-pedigree override"


def test_trace_disabled_skips_gating_and_pedigree_writes(tmp_path):
    _project(tmp_path, trace=False)
    vm = _register(tmp_path)

    assert vm.try_verify("CV-1").allowed is True
    assert vm.get_view("CV-1").status == ViewStatus.VERIFIED
    assert not PedigreeStore(tmp_path).directory.exists()


def _cli_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _project(tmp_path)
    vm = ViewManager(tmp_path)
    vm.register_view("CV-1", change_name="demo")
    vm.register_view("OV-2", change_name="demo")
    PedigreeStore(tmp_path).save(Pedigree.from_dict({"view_id": "CV-1", "author": {"type": "human"}}))
    return tmp_path


def test_cli_view_list_json_includes_pedigree_state(tmp_path, monkeypatch):
    _cli_project(tmp_path, monkeypatch)
    result = CliRunner().invoke(app, ["view", "list", "--json"])
    assert result.exit_code == 0, result.stdout
    views = {view["id"]: view for view in json.loads(result.stdout)["data"]["views"]}
    assert views["CV-1"]["pedigree_status"] == "incomplete"
    assert views["CV-1"]["pedigree_missing"] == ["creation_date", "source"]
    assert views["OV-2"]["pedigree_status"] == "absent"


def test_cli_view_list_filters_by_pedigree_status(tmp_path, monkeypatch):
    _cli_project(tmp_path, monkeypatch)
    result = CliRunner().invoke(app, ["view", "list", "--pedigree-status", "incomplete", "--json"])
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)["data"]
    assert [view["id"] for view in data["views"]] == ["CV-1"]
    assert data["count"] == 1


def test_cli_view_list_rejects_an_unknown_pedigree_status(tmp_path, monkeypatch):
    _cli_project(tmp_path, monkeypatch)
    result = CliRunner().invoke(app, ["view", "list", "--pedigree-status", "bogus", "--json"])
    payload = json.loads(result.stdout)
    assert result.exit_code == 1
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "INVALID_PEDIGREE_STATUS"
