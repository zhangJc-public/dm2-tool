"""CLI contract tests for the redesigned `dm2 cynefin` command."""
import json

import yaml
from typer.testing import CliRunner

from test.test_cynefin_deriver import GOLDEN_CORPUS

runner = CliRunner()


def _run(*args):
    from dm2.cli.main import app
    return runner.invoke(app, ["cynefin", *args])


def _payload(result):
    return json.loads(result.stdout)["data"]


COMPLEX_DESC = next(text for expected, text in GOLDEN_CORPUS if expected == "Complex")
CLEAR_DESC = next(text for expected, text in GOLDEN_CORPUS if expected == "Clear")
CHAOTIC_DESC = next(text for expected, text in GOLDEN_CORPUS if expected == "Chaotic")
PLANNING_DESC = "编制网络安全应急预案，开展应急演练，完善中断处置流程"


class TestCliBehavior:
    def test_bare_invocation_is_disorder_success(self):
        result = _run("--json")
        assert result.exit_code == 0, result.stdout
        data = _payload(result)
        assert data["domain"] == "Disorder"
        assert data["needs_clarification"] is True
        assert data["depth_tier"] == "none"

    def test_desc_json_full_contract(self):
        result = _run("-d", COMPLEX_DESC, "--json")
        assert result.exit_code == 0, result.stdout
        data = _payload(result)
        assert data["domain"] == "Complex"
        for key in ("domain", "domain_label", "confidence", "confidence_breakdown",
                    "crisis", "needs_clarification", "depth_tier", "depth_guidance",
                    "dimensions", "scale_profile"):
            assert key in data
        # 三层语义契约：解析状态 + 证据卷宗 + 评估量表
        for key in ("resolution", "suggested_domain", "warnings",
                    "signal_report", "rubric"):
            assert key in data, f"missing {key}"
        assert data["resolution"] == "heuristic"
        assert len(data["rubric"]) == 5
        for item in data["rubric"]:
            assert item["question"]
            assert set(item["anchors"]) == {"clear", "complicated", "complex"}
            assert item["prefill"] in {"clear", "complicated", "complex", None}
        assert len(data["dimensions"]) == 5
        complex_votes = [d for d in data["dimensions"] if d["tendency"] == "complex"]
        assert len(complex_votes) >= 3
        assert all(d["evidence"] for d in complex_votes)

    def test_explicit_option_overrides_single_dimension(self):
        result = _run("-d", CLEAR_DESC, "--maturity", "complex", "--json")
        assert result.exit_code == 0, result.stdout
        maturity = next(
            d for d in _payload(result)["dimensions"]
            if d["id"] == "practice_maturity"
        )
        assert maturity["tendency"] == "complex"
        assert maturity["source"] == "user"
        # 任一显式维度选项 → 已裁定
        assert _payload(result)["resolution"] == "adjudicated"
        # 其他维度仍来自推导
        knowability = next(
            d for d in _payload(result)["dimensions"]
            if d["id"] == "requirement_knowability"
        )
        assert knowability["source"] == "derived"

    def test_manual_only_without_desc(self):
        result = _run(
            "--knowability", "clear", "--maturity", "clear", "--dynamics", "clear",
            "--alignment", "clear", "--constraints", "clear", "--json",
        )
        assert result.exit_code == 0, result.stdout
        data = _payload(result)
        assert data["domain"] == "Clear"
        assert all(d["source"] == "user" for d in data["dimensions"])

    def test_invalid_tendency_rejected(self):
        result = _run("--knowability", "huge", "--json")
        assert result.exit_code == 1
        payload = json.loads(result.stdout)
        assert payload["status"] == "error"

    def test_rubric_only_blank_rubric(self):
        """--rubric-only 无需描述：空白量表 + 档位说明，exit 0。"""
        result = _run("--rubric-only", "--json")
        assert result.exit_code == 0, result.stdout
        data = _payload(result)
        assert len(data["rubric"]) == 5
        for item in data["rubric"]:
            assert item["question"]
            assert set(item["anchors"]) == {"clear", "complicated", "complex"}
            assert item["prefill"] is None
            assert item["prefill_evidence"] == []
        assert set(data["depth_tiers"]) == {"Clear", "Complicated", "Complex", "Chaotic", "Disorder"}

    def test_domain_override_bypasses_crisis_and_keeps_trace(self):
        """--domain 终裁越过机械危机一票否决，但保留 mechanical_suggestion 留痕。"""
        result = _run("-d", CHAOTIC_DESC, "--domain", "Complex", "--json")
        assert result.exit_code == 0, result.stdout
        data = _payload(result)
        assert data["resolution"] == "adjudicated"
        assert data["domain"] == "Complex"
        assert data["mechanical_suggestion"] == "Chaotic"
        assert data["suggested_domain"] == "Chaotic"

    def test_domain_override_on_planning_text(self):
        result = _run("-d", PLANNING_DESC, "--domain", "Complicated", "--json")
        assert result.exit_code == 0, result.stdout
        data = _payload(result)
        assert data["crisis"] is False
        assert data["resolution"] == "adjudicated"
        assert data["domain"] == "Complicated"
        assert data["suggested_domain"] in {"Clear", "Complicated", "Complex", "Chaotic", "Disorder"}

    def test_invalid_domain_rejected(self):
        result = _run("--domain", "bogus", "--json")
        assert result.exit_code == 1
        payload = json.loads(result.stdout)
        assert payload["status"] == "error"
        assert payload["error"]["code"] == "INVALID_ARG"

    def test_crisis_corpus_chaotic(self):
        crisis_desc = next(text for expected, text in GOLDEN_CORPUS if expected == "Chaotic")
        result = _run("-d", crisis_desc, "--json")
        data = _payload(result)
        assert data["domain"] == "Chaotic"
        assert data["crisis"] is True


class TestPersistence:
    def test_state_persisted_new_format(self, tmp_dm2_project_cwd):
        result = _run("-d", COMPLEX_DESC, "--json")
        assert result.exit_code == 0, result.stdout
        state_file = tmp_dm2_project_cwd / ".dm2" / "analysis-state.yaml"
        state = yaml.safe_load(state_file.read_text(encoding="utf-8"))
        assert state["cynefin"]["domain"] == "Complex"
        assert state["cynefin"]["depth_tier"] == "extended"
        assert "dimensions" in state["cynefin"]
        assert state["cynefin"]["resolution"] == "heuristic"

    def test_state_persisted_adjudicated_after_domain(self, tmp_dm2_project_cwd):
        _run("-d", COMPLEX_DESC, "--domain", "Complex", "--json")
        state_file = tmp_dm2_project_cwd / ".dm2" / "analysis-state.yaml"
        state = yaml.safe_load(state_file.read_text(encoding="utf-8"))
        assert state["cynefin"]["resolution"] == "adjudicated"
        assert state["cynefin"]["mechanical_suggestion"] is not None

    def test_status_marks_resolution(self, tmp_dm2_project_cwd):
        from dm2.cli.main import app

        _run("-d", COMPLEX_DESC, "--json")
        draft = runner.invoke(app, ["status"])
        assert draft.exit_code == 0, draft.output
        assert "～草案" in draft.output
        _run("-d", COMPLEX_DESC, "--domain", "Complex", "--json")
        done = runner.invoke(app, ["status"])
        assert done.exit_code == 0, done.output
        assert "✓已裁定" in done.output

    def test_status_reads_legacy_state_format(self, tmp_dm2_project_cwd):
        state_file = tmp_dm2_project_cwd / ".dm2" / "analysis-state.yaml"
        state_file.write_text(
            yaml.dump({"cynefin": {"domain": "明晰（Simple）",
                                   "confidence": 0.85,
                                   "recommended_view_count": "2-4 个"}},
                      allow_unicode=True),
            encoding="utf-8",
        )
        from dm2.cli.main import app
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0, result.stdout
        assert "明晰（Simple）" in result.output
