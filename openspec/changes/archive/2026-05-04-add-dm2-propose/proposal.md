## Why

dm2 当前缺少类似 openspec `/opsx:propose` 的指令。`/dm2:new` 实际行为过于沉重（Cynefin → 6W → 视图推荐 → 全流程），而 openspec 在三阶段体验（new → propose → apply）中每个指令职责明确：`new` 只是最小 scaffold，`propose` 才是完整产物生成入口。

同时，现有视图推荐仅依赖单一 6W 维度（`0.5 + 0.3*(6W match) + 0.2*(concept match)`），过于片面。DM2 元模型有 17 个数据组，每组定义为自然"镜头"映射到对应的 DoDAF 视图——推荐系统应基于这个完整的元模型，而非缩减版的 6W。

## What Changes

- **新增 `/dm2:propose`** — 一步生成全部架构产物：创建 change → DM2 数据组激活检测 → 视图推荐 → proposal.md → design.md → tasks.md
- **新增 `dm2-propose-workflow` 技能** — 对应 `/dm2:propose` 命令的 AI Agent 工作流
- **调整 `/dm2:new`** — 简化为轻量 scaffold（只创建 change 目录 + 初始状态），停住等待用户确认或指令
- **调整 `dm2-new-workflow` 技能** — 行为从"全流程"缩减为"scaffold + 等待"
- **增强 `ViewRecommender`** — 从 6W 单维度升级为 17 个 DM2 数据组激活检测驱动
- **新增外部映射文件** — `dm2-reference/group-to-views.yaml`，数据组→视图的映射表（可调试，不改代码）
- **扩展模板 frontmatter** — 17 个数据组模板增加 `keywords` 和 `related_dm2_views` 字段
- **CLI→AI Agent 数据契约** — CLI 只输出原始激活向量和映射，不做优先级排序，由 AI Agent (LLM) 结合对话上下文决策

## Capabilities

### New Capabilities
- `dm2-propose-workflow`: /dm2:propose 命令及其对应的 Claude Code 技能，基于 DM2 数据组做多维度分析后生成完整架构变更产物
- `dm2-data-group-activation`: ViewRecommender 升级为 17 个 DM2 数据组的激活检测，替代单一的 6W 分类，关键词从模板 frontmatter 加载

### Modified Capabilities
- `dm2-new-workflow`: /dm2:new 命令行为从"全流程分析"简化为"最小 scaffold + 停住等待"
- `dm2-reference-group-templates`: 17 个数据组模板的 frontmatter 增加 `keywords`（激活检测用）和 `related_dm2_views`（视图引用）字段

## Impact

- `.claude/commands/dm2/new.md` — 更新行为描述
- `.claude/skills/dm2-new-workflow/SKILL.md` — 缩减步骤，改为 scaffold 后等待
- `.claude/commands/dm2/propose.md` — 新增文件
- `.claude/skills/dm2-propose-workflow/SKILL.md` — 新增技能
- `src/dm2/cognitive/view_recommender.py` — 重构推荐逻辑，支持数据组激活检测
- `dm2-reference/core/groups/*/*-Template.md` — 17 个模板增加 keywords + related_dm2_views
- `dm2-reference/group-to-views.yaml` — 新增外部映射文件
