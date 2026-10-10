"""Unit tests for fact-layer capture (`PedigreeRecorder`) and lifecycle events.

Spec: openspec/changes/add-view-provenance (view-provenance / dm2-apply-workflow)
"""

import json

import yaml
from typer.testing import CliRunner

from dm2.cli.main import app
from dm2.core.pedigree import Author, Pedigree, Source
from dm2.core.pedigree.recorder import PedigreeRecorder
from dm2.core.pedigree.store import PedigreeStore
from dm2.core.views.events import ViewEvent
from dm2.core.views.manager import ViewManager, ViewStatus


def _project(tmp_path, *, trace: bool = True):
    (tmp_path / ".dm2").mkdir(exist_ok=True)
    (tmp_path / ".dm2" / "config.yaml").write_text(
        f"trace:\n  enabled: {'true' if trace else 'false'}\n", encoding="utf-8"
    )
    return tmp_path


def _history(tmp_path, view_id: str = "CV-1"):
    record = PedigreeStore(tmp_path).load(view_id)
    return [(entry.actor, entry.change_description) for entry in record.modification_history]


def _complete(view_id: str = "CV-1") -> Pedigree:
    return Pedigree.new(
        view_id,
        author=Author(type="human"),
        source=Source(standard="DoDAF V2.02 Vol 2"),
    )


def test_registration_creates_a_stub_record(tmp_path):
    _project(tmp_path)
    ViewManager(tmp_path).register_view("CV-1", change_name="demo")

    record = PedigreeStore(tmp_path).load("CV-1")
    assert record.creation_date
    assert record.pedigree_id
    assert _history(tmp_path) == [("cli", "view registered")]


def test_registration_fills_a_missing_creation_date(tmp_path):
    _project(tmp_path)
    store = PedigreeStore(tmp_path)
    store.save(Pedigree.from_dict({"view_id": "CV-1", "author": {"type": "human"}}))

    ViewManager(tmp_path).register_view("CV-1", change_name="demo")

    record = store.load("CV-1")
    assert record.creation_date
    assert record.missing_core_fields() == ["source"]


def test_status_transitions_are_recorded_with_the_new_state(tmp_path):
    _project(tmp_path)
    vm = ViewManager(tmp_path)
    vm.register_view("CV-1", change_name="demo")
    vm.update_status("CV-1", ViewStatus.IN_PROGRESS)
    vm.update_status("CV-1", ViewStatus.GENERATED)

    assert _history(tmp_path) == [
        ("cli", "view registered"),
        ("cli", "state: generated → in_progress"),
        ("cli", "state: in_progress → generated"),
    ]


def test_verified_transition_carries_its_outcome_text(tmp_path):
    _project(tmp_path)
    store = PedigreeStore(tmp_path)
    vm = ViewManager(tmp_path)
    vm.register_view("CV-1", change_name="demo")
    store.save(_complete())

    assert vm.try_verify("CV-1").allowed is True
    assert _history(tmp_path) == [("cli", "verified: validation passed")]


def test_force_override_is_recorded_with_the_operator_actor(tmp_path):
    _project(tmp_path)
    store = PedigreeStore(tmp_path)
    vm = ViewManager(tmp_path)
    vm.register_view("CV-1", change_name="demo")
    store.save(Pedigree.from_dict({"view_id": "CV-1", "author": {"type": "human"}}))

    assert vm.try_verify("CV-1", force=True).forced is True
    assert _history(tmp_path)[-1] == ("operator", "verified via --force-pedigree override")


def test_human_edit_is_detected_on_the_next_observation(tmp_path):
    _project(tmp_path)
    view = tmp_path / "CV-1.md"
    view.write_text("# CV-1\n", encoding="utf-8")

    vm = ViewManager(tmp_path)
    vm.register_view("CV-1", output_path=str(view), change_name="demo")
    assert [description for _, description in _history(tmp_path)] == ["view registered"]

    # The first observation only stores the baseline.
    assert vm.recorder.detect_content_change("CV-1", str(view)) is False

    view.write_text("# CV-1 (edited by hand)\n", encoding="utf-8")
    assert vm.recorder.detect_content_change("CV-1", str(view)) is True
    assert _history(tmp_path)[-1] == ("human", "content modified post-generation")

    # Re-baselined: the same content is not reported twice.
    assert vm.recorder.detect_content_change("CV-1", str(view)) is False
    assert [d for _, d in _history(tmp_path)].count("content modified post-generation") == 1


def test_content_change_is_ignored_for_an_unknown_view(tmp_path):
    _project(tmp_path)
    view = tmp_path / "OV-9.md"
    view.write_text("# OV-9\n", encoding="utf-8")
    recorder = PedigreeRecorder(PedigreeStore(tmp_path))
    assert recorder.detect_content_change("OV-9", str(view)) is False
    assert not PedigreeStore(tmp_path).exists("OV-9")


def test_record_modification_appends_an_entry(tmp_path):
    _project(tmp_path)
    recorder = PedigreeRecorder(PedigreeStore(tmp_path))
    path = recorder.record_modification("OV-2", "human", "manual note")
    assert path is not None and path.exists()
    assert _history(tmp_path, "OV-2") == [("human", "manual note")]


def test_trace_disabled_records_nothing(tmp_path):
    _project(tmp_path, trace=False)
    view = tmp_path / "CV-1.md"
    view.write_text("# CV-1\n", encoding="utf-8")

    vm = ViewManager(tmp_path)
    vm.register_view("CV-1", output_path=str(view), change_name="demo")
    vm.update_status("CV-1", ViewStatus.IN_PROGRESS)

    assert not PedigreeStore(tmp_path).directory.exists()
    assert vm.recorder.record_modification("CV-1", "cli", "x") is None
    assert vm.recorder.detect_content_change("CV-1", str(view)) is False


def test_observers_receive_lifecycle_events(tmp_path):
    _project(tmp_path)
    seen = []
    vm = ViewManager(tmp_path)
    vm.add_observer(seen.append)
    vm.register_view("CV-1", output_path="out.md", change_name="demo")
    vm.update_status("CV-1", ViewStatus.IN_PROGRESS)

    assert [event.kind for event in seen] == ["register", "status"]
    assert isinstance(seen[0], ViewEvent)
    assert seen[0].view_id == "CV-1"
    assert seen[0].output_path == "out.md"
    assert seen[0].change_name == "demo"
    assert seen[1].previous_status == "generated"
    assert seen[1].status == "in_progress"
    assert seen[0].at


def test_detached_manager_records_nothing(tmp_path):
    _project(tmp_path)
    vm = ViewManager(tmp_path, attach_recorder=False)
    assert vm.recorder is None
    vm.register_view("CV-1", change_name="demo")
    assert not PedigreeStore(tmp_path).exists("CV-1")


def test_cli_register_opens_the_record(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _project(tmp_path)
    result = CliRunner().invoke(app, ["view", "register", "CV-1", "-c", "demo", "-j"])
    assert result.exit_code == 0, result.stdout
    assert _history(tmp_path) == [("cli", "view registered")]


def test_init_creates_the_pedigree_directory_and_switch(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["init", ".", "-j"])
    assert result.exit_code == 0, result.stdout

    assert (tmp_path / ".dm2" / "pedigree").is_dir()
    assert ".dm2/pedigree" in json.loads(result.stdout)["data"]["directories"]

    config = yaml.safe_load((tmp_path / ".dm2" / "config.yaml").read_text(encoding="utf-8"))
    assert config["trace"]["enabled"] is True
