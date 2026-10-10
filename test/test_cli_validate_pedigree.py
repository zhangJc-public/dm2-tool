"""`dm2 validate` integration with pedigree persistence and the verified gate.

Spec: openspec/changes/add-view-provenance (view-validation delta)
"""

import json

from typer.testing import CliRunner

from dm2.cli.main import app
from dm2.core.pedigree import Author, Pedigree, Source
from dm2.core.pedigree.store import PedigreeStore
from dm2.core.views.manager import ViewManager, ViewStatus


def _validate_project(tmp_path, monkeypatch, pedigree=None, *, trace: bool = True):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".dm2").mkdir()
    (tmp_path / ".dm2" / "config.yaml").write_text(
        f"trace:\n  enabled: {'true' if trace else 'false'}\n", encoding="utf-8"
    )
    views_dir = tmp_path / "dm2-changes" / "demo" / "views"
    views_dir.mkdir(parents=True)
    (views_dir / "CV-1.md").write_text("---\nid: CV-1\n---\n# CV-1\n", encoding="utf-8")

    vm = ViewManager(tmp_path)
    vm.register_view("CV-1", output_path=str(views_dir / "CV-1.md"), change_name="demo")
    if pedigree is not None:
        PedigreeStore(tmp_path).save(pedigree)
    return tmp_path


def _run(*args: str):
    result = CliRunner().invoke(app, ["validate", *args, "--json"])
    assert result.stdout, "expected a JSON envelope on stdout"
    return result, json.loads(result.stdout)


def _complete(view_id: str = "CV-1") -> Pedigree:
    return Pedigree.new(
        view_id,
        author=Author(type="agent-assisted"),
        source=Source(standard="DoDAF V2.02 Vol 2"),
    )


def test_validate_persists_validation_into_an_existing_pedigree(tmp_path, monkeypatch):
    _validate_project(tmp_path, monkeypatch, _complete())
    result, payload = _run("CV-1", "--change", "demo")
    assert result.exit_code == 0, result.stdout
    data = payload["data"]
    assert data["pedigree_updated"] is True
    assert data["verified"] is True
    assert ViewManager(tmp_path).get_view("CV-1").status == ViewStatus.VERIFIED

    record = PedigreeStore(tmp_path).load("CV-1")
    assert record.validation.last_validated
    assert all(getattr(record.validation, f"ran_R{index}") for index in range(1, 6))
    assert [entry.change_description for entry in record.modification_history] == [
        "verified: validation passed"
    ]


def test_validate_persists_suggested_fixes(tmp_path, monkeypatch):
    _validate_project(tmp_path, monkeypatch, _complete())
    _, payload = _run("CV-1", "--change", "demo")
    reported = [issue for issue in payload["data"]["issues"] if issue["suggestion"]]
    assert reported, "CV-1 has necessary associations, so R5 reports a fix suggestion"

    record = PedigreeStore(tmp_path).load("CV-1")
    persisted = [issue for issue in record.validation.issues if issue.suggested_fix]
    assert persisted, "machine-parseable suggestions must reach the pedigree"
    assert persisted[0].rule == "R5"


def test_validate_blocks_verified_and_reports_the_gap(tmp_path, monkeypatch):
    _validate_project(tmp_path, monkeypatch, Pedigree.from_dict({"view_id": "CV-1"}))
    _, payload = _run("CV-1", "--change", "demo")
    data = payload["data"]
    assert data["verified"] is False
    assert any(issue["type"] == "pedigree" and issue["severity"] == "error" for issue in data["issues"])
    assert ViewManager(tmp_path).get_view("CV-1").status == ViewStatus.GENERATED

    record = PedigreeStore(tmp_path).load("CV-1")
    assert any(issue.rule == "pedigree" for issue in record.validation.issues)
    assert [entry.change_description for entry in record.modification_history] == [
        "verified blocked: pedigree incomplete"
    ]


def test_validate_never_creates_a_missing_pedigree(tmp_path, monkeypatch):
    _validate_project(tmp_path, monkeypatch, None)
    # Registration opens a stub; drop it to model a legacy view without a record.
    PedigreeStore(tmp_path).delete("CV-1")
    _, payload = _run("CV-1", "--change", "demo")
    data = payload["data"]
    assert data["pedigree_updated"] is False
    assert not PedigreeStore(tmp_path).exists("CV-1")
    assert data["verified"] is False


def test_force_pedigree_overrides_the_gate_and_is_recorded(tmp_path, monkeypatch):
    _validate_project(tmp_path, monkeypatch, Pedigree.from_dict({"view_id": "CV-1"}))
    _, payload = _run("CV-1", "--change", "demo", "--force-pedigree")
    assert payload["data"]["verified"] is True
    assert ViewManager(tmp_path).get_view("CV-1").status == ViewStatus.VERIFIED

    record = PedigreeStore(tmp_path).load("CV-1")
    assert record.modification_history[-1].change_description == "verified via --force-pedigree override"


def test_trace_disabled_skips_persistence_and_gating(tmp_path, monkeypatch):
    _validate_project(tmp_path, monkeypatch, Pedigree.from_dict({"view_id": "CV-1"}), trace=False)
    _, payload = _run("CV-1", "--change", "demo")
    data = payload["data"]
    assert data["pedigree_updated"] is False
    assert data["verified"] is True
    assert ViewManager(tmp_path).get_view("CV-1").status == ViewStatus.VERIFIED

    record = PedigreeStore(tmp_path).load("CV-1")
    assert record.validation.last_validated is None
    assert record.modification_history == []


def test_validate_reports_missing_views_as_before(tmp_path, monkeypatch):
    _validate_project(tmp_path, monkeypatch, _complete())
    result, payload = _run("OV-9", "--change", "demo")
    assert result.exit_code == 0
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "VIEW_NOT_FOUND"
