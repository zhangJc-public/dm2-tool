## Context

`dm2 change new` 自动创建 `analysis/` 子目录。当前 propose 模板要求 agent 强制写入 CLI cynefin/analyze 输出。改为软指引。

## Decisions

**D1: 模板措辞从强制改为建议**

propose.py 中当前文本：

```
Save the Cynefin result to `dm2-changes/<name>/analysis/cynefin.md`.
Save analysis results to `dm2-changes/<name>/analysis/data-group-activation.md`.
```

改为：

```
Optionally save your own rich analysis artifacts to
`dm2-changes/<name>/analysis/` for audit trail:
- `cynefin-assessment.md` — your deep Cynefin domain analysis
- `data-group-activation.md` — your data group activation breakdown
- `concern-match.md` — concern matching rationale
Do NOT dump raw CLI JSON output — capture your own reasoning, not the thin keyword-match results.
```

**D2: analysis/ 目录定位**

- 审计用途，不是必需产物
- agent 自行判断分析深度是否值得独立成文
- 浅分析由 proposal/design 承载即可，不重复写入
