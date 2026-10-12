## 1. Vocabulary reverse lookup

- [x] 1.1 `ElementVocabulary.load()` 构建 `reverse`：中文词条 → 词元列表（含复合数据元）
- [x] 1.2 提供 `tokens_for(text) -> list[str]`（无命中返回空列表，不抛异常）
- [x] 1.3 单测：`能力 → [capability]`、`区域 → {area, region}`（一对多）、未知词 → 空

## 2. Derived index

- [x] 2.1 `scripts/build_knowledge_indexes.py` 通过 `dm2.kernel.elements` 生成 `canonical_zh`（未安装时 `sys.path` 兜底）
- [x] 2.2 `terms.json` 每条术语新增 `canonical_zh`（组合失败为空串，不写 null）
- [x] 2.3 构建输出报告组合覆盖率（实体/关联分别统计）
- [x] 2.4 重生成 `terms.json`；快照测试覆盖新字段

## 3. Retrieval

- [x] 3.1 `DM2Term` 增加 `canonical_zh`，从 `terms.json` 加载
- [x] 3.2 `DM2KnowledgeIndexer` 持有词表（懒加载一次），供检索归一使用
- [x] 3.3 `search_terms`：查询分段归一（段内 OR、跨段 AND），结构化命中作为独立层级
- [x] 3.4 `canonical_zh` 进入可检索文本
- [x] 3.5 `KnowledgeSearchResult` 增加 `canonical_zh`，`knowledge search --json` 结果项带上
- [x] 3.6 兜底：无法归一的片段仍走子串匹配（零召回回退）

## 4. Tests

- [x] 4.1 词元归一反查单测（含一对多与未知词）
- [x] 4.2 结构化匹配：`能力 活动` 的关系术语排在 `Activity` 之前；`activityPartOfCapability` 出现在前若干条
- [x] 4.3 中英互召回：中文片段命中英文术语名，英文片段命中中文别名（既有行为不回退）
- [x] 4.4 规范名可检索：按 `canonical_zh` 检索能命中该术语
- [x] 4.5 回归：`Performer`/`Actor`/`01-performer`/`资源流`/`活动属于能力` 既有断言全绿
- [x] 4.6 派生索引：每条术语 `canonical_zh` 非空；快照一致

## 5. Documentation

- [x] 5.1 `docs/readme.md`：检索一节补充词元归一与结构化匹配、`canonical_zh` 字段
- [x] 5.2 `docs/foundation.md`：基线数字更新 + P2 记录
- [x] 5.3 `CLAUDE.md`：数据元模型规则补充「检索侧归一」
- [x] 5.4 `CHANGELOG.md`：Added 记录检索接入

## 6. Quality gates & archive

- [x] 6.1 `python3 scripts/build_knowledge_indexes.py` 干净通过
- [x] 6.2 `pytest test/` 全绿；`ruff check src/ test/ scripts/` 干净
- [x] 6.3 `openspec validate --all --strict` 通过
- [x] 6.4 端到端人工验证：`search "能力 活动"`、`search "能力"`、`search "活动属于能力"`、`search "Performer"`
- [ ] 6.5 `openspec archive wire-element-model-into-search` 并复核基线
