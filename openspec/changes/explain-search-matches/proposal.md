## Why

P2 让检索用上了数据元词表，但**命中理由不可见**：调用方只看到一串术语，不知道某条为什么命中、查询被如何理解。这带来两个问题：

- **Agent 无法判断结果可信度**：`能力 活动` 返回 9 条，第一条 `activityMapsToCapabilityType` 是词元命中，第 3 条 `Activity` 只是靠数据组中文别名蹭到；输出里看不出这个差别
- **排序还能更准**：P2 只做「段级」判定——每段各自命中词元即可，**不关心词元顺序**。而 DM2 关系术语是「主语 + 谓词 + 宾语」的序列（`activityPartOfCapability` = activity·part·of·capability），查询 `活动 属于 能力` 应当匹配**词元模式**，而不是仅仅「同时含有这几个词元」

P3 做两件事：**查询反向分解**（把中文查询解析为「数据元 + 限定词」序列，得到词元模式）与 **`--explain` 命中理由**。

## What Changes

- **查询分解**：`ElementVocabulary.plan_query(text)` 把查询切分为片段，逐段判定 `element` / `qualifier` / `unknown`，解析出候选词元与**词元模式**
- **模式匹配层**：新增最高优先级的结构层——查询的每个片段都能解析、且其词元序列是术语词元序列的**顺序子序列**时判为 `pattern` 命中，排在「段级结构化命中」之前
- **命中理由**：`DM2KnowledgeIndexer.match_terms(query)` 返回「术语 + 解释」（层级、片段路由、命中的词元）；`search_terms` 保持原签名（薄包装）
- **CLI**：`dm2 knowledge search <query> --explain` 输出命中理由（JSON 加 `match` 字段，人类模式打印一行理由）；不带 `--explain` 时输出与现在完全一致
- **规范与文档**：`dm2-element-vocabulary` 增加查询分解要求，`dm2-metamodel-knowledge` 增加可解释匹配要求；readme/CLAUDE/foundation/CHANGELOG 同步

## Capabilities

### Modified Capabilities

- `dm2-element-vocabulary`：词表除组合（生成规范名）外，还要支持**分解**（把中文查询解析为数据元/限定词序列）。
- `dm2-metamodel-knowledge`：术语检索除返回结果外，还要能解释每条结果的命中原因，并把词元**顺序**纳入排序。

## Impact

**Affected code**:
- `src/dm2/kernel/elements.py`（`QueryPlan` / `plan_query`）
- `src/dm2/kernel/indexer.py`（`match_terms` + 解释模型，`search_terms` 变薄包装）
- `src/dm2/core/knowledge/api.py`（`search_terms(query, explain=False)`，结果项新增 `match`）
- `src/dm2/cli/commands/knowledge.py`（`--explain` 与人类可读理由）

**Compatibility**:
- `search_terms(query)` 与既有 JSON 输出**默认不变**；`match` 仅在 `explain=True`/`--explain` 时出现
- 排序会变化（词元模式命中提前），既有测试必须全绿；子串兜底与召回集合不变

**Invariant check**:
- 零 LLM：分解与解释都是词表查表 + 序列匹配
- 不新增包层级、不新增依赖
- 输出形状：`knowledge search` 未在 `schemas/` 声明，新增字段为**按需附加**
