"""Tests for PipelineOrchestrator (dm2.engine.pipeline.pipeline_orchestrator).

This is the legacy V1 engine behind ``dm2 run`` without ``--agent`` — the only
caller of the whole ``dm2.engine`` layer (src/dm2/cli/main.py:1391). It had no
test coverage before this file, which is why its steps could rot unnoticed.

The orchestration itself matches the pipeline-orchestrator spec: four steps run
in order, each persisted to ``.dm2/steps/<step-id>.md``, with pipeline state in
``.dm2/state.yaml``. What the individual steps produce is covered by
test_step1_intent_scope.py, test_step3_data_requirements.py,
test_step5_analysis.py and test_step6_documentation.py — several of which pin
defects. These tests assert the sequencing contract only.
"""

import pytest
import yaml

from dm2.engine.pipeline.pipeline_orchestrator import STEP_NAMES, PipelineOrchestrator

DESCRIPTION = "某安全运营平台检测网络威胁，安全团队负责处置"


@pytest.fixture
def orchestrator(tmp_dm2_project_cwd):
    """An orchestrator rooted at a throwaway .dm2 project."""
    return PipelineOrchestrator()


class TestStepCatalogue:
    def test_the_four_documented_steps_are_registered(self):
        assert list(STEP_NAMES) == [
            "step1-intent-scope",
            "step3-data-requirements",
            "step5-analysis",
            "step6-documentation",
        ]

    def test_every_step_has_a_label(self):
        for step_id, label in STEP_NAMES.items():
            assert label, step_id


class TestFullRun:
    def test_writes_a_step_document_for_each_step(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION)

        for step_id in STEP_NAMES:
            assert (tmp_project / ".dm2" / "steps" / f"{step_id}.md").exists(), step_id

    def test_step_documents_are_not_empty(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION)

        for step_id in STEP_NAMES:
            path = tmp_project / ".dm2" / "steps" / f"{step_id}.md"
            assert path.read_text(encoding="utf-8").strip(), step_id

    def test_pipeline_state_ends_completed(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION)

        data = yaml.safe_load((tmp_project / ".dm2" / "state.yaml").read_text(encoding="utf-8"))
        assert data["pipeline"]["status"] == "completed"
        assert data["pipeline"]["current_step"] == ""

    def test_every_step_is_recorded_as_completed(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION)

        data = yaml.safe_load((tmp_project / ".dm2" / "state.yaml").read_text(encoding="utf-8"))
        for step_id in STEP_NAMES:
            assert data["pipeline"]["steps"][step_id]["status"] == "completed", step_id

    def test_each_step_records_where_its_output_lives(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION)

        data = yaml.safe_load((tmp_project / ".dm2" / "state.yaml").read_text(encoding="utf-8"))
        for step_id in STEP_NAMES:
            assert data["pipeline"]["steps"][step_id]["output"] == f".dm2/steps/{step_id}.md"

    def test_the_description_is_carried_into_the_state(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION)

        data = yaml.safe_load((tmp_project / ".dm2" / "state.yaml").read_text(encoding="utf-8"))
        assert data["pipeline"]["description"] == DESCRIPTION

    def test_view_files_land_in_dot_dm2_output(self, orchestrator, tmp_project):
        """Spec: Step 6 puts generated views in `.dm2/output/`.

        The orchestrator used to pass a bare ``output/`` while its own step's
        spec, docstring and result field all said ``.dm2/output/``.
        """
        orchestrator.run(DESCRIPTION)

        out = tmp_project / ".dm2" / "output"
        assert (out / "composite-view.md").exists()
        for view_id in ("OV-1", "OV-2", "OV-5a"):
            assert (out / f"{view_id}.md").exists(), view_id

    def test_view_files_are_not_empty_documents(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION)

        out = tmp_project / ".dm2" / "output"
        for path in out.glob("*.md"):
            assert len(path.read_text(encoding="utf-8")) > 100, path

    def test_no_bare_output_directory_is_created(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION)

        assert not (tmp_project / "output").exists()


class TestStepOnly:
    def test_runs_just_the_requested_step(self, orchestrator, tmp_project):
        orchestrator.run("", step_only="step5-analysis")

        assert (tmp_project / ".dm2" / "steps" / "step5-analysis.md").exists()
        assert not (tmp_project / ".dm2" / "steps" / "step1-intent-scope.md").exists()

    def test_leaves_the_pipeline_unfinished(self, orchestrator, tmp_project):
        orchestrator.run("", step_only="step5-analysis")

        data = yaml.safe_load((tmp_project / ".dm2" / "state.yaml").read_text(encoding="utf-8"))
        assert data["pipeline"]["status"] != "completed"

    def test_an_unknown_step_writes_nothing(self, orchestrator, tmp_project):
        orchestrator.run("", step_only="step9-nonsense")

        assert not list((tmp_project / ".dm2" / "steps").glob("*.md"))


class TestResume:
    def test_resume_continues_from_the_recorded_step(self, orchestrator, tmp_project):
        from dm2.engine.pipeline.state_manager import PipelineStateManager

        manager = PipelineStateManager(tmp_project)
        manager.init_state(DESCRIPTION)
        manager.update_step("step1-intent-scope", "completed")

        orchestrator.run(DESCRIPTION, resume=True)

        # Step 1 was already done, so only the remaining steps run this time.
        assert (tmp_project / ".dm2" / "steps" / "step5-analysis.md").exists()
        assert (tmp_project / ".dm2" / "steps" / "step6-documentation.md").exists()

        data = yaml.safe_load((tmp_project / ".dm2" / "state.yaml").read_text(encoding="utf-8"))
        assert data["pipeline"]["status"] == "completed"

    def test_resume_without_prior_state_starts_fresh(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION, resume=True)

        assert (tmp_project / ".dm2" / "steps" / "step1-intent-scope.md").exists()


class TestIteration:
    def test_iterate_rewinds_to_the_first_step(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION)

        orchestrator.iterate()

        data = yaml.safe_load((tmp_project / ".dm2" / "state.yaml").read_text(encoding="utf-8"))
        assert data["pipeline"]["current_step"] == "step1-intent-scope"
        assert data["pipeline"]["iteration"] == 2

    def test_iterate_keeps_the_previous_round_on_disk(self, orchestrator, tmp_project):
        orchestrator.run(DESCRIPTION)
        before = (tmp_project / ".dm2" / "steps" / "step1-intent-scope.md").read_text(
            encoding="utf-8"
        )

        orchestrator.iterate()

        after = (tmp_project / ".dm2" / "steps" / "step1-intent-scope.md").read_text(
            encoding="utf-8"
        )
        assert after == before


class TestProgress:
    def test_progress_reports_every_step(self, orchestrator, tmp_project, capsys):
        orchestrator.run(DESCRIPTION)
        capsys.readouterr()

        orchestrator.show_progress()

        printed = capsys.readouterr().out
        for step_id in STEP_NAMES:
            assert step_id in printed or STEP_NAMES[step_id] in printed, step_id
