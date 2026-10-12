## 1. Query decomposition

- [x] 1.1 `QuerySegment` / `QueryPlan` 数据模型（片段文本、kind、候选词元、命中的词条）
- [x] 1.2 `ElementVocabulary.plan_query(text)`：分词 → 逐段反查 → 判定 element/qualifier/unknown
- [x] 1.3 单测：`活动 属于 能力` → element/qualifier/element；`资源流` → unknown；英文片段按词元识别

## 2. Order-sensitive matching

- [x] 2.1 顺序子序列匹配器（候选回溯），返回命中的词元序或 None
- [x] 2.2 `DM2KnowledgeIndexer.match_terms(query) -> list[TermMatch]`：术语 + 解释
- [x] 2.3 五层排序：整串精确 → 词元模式 → 段级结构化 → 名称/别名子串 → 仅文本
- [x] 2.4 `search_terms` 变薄包装（签名不变，既有调用点零改动）
- [x] 2.5 回溯失败不抛异常：退化为段级结构化

## 3. Explanation surface

- [x] 3.1 `MatchExplanation`（tier/kind/pattern/segments）与 `SegmentMatch`（segment/route/entry/tokens/matched）
- [x] 3.2 `KnowledgeAPI.search_terms(query, explain=False)`；`explain=True` 时结果项带 `match`
- [x] 3.3 默认输出与既有字段完全不变（`match` 缺席）
- [x] 3.4 CLI `--explain`：JSON 附加 `match`；人类模式打印一行理由

## 4. Tests

- [x] 4.1 分解单测（含 unknown 片段与一对多候选）
- [x] 4.2 模式匹配测试：`活动 属于 能力` 由 `activityPartOfCapability` 领先，且其 `kind == "pattern"`
- [x] 4.3 顺序敏感测试：反序查询（`能力 属于 活动`）不判为 pattern
- [x] 4.4 解释结构测试：`tier`/`kind` 取值受限、segments 覆盖每个查询片段
- [x] 4.5 默认无解释：不带 explain 时结果项**没有** `match` 字段
- [x] 4.6 CLI：`--explain` 的 JSON 与人类输出均可解析/包含理由；不带 flag 时输出不变
- [x] 4.7 回归：既有 429 条测试全绿（含 P1/P2 的检索断言）

## 5. Documentation

- [x] 5.1 `docs/readme.md`：检索一节补 `--explain` 与五层排序
- [x] 5.2 `docs/foundation.md`：基线数字更新 + P3 记录
- [x] 5.3 `CLAUDE.md`：数据元模型规则补充「查询分解与命中理由」
- [x] 5.4 `CHANGELOG.md`：Added 记录

## 6. Quality gates & archive

- [x] 6.1 `python3 scripts/build_knowledge_indexes.py` 干净通过
- [x] 6.2 `pytest test/` 全绿；`ruff check src/ test/ scripts/` 干净
- [x] 6.3 `openspec validate --all --strict` 通过
- [x] 6.4 端到端人工验证：`search "活动 属于 能力" --explain`、`search "能力 活动" --explain`、`search "资源流"`（无解释）
- [ ] 6.5 `openspec archive explain-search-matches` 并复核基线
