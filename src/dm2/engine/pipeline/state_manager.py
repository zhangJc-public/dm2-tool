from __future__ import annotations
"""Pipeline State Manager - 读写 .dm2/state.yaml 管理步骤状态"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class StepState:
    status: str = "pending"  # pending | in_progress | completed | failed
    output: str = ""


@dataclass
class PipelineState:
    status: str = "idle"  # idle | in_progress | completed | failed
    current_step: str = ""
    started_at: str = ""
    steps: dict[str, StepState] = field(default_factory=dict)
    iteration: int = 1
    previous_outputs: list[str] = field(default_factory=list)
    description: str = ""


class PipelineStateManager:
    """Pipeline 状态管理器"""

    STEP_IDS = [
        "step1-intent-scope",
        "step3-data-requirements",
        "step5-analysis",
        "step6-documentation",
    ]

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.state_file = project_root / ".dm2" / "state.yaml"
        self.steps_dir = project_root / ".dm2" / "steps"

    def init_state(self, description: str = "") -> PipelineState:
        """初始化 pipeline 状态"""
        import yaml

        self.steps_dir.mkdir(parents=True, exist_ok=True)

        state = PipelineState(
            status="in_progress",
            current_step="step1-intent-scope",
            started_at=datetime.now().isoformat(),
            description=description,
            steps={step_id: StepState() for step_id in self.STEP_IDS},
        )
        self._write(state)
        return state

    def load(self) -> Optional[PipelineState]:
        """加载当前状态"""
        import yaml

        if not self.state_file.exists():
            return None

        with open(self.state_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data or "pipeline" not in data:
            return None

        p = data["pipeline"]
        steps = {}
        for step_id, sd in p.get("steps", {}).items():
            steps[step_id] = StepState(
                status=sd.get("status", "pending"),
                output=sd.get("output", ""),
            )

        return PipelineState(
            status=p.get("status", "idle"),
            current_step=p.get("current_step", ""),
            started_at=p.get("started_at", ""),
            steps=steps,
            iteration=p.get("iteration", 1),
            previous_outputs=p.get("previous_outputs", []),
            description=p.get("description", ""),
        )

    def update_step(self, step_id: str, status: str, output: str = ""):
        """更新步骤状态"""
        state = self.load()
        if state is None:
            return

        if step_id not in state.steps:
            return

        state.steps[step_id].status = status
        if output:
            state.steps[step_id].output = output

        if status == "completed":
            # 推进到下一步
            try:
                idx = self.STEP_IDS.index(step_id)
                if idx + 1 < len(self.STEP_IDS):
                    state.current_step = self.STEP_IDS[idx + 1]
                else:
                    state.status = "completed"
                    state.current_step = ""
            except ValueError:
                pass

        self._write(state)

    def reset_for_iteration(self):
        """迭代：重置所有步骤，准备下一轮"""
        state = self.load()
        if state is None:
            return

        state.iteration += 1
        state.status = "in_progress"
        state.current_step = "step1-intent-scope"
        state.previous_outputs.append(
            f"迭代 {state.iteration - 1} @ {datetime.now().isoformat()}"
        )
        for step_id in self.STEP_IDS:
            state.steps[step_id] = StepState()

        self._write(state)

    def get_current_step(self) -> Optional[str]:
        """获取当前应执行的步骤"""
        state = self.load()
        if state is None or state.status == "completed":
            return None
        return state.current_step

    def get_step_output(self, step_id: str) -> Optional[str]:
        """读取步骤输出文件内容"""
        state = self.load()
        if state is None:
            return None

        step = state.steps.get(step_id)
        if step is None or not step.output:
            return None

        output_path = self.project_root / step.output
        if output_path.exists():
            return output_path.read_text(encoding='utf-8')
        return None

    def _write(self, state: PipelineState):
        """写入状态文件"""
        import yaml

        steps_data = {}
        for step_id, ss in state.steps.items():
            steps_data[step_id] = {"status": ss.status, "output": ss.output}

        data = {
            "pipeline": {
                "status": state.status,
                "current_step": state.current_step,
                "started_at": state.started_at,
                "steps": steps_data,
                "iteration": state.iteration,
                "previous_outputs": state.previous_outputs,
                "description": state.description,
            }
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def is_resumable(self) -> bool:
        """检查是否有可恢复的 pipeline"""
        state = self.load()
        if state is None:
            return False
        return state.status == "in_progress"
