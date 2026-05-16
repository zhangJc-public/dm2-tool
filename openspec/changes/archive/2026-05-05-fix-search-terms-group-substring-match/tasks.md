## 1. 修复 group 匹配逻辑

- [x] 1.1 `indexer.py` `search_terms()`: 精确相等 `==` 改为子串包含 `in`

## 2. 验证

- [x] 2.1 `search_terms("Foundation")` 返回 ≥ 5 条术语（含 DM2 Foundation / IDEAS Foundation 组）
- [x] 2.2 `search_terms("ResourceFlow")` 仍然 ≥ 5 条（回归确认）
- [x] 2.3 `search_terms("Activity")` 仍然正常匹配（回归确认无误匹配）
