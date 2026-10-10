## 1. Authoritative source — 中文别名

- [x] 1.1 Create `dm2-reference/dm2-term-zh-aliases.yaml`（`version` + `aliases:` 段），头部注释说明：dm2 策展、独立于 DoDAF 字典、只影响召回
- [x] 1.2 为全部 279 个术语各写 1–4 条中文别名（实体优先通行译名；关联按 CamelCase 语义直译）
- [x] 1.3 复核别名唯一性（同术语内不得重复）与精度（避免宽泛词污染排序）

## 2. Build — 合并与校验

- [x] 2.1 `scripts/build_knowledge_indexes.py` 读取别名源，键不存在于字典术语集合时报错退出（列出未知键）
- [x] 2.2 校验别名非空、去重、去除首尾空白；违规即失败
- [x] 2.3 `build_terms()` 在每条术语写入 `zh_aliases`（无别名时不静默留空——由 2.1 保证）
- [x] 2.4 重生成 `dm2-reference/core/terms.json`
- [x] 2.5 更新脚本 docstring 的 emit 说明（terms.json 字段列表加入 `zh_aliases`）

## 3. Retrieval — 检索与输出

- [x] 3.1 `DM2KnowledgeIndexer.search_terms`：可检索面加入 `zh_aliases`
- [x] 3.2 查询分词（空白 + 中英文标点），多 token 采用 AND 语义；单 token 保持子串语义
- [x] 3.3 分层排序：术语名/中文别名命中 → 定义/数据组命中 → 其余，段内字典序
- [x] 3.4 `KnowledgeSearchResult` 增加 `zh_aliases` 字段并在 `KnowledgeAPI.search_terms` 填充
- [x] 3.5 `dm2 knowledge search --json` 结果项带上 `zh_aliases`（附加字段，不改既有字段）

## 4. Tests

- [x] 4.1 `test/test_knowledge_indexes.py`：快照包含 `zh_aliases`；每条术语别名非空（全量守护）
- [x] 4.2 别名源校验测试：未知术语键 → 构建失败；空别名/重复别名 → 构建失败
- [x] 4.3 检索单测：`资源流`/`能力`/`执行者` 等中文命中；CamelCase 关联的中文别名命中
- [x] 4.4 分词测试：`能力 活动`、`activity capability` 按 AND 命中；不相关词组合返回空
- [x] 4.5 回归测试：原有英文行为不变（`Performer`、别名 `Actor`、数据组 `01-performer`）
- [x] 4.6 CLI 信封测试：`dm2 knowledge search 资源流 --json` 返回 `count > 0` 且信封合法

## 5. Documentation

- [x] 5.1 `docs/readme.md`：`dm2 knowledge` 一节说明中文别名与分词检索、`zh_aliases` 字段
- [x] 5.2 `docs/foundation.md`：D9 从「明确延后」移入「已修复」，并在 §4 基线备注本次变更；§5 已修复表补一行
- [x] 5.3 `CLAUDE.md`：索引派生规则处补「改术语中文别名须重跑构建脚本」
- [x] 5.4 `CHANGELOG.md`：Unreleased/Added 记录中文别名检索

## 6. Quality gates & archive

- [x] 6.1 `python3 scripts/build_knowledge_indexes.py` 干净通过并留下 `terms.json` 变更
- [x] 6.2 `pytest test/` 全绿；`ruff check src/ test/ scripts/` 干净
- [x] 6.3 `openspec validate --all --strict` 通过
- [x] 6.4 端到端人工验证：`dm2 knowledge search "资源流" --json`、`search "活动属于能力"`、`search "activity capability"`
- [ ] 6.5 `openspec archive add-chinese-term-aliases`，并复核归档后 spec/测试计数
