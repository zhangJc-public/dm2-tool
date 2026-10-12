## 1. Authoritative source — 词表

- [x] 1.1 创建 `dm2-reference/dm2-element-vocabulary.yaml`（`version` + `elements` + `qualifiers` + `templates` 四段），头部注释说明来源、血统与「未登记词元即失败」
- [x] 1.2 登记全部 131 个词元：对象类入 `elements`，结构词（of/type/instance/whole/part 等）与关系谓词入 `qualifiers`
- [x] 1.3 编写关系模板表（连接词序列 + 中文模板），覆盖关联层的核心句式
- [x] 1.4 记录结构规则（结尾 `type` / `type type`）在文件注释或模板段中

## 2. Composer — 组合器

- [x] 2.1 新增 `src/dm2/kernel/elements.py`：加载词表、词元分解（CamelCase + casefold）
- [x] 2.2 `compose(term) -> Optional[str]`：最长连接词优先匹配模板 → 槽位递归组合 → 回退对象类拼接
- [x] 2.3 结构规则：结尾 `type type` → `{前缀}的类型`；结尾 `type` → `{前缀}类型`
- [x] 2.4 未登记词元返回 `None` 并携带原因（不猜、不静默）
- [x] 2.5 纯函数、无 I/O 副作用；词表加载走 `get_reference_path()` 同源路径解析

## 3. Build-time validation

- [x] 3.1 `scripts/build_knowledge_indexes.py` 校验词表：`terms.json` 每个词元都已登记，否则构建失败并列出未登记词元
- [x] 3.2 校验模板良构：槽位与中文模板占位符一致、连接词均已登记、模板不重复
- [x] 3.3 构建输出报告组合覆盖率（实体/关联分列）

## 4. Reconciliation tests

- [x] 4.1 `test/test_element_vocabulary.py`：全部 131 词元已登记（无遗漏）
- [x] 4.2 组合器对 279 个术语逐一组合，与别名层对账；断言实体 ≥ 90%、关联 ≥ 90% 精确复现
- [x] 4.3 差异逐条打印（术语 / 组合名 / 别名层现值），便于人工修订词元
- [x] 4.4 词表校验失败用例：未登记词元、坏模板（占位符不匹配、连接词未登记）均导致失败
- [x] 4.5 幂类型家族专项：`XType` 与 `XTypeType` 的组合结果与别名层完全一致

## 5. Documentation

- [x] 5.1 `docs/readme.md`：新增「数据元模型（GB/T 18391）」一节，说明三层结构、组合规则与对账门限
- [x] 5.2 `docs/foundation.md`：基线数字更新 + 本次变更记录；说明这是 D9 之后的检索质量路线（P1–P4）
- [x] 5.3 `CLAUDE.md`：索引派生规则处补充「词表是权威源，未登记词元构建失败」
- [x] 5.4 `CHANGELOG.md`：Added 记录数据元/限定词模型

## 6. Quality gates & archive

- [x] 6.1 `python3 scripts/build_knowledge_indexes.py` 干净通过（词表校验 + 覆盖率报告）
- [x] 6.2 `pytest test/` 全绿；`ruff check src/ test/ scripts/` 干净
- [x] 6.3 `openspec validate --all --strict` 通过
- [x] 6.4 人工抽查：任取 10 个术语核对组合名与 DM2 语义一致
- [x] 6.5 `openspec archive add-data-element-qualifier-model` 并复核基线
