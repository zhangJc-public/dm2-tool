## Why

dm2 现有 7 个工作流（propose / continue / new / ff / verify / onboard / bulk-archive）全部面向"产出"——生成视图、规划变更、验证结果。缺少一个只读的探索/思考模式，让用户在没有生成压力的情况下理解 DoDAF 概念、讨论架构选择、学习视图定义。OpenSpec 有 `/opsx:explore`，dm2 没有对应物。

## What Changes

- 新增 `workflows/explore.py` — `/dm2:explore` 工作流的 Skill + Command Python 模板
- 在 `workflows/__init__.py` 的 `_all_workflows` 列表中注册该工作流
- `dm2 init` 后用户将自动获得 `.claude/skills/dm2-explore-workflow/SKILL.md` 和 `.claude/commands/dm2/explore.md`
- 该工作流为只读模式：可使用 `dm2 knowledge *` 命令查询 DM2 知识库，但不触发变更、生成或修改

## Capabilities

### New Capabilities

- `dm2-explore-workflow`: DoDAF 架构探索工作流，只读思考模式。Agent 通过 `dm2 knowledge search/view/views/concept/stats` 等命令获取信息，以可视化、对比、讨论的方式帮助用户探索架构决策。

### Modified Capabilities

（无）

## Impact

- `src/dm2/core/templates/workflows/explore.py` — 新增文件
- `src/dm2/core/templates/workflows/__init__.py` — 添加 import 和注册
- 不涉及 CLI 命令修改
- 不涉及 kernel/engine/cognitive 层修改
