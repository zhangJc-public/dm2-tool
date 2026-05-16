## 1. knowledge.py 重构

- [x] 1.1 `view` 命令：手工 15 字段 dict → `dataclasses.asdict(v)`
- [x] 1.2 `views` 命令：手工 5 字段 dict → `asdict(v)` + summary_fields 过滤
- [x] 1.3 `search` 命令：手工 4 字段 dict → `dataclasses.asdict(r)`
- [x] 1.4 `concept` 命令：手工 8 字段 dict → `dataclasses.asdict(c)`

## 2. 验证

- [x] 2.1 `dm2 knowledge view OV-2 --json` 输出所有字段且值与重构前一致
- [x] 2.2 `dm2 knowledge views --json` 仅含 5 个摘要字段
- [x] 2.3 `dm2 knowledge search "Activity" --json` 输出所有 KnowledgeSearchResult 字段
- [x] 2.4 `dm2 knowledge concept "Activity" --json` 输出所有 ConceptResult 字段
- [x] 2.5 非 JSON 文本输出不变（view/views/search/concept 的 typer.echo 不受影响）
