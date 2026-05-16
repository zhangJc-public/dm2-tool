## Why

对照 openspec 的 CLI 设计模式（对领域对象的原子 CRUD + Status + Instructions + Validate），dm2 CLI 在 View 和 Analysis 两个领域对象上缺少关键的 list/show/validate 原语。AI Agent 生成视图后无法查询"已生成哪些视图、状态是什么"；分析结果不持久化，跨 session 丢失上下文；reasoning 模块的一致性检查逻辑没有 CLI 暴露。补齐这些原语是后续构建 AI Agent 工作流技能的前提。

## What Changes

- 新增 `ViewManager`：追踪视图生成生命周期（pending → in_progress → generated → verified），状态持久化到 `.dm2/view-state.yaml`
- 新增 `dm2 view list` 子命令：列出项目中的视图及其状态
- 新增 `dm2 validate <view>` 命令：对已生成的视图运行一致性检查（暴露 reasoning 模块）
- 分析结果持久化：`cynefin` 和 `analyze` 的结果存储到 `.dm2/analysis-state.yaml`
- 增强 `dm2 status`：输出中增加 view 进度统计

## Capabilities

### New Capabilities
- `view-lifecycle`: ViewManager 状态管理 + `dm2 view list` CLI。追踪视图的生成生命周期，支持 pending/in_progress/generated/verified 状态流转。
- `view-validation`: `dm2 validate` CLI 命令。调用 reasoning 模块对已生成视图进行一致性检查，输出结构化的校验报告。
- `analysis-persistence`: 分析结果持久化。cynefin 和 analyze 的 JSON 输出自动存储到 `.dm2/analysis-state.yaml`，支持跨 session 查询。

### Modified Capabilities
- `pipeline-orchestrator`: Pipeline 步骤完成时自动更新 ViewManager 状态（step6-documentation 完成 → 对应 view 标记为 generated）。

## Impact

- `src/dm2/core/views/manager.py`（新增，ViewManager）
- `src/dm2/cli/commands/view.py`（新增，view list 子命令）
- `src/dm2/cli/main.py`（修改：新增 validate 命令、view 子命令组、增强 status 输出）
- `src/dm2/engine/pipeline/step6_documentation.py`（修改：完成时更新 ViewManager）
- `src/dm2/engine/pipeline/step1_intent_scope.py`（修改：分析结果持久化）
- `src/dm2/engine/pipeline/step5_analysis.py`（修改：分析结果持久化）
- `.dm2/view-state.yaml`（新增，运行时状态文件）
- `.dm2/analysis-state.yaml`（新增，运行时状态文件）
