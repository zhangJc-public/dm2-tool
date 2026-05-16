## Context

openspec 的 6 个工作流技能（new/continue/ff/verify/bulk-archive/onboard）是领域无关的工作流模式。它们操作的核心抽象是：
- **new**: 有依赖关系的 artifact 增量构建
- **continue**: 断点续传（状态驱动）
- **ff**: 批量 artifact 一键生成
- **verify**: intent vs reality 差距分析
- **bulk-archive**: 多对象批量操作 + 冲突检测
- **onboard**: 引导式教学

dm2 可以直接复用这些模式，只需将领域对象和 CLI 原语替换。

## Goals / Non-Goals

**Goals:**
- 6 个 skill 文件严格遵循 openspec 对应 skill 的结构（Steps、Guardrails、Output 格式）
- 技能通过 dm2 CLI 原语操作领域对象（不包含领域知识）
- 用户通过 `/dm2:xxx` 斜杠命令触发

**Non-Goals:**
- 不修改 dm2 CLI 代码
- 不重新设计工作流（直接复用 openspec 的经过验证的模式）
- 技能文件不包含 DM2 领域知识（由 CLI 的 `InstructionBuilder` 动态提供）

## Decisions

### Decision 1: 领域对象映射

| openspec 领域对象 | dm2 对应 | 说明 |
|------|------|------|
| Change | Architecture Change / Analysis Session | dm2 change 是架构变更容器 |
| Artifact (proposal/specs/design/tasks) | View (OV-1, OV-2, SV-1...) + Analysis Result | dm2 的核心产出是视图和分析结果 |
| Artifact dependency graph | View dependency graph (ArtifactGraph) | 52 个视图的拓扑依赖关系 |
| Spec | DM2 View metadata + rules | 每个视图有定义好的结构、数据组、规则 |
| Main spec | Knowledge base (DM2 reference) | 不可变的参考知识 |

### Decision 2: 每个 openspec skill 到 dm2 skill 的映射

**new**: openspec 逐个创建 proposal → specs → design → tasks。dm2 逐个推进：cynefin → 6W → 视图推荐 → 选择视图 → 生成视图。每一步由 `dm2 instructions` 驱动。

**continue**: openspec 读 status 找第一个 ready artifact。dm2 读 `dm2 status` 找第一个 pending 视图或当前 pipeline 步骤。

**ff**: openspec 循环创建全部 artifact 直到 apply-ready。dm2 循环执行：`dm2 analyze` → 遍历推荐视图 → `dm2 instructions <view>` → 生成。

**verify**: openspec 三维检查（completeness/correctness/coherence）。dm2 对应三维：视图完整性（推荐的全部生成了？）、DM2 规则遵守（内容符合模板？）、视图间一致性（ConsistencyChecker）。

**bulk-archive**: openspec 检测同一 capability 被多个 change 修改的冲突。dm2 检测同一 view 被多个 change 引用/修改的冲突。

**onboard**: openspec 用 Explain→Do→Show→Pause 节奏走完全流程。dm2 引导用户：描述系统 → Cynefin → 6W → 推荐视图 → 生成一个视图 → 验证 → 归档。

### Decision 3: Skill 文件位置

遵循 openspec 模式：
- `.claude/skills/dm2-<name>-workflow/SKILL.md` — AI agent 技能
- `.claude/commands/dm2/<name>.md` — 用户斜杠命令
- 模板源：`templates/init/.claude/`（供 `dm2 init` 复制）

## Risks / Trade-offs

- [Risk] 技能依赖的 CLI 原语（如 `dm2 view list`, `dm2 validate`）尚未实现 → 这些是 `complete-dm2-cli-primitives` change 的范围；本 change 的技能文件可以引用这些命令，实现时需先完成 CLI 原语
- [Risk] dm2 的 artifact 依赖图不如 openspec 严格 → new/ff 技能中的"下一步"逻辑需要适配 dm2 的 ArtifactGraph
