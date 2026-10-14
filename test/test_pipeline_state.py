"""Tests for PipelineStateManager (dm2.engine.pipeline.state_manager).

The manager owns ``.dm2/state.yaml`` and ``.dm2/steps/``, which the
pipeline-orchestrator spec names as the persistence contract: step outputs go to
``.dm2/steps/step<N>-<name>.md`` and pipeline state to ``.dm2/state.yaml`` so a
run can resume. It had no test coverage before this file.

Nothing here is pinned as defective — the state machine behaves as specified.
"""

import pytest
import yaml

from dm2.engine.pipeline.state_manager import PipelineStateManager

STEP_IDS = [
    "step1-intent-scope",
    "step3-data-requirements",
    "step5-analysis",
    "step6-documentation",
]


@pytest.fixture
def manager(tmp_project):
    return PipelineStateManager(tmp_project)


class TestInitState:
    def test_creates_the_state_file_and_steps_directory(self, manager, tmp_project):
        manager.init_state("a description")

        assert (tmp_project / ".dm2" / "state.yaml").exists()
        assert (tmp_project / ".dm2" / "steps").is_dir()

    def test_starts_at_the_first_step(self, manager):
        state = manager.init_state("d")

        assert state.status == "in_progress"
        assert state.current_step == "step1-intent-scope"

    def test_every_step_starts_pending(self, manager):
        state = manager.init_state("d")

        assert list(state.steps) == STEP_IDS
        assert all(s.status == "pending" for s in state.steps.values())

    def test_records_the_description_and_a_timestamp(self, manager):
        state = manager.init_state("描述内容")

        assert state.description == "描述内容"
        assert state.started_at


class TestLoad:
    def test_missing_file_loads_as_none(self, manager):
        assert manager.load() is None

    def test_round_trips_every_field(self, manager):
        manager.init_state("原始描述")
        manager.update_step("step1-intent-scope", "completed", ".dm2/steps/step1-intent-scope.md")

        state = manager.load()

        assert state.description == "原始描述"
        assert state.steps["step1-intent-scope"].status == "completed"
        assert state.steps["step1-intent-scope"].output == ".dm2/steps/step1-intent-scope.md"

    def test_state_file_is_valid_yaml_under_a_pipeline_key(self, manager, tmp_project):
        manager.init_state("d")

        data = yaml.safe_load((tmp_project / ".dm2" / "state.yaml").read_text(encoding="utf-8"))

        assert "pipeline" in data
        assert data["pipeline"]["current_step"] == "step1-intent-scope"

    def test_a_file_without_the_pipeline_key_loads_as_none(self, manager, tmp_project):
        (tmp_project / ".dm2" / "state.yaml").write_text("other: 1\n", encoding="utf-8")

        assert manager.load() is None


class TestUpdateStep:
    def test_records_status_and_output(self, manager):
        manager.init_state("d")

        manager.update_step("step1-intent-scope", "in_progress")

        assert manager.load().steps["step1-intent-scope"].status == "in_progress"

    def test_completing_a_step_advances_to_the_next(self, manager):
        manager.init_state("d")

        manager.update_step("step1-intent-scope", "completed")

        assert manager.load().current_step == "step3-data-requirements"

    def test_completing_the_last_step_finishes_the_pipeline(self, manager):
        manager.init_state("d")

        manager.update_step("step6-documentation", "completed")

        state = manager.load()
        assert state.status == "completed"
        assert state.current_step == ""

    def test_an_unknown_step_is_ignored(self, manager):
        manager.init_state("d")

        manager.update_step("no-such-step", "completed")

        assert manager.load().steps["step1-intent-scope"].status == "pending"

    def test_updating_without_state_does_nothing(self, manager):
        manager.update_step("step1-intent-scope", "completed")

        assert manager.load() is None

    def test_an_empty_output_does_not_clear_an_existing_one(self, manager):
        manager.init_state("d")
        manager.update_step("step1-intent-scope", "in_progress", "out.md")

        manager.update_step("step1-intent-scope", "completed")

        assert manager.load().steps["step1-intent-scope"].output == "out.md"


class TestIteration:
    def test_reset_bumps_the_iteration_and_rewinds(self, manager):
        manager.init_state("d")
        manager.update_step("step1-intent-scope", "completed")

        manager.reset_for_iteration()

        state = manager.load()
        assert state.iteration == 2
        assert state.current_step == "step1-intent-scope"
        assert state.status == "in_progress"

    def test_reset_clears_every_step(self, manager):
        manager.init_state("d")
        manager.update_step("step1-intent-scope", "completed")

        manager.reset_for_iteration()

        assert all(s.status == "pending" for s in manager.load().steps.values())

    def test_reset_records_the_previous_round(self, manager):
        manager.init_state("d")

        manager.reset_for_iteration()

        assert manager.load().previous_outputs


class TestQueries:
    def test_current_step_is_none_once_completed(self, manager):
        manager.init_state("d")
        manager.update_step("step6-documentation", "completed")

        assert manager.get_current_step() is None

    def test_current_step_without_state_is_none(self, manager):
        assert manager.get_current_step() is None

    def test_step_output_reads_the_referenced_file(self, manager, tmp_project):
        manager.init_state("d")
        (tmp_project / ".dm2" / "steps" / "step1-intent-scope.md").write_text(
            "内容", encoding="utf-8"
        )
        manager.update_step("step1-intent-scope", "completed", ".dm2/steps/step1-intent-scope.md")

        assert manager.get_step_output("step1-intent-scope") == "内容"

    def test_step_output_is_none_when_unrecorded(self, manager):
        manager.init_state("d")

        assert manager.get_step_output("step5-analysis") is None

    def test_step_output_is_none_when_the_file_is_gone(self, manager):
        manager.init_state("d")
        manager.update_step("step1-intent-scope", "completed", ".dm2/steps/missing.md")

        assert manager.get_step_output("step1-intent-scope") is None

    def test_is_resumable_only_while_in_progress(self, manager):
        manager.init_state("d")
        assert manager.is_resumable()

        manager.update_step("step6-documentation", "completed")
        assert not manager.is_resumable()

    def test_is_resumable_without_state(self, manager):
        assert not manager.is_resumable()
