"""CLI tests for `dm2 audit` / `dm2 audit-report` (spec: audit-report capability)."""

import json
from datetime import date

from typer.testing import CliRunner

from dm2.cli.main import app
from dm2.core.pedigree import Author, Pedigree, Reasoning, Source
from dm2.core.pedigree.store import PedigreeStore
from dm2.core.views.manager import ViewManager


def _project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".dm2").mkdir()
    (tmp_path / ".dm2" / "config.yaml").write_text("trace:\n  enabled: true\n", encoding="utf-8")
    ViewManager(tmp_path).register_view("CV-1", change_name="demo")
    return tmp_path


def _run(*args):
    result = CliRunner().invoke(app, list(args))
    assert result.stdout, "expected a JSON envelope on stdout"
    return result, json.loads(result.stdout)


def _complete(view_id: str = "CV-1", confidence: float = 0.8) -> Pedigree:
    return Pedigree.new(
        view_id,
        author=Author(type="agent-assisted", model="deepseek-v3", operator="vano"),
        source=Source(standard="DoDAF V2.02 Vol 2", section="CV-1 Capability Taxonomy"),
        reasoning=Reasoning(summary="capability taxonomy"),
        reliability="medium",
        confidence=confidence,
    )


def test_audit_writes_a_markdown_report_with_every_section(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    store = PedigreeStore(tmp_path)
    record = _complete()
    record.append_modification("cli", "view registered")
    store.save(record)

    result = CliRunner().invoke(app, ["audit", "CV-1"])
    assert result.exit_code == 0, result.stdout
    assert "## 作者与时间" in result.stdout
    assert "Agent 自述、未经验证" in result.stdout

    path = tmp_path / ".dm2" / "audit" / "CV-1-audit.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for section in (
        "## 作者与时间",
        "## 标准引用（Standard Reference）",
        "## 理由摘要",
        "## 决策因素",
        "## 备选方案",
        "## 修改历史",
        "## 校验历史",
        "## 已知局限",
    ):
        assert section in text
    assert "view registered" in text


def test_audit_json_shape_and_output_path(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    PedigreeStore(tmp_path).save(_complete())

    result, payload = _run("audit", "CV-1", "--json")
    assert result.exit_code == 0
    data = payload["data"]
    assert data["view_id"] == "CV-1"
    assert data["lifecycle_state"] == "generated"
    assert data["generated_at"]
    assert data["pedigree_status"] == "complete"
    assert data["pedigree"]["reasoning"]["summary"] == "capability taxonomy"
    assert data["output_path"].endswith("CV-1-audit.md")


def test_audit_reports_a_missing_record(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    result, payload = _run("audit", "OV-9", "--json")
    assert result.exit_code == 0
    assert payload["data"]["pedigree"] is None
    assert payload["data"]["pedigree_status"] == "absent"

    text = (tmp_path / ".dm2" / "audit" / "OV-9-audit.md").read_text(encoding="utf-8")
    assert "No pedigree record found for view OV-9" in text
    assert "dm2 trace record OV-9" in text


def test_audit_marks_an_unrecorded_standard_reference(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    PedigreeStore(tmp_path).save(Pedigree.from_dict({"view_id": "CV-1", "author": {"type": "human"}}))

    result = CliRunner().invoke(app, ["audit", "CV-1"])
    assert result.exit_code == 0
    assert "Standard reference: NOT RECORDED" in result.stdout


def test_audit_custom_output_path_creates_parents(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    PedigreeStore(tmp_path).save(_complete())

    _, payload = _run("audit", "CV-1", "--output", "reports/cv1-audit.md", "--json")
    assert (tmp_path / "reports" / "cv1-audit.md").exists()
    assert payload["data"]["output_path"].endswith("reports/cv1-audit.md")


def test_audit_report_summarises_views_and_lists_gaps(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    ViewManager(tmp_path).register_view("OV-2", change_name="demo")
    PedigreeStore(tmp_path).save(_complete())

    result, payload = _run("audit-report", "--json")
    assert result.exit_code == 0
    data = payload["data"]
    assert data["summary"]["total_views"] == 2
    assert data["summary"]["with_pedigree"] == 1
    assert data["summary"]["without_pedigree"] == 1
    assert data["summary"]["filtered_out"] == 0
    assert data["trace_gaps"] == ["OV-2"]
    entries = {entry["view_id"]: entry for entry in data["views"]}
    assert entries["CV-1"]["pedigree_status"] == "complete"
    assert entries["OV-2"]["pedigree_status"] == "absent"
    assert entries["OV-2"]["author"] == "NOT RECORDED"

    default = tmp_path / ".dm2" / "audit" / f"project-audit-{date.today():%Y%m%d}.md"
    assert default.exists()
    assert "## 溯源缺口（Trace gaps）" in default.read_text(encoding="utf-8")


def test_audit_report_min_confidence_filters_and_counts(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    ViewManager(tmp_path).register_view("OV-2", change_name="demo")
    PedigreeStore(tmp_path).save(_complete("CV-1", confidence=0.8))
    PedigreeStore(tmp_path).save(_complete("OV-2", confidence=0.4))

    _, payload = _run("audit-report", "--min-confidence", "0.7", "--json")
    data = payload["data"]
    assert [entry["view_id"] for entry in data["views"]] == ["CV-1"]
    assert data["summary"]["filtered_out"] == 1
    assert data["summary"]["min_confidence"] == 0.7


def test_audit_report_data_group_coverage(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    PedigreeStore(tmp_path).save(_complete())

    _, payload = _run("audit-report", "--json")
    assert payload["data"]["data_group_coverage"], "CV-1 has DM2 data groups in views.yaml"


def test_audit_report_marks_a_missing_standard_as_a_gap(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    PedigreeStore(tmp_path).save(Pedigree.from_dict({
        "view_id": "CV-1",
        "author": {"type": "human"},
        "creation_date": "2026-01-01T00:00:00",
        "source": {"standard": ""},
    }))

    _, payload = _run("audit-report", "--json")
    assert payload["data"]["trace_gaps"] == ["CV-1"]

    text = (tmp_path / ".dm2" / "audit" / f"project-audit-{date.today():%Y%m%d}.md").read_text(encoding="utf-8")
    assert "标准出处未记录" in text


def test_audit_report_human_mode_prints_markdown(tmp_path, monkeypatch):
    _project(tmp_path, monkeypatch)
    result = CliRunner().invoke(app, ["audit-report"])
    assert result.exit_code == 0
    assert "# 项目溯源审计报告" in result.stdout
