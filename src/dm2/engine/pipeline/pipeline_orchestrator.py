from __future__ import annotations
"""
Pipeline Orchestrator - 6步流程主控制器

职责:
  1. 步骤调度（Step 1+2 → Step 3+4 → Step 5 → Step 6）
  2. 状态管理（读/写 .dm2/state.yaml）
  3. 断点续跑（--resume）
  4. 单步执行（--step <N>）
  5. 迭代循环（Step 6 → Step 1）
  6. 进度输出
"""

from pathlib import Path

from dm2.engine.pipeline.state_manager import PipelineStateManager
from dm2.engine.pipeline.step1_intent_scope import Step1IntentScope
from dm2.engine.pipeline.step3_data_requirements import Step3DataRequirements
from dm2.engine.pipeline.step5_analysis import Step5Analysis
from dm2.engine.pipeline.step6_documentation import Step6Documentation
from dm2.kernel.indexer import DM2KnowledgeIndexer
from dm2.utils.paths import get_project_root


STEP_NAMES = {
    "step1-intent-scope": "Step 1+2：意图澄清 + 范围界定",
    "step3-data-requirements": "Step 3+4：数据定义 + 知识沉淀",
    "step5-analysis": "Step 5：分析执行",
    "step6-documentation": "Step 6：文档化 + 知识回流",
}


class PipelineOrchestrator:
    """Pipeline 主协调器"""

    def __init__(self):
        self.project_root = get_project_root()
        self.state_mgr = PipelineStateManager(self.project_root)
        self.indexer = DM2KnowledgeIndexer()
        self.indexer.load_all()

        # 初始化各步骤
        self.step1 = Step1IntentScope(self.indexer)
        self.step3 = Step3DataRequirements(self.indexer)
        self.step5 = Step5Analysis()
        self.step6 = Step6Documentation(self.indexer)

    def run(self, description: str, resume: bool = False, step_only: str = None):
        """执行 pipeline"""

        # 初始化或恢复状态
        if resume and self.state_mgr.is_resumable():
            state = self.state_mgr.load()
            print(f"📂 恢复 Pipeline: 迭代 #{state.iteration}, 当前步骤 {state.current_step}")
        else:
            self.state_mgr.init_state(description)
            print("🚀 启动 DoDAF 6步融合流程")
            print(f"   描述: {description[:80]}...")
            print()

        # 单步模式
        if step_only:
            self._execute_step(step_only)
            return

        # 全流程模式
        current_step = self.state_mgr.get_current_step()
        while current_step:
            self._execute_step(current_step)
            current_step = self.state_mgr.get_current_step()

        # 完成
        state = self.state_mgr.load()
        print()
        print("=" * 60)
        print(f"✅ DoDAF 6步融合流程完成！")
        print(f"   迭代次数: {state.iteration}")
        print(f"   产物位置: {self.project_root / '.dm2' / 'steps' / ''}")
        print(f"   视图输出: {self.project_root / 'output' / ''}")
        print()
        print("💡 如需迭代优化，运行: dm2 run --resume （将自动回 Step 1）")

    def _execute_step(self, step_id: str):
        """执行单个步骤"""
        if step_id not in STEP_NAMES:
            print(f"❌ 未知步骤: {step_id}")
            return

        step_name = STEP_NAMES[step_id]
        print(f"\n{'─' * 50}")
        print(f"▶ {step_name}")
        print(f"{'─' * 50}")

        self.state_mgr.update_step(step_id, "in_progress")
        state = self.state_mgr.load()
        desc = state.description if state else ""

        output_file = f".dm2/steps/{step_id}.md"
        output_path = self.project_root / output_file

        if step_id == "step1-intent-scope":
            result = self.step1.execute(desc)
            content = self.step1.format_output(result)
            output_path.write_text(content, encoding='utf-8')
            print(f"   ✓ Cynefin 域: {result.cynefin_domain}")
            print(f"   ✓ 反向质问: {len(result.clarification_questions)} 个问题")
            print(f"   ✓ 数据组: {len(result.selected_data_groups)} 个")

        elif step_id == "step3-data-requirements":
            # 读取 Step 1+2 的输出获取数据组选择
            scope_content = self.state_mgr.get_step_output("step1-intent-scope") or ""
            primary_w = "What"
            secondary_ws = []

            step1_result = self._parse_step1_output(scope_content)
            if step1_result:
                primary_w = step1_result.get("primary_w", "What")
                secondary_ws = step1_result.get("secondary_ws", [])
                selected_groups = step1_result.get("selected_groups", [])
            else:
                selected_groups = []

            result = self.step3.execute(desc, selected_groups, primary_w, secondary_ws)
            content = self.step3.format_output(result)
            output_path.write_text(content, encoding='utf-8')
            print(f"   ✓ 数据需求: {len(result.requirements)} 个维度")
            print(f"   ✓ 检索概念: {len(result.retrieved_concepts)} 条")
            print(f"   ✓ 检索术语: {len(result.retrieved_terms)} 条")
            print(f"   ✓ 数据缺口: {len(result.gaps)} 个")

        elif step_id == "step5-analysis":
            data_content = self.state_mgr.get_step_output("step3-data-requirements") or ""
            result = self.step5.execute(desc, data_content)
            content = self.step5.format_output(result)
            output_path.write_text(content, encoding='utf-8')
            print(f"   ✓ 溯因推断: {len(result.abductive_inferences)} 条")
            print(f"   ✓ OODA 断点: {len(result.ooda_breakpoints)} 个")
            print(f"   ✓ TOC 瓶颈: {len(result.toc_bottlenecks)} 个")
            print(f"   ✓ 一致性问题: {len(result.consistency_issues)} 个")

        elif step_id == "step6-documentation":
            analysis_content = self.state_mgr.get_step_output("step5-analysis") or ""
            scope_content = self.state_mgr.get_step_output("step1-intent-scope") or ""
            data_content = self.state_mgr.get_step_output("step3-data-requirements") or ""

            result = self.step6.execute(
                desc, analysis_content, data_content, scope_content
            )
            content = self.step6.format_output(result)
            output_path.write_text(content, encoding='utf-8')

            # 保存视图文件
            output_dir = self.project_root / "output"
            self.step6.save_views(result, output_dir)

            print(f"   ✓ Composite View: 已生成")
            print(f"   ✓ 独立视图: {len(result.views)} 个")
            print(f"   ✓ Wikilinks: {len(result.wikilinks_map)} 个实体")
            print(f"   ✓ 迭代建议: {len(result.knowledge_delta.iteration_suggestions)} 条")
            print(f"   ✓ 视图输出: {output_dir}/")

        self.state_mgr.update_step(step_id, "completed", output_file)
        print(f"   📄 输出: {output_file}")

    def _parse_step1_output(self, content: str) -> dict:
        """从 Step 1+2 输出中解析关键信息"""
        import re

        result = {"primary_w": "What", "secondary_ws": [], "selected_groups": []}

        pw_match = re.search(r'\*\*主要 6W\*\*:\s*(\w+)', content)
        if pw_match:
            result["primary_w"] = pw_match.group(1)

        sw_match = re.search(r'\*\*次要 6W\*\*:\s*(.+)', content)
        if sw_match and sw_match.group(1).strip() != "无":
            result["secondary_ws"] = [
                w.strip() for w in sw_match.group(1).split(",")
            ]

        groups = re.findall(r'^\s*-\s*(.+)$', content, re.MULTILINE)
        # 过滤出 DM2 数据组格式的行
        group_section = False
        for line in content.split("\n"):
            line = line.strip()
            if "选定 DM2 数据组" in line:
                group_section = True
                continue
            if group_section and line.startswith("- "):
                g = line[2:].strip()
                if g and not g.startswith("##"):
                    result["selected_groups"].append(g)
            elif group_section and (line.startswith("##") or line.startswith("---")):
                group_section = False

        return result

    def iterate(self):
        """触发迭代循环"""
        self.state_mgr.reset_for_iteration()
        print("🔄 已重置 Pipeline，准备新一轮迭代...")
        print(f"   上一轮产物已保留在 .dm2/steps/ 中")

    def show_progress(self):
        """显示当前进度"""
        state = self.state_mgr.load()
        if state is None:
            print("无活跃的 Pipeline（运行 dm2 run 启动）")
            return

        print(f"Pipeline 状态: {state.status}")
        print(f"迭代: #{state.iteration}")
        print(f"描述: {state.description[:80]}...")
        print()

        for step_id, step_name in STEP_NAMES.items():
            step_state = state.steps.get(step_id)
            if step_state is None:
                icon = "⬜"
                status_text = "未开始"
            elif step_state.status == "completed":
                icon = "✅"
                status_text = "完成"
                if step_state.output:
                    status_text += f" → {step_state.output}"
            elif step_state.status == "in_progress":
                icon = "🔄"
                status_text = "进行中"
            elif step_state.status == "failed":
                icon = "❌"
                status_text = "失败"
            else:
                icon = "⬜"
                status_text = "待执行"

            print(f"  {icon} {step_name:<30} [{status_text}]")
