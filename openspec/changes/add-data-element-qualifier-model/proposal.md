## Why

`add-chinese-term-aliases` 解决了中文「查得到」，但代价是 **279 条逐条手写的中文别名**：它只覆盖已知术语，新增术语必须人工补写，且中文名与英文名之间没有可解释的结构关系——查询「能力 分类」仍然 0 命中，因为别名层做不了词元级归一。

对 279 个术语的实测表明，DM2 术语名有强规则结构，可以按 **GB/T 18391（ISO/IEC 11179）「对象类 + 特性 + 表示」** 的数据元命名思路重构：

| 实测维度 | 结果 |
|---|---|
| 词元总量 | 279 个名字 → **131 个唯一词元**（大小写归一）；106 个出现 ≥2 次，仅 **25 个是孤例** |
| 幂类型层（95 个术语，34%） | **100% 规则化**：`XType` = 基名 + 「类型」（66/70 精确，其余 4 个缺基名）；`XTypeType` = 中间名 + 「的类型」（25/25） |
| 实体层（173） | 纯词元顺序拼接精确复现 **124/173 = 71.7%**；补一条「的类型」规则 → **149/173 ≈ 86%** |
| 关联层（106） | 纯顺序拼接仅 **24/106 = 22.6%**；加 `by`/`of` 语序规则 → **36/106 = 34%** |

关键结论：**两层（数据元 + 限定词）不够**。关联层的失败不是词表缺口，而是**语序/句式**——英文「主语+动词+宾语」对不上中文关系句式（`X属于Y`、`X由Y执行`、`X由Y实现`、`X在Y下可执行`）。因此模型必须是三层：**数据元词表 + 限定词词表 + 组合语法（关系模板表）**。

## What Changes

本变更只做 **P1：模型与校验**（不改运行时检索行为）。

- **新增权威源** `dm2-reference/dm2-element-vocabulary.yaml`：数据元（对象类）、限定词（含关系谓词与 `of`/`type`/`instance` 等结构词）、关系模板三类条目
- **新增组合器** `src/dm2/kernel/elements.py`：把术语名按词元分解，优先匹配关系模板，否则走对象类拼接，产出**规范中文名**（确定性、零 LLM）
- **构建期强制**：`scripts/build_knowledge_indexes.py` 校验词表——`terms.json` 里出现的每个词元都必须登记为数据元或限定词，模板必须良构；**未登记词元即构建失败**
- **对账测试**：新增 `test/test_element_vocabulary.py`，用组合器复现 279 个术语，与既有别名层逐条对账，并设**覆盖率门限**（实体 ≥ 90%、关联 ≥ 90%），差异逐条列出
- **文档**：`docs/readme.md` 增加「数据元模型」一节；`docs/foundation.md` 记录基线数字与本次变更；`CHANGELOG.md` 记录

现有 279 条别名**保留**，降级为「显示/同义词层」；组合层负责规范名、词元归一与后续检索扩展（P2）。

## Capabilities

### New Capabilities

- `dm2-element-vocabulary`：数据元/限定词词表 + 关系模板 + 组合器 + 对账门限。

### Modified Capabilities

（无。P1 不改运行时检索契约；P2 再修改 `dm2-metamodel-knowledge`。）

## Impact

**Affected code**:
- 新增 `src/dm2/kernel/elements.py`（词表加载 + 组合器）
- `scripts/build_knowledge_indexes.py`（词表校验；P1 不新增派生字段）

**Affected artifacts**:
- 新增 `dm2-reference/dm2-element-vocabulary.yaml`（权威源，入库）
- 新增 `test/test_element_vocabulary.py`

**Compatibility**:
- 运行时行为不变：`terms.json` 字段与 CLI 输出均不改（P1 只加词表与校验）
- 现有 `zh_aliases` 检索路径保持不变，回退风险为零

**Invariant check**:
- 零 LLM：组合器是纯词表 + 模板替换
- 不新增包层级：`src/dm2/kernel/elements.py` 落在既有 `kernel`(L1)，无需登记新层
- 索引派生：词表是**权威源**，P2 才会派生进索引；P1 仅校验
