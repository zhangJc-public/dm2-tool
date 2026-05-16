## Context

`knowledge.py` 中 search/concept/views/view 四个命令手动从 dataclass 挑选字段构造 JSON dict。dataclass 定义在 `api.py`（KnowledgeSearchResult / ConceptResult / ViewResult），CLI 输出 dict 是这些 dataclass 的字段子集或全集。当前手动维护，新增字段时需同步更新 CLI。

## Goals / Non-Goals

**Goals:**
- CLI JSON 输出字段集合自动与 dataclass 定义保持同步
- 列表类输出（`knowledge views`）保持简洁，不全量输出

**Non-Goals:**
- 不改变非 JSON 输出（typer.echo 文本格式）
- 不改 main.py 中的复合结构输出
- 不改变 API 层 dataclass 定义

## Decisions

### 1. 使用 `dataclasses.asdict()` 替代手工 dict

`dataclasses.asdict()` 递归转换 dataclass 为 dict，字段名即 key。与当前手工 dict key 完全一致（dataclass field 名未变过）。

对列表摘要命令（`knowledge views`），先 `asdict()` 再用 dict comprehension 过滤到目标字段：

```python
# views 列表摘要：只保留 5 个关键字段
summary_fields = {"view_id", "view_name", "viewpoint", "description", "dependencies"}
data = [{k: v for k, v in asdict(v).items() if k in summary_fields} for v in vlist]
```

对详情命令（search/concept/view），直接 `asdict()` 全量输出。

### 2. 不引入第三方库

`dataclasses.asdict()` 是 Python 标准库，无需额外依赖。

## Risks / Trade-offs

- [Risk] `asdict()` 会递归深层 dataclass，若未来 dataclass 包含不可序列化对象 → 实际字段都是 str/list/dict/int/Optional[str]，不存在此风险
- [Risk] 输出字段变多可能导致 AI Agent context 浪费 → `knowledge views` 列表保持过滤，`view/search/concept` 本身就是详情查询，字段多是有益的
