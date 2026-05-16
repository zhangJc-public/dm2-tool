## Context

目前 dm2 的 6 个 Claude Code 工作流（new/continue/ff/verify/bulk-archive/onboard）参照 openspec 的模式设计，但 `/dm2:new` 的行为不符合 openspec 的三阶段设计哲学（new → propose → apply）。openspec 中 `/opsx:new` 只做最小 scaffold 后停住，`/opsx:propose` 负责完整产物生成。

同时，`ViewRecommender` 当前仅依赖 6W 单维度推荐，忽略 DM2 元模型自身丰富的语义结构。经过多轮讨论，确定最终方案为：

1. **/dm2:propose** — 工作流层编排，复用现有 CLI 原语
2. **/dm2:new** — 简化为 scaffold-only
3. **视图推荐** — 基于 17 个 DM2 数据组的激活检测
4. **关键词数据源** — 数据组模板 frontmatter 的 `keywords` 字段
5. **映射表** — `dm2-reference/group-to-views.yaml` 外部 YAML
6. **CLI→AI Agent 分工** — CLI 输出原始数据，Agent 做决策

## Goals / Non-Goals

**Goals:**
- 新增 `/dm2:propose` 命令和 `dm2-propose-workflow` 技能
- 简化 `/dm2:new` 为轻量 scaffold
- 将 ViewRecommender 升级为 DM2 17 数据组驱动
- 在 dm2-reference 中建立关键词和视图映射的外部化数据体系

**Non-Goals:**
- 不改动现有的其他 5 个 dm2 技能（continue/ff/verify/bulk-archive/onboard）
- 不改动 Pipeline 核心流程
- 不引入向量 embedding（Phase 1 仅用关键词匹配）

## Decisions

**决定 1: propose 使用已有的 CLI 原语，不新增后端命令**
- `/dm2:propose` 技能内部调用 `dm2 change new`, `dm2 cynefin`, `dm2 analyze`, `dm2 instructions` 等已有命令
- 无需在 `main.py` 新增 CLI 命令层，纯粹是技能层面的编排
- 好处：精简，复用已有 view-state 和 analysis-state 持久化机制

**决定 2: `dm2-new-workflow` 缩减为三步**
- Step 1: 询问系统描述 → Step 2: dm2 change new → Step 3: 展示变更信息 + 提示可运行 `/dm2:propose`
- 去掉原有的 cynefin/analyze/视图生成步骤，将它们移到 propose

**决定 3: 视图推荐基于 17 个 DM2 数据组，而非 6W + 多因子加权**
- DM2 的 17 个数据组是视图推荐的自然框架，每组有对应的 DoDAF 视图
- 用户描述 → 数据组激活度向量(17维) → 映射到候选视图 → AI Agent 做最终排序
- 6W 作为数据组激活检测的子模块，不再是独立推荐维度
- 不再需要猜测权重参数

**决定 4: 关键词和映射数据外部化，不改代码**
- 每个数据组模板 frontmatter 增加 `keywords` 字段，用于激活检测
- 每个数据组模板 frontmatter 增加 `related_dm2_views` 字段，作为视图引用的语义标签
- 独立的 `dm2-reference/group-to-views.yaml` 文件管理数据组↔视图映射表
- CLI 运行时从磁盘加载，修改关键词或映射无需重装包

**决定 5: CLI 输出原始数据，AI Agent 做推理决策**
- CLI 输出：数据组激活向量、关键词命中记录、候选视图列表、依赖就绪度
- Agent 决策：视图优先级排序、跨组映射的逻辑综合、Phase 推进策略
- 对齐"CLI 是大脑（结构化数据），AI 是手脚（推理决策）"的核心模式

**决定 6: 17 个数据组的 keywords 和 related_dm2_views 由设计确认后批量补入**
- 每个组约 5-15 个关键词（中英双语）
- related_dm2_views 列出与该组直接相关的所有视图
- 如 01-Performer: keywords ["角色","组织","团队","performer","operator"...], related ["OV-4","PV-1"]

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 用户习惯的 `/dm2:new` 行为突然变少 | 在 new 的最终输出中明确提示 "要完整分析请运行 /dm2:produce" |
| 关键词覆盖不准，导致激活检测偏差 | 关键词放在模板 frontmatter 中，外部可调，迭代优化；Phase 2 可升级为加权关键词 |
| 数据组模板修改会影响激活检测 | 属于设计预期——修改模板自动更新激活行为，无需额外同步 |
| AI Agent 决策质量不确定 | CLI 已经提供完整的结构化数据，LLM 只需做排序决策而非内容生成，风险可控 |
