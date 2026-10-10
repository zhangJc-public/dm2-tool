## Context

`dm2 knowledge search` 的可检索文本来自派生索引 `terms.json`，而该索引的 `definition`/`aliases` 完全继承自 DoDAF 数据字典（英文）。实测 279 个术语中含中文的定义与别名均为 0，所以中文查询必然空结果；`docs/foundation.md` §5 把这项记为 D9「已记录、明确延后」。

本变更的目标是**在不引入 LLM、不改动 DoDAF 血统**的前提下补齐中文召回。

## Goals / Non-Goals

**Goals**

- 279 个术语各有中文别名，且这份别名有单一权威源、被构建校验、被测试守护
- `dm2 knowledge search "能力"`、`"资源流"`、`"活动属于能力"` 等中文查询能命中正确术语
- 多词查询（`activity capability`、`能力 活动`）按 token AND 命中，不再要求整串子串
- 结果顺序稳定：术语名/中文别名命中优先于定义命中

**Non-Goals**

- 不做自动翻译、母语模型、术语自动扩充（零 LLM 契约）
- 不做拼音、错别字纠正、同义词扩展
- 不覆盖 52 个视图名与 17 个数据组名的中文（另开变更）
- 不改 `knowledge term/taxonomy/associations/content/views/stats` 的输出形状

## Decisions

### Decision 1: 独立权威源，不往 DoDAF 数据字典里塞中文

**选择**：新增 `dm2-reference/dm2-term-zh-aliases.yaml`，顶层 `version` + `aliases: {<term>: [中文, …]}`。

**理由**：`dm2-data-dictionary.yaml` 是从 DoDAF 标准 XLS 解析出的权威源，注释里明确保留其来源与 id 规则；把 dm2 自产的中文别名混进去会污染「这一行来自标准」的血统。独立文件同时让中文别名可以单独评审、单独演进而不动标准数据。

**Alternatives**：A. 直接改字典条目加 `zh_aliases`（拒绝：血统混淆，且字典重建脚本已删除，改动无法从 XLS 复现）；B. 运行时查一个不校验的 JSON（拒绝：违反「索引派生」，且拼错术语名不会报错）。

### Decision 2: 构建时强校验 + 「每术语必有别名」测试

**选择**：`build_knowledge_indexes.py` 读别名源后逐键校验：键必须存在于数据字典术语集合、值必须是非空且去重的中文串；任何违规**报错退出**。另加测试断言 `terms.json` 中 279 条术语的 `zh_aliases` 均非空。

**理由**：别名漏一条，对应中文查询就是 0 命中——这种失败必须响。测试把「全量」变成可执行约束，也让**将来新增术语**必然被拦下（新术语必须同时补中文别名），而不是悄悄缺一条。

### Decision 3: 检索语义 = 分词 AND + 分层排序

**选择**：`search_terms(query)`：

1. 归一化（casefold、去首尾空白），按空白与常见中文/英文标点切分 token；
2. 单 token：沿用子串匹配；多 token：**全部 token** 都要在该术语的可检索文本中出现（AND），避免「能力 视图」把整库拉进来；
3. 可检索文本面 = 术语名 + 定义 + 标准别名 + **中文别名** + 数据组 id；
4. 排序：术语名或中文别名命中 → 定义/组命中 → 其余，段内保持字典序，保证结果可比。

**理由**：AND 比 OR 精度高得多，且中文用户常用「定语+术语」的写法（「作战活动」）。分层排序让最可能的答案稳定排第一，Agent 不必猜。

**Alternatives**：A. 只做子串不做分词（拒绝：多词查询继续 0 命中，而 D9 的复现就包含这一类）；B. 引入分词库（拒绝：新增依赖，且中文术语查询不需要 NLP，标点/空白切分足够）。

### Decision 4: 结果里区分标准别名与中文别名

**选择**：`KnowledgeSearchResult` 保留 `aliases`（DoDAF 标准别名），新增 `zh_aliases`。

**理由**：审计与提示词都要能分辨「这条是标准里的别名」还是「dm2 策展的中文对照」。两者混在一个数组里会丢失这层信息，且 `aliases` 的语义会被悄悄改写。

### Decision 5: 别名撰写规范

- 优先采用 DoDAF/DM2 中文文献的通行译名（Performer→执行者、Capability→能力、Measure→度量）。
- 关联术语按 CamelCase 语义直译（`activityPartOfCapability` → 活动属于能力、活动归属能力）。
- 每术语 1–4 条：一条主译名 + 必要近义词；**不塞宽泛词**（如不给 System 加「东西」），宽泛词会污染排序。
- 别名只影响召回，不影响权威定义；写错低危且可随时修正（有测试守护一致性）。

## Risks / Trade-offs

- **[风险] 别名歧义导致误召回**（例如「服务」同时指向 Services 组与 Service）→ 排序分层 + 别名去重；必要时把更精确的译名排在前面。
- **[风险] 279 条人工撰写存在错译** → 别名不影响权威定义；用测试锁定结构（非空、去重、键存在），语义质量靠评审与后续增量修正。
- **[风险] 拆分后 `search "01-performer"` 之类原有英文行为改变** → 单 token 子串语义保留，现有测试（`search Performer` → 10、别名 `Actor` 命中 Performer）必须继续绿。
- **[取舍] 新增术语会被测试拦住** → 这是有意的成本，换掉「静默缺别名」。

## Migration Plan

1. 落地别名源与构建校验，重生成 `terms.json`（一次构建，无运行时迁移）。
2. 项目本地 `.dm2/reference/` 副本：`dm2 init` 会复制新索引；既有项目重跑 `dm2 init`（或自行复制 `terms.json`）即可获得中文召回，旧副本只是检索不到中文，不报错。

## Open Questions

- 是否需要在 `dm2 instructions` 的 `context.dm2_terms` 里也带上中文别名（让指令正文显示中英对照）？**当前默认**：本次不做，避免扩大输出面；若需要另开小变更。
