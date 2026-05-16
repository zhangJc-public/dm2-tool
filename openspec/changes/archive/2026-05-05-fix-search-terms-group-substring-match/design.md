## Context

`align-view-groups-to-data-groups` 在 `search_terms()` 中新增了 group 匹配：当 query 未命中 term/definition 时，尝试匹配 term 的 `groups` 字段。当前实现使用精确相等 (`q_nospace == g_nospace`)，但 DM2 术语的 group 名称使用了前缀形式：

- "DM2 Foundation" (163 terms) vs views.yaml 中的 "Foundation"
- "IDEAS Foundation" (17 terms) vs views.yaml 中的 "Foundation"

这导致 `search_terms("Foundation")` 只返回 1 条结果（定义中碰巧含 "foundation" 的术语），遗漏了 180 条 Foundation 组术语。

## Goals / Non-Goals

**Goals:**
- `search_terms("Foundation")` 能匹配 "DM2 Foundation" 和 "IDEAS Foundation" 组下的术语
- 所有已有匹配保持正确（ResourceFlow、InformationPedigree、OrganizationalStructure 等）
- 不引入反向误匹配（如搜索 "Activity" 不应匹配 Foundation 组）

**Non-Goals:**
- 不改 InstructionBuilder、CLI、views.yaml
- 不改 DM2DataGroup 枚举

## Decisions

### 1. 精确相等 → 子串包含

```python
# Before (exact match)
elif any(q_nospace == g.lower().replace(" ", "") for g in t.groups):

# After (substring match)
elif any(q_nospace in g.lower().replace(" ", "") for g in t.groups):
```

**理由**: "Foundation" ("foundation") 是 "DM2 Foundation" ("dm2foundation") 的子串，也是 "IDEAS Foundation" ("ideasfoundation") 的子串。改为 `in` 后两者都能命中。

**备选**: 双向子串匹配 (`q in g or g in q`)。不需要——视图的 groups 是短名，DM2 术语的 groups 是带前缀的长名，单向 `q in g` 已覆盖所有情况。双向还可能引入反向误匹配（如 query="信息基础模式" 匹配 group "Foundation"）。

## Risks / Trade-offs

- [Risk] 子串匹配可能引入误匹配（如 query="Data" 匹配 "Information And Data"）→ Data 不是合法的 groups 值，InstructionBuilder 只传 groups 列表中的值，而合法 groups 值之间无子串关系（如 "ResourceFlow" 不是任何其他 group 名的子串），误匹配风险极低
