## Context

dm2 工作流模板系统（`core/templates/`）定义了 7 个 WorkflowTemplate，每个包含:
- `SkillTemplate` — 生成 `.claude/skills/<skill-dir>/SKILL.md`（Agent 执行的完整指令）
- `CommandTemplate` — 生成 `.claude/commands/dm2/<name>.md`（用户可见的斜杠命令描述）

`/dm2:explore` 遵循同一模式，纯 Python 模板定义，无新依赖。

## Goals / Non-Goals

**Goals:**
- 新增 `/dm2:explore` 工作流，提供只读 DoDAF 探索模式
- Agent 可通过 `dm2 knowledge *` 命令查询视图定义、术语、概念
- Skill 指令鼓励可视化（ASCII 图）、对比表、自由讨论，不强制产出
- `dm2 init` 自动分发生成的技能文件

**Non-Goals:**
- 不改 CLI 命令
- 不新增 Python 后端逻辑（纯 Agent 行为定义）
- 不触及 kernel/engine/cognitive 层

## Decisions

### 1. Skill 指令设计：宽松指南而非操作手册

与 `propose`（精确算法步骤）不同，`/dm2:explore` 的 Skill 指令不给固定步骤，而是描述一种"姿态"——好奇、开放、可视化。指令提供以下工具清单和典型场景，但让 Agent 根据用户问题自行判断该调用哪个。

可用的 CLI 工具：
- `dm2 knowledge search <q> --json` — 搜索术语
- `dm2 knowledge concept <name> --json` — 概念详情
- `dm2 knowledge view <id> --json` — 视图元数据（含新字段）
- `dm2 knowledge views --json` — 全部 52 个视图
- `dm2 knowledge stats --json` — 知识库统计

典型探索场景：
- 理解视图：`knowledge view OV-2 --json` → 解读 standard_name/purpose/sections
- 对比视图：`knowledge view OV-6b` vs `knowledge view SvcV-10b`
- 数据组探索：查某个数据组包含哪些概念和视图
- 依赖链追踪：`knowledge view SV-1` → 追溯 dependencies

### 2. Command 描述：强调"只读 + 无产出"

Command 的 body 部分明确标示"只读模式"、"不生成视图"、"不创建变更"，让用户知道这和 `/dm2:propose` 的区别。

## Risks / Trade-offs

- [Risk] Agent 在 explore 模式下仍可能尝试修改文件 → Skill 指令明确约束"只读"，严重违反时用户会制止
