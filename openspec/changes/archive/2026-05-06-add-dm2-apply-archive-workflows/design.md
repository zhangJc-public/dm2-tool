## Context

dm2 当前有 8 个工作流（new, propose, continue, ff, verify, bulk-archive, explore, onboard）。对照 OpenSpec 的 core profile，缺少 `/dm2:apply`（task-driven 实现）和 `/dm2:archive`（单变更归档）。两者都是 dm2 工作流链中的关键环节，CLI 层已有支撑（`dm2 archive`, `dm2 change status` 等），缺失仅在 AI Agent 侧的 skill/command 模板。

## Goals / Non-Goals

**Goals:**
- 新增 `/dm2:apply` 工作流：读取 tasks.md，按依赖顺序生成视图，勾选 checkbox
- 新增 `/dm2:archive` 工作流：单变更简单归档（含验证、确认）
- 更新 `/dm2:propose` 输出：推荐 apply 为下一步
- 所有新工作流遵循现有的 WorkflowTemplate / SkillTemplate / CommandTemplate 模式

**Non-Goals:**
- 不修改 CLI 层（CLI 已有足够支撑）
- 不移除或重定义 `/dm2:continue` 和 `/dm2:ff`
- 不引入 profile system（不做 core/expanded 分离）
- 不修改 `/dm2:bulk-archive`

## Decisions

### Decision 1: apply 用 tasks.md 驱动，而非重跑分析

`/dm2:continue` 和 `/dm2:ff` 都是重跑 cynefin/analyze 来确定要生成哪些视图。`/dm2:apply` 的关键区别是它**读 tasks.md**（propose 阶段的产出）来驱动执行。

**理由**: 这保持了 propose→apply 之间的契约——propose 决定做什么，apply 负责做完。也使得 apply 可以恢复（已勾选的 task 跳过）。

**备选方案**: 修改 continue/ff 让它们也读 tasks.md。但这样会改变现有语义，且 continue/ff 有其独立用途（不依赖 propose 的快速路径）。

### Decision 2: apply 批量执行但不跳过可恢复性

apply 一次性跑完所有 pending tasks，但通过 tasks.md 的 checkbox 状态支持中断后恢复。

**理由**: 对齐 OpenSpec 的 apply 语义——批量执行，可恢复。区别于 continue（单步）和 ff（无状态，重跑分析）。

### Decision 3: archive 聚焦单变更

`/dm2:archive` 只处理单个变更，不做 conflict detection（那是 bulk-archive 的职责）。

**理由**: 简单、直接。用户跑完 propose→apply 后只需 `/dm2:archive` 就能收尾，不需要面对 bulk-archive 的多选 UI。

### Decision 4: 沿用现有模板模式

新工作流遵循 `WorkflowTemplate` dataclass + `SkillTemplate` + `CommandTemplate` 模式，放在 `workflows/` 目录下，注册到 `WORKFLOWS`。

**理由**: 一致性。生成引擎 `generate_agent_config()` 对 WORKFLOWS 做统一迭代，无需修改。

## Risks / Trade-offs

- **apply 与 continue/ff 的语义重叠**: 三者都能生成视图，用户可能困惑选哪个。Mitigation: 在 propose 输出中明确推荐 apply 为主路径，continue/ff 为备选。
- **apply 依赖 tasks.md 格式**: 如果 propose 产出的 tasks.md 格式变化，apply 解析可能失败。Mitigation: tasks.md 的格式由 propose.py 的 SKILL 指令控制，是内部契约，可控。
- **archive 没有 delta spec sync**: dm2 没有 OpenSpec 的 delta spec 概念，archive 只是移动目录。Mitigation: 当前 dm2 不需要 delta spec sync；未来如有类似机制再加。

## Open Questions

- 无
