## Why

dm2-tool 已有 15 个 CLI 命令（全部支持 `--json`）和 InstructionBuilder 引擎，但在 Claude Code 中只能通过裸 shell 命令调用。对照 openspec 的集成模式（`.claude/skills/` + `.claude/commands/` + 运行时状态目录），dm2 缺少的不是简单的 CLI 封装，而是 **AI Agent 工作流编排**和**架构活动状态追踪**。本次 change 基于 openspec 的设计模式研究，为 dm2 设计在 Claude Code 中实际工程所需的复合工作流和状态记录。

## What Changes

- 新增 3 个 Claude Code 技能：`dm2-explore`（架构探索）、`dm2-generate`（视图生成）、`dm2-pipeline`（Agent 驱动 Pipeline）
- 新增 4 个 Claude Code 斜杠命令：`/dm2:explore`、`/dm2:generate`、`/dm2:pipeline`、`/dm2:status`
- 新增 `dm2-claude-setup` 能力：`dm2 init` 自动生成 `.claude/` 配置，已有项目可通过命令安装
- 补齐缺失状态：View generation state（视图生成进度追踪）
- 更新 CLAUDE.md，添加 dm2 工作流索引

## Capabilities

### New Capabilities
- `dm2-explore-workflow`: 架构探索工作流技能。AI Agent 按 知识查询→Cynefin评估→6W分析→视图推荐 的流程引导用户探索架构问题。对应 dm2 CLI 的 `knowledge *`, `cynefin`, `analyze` 命令。
- `dm2-generate-workflow`: 视图生成工作流技能。AI Agent 按 选择视图→获取指令→生成内容→验证一致性 的流程协助用户生成 DoDAF 视图。对应 dm2 CLI 的 `instructions`, `generate`, `reasoning` 模块。
- `dm2-pipeline-workflow`: Agent 驱动 Pipeline 工作流技能。AI Agent 按 Intent→Data→Analysis→Documentation 四步流程自动推进。对应 dm2 CLI 的 `run --agent/--status/--instructions/--complete-step`。
- `dm2-claude-setup`: Claude Code 配置安装能力。`dm2 init` 自动生成 `.claude/` 目录（skills + commands），已有项目可通过 `dm2 setup-claude` 安装。
- `dm2-view-state`: 视图生成状态追踪。ViewManager 管理视图生命周期（pending→in_progress→generated→verified），持久化到 `.dm2/view-state.yaml`。

### Modified Capabilities
<!-- None: this is additive. Existing CLI behavior is unchanged. -->

## Impact

- `.claude/skills/dm2-*/` 目录（新增，3 个技能文件）
- `.claude/commands/dm2/` 目录（新增，4 个命令文件）
- `templates/init/.claude/` 模板（新增，供 `dm2 init` 复制）
- `src/dm2/core/views/manager.py`（新增，ViewManager 状态管理）
- `src/dm2/cli/main.py`（修改：`init` 命令 + 新增 `setup-claude` 命令）
- `CLAUDE.md`（更新）
