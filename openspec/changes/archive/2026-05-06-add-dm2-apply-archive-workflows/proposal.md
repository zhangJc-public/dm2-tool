## Why

dm2 当前缺少 `/dm2:apply` 和 `/dm2:archive` 两个工作流，导致核心路径 `/dm2:propose → /dm2:apply → /dm2:archive` 不完整。这与 OpenSpec 的 core profile（propose → apply → archive）不一致。`/dm2:apply` 填补"按计划执行 tasks.md 生成视图"的空缺（现有 `/dm2:continue` 和 `/dm2:ff` 都是重跑分析而非读 tasks.md），`/dm2:archive` 提供单变更简单归档入口（现有只有 bulk-archive）。

## What Changes

- 新增 `/dm2:apply` 工作流 — 读取 propose 产出的 tasks.md，按依赖顺序生成全部视图，勾选 checkbox
- 新增 `/dm2:archive` 工作流 — 单个变更的简单归档，含验证、确认、执行三步
- 修改 `/dm2:propose` 输出提示 — 推荐 `/dm2:apply` 作为下一步（替代原有的 continue/ff）
- 在 WORKFLOWS 注册表中注册两个新工作流
- 重新生成 `.claude/skills/` 和 `.claude/commands/dm2/`

## Capabilities

### New Capabilities
- `dm2-apply-workflow`: task-driven 视图生成工作流，读取 tasks.md 执行实现阶段，区别于分析驱动的 `/dm2:continue` 和 `/dm2:ff`
- `dm2-archive-workflow`: 单变更归档工作流，区别于多变更批量归档 `/dm2:bulk-archive`

### Modified Capabilities
- `dm2-propose-workflow`: 更新步骤 8 的输出提示，将推荐下一步从 `/dm2:continue`/`dm2:ff` 改为 `/dm2:apply`（continue/ff 保留为备选）
- `skill-template-generation`: `workflows/__init__.py` 新增 apply 和 archive 两个模块的注册

## Impact

- `src/dm2/core/templates/workflows/apply.py` — 新文件
- `src/dm2/core/templates/workflows/archive.py` — 新文件
- `src/dm2/core/templates/workflows/__init__.py` — 新增 import 和注册
- `src/dm2/core/templates/workflows/propose.py` — 修改第 157 行输出提示
- `.claude/skills/dm2-apply-workflow/SKILL.md` — 重新生成
- `.claude/skills/dm2-archive-workflow/SKILL.md` — 重新生成
- `.claude/commands/dm2/apply.md` — 重新生成
- `.claude/commands/dm2/archive.md` — 重新生成
