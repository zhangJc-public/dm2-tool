## Why

当前 DM2 工具实现了 DoDAF 6 步流程中的部分能力（Cynefin 判定、6W 分析、单视图生成），但各命令相互独立，缺少贯穿 6 步的集成管道。用户无法从一个架构意图出发，经过完整的 6 步流程最终产出文档化的架构结果。本次变更的目标是保证流程完整性——让 6 步流程可端到端执行，暂不追求各步骤的深度优化。

## What Changes

- 新增 `dm2 run` 命令，驱动完整的 LLM 融合 6 步流程（Step 1+2 → Step 3+4 → Step 5 → Step 6 → 迭代）
- Step 1+2（意图澄清+范围界定）：整合 Cynefin 判定 + 反向质问机制 + 上下文预算，输出范围定义文档
- Step 3+4（数据定义+知识沉淀）：6W 矩阵驱动数据采集 + DM2 知识库检索，输出数据需求清单
- Step 5（分析执行）：整合溯因推理 + OODA + TOC 约束分析 + 一致性检查，输出分析报告
- Step 6（文档化+知识回流）：Composite View 优先 + wikilinks 双向关联 + 迭代回 Step 1，输出架构视图文档
- 各步骤之间通过 `.dm2/state.yaml` 传递状态，支持断点续跑
- 每步产生明确的中间产物，存入 `.dm2/steps/` 目录

## Capabilities

### New Capabilities

- `pipeline-orchestrator`: 6 步流程的主控制器，负责步骤调度、状态管理和迭代循环
- `step1-intent-scope`: Step 1+2 融合——意图收敛、反向质问、Cynefin 复杂度判定、上下文预算管理
- `step3-data-requirements`: Step 3+4 融合——6W 矩阵驱动数据需求定义、DM2 知识库检索与数据组织
- `step5-analysis`: Step 5——溯因推理补全、OODA 韧性分析、TOC 瓶颈识别、一致性校验
- `step6-documentation`: Step 6——Composite View 生成、wikilinks 双向关联、知识回流

### Modified Capabilities

<!-- 现有命令保持不变，本次不改动已有功能 -->

## Impact

- `src/dm2/cli/main.py`：新增 `dm2 run` 命令
- `src/dm2/engine/`：新增 pipeline 模块（orchestrator + 各 step 实现）
- `src/dm2/cognitive/`：step1-intent-scope 复用 cynefin_analyzer、six_w_analyzer
- `src/dm2/llm/`：step3-data-requirements 复用 rag.py；step6 复用 prompts.py
- `src/dm2/reasoning/`：step5-analysis 复用 consistency.py
- `.dm2/` 项目结构：新增 `steps/` 目录和 `state.yaml`
- `dm2-reference/`：无改动
