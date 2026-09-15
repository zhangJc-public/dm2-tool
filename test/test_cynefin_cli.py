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
