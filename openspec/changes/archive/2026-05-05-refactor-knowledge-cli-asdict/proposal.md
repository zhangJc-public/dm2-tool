## Why

`knowledge.py` 中 4 个命令（search/concept/views/view）手动从 dataclass 逐个挑选字段构造 JSON dict。当 dataclass 新增字段时（如 `enhance-views-yaml-metadata` 中 ViewResult 加了 6 个字段），CLI 手工 dict 必须同步更新。刚完成的 `enhance-views-yaml-metadata` 就漏了这一步，事后才补上。消除这个手工同步点是低风险高收益的改善。

## What Changes

- `knowledge view`：手工 15 字段 dict → `dataclasses.asdict(v)` 全量自动输出
- `knowledge views`：手工 5 字段 dict → `dataclasses.asdict(v)` + 显式字段过滤（列表摘要保留简洁）
- `knowledge search`：手工 4 字段 dict → `dataclasses.asdict(r)` 全量自动输出
- `knowledge concept`：手工 8 字段 dict → `dataclasses.asdict(c)` 全量自动输出
- 以上 4 个命令的非 JSON 文本输出行为不变

## Capabilities

### New Capabilities

- `cli-auto-field-sync`: CLI knowledge 命令的 JSON 输出自动与 dataclass 字段保持同步，不再需要手动维护字段列表

### Modified Capabilities

（无）—— 不改变任何 spec 级别的行为，JSON 字段集合与当前输出一致（只是自动化来源）

## Impact

- `src/dm2/cli/commands/knowledge.py` — 4 处手工 dict 构造替换为 `dataclasses.asdict()` + 必要时过滤
- 不涉及其他文件
- API 输出不变量：JSON key 名由 dataclass field 名决定，当前 field 名与手动 dict key 完全一致
