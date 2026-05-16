## Why

`search_terms()` 的 group 匹配使用了精确相等 (`==`)，导致 `search_terms("Foundation")` 无法匹配 DM2 术语中前缀化的组名（如 "DM2 Foundation"、"IDEAS Foundation"）。`InstructionBuilder` 为 Foundation 组视图（AV-2, CV-1, DIV-1）调用 `search_terms("Foundation")` 时只能靠术语定义文本模糊命中的 1 条，而实际关联的 180 条 Foundation 术语全部遗漏。

## What Changes

- `src/dm2/kernel/indexer.py` `search_terms()`: group 匹配逻辑从精确相等 (`==`) 改为子串包含 (`in`)，使 "Foundation" 能匹配 "DM2 Foundation" 和 "IDEAS Foundation"

## Capabilities

### Modified Capabilities

- `view-group-alignment`: search_terms group 匹配规则从精确相等改为子串包含，确保前缀化组名也能被命中

## Impact

- `src/dm2/kernel/indexer.py` — `search_terms()` 方法，改一行逻辑
- 不影响 InstructionBuilder、CLI、views.yaml
