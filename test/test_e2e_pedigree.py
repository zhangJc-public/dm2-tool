"""End-to-end provenance cycle: register → trace → validate → audit.

Spec: openspec/changes/add-view-provenance (12.1 / 12.2). The complete-trace
example is built inline with ``tmp_path`` — this repository has no fixture
directory, and an inline project keeps the cycle readable in one place.
"""

import json
from pathlib import Path

from typer.testing import CliRunner

from dm2.cli.main import app
from dm2.core.pedigree.store import PedigreeStore
from dm2.core.views.manager import ViewManager, ViewStatus

REASONING_YAML = """\
author:
  type: agent-assisted
  model: deepseek-v3
  operator: architecture-lead
source:
  standard: DoDAF V2.02 Vol 2
  section: CV-1 Capability Taxonomy
  dm2_terms_used:
    - term: Capability
      definition_ref: terms.json#Capability
reasoning:
  summary: Capability taxonomy grounded in the 03-capability data group.
  decision_factors:
    - factor: "data group activation: 03-capability"
      score: 0.85
      source: "dm2 analyze --json"
  alternatives_considered:
    - option: Generate OV-5a instead
      rejected_because: the description is capability-centric
known_limitations:
  - 术语别名未逐一核对
reliability: medium
confidence: 0.8
"""


def _invoke(*args):
    result = CliRunner().invoke(app, list(args))
    assert result.stdout, f"no stdout for {args}"
    return result, json.loads(result.stdout)


def test_propose_apply_validate_audit_cycle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # 1. Project scaffold: tracing on, pedigree directory present.
    result, init = _invoke("init", ".", "-j")
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / ".dm2" / "pedigree").is_dir()
    assert ".dm2/pedigree" in init["data"]["directories"]

    # 2. Propose: a change plan and the view file it planned.
    result, _ = _invoke("change", "new", "demo", "-j")
    assert result.exit_code == 0, result.stdout
    views_dir = tmp_path / "dm2-changes" / "demo" / "views"
    views_dir.mkdir(parents=True, exist_ok=True)
    view_file = views_dir / "CV-1.md"
    view_file.write_text(
        "---\nid: CV-1\ntitle: Capability Taxonomy\n---\n# CV-1\n", encoding="utf-8"
    )

    # 3. Apply: register the generated view, then record its generation reasoning.
    result, register = _invoke(
        "view", "register", "CV-1", "-c", "demo", "-p", str(view_file), "-j"
    )
    assert result.exit_code == 0, result.stdout
    assert register["status"] == "success"

    reasoning = tmp_path / "trace-CV-1.yaml"
    reasoning.write_text(REASONING_YAML, encoding="utf-8")
    result, trace = _invoke(
        "trace", "record", "CV-1",
        "--summary", "Capability taxonomy",
        "--reasoning-file", str(reasoning),
        "-j",
    )
    assert result.exit_code == 0, result.stdout
    assert trace["data"]["pedigree_status"] == "complete"
    assert trace["data"]["pedigree_missing"] == []

    _, listing = _invoke("view", "list", "--json")
    entry = next(view for view in listing["data"]["views"] if view["id"] == "CV-1")
    assert entry["pedigree_status"] == "complete"

    # 4. Validate: results are written back and the gate lets the view through.
    result, validated = _invoke("validate", "CV-1", "--change", "demo", "--json")
    assert result.exit_code == 0, result.stdout
    assert validated["data"]["verified"] is True
    assert validated["data"]["pedigree_updated"] is True
    assert ViewManager(tmp_path).get_view("CV-1").status == ViewStatus.VERIFIED

    record = PedigreeStore(tmp_path).load("CV-1")
    assert record.validation.last_validated
    assert all(getattr(record.validation, f"ran_R{index}") for index in range(1, 6))
    assert [entry.change_description for entry in record.modification_history] == [
        "view registered",
        "reasoning recorded",
        "verified: validation passed",
    ]

    # 5. Audit: the report is written and explains the provenance.
    result, audit = _invoke("audit", "CV-1", "--json")
    assert result.exit_code == 0, result.stdout
    assert audit["data"]["pedigree_status"] == "complete"
    report = Path(audit["data"]["output_path"]).read_text(encoding="utf-8")
    for section in (
        "## 作者与时间",
        "## 标准引用（Standard Reference）",
        "## 决策因素",
        "## 校验历史",
    ):
        assert section in report
    assert "Agent 自述、未经验证" in report

    # 6. Project report: nothing is missing any more.
    result, project = _invoke("audit-report", "--json")
    assert result.exit_code == 0, result.stdout
    assert project["data"]["trace_gaps"] == []
    assert project["data"]["summary"]["with_pedigree"] == 1
    assert project["data"]["summary"]["without_pedigree"] == 0
    assert project["data"]["data_group_coverage"]
