## Why

`dm2 knowledge search` 是 AI Agent 与中文用户查询 DM2 知识库的主入口，但它的可检索文本**全部是英文**：279 个术语的 `definition` 与 `aliases` 中含中文的条数实测为 **0**。因此任何中文查询必然 0 命中——`dm2 knowledge search "资源流"` → 0，`"resource flow"` → 0（后者是因为没有术语名或定义包含该短语，`ResourceFlow` 也不是术语名）。

这是 `docs/foundation.md` §5 中**唯一仍未关闭的功能性缺口（D9）**，当时判定为「知识库内容层，独立变更更清晰」，现在正是这个变更。

用户可见面全是中文（CLI 提示、技能正文、文档），知识库却是英文可检索——Agent 拿到中文需求后无法用 DM2 术语定位知识，只能靠猜英文名。实测从 `docs/reference/` 语料机械抽取中英对照不可行：743 条候选里仅 89 条能与术语名对齐，且多为噪声（如 `Performer（IS-A Performer）`）。

## What Changes

- **新增权威源** `dm2-reference/dm2-term-zh-aliases.yaml`：279 个术语的中文别名（每术语至少 1 条），由 dm2 策展，独立于 DoDAF 数据字典，保持「字典来自标准」的血统
- **构建时校验**：`scripts/build_knowledge_indexes.py` 合并别名进派生索引 `terms.json` 的 `zh_aliases`；键不存在于术语表、别名空值或重复即**报错退出**，不产生静默空档
- **检索改造**：`DM2KnowledgeIndexer.search_terms` 认 `zh_aliases`，并把查询按空白/标点**分词**（多 token 采用 AND 语义），使 `能力 分类`、`capability taxonomy` 这类多词与中文查询都能命中
- **结果可区分**：`knowledge search --json` 的结果项保留标准 `aliases`，新增 `zh_aliases`，让调用方区分「DoDAF 标准别名」与「dm2 策展中文别名」
- **稳定排序**：术语名/中文别名命中排在定义命中之前，结果顺序可比
- **文档与基线**：readme 检索一节说明中文别名；`docs/foundation.md` D9 从「明确延后」移入「已修复」

## Capabilities

### Modified Capabilities

- `dm2-metamodel-knowledge`：权威源增加「中文别名」一条派生输入与校验；派生索引 `terms.json` 增加 `zh_aliases`；知识检索需求扩展为「中文与多词查询可召回」。

## Impact

**Affected code**:
- `scripts/build_knowledge_indexes.py`（读取并校验别名源、写入 `zh_aliases`）
- `src/dm2/kernel/indexer.py`（`search_terms`：别名匹配 + 查询分词 + 稳定排序）
- `src/dm2/core/knowledge/api.py`（`KnowledgeSearchResult` 增加 `zh_aliases`）

**Affected artifacts**:
- 新增 `dm2-reference/dm2-term-zh-aliases.yaml`（权威源，入库）
- 重生成 `dm2-reference/core/terms.json`（派生索引，入库；快照测试守护）

**Compatibility**:
- `knowledge search --json` 现有字段不变，仅新增 `zh_aliases`（附加字段，非破坏性）
- `terms.json` 消费者（indexer / KnowledgeAPI / 指令上下文）只读新增字段，无行为回退
- 未新增依赖（仍是 PyYAML）

**Invariant check**:
- 不违反 `dm2-no-llm-dependency`：别名是**策展内容**，不是运行时翻译，dm2 不调用任何 LLM
- 不违反「索引派生」：权威源 YAML → 派生 JSON，运行时只加载 JSON
- 不违反「输出形状以 schema 声明」：`knowledge search` 不在 `schemas/` 声明内，本次仅附加字段
