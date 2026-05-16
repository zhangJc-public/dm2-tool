"""Pipeline V2 — Agent-driven 6-step orchestration."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StepState:
    step_id: str
    status: StepStatus
    output_path: str = ""

@dataclass
class PipelineState:
    status: str
    current_step: str
    description: str
    iteration: int
    steps: dict[str, StepState]


STEP_IDS = ["step1-intent-scope", "step3-data-requirements", "step5-analysis", "step6-documentation"]


class PipelineOrchestratorV2:
    """Agent-driven 6-step pipeline V2.

    CLI manages step state and generates instructions;
    AI Agent executes each step based on instructions.
    """

    def __init__(self, steps_dir: Optional[Path] = None):
        self._steps_dir = steps_dir or Path.cwd() / ".dm2" / "steps"
        self._state_file = self._steps_dir.parent / "state.yaml"

    def init_pipeline(self, description: str) -> PipelineState:
        self._steps_dir.mkdir(parents=True, exist_ok=True)

        steps = {}
        for sid in STEP_IDS:
            steps[sid] = StepState(
                step_id=sid,
                status=StepStatus.PENDING,
                output_path=str(self._steps_dir / f"{sid}.md"),
            )

        state = PipelineState(
            status="running",
            current_step="step1-intent-scope",
            description=description,
            iteration=1,
            steps=steps,
        )
        self._save_state(state)
        return state

    def load_state(self) -> Optional[PipelineState]:
        if not self._state_file.exists():
            return None
        with open(self._state_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not data:
            return None

        steps = {}
        for sid, sdata in data.get("steps", {}).items():
            steps[sid] = StepState(
                step_id=sid,
                status=StepStatus(sdata.get("status", "pending")),
                output_path=sdata.get("output_path", ""),
            )

        return PipelineState(
            status=data.get("status", "unknown"),
            current_step=data.get("current_step", ""),
            description=data.get("description", ""),
            iteration=data.get("iteration", 1),
            steps=steps,
        )

    def _save_state(self, state: PipelineState) -> None:
        data = {
            "status": state.status,
            "current_step": state.current_step,
            "description": state.description,
            "iteration": state.iteration,
            "steps": {
                sid: {"status": s.status.value, "output_path": s.output_path}
                for sid, s in state.steps.items()
            },
        }
        with open(self._state_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def get_status(self) -> Optional[dict]:
        state = self.load_state()
        if not state:
            return None
        return {
            "status": state.status,
            "current_step": state.current_step,
            "description": state.description,
            "iteration": state.iteration,
            "steps": {
                sid: {"status": s.status.value, "output_path": s.output_path}
                for sid, s in state.steps.items()
            },
        }

    def complete_step(self, step_id: str) -> Optional[str]:
        state = self.load_state()
        if not state:
            return None

        if step_id in state.steps:
            state.steps[step_id].status = StepStatus.COMPLETED

        # Advance to next step
        try:
            idx = STEP_IDS.index(step_id)
            if idx < len(STEP_IDS) - 1:
                next_step = STEP_IDS[idx + 1]
                state.current_step = next_step
                state.steps[next_step].status = StepStatus.IN_PROGRESS
            else:
                state.status = "complete"
                state.current_step = ""
        except ValueError:
            pass

        self._save_state(state)
        return state.current_step if state.status != "complete" else None

    def iterate(self) -> PipelineState:
        state = self.load_state()
        if not state:
            raise RuntimeError("No pipeline state to iterate")

        state.iteration += 1
        state.status = "running"
        state.current_step = "step1-intent-scope"
        for sid in STEP_IDS:
            state.steps[sid].status = StepStatus.PENDING
        state.steps["step1-intent-scope"].status = StepStatus.IN_PROGRESS

        self._save_state(state)
        return state
