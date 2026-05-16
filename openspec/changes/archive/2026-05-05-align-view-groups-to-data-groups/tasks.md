## 1. 命名统一

- [x] 1.1 `InfoAndData` → `InformationAndData`：DIV-1, DIV-2, DIV-3 的 groups 更新
- [x] 1.2 `OrgStructure` → `OrganizationalStructure`：OV-4, CV-5 的 groups 更新

## 2. 补全缺失数据组

- [x] 2.1 `ResourceFlow` 加到 SV-2, SV-4, SV-6, OV-2, OV-3, DIV-2, DIV-3
- [x] 2.2 `InformationPedigree` 加到 DIV-1, DIV-2
- [x] 2.3 `Foundation` 加到 AV-2, CV-1（DIV-1 已有）

## 3. 验证

- [x] 3.1 全部 52 视图加载无校验警告
- [x] 3.2 所有 groups 值 ∈ 15 合法名（不含 Pedigree, Reification）
- [x] 3.3 `knowledge view SV-4 --json` 确认 groups 含 ResourceFlow
- [x] 3.4 `knowledge view DIV-1 --json` 确认 groups 含 InformationPedigree + Foundation + InformationAndData
- [x] 3.5 `search_terms("ResourceFlow")` 返回 ≥ 5 条术语（实际 10 条）
- [x] 3.6 确认无视图使用 `InfoAndData`, `OrgStructure` 旧名
