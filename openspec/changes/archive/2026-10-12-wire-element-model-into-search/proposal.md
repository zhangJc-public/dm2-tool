## Why

P1（`add-data-element-qualifier-model`）建立了数据元/限定词模型与组合器，但对运行时检索**零影响**：`dm2 knowledge search` 仍然只做「别名/定义子串匹配」。实测暴露两个问题：

- **精度不足**：查询 `能力 活动` 的首条命中是 `Activity`——它命中的是**数据组中文别名**（`03-capability` 继承的「能力」），而不是「活动—能力」关系；真正的答案 `activityPartOfCapability` 排在后面
- **词元未归一**：模型已经知道「能力 = capability」「执行者 = performer」，检索却用不上，同一概念的中英写法无法互相召回；组合出的规范名（如 `结束边界类型的度量`）也不在检索面内

P2 把模型接进检索：`terms.json` 派生 `canonical_zh`，查询先做**词元归一**（片段 → 数据元/限定词），再做**结构化匹配**（分段 OR、跨段 AND），最后才回退到子串匹配。

## What Changes

- **派生字段**：`terms.json` 增加 `canonical_zh`（组合器产出的规范中文名；组合失败为空串），由 `scripts/build_knowledge_indexes.py` 通过 `dm2.kernel.elements` 生成
- **词元归一**：`ElementVocabulary` 增加反查（中文词条 → 词元，一对多），检索把查询片段映射为候选词元集合
- **结构化匹配**：查询分段后，**段内 OR、跨段 AND**——某段能归一为候选词元时，要求术语词元集合与之相交；不能归一的段回退子串匹配。结构化命中排在「名称/别名命中」之后、「仅定义/数据组命中」之前
- **规范名可检索**：`canonical_zh` 进入可检索文本
- **输出**：`knowledge search --json` 结果项增加 `canonical_zh`（附加字段，既有字段不变）
- **构建报告**：构建脚本输出组合覆盖率（实体/关联）

## Capabilities

### Modified Capabilities

- `dm2-metamodel-knowledge`：派生索引 `terms.json` 增加 `canonical_zh`；运行时术语检索扩展为「词元归一 + 结构化匹配 + 规范名可检索」。

## Impact

**Affected code**:
- `src/dm2/kernel/elements.py`（反查表：中文词条 → 词元）
- `src/dm2/kernel/indexer.py`（`DM2Term.canonical_zh`、`search_terms` 归一与分层）
- `src/dm2/core/knowledge/api.py`（`KnowledgeSearchResult.canonical_zh`）
- `scripts/build_knowledge_indexes.py`（生成 `canonical_zh`、覆盖率报告）

**Affected artifacts**:
- `dm2-reference/core/terms.json`（重生成，新增 `canonical_zh`）

**Compatibility**:
- `knowledge search --json` 既有字段与语义不变，仅新增 `canonical_zh`
- 子串匹配仍然保留（作为兜底层），因此召回不会回退；排序会变化（结构化命中提前）
- 未新增依赖、未新增包层级（改动都在 `kernel`/`core` 既有位置）

**Invariant check**:
- 零 LLM：归一与匹配都是词表查表
- 索引派生：`canonical_zh` 由权威源派生，快照测试守护
- 输出形状：`knowledge search` 不在 `schemas/` 声明内，本次仅附加字段
