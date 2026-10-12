## Context

P2 建立了「段级」词元归一：查询分词后，每段独立映射为候选词元，术语词元集合与之交即算结构化命中。它解决了 `能力 活动` 的排序问题，但有两个缺口：

1. **不看顺序**：`活动 属于 能力` 与 `能力 活动` 在 P2 眼里差别不大（都只是「含有这些词元」），而 DM2 关系术语是「主语 + 谓词 + 宾语」序列
2. **不可解释**：调用方拿不到「这条为什么命中」，无法判断是词元命中还是纯文本蹭到

## Goals / Non-Goals

**Goals**

- 把中文查询解析为「数据元 + 限定词」序列，得到**词元模式**
- 词元模式按**顺序子序列**匹配术语词元，作为最高优先级的结构层
- 每条结果附带机器可读的命中理由（层级、片段路由、命中词元），`--explain` 时输出
- 默认输出与行为**不扩张**：不带 `--explain` 时 JSON 与现在一致

**Non-Goals**

- 不做自然语言句法分析（不引入分词库/NLP）：只按空白与标点切分 + 词表反查
- 不做同义词/拼音/纠错扩展
- 不改 `knowledge term/taxonomy/...` 的输出
- 不做排名的机器学习调参：层级是显式规则

## Decisions

### Decision 1: 查询分解产出「片段 + 候选词元」，模式允许候选不确定

**选择**：`plan_query(text) -> QueryPlan`，每个片段带 `kind`（element/qualifier/unknown）与候选词元列表。词元模式匹配用**回溯**在候选之间选取，形成术语词元的顺序子序列。

**理由**：中文词条天然一对多（`区域` → area/region），把不确定性交给匹配阶段比在分解阶段硬选一个更稳；片段少（≤6）、候选少（≤3），回溯成本可忽略。

### Decision 2: 顺序子序列匹配，而不是连续子串匹配

**选择**：模式命中的判据是「查询各段的词元按序出现在术语词元序列中（允许中间有其他词元）」。

**理由**：`活动 属于 能力` → [activity, part, capability]；`activityPartOfCapability` 的词元是 [activity, part, of, capability]——中间夹着结构词 `of`，连续匹配会失败，顺序子序列则正确命中。反过来 `activityMapsToCapabilityType`（[activity, maps, to, capability, type]）没有 `part` 词元 → 不命中模式层，退到段级结构层。

### Decision 3: 排序层级扩展为五层

| 层 | 判定 | 理由 |
|---|---|---|
| 0 | 整串精确（名称/别名/规范名） | 用户输入的就是这个名字 |
| 1 | **词元模式**（顺序子序列） | 关系结构完全对上 |
| 2 | 段级结构化（P2） | 概念都对，结构未对上 |
| 3 | 名称/别名子串 | 文本命中，语义未结构 |
| 4 | 仅定义/数据组/规范名 | 最弱 |

**理由**：把「结构对上」与「概念对上」分开，`活动 属于 能力` 能把 `activityPartOfCapability` 稳定排在 `activityMapsToCapabilityType` 之前。

### Decision 4: 解释是**按需**附加，不改变默认契约

**选择**：`search_terms(query, explain=False)`；`explain=True` 时结果项带 `match`（`tier`/`kind`/`pattern`/`segments`）。CLI `--explain` 打开；人类模式额外打印一行理由。

**理由**：解释会显著增大输出体积，默认关闭可保持既有消费者零影响（也守住「既有 JSON 字段不变」的兼容承诺）。

### Decision 5: `search_terms` 保持签名，新增 `match_terms`

**选择**：indexer 提供 `match_terms(query) -> list[TermMatch]`（术语 + 解释），`search_terms` 变成 `[m.term for m in match_terms(query)]` 的薄包装。

**理由**：既有调用点（`KnowledgeAPI`、测试、pipeline）无需改动即获得新排序；需要解释的调用方走新入口。

## Risks / Trade-offs

- **[风险] 排序变化影响既有断言** → 已有 429 条测试是回归网；实施后必须全绿，若有依赖旧序的断言，按语义评估后修正并说明。
- **[风险] 回溯匹配的性能** → 片段与候选规模极小（实测 279 术语、131 词元），且只在命中候选后进行；无实测性能问题即不优化。
- **[取舍] 解释结构成为新的对外形状** → 用 `kind` 枚举（exact/pattern/structural/substring/text）锁定语义，测试断言其取值集合，避免自由文本漂移。

## Migration Plan

- P3 只改检索与 CLI 输出；派生索引不变（`canonical_zh` 已在 P2 落地）。
- P4（新术语自动命名）随后：构建期用组合器为新术语生成规范名，未覆盖即要求登记词元。

## Open Questions

- 人类模式的理由行是否要为每条结果都打印？**当前默认**：打印，因为 `--explain` 是显式请求；不带该 flag 时完全不打印。
