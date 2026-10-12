## 1. Relax per-term alias requirement

- [x] 1.1 `load_zh_aliases` 去掉「术语缺别名即失败」；保留键存在性与值非空/去重校验
- [x] 1.2 `groups:` 段转为**必需**且必须覆盖全部 17 个数据组（缺失即构建失败）
- [x] 1.3 构建报告输出「策展别名覆盖 X/279」与「组合覆盖 279/279」

## 2. Composition as the mandatory Chinese name

- [x] 2.1 `build_all` 硬校验：任何术语 `canonical_zh` 为空即构建失败（不允许无中文名的术语）
- [x] 2.2 构建脚本 docstring 说明新的约束分工

## 3. Naming preview

- [x] 3.1 `ElementVocabulary.describe(name)`：词元、类型（element/qualifier/unknown）、中文、组合结果、未登记词元
- [x] 3.2 CLI `dm2 knowledge compose <术语名>`：人类模式打印分解与结果；`--json` 输出同一结构
- [x] 3.3 「无法组合」返回 success + 空 `composed` + `unregistered` 清单（退出码 0）
- [x] 3.4 `test_cli_json_contract.py` 纳入新命令的 `--json` 覆盖

## 4. Tests

- [x] 4.1 `describe()` 单测：全部已登记 → 组合名；含未登记词元 → `composed` 为空且 `unregistered` 列出
- [x] 4.2 构建放宽测试：部分覆盖的别名源**通过**；`groups` 段缺失**失败**
- [x] 4.3 强制转移测试：`canonical_zh` 为空时构建失败（用篡改的词表触发）
- [x] 4.4 中文名保证测试：每个术语「有策展别名 **或** 有 `canonical_zh`」
- [x] 4.5 新术语端到端：把合成术语写进临时 `terms.json`（无任何 `zh_aliases`），断言可被**组合名**与**中文模式查询**检索到
- [x] 4.6 回归：279 个术语的既有断言与 P1–P3 测试全绿

## 5. Documentation

- [x] 5.1 `docs/readme.md`：新增 `dm2 knowledge compose`；「中文检索」一节说明中文名的来源分工（组合为主、别名为补）
- [x] 5.2 `docs/foundation.md`：基线数字更新 + P4 记录（路线完成）
- [x] 5.3 `CLAUDE.md`：索引派生规则改写（词元全覆盖为硬约束，别名按术语为可选补充，`groups` 必需）
- [x] 5.4 `CHANGELOG.md`：Added 记录

## 6. Quality gates & archive

- [x] 6.1 `python3 scripts/build_knowledge_indexes.py` 干净通过并打印覆盖率
- [x] 6.2 `pytest test/` 全绿；`ruff check src/ test/ scripts/` 干净
- [x] 6.3 `openspec validate --all --strict` 通过（本变更 delta 已 strict 干净；仓库另 5 个 spec 因 openspec 1.14.1 新增长文本警告而红，见 foundation §5 D11）
- [x] 6.4 端到端人工验证：`knowledge compose CapabilityType`、`compose ZzzThing`（未登记）、`compose --json`
- [x] 6.5 `openspec archive auto-name-new-terms` 并复核基线
