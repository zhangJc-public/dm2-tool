## Why

openspec 的 6 个工作流技能（new/continue/ff/verify/bulk-archive/onboard）经过了充分设计，其核心模式——增量构建、断点续传、差距分析、批量操作——是领域无关的。dm2 可以直接复用这套工作流模式，只需将领域对象从"Software Change"替换为"DoDAF Architecture View"，将 CLI 原语从 openspec 替换为 dm2。这避免了重复设计，也让用户用统一的心智模型操作两个工具。

## What Changes

- 创建 6 个 Claude Code 技能文件（`.claude/skills/dm2-*/SKILL.md`），每个对应一个 openspec 工作流模式
- 创建 6 个 Claude Code 斜杠命令（`.claude/commands/dm2/*.md`），供用户手动触发
- 技能文件不包含领域知识——通过调用 dm2 CLI（`dm2 instructions`, `dm2 knowledge`, `dm2 analyze`, `dm2 run` 等）动态获取
- 建立 dm2 skill 模板目录（`templates/init/.claude/`），供 `dm2 init` 复制到新项目

## Capabilities

### New Capabilities
- `dm2-new-workflow`: `/dm2:new` — 创建架构分析容器，逐个推进：Cynefin评估 → 6W分析 → 视图推荐 → 选择视图 → 生成
- `dm2-continue-workflow`: `/dm2:continue` — 断点续传：自动检测项目状态（哪些视图已生成、pipeline 进度），推进到下一步
- `dm2-ff-workflow`: `/dm2:ff` — 一键分析+生成：输入系统描述 → 自动完成 Cynefin+6W+全部推荐视图生成
- `dm2-verify-workflow`: `/dm2:verify` — 三维验证：Completeness（推荐视图是否全部生成？）+ Correctness（视图是否符合 DM2 规则？）+ Coherence（视图间是否一致？）
- `dm2-bulk-archive-workflow`: `/dm2:bulk-archive` — 批量归档架构变更，检测跨变更的视图引用冲突
- `dm2-onboard-workflow`: `/dm2:onboard` — 引导式教学：通过一个真实系统描述，走完 dm2 全流程

### Modified Capabilities
<!-- None — skills are additive, CLI primitives unchanged -->

## Impact

- `.claude/skills/dm2-*/` 目录（新增，6 个技能文件）
- `.claude/commands/dm2/` 目录（新增，6 个命令文件）
- `templates/init/.claude/` 模板（新增或更新，供 `dm2 init` 复制）
- 不修改 dm2 CLI 代码（skills 通过现有 CLI 原语工作）
