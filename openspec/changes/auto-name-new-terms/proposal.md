## Why

P1–P3 建立了完整的「数据元 + 限定词 + 组合语法」模型，并让检索用上它。但**约束还是旧时代的那一条**：构建期强制「每个术语都必须有手写中文别名」（`dm2-term-zh-aliases.yaml` 缺一条就构建失败）。这条约束在 D9 修复时是必要的——当时没有别名就等于中文 0 命中——但现在**已经不成立**：

- 组合器为全部 279 个术语都能产出规范名（`canonical_zh`，实体 100%、关联 96.2% 与人工别名一致），且构建期已强制「术语名分解出的每个词元都必须登记」
- 因此**新术语天然会被自动命名**：只要它由既有词元组成，规范名立刻可得；否则构建失败要求登记词元——这正是 P4 想要的闭环

继续强制手写别名有两个坏处：**新术语的第一道门槛是人力**（写 279 条的经验不可复用），以及**别名层与模型层的职责混淆**（别名本该是「补充同义词」，不是「中文名的唯一来源」）。

## What Changes

- **解除按术语的别名强制**：`dm2-term-zh-aliases.yaml` 允许**部分覆盖**——构建不再因「某术语没有别名」失败；但键必须是现有术语名、值不得为空或重复（防错字保护保留）
- **数据组别名转为强制**：`groups:` 段（17 个数据组）必须存在且完整——它是「资源流」这类组级中文召回的唯一来源，不能悄悄缺失
- **中文名的强制来源转移**：构建期改为要求**每个术语都有非空 `canonical_zh`**（由词元全覆盖保证）；别名层降级为可选补充
- **命名预检入口**：新增 `dm2 knowledge compose <术语名>`，对任意名字（入库或待定）给出词元分解、各词元中文、组合结果与**未登记词元**清单——新术语命名与词表补登记的工作流入口
- **构建报告**：输出「有策展别名的术语数 X/279」与「组合覆盖 279/279」，让缺口可见但不致命
- **文档**：readme、foundation、CLAUDE.md（索引派生规则改写）、CHANGELOG 同步

## Capabilities

### Modified Capabilities

- `dm2-metamodel-knowledge`：中文名保证改为由组合层提供（`canonical_zh`），策展别名成为可选补充；新增术语自动命名的要求与场景。
- `dm2-element-vocabulary`：词表要能**描述任意术语名**（含未入库的待定名），给出组合结果与未登记词元。

## Impact

**Affected code**:
- `scripts/build_knowledge_indexes.py`（`load_zh_aliases` 放宽按术语强制、`groups` 段转为必需、`canonical_zh` 非空硬校验、覆盖率报告）
- `src/dm2/kernel/elements.py`（`describe(name)`）
- `src/dm2/cli/commands/knowledge.py`（`compose` 子命令）

**Affected artifacts**:
- `dm2-reference/core/terms.json`（重生成；内容不变，本次只是构建约束变化）
- `test/test_knowledge_indexes.py`、`test/test_element_vocabulary.py`、`test/test_cli_json_contract.py`（新命令纳入契约覆盖）

**Compatibility**:
- 现有 279 个术语仍全部有策展别名，**输出与检索行为不变**
- 变更的本质是「新增术语时的约束」：从「必须写别名」变为「必须能组合（否则登记词元）」
- `terms.json` 字段不变

**Invariant check**:
- 零 LLM：组合与描述都是词表查表
- 不新增包层级/依赖
- 「无静默降级」：词元缺登记仍然构建失败，只是把「让人写别名」换成「让人登记词元」
