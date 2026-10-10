"""CLI tests for `dm2 trace` (spec: openspec/changes/add-view-provenance)."""

import json

from typer.testing import CliRunner

from dm2.cli.main import app
from dm2.core.pedigree import Author, Pedigree, Source, TermReference
from dm2.core.pedigree.store import PedigreeStore
from dm2.core.views.manager import ViewManager

REASONING_YAML = """\
source:
  standard: DoDAF V2.02 Vol 2
  section: CV-1 Capability Taxonomy
  dm2_terms_used:
    - term: Capability
      definition_ref: terms.json#Capability
author:
  type: agent-assisted
  model: deepseek-v3
  operator: vano
confidence: 0.8
reliability: medium
reasoning:
  decision_factors:
    - factor: "data group activation: 03-capability"
      score: 0.85
      source: "dm2 analyze --json"
  alternatives_considered:
    - option: "Generate OV-5a instead"
      rejected_because: "capability-centric description"
known_limitations:
  - "术语别名未逐一核对"
"""


def _project(tmp_path, monkeypatch, *, trace: bool = True, recorder: bool = True):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".dm2").mkdir()
    (tmp_path / ".dm2" / "config.yaml").write_text(
        f"trace:\n  enabled: {'true' if trace else 'false'}\n", encoding="utf-8"
    )
    ViewManager(tmp_path, attach_recorder=recorder).register_view("CV-1", change_name="demo")
    return tmp_path


def _run(*args, stdin: str = ""):
    argv = ["trace", *args]
    if "--json" not in argv:
        argv.append("--json")
    result = CliRunner().invoke(app, argv, input=stdin or None)
    assert result.stdout, "expected a JSON envelope on stdout"
    return result, json.loads(result.stdout)


def _complete(view_id: str = "CV-1") -> Pedigree:
    return Pedigree.new(
        view_id,
        author=Author(type="human", operator="vano"),
        source=Source(
            standard="DoDAF V2.02 Vol 2",
            dm2_terms_used=[TermReference(term="Capability", definition_ref="terms.json#Capability")],
        ),
        reliability="medium",
        confidence=0.8,
    )


def test_record_with_summary_creates_a_record(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    result, payload = _run("record", "CV-1", "--summary", "capability taxonomy")
    assert result.exit_code == 0, result.stdout

    data = payload["data"]
    assert data["pedigree_status"] == "incomplete"
    assert data["pedigree_missing"] == ["author", "source"]
    assert data["reasoning_recorded"] is True

    record = PedigreeStore(tmp_path).load("CV-1")
    assert record.reasoning.summary == "capability taxonomy"
    assert record.creation_date
    assert record.pedigree_id
    assert record.modification_history[-1].actor == "agent"


def test_record_requires_some_input(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    result, payload = _run("record", "CV-1")
    assert result.exit_code == 1
    assert payload["error"]["code"] == "MISSING_ARG"


def test_reasoning_file_supplies_source_and_author(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    file = tmp_path / "reason.yaml"
    file.write_text(REASONING_YAML, encoding="utf-8")

    result, payload = _run("record", "CV-1", "--reasoning-file", str(file))
    assert result.exit_code == 0, result.stdout
    assert payload["data"]["pedigree_status"] == "complete"

    record = PedigreeStore(tmp_path).load("CV-1")
    assert record.author.type == "agent-assisted"
    assert record.source.standard == "DoDAF V2.02 Vol 2"
    assert record.source.dm2_terms_used[0].term == "Capability"
    assert record.reasoning.decision_factors[0].source == "dm2 analyze --json"
    assert record.reasoning.alternatives_considered[0].option == "Generate OV-5a instead"
    assert record.known_limitations == ["术语别名未逐一核对"]
    assert record.confidence == 0.8
    assert record.reliability == "medium"


def test_stdin_merge_only_touches_supplied_fields(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    store = PedigreeStore(tmp_path)
    store.save(_complete())

    result, payload = _run("record", "CV-1", "--stdin", stdin="reasoning:\n  summary: from stdin\n")
    assert result.exit_code == 0, result.stdout

    record = store.load("CV-1")
    assert record.reasoning.summary == "from stdin"
    assert record.author.type == "human"
    assert record.source.standard == "DoDAF V2.02 Vol 2"


def test_pedigree_id_is_stable_across_updates(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    _, first = _run("record", "CV-1", "--summary", "first pass")
    _, second = _run("record", "CV-1", "--summary", "second pass")
    assert first["data"]["pedigree_id"] == second["data"]["pedigree_id"]

    record = PedigreeStore(tmp_path).load("CV-1")
    assert record.reasoning.summary == "second pass"
    assert [entry.change_description for entry in record.modification_history] == [
        "view registered",
        "reasoning recorded",
        "reasoning recorded",
    ]


def test_malformed_decision_factor_is_rejected_without_writing(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    before = PedigreeStore(tmp_path).load("CV-1").to_yaml()
    bad = "reasoning:\n  decision_factors:\n    - factor: x\n"
    result, payload = _run("record", "CV-1", "--stdin", stdin=bad)
    assert result.exit_code == 1
    assert payload["error"]["code"] == "INVALID_ARG"
    assert "decision_factors[0].source" in payload["error"]["message"]
    assert PedigreeStore(tmp_path).load("CV-1").to_yaml() == before


def test_conflicting_input_flags_are_rejected(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    file = tmp_path / "reason.yaml"
    file.write_text(REASONING_YAML, encoding="utf-8")
    result, payload = _run("record", "CV-1", "--stdin", "--reasoning-file", str(file))
    assert result.exit_code == 1
    assert payload["error"]["code"] == "INVALID_ARG"


def test_missing_reasoning_file_is_reported(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    result, payload = _run("record", "CV-1", "--reasoning-file", str(tmp_path / "nope.yaml"))
    assert result.exit_code == 1
    assert payload["error"]["code"] == "FILE_NOT_FOUND"


def test_non_mapping_yaml_is_rejected(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    result, payload = _run("record", "CV-1", "--stdin", stdin="- a\n- b\n")
    assert result.exit_code == 1
    assert payload["error"]["code"] == "INVALID_ARG"


def test_trace_disabled_refuses_writes(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch, trace=False)
    result, payload = _run("record", "CV-1", "--summary", "x")
    assert payload["error"]["code"] == "TRACE_DISABLED"
    assert not PedigreeStore(tmp_path).exists("CV-1")


def test_show_reports_an_absent_record(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    _, payload = _run("show", "OV-9")
    data = payload["data"]
    assert data["pedigree"] is None
    assert data["pedigree_status"] == "absent"
    assert data["pedigree_missing"] == ["author", "creation_date", "source"]


def test_show_human_mode_prints_the_record(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    _run("record", "CV-1", "--summary", "capability taxonomy")
    result = CliRunner().invoke(app, ["trace", "show", "CV-1"])
    assert result.exit_code == 0
    assert "view_id: CV-1" in result.stdout
    assert "capability taxonomy" in result.stdout


def test_lineage_requires_exactly_one_criterion(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    result, payload = _run("lineage")
    assert result.exit_code == 1
    assert payload["error"]["code"] == "INVALID_ARG"

    result, payload = _run("lineage", "--term", "Capability", "--capability", "X")
    assert result.exit_code == 1
    assert payload["error"]["code"] == "INVALID_ARG"


def test_lineage_matches_terms_case_insensitively_and_groups_by_change(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    PedigreeStore(tmp_path).save(_complete())

    _, payload = _run("lineage", "--term", "capability")
    data = payload["data"]
    assert data["criterion"] == "term"
    assert data["count"] == 1
    assert data["views"][0]["view_id"] == "CV-1"
    assert data["views"][0]["change"] == "demo"
    assert data["views"][0]["pedigree_status"] == "complete"
    assert data["by_change"] == {"demo": ["CV-1"]}


def test_lineage_capability_matches_reasoning_summary(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    record = _complete()
    record.reasoning.summary = "Multi-Task Scheduling across nodes"
    PedigreeStore(tmp_path).save(record)

    _, payload = _run("lineage", "--capability", "multi-task scheduling")
    assert payload["data"]["count"] == 1
    assert payload["data"]["views"][0]["view_id"] == "CV-1"


def test_lineage_capability_matches_view_frontmatter(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    view_file = tmp_path / "CV-1.md"
    view_file.write_text("---\ncapabilities:\n  - Multi-Task Scheduling\n---\n# CV-1\n", encoding="utf-8")
    ViewManager(tmp_path).register_view("CV-1", output_path=str(view_file), change_name="demo")
    PedigreeStore(tmp_path).save(_complete())

    _, payload = _run("lineage", "--capability", "Multi-Task Scheduling")
    assert payload["data"]["count"] == 1


def test_lineage_falls_back_to_the_change_directory(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    views_dir = tmp_path / "dm2-changes" / "legacy" / "views"
    views_dir.mkdir(parents=True)
    (views_dir / "SV-1.md").write_text("# SV-1\n", encoding="utf-8")
    PedigreeStore(tmp_path).save(_complete("SV-1"))

    _, payload = _run("lineage", "--term", "Capability")
    assert payload["data"]["views"][0]["change"] == "legacy"


def test_lineage_without_matches_returns_an_empty_result(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    PedigreeStore(tmp_path).save(_complete())
    _, payload = _run("lineage", "--term", "Performer")
    assert payload["data"]["count"] == 0
    assert payload["data"]["views"] == []
    assert payload["data"]["by_change"] == {}


def test_migrate_stamps_absent_statuses_without_creating_records(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch, recorder=False)
    result, payload = _run("migrate")
    assert result.exit_code == 0
    assert payload["data"]["views"] == {"CV-1": "absent"}
    assert payload["data"]["summary"] == {"absent": 1}
    assert not PedigreeStore(tmp_path).directory.exists()
