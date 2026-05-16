## Why

views.yaml 的 `groups` 字段使用 14 个自造短名称（"Activity", "InfoAndData", "OrgStructure" 等），既不匹配 DM2DataGroup 枚举的 17 个标准名，也不匹配 `_dm2_v202_extract.json` 中的术语组名。InstructionBuilder 通过 `search_terms(group)` 检索上下文时命中率低——搜索 "Activity" 只能靠术语定义文本的模糊匹配碰运气。同时，ResourceFlow（31 个术语）和 InformationPedigree（19 个术语）两个数据组有实体术语但无任何视图引用，浪费了知识库资源。

## What Changes

- 统一命名：`InfoAndData` → `InformationAndData`（3 视图），`OrgStructure` → `OrganizationalStructure`（2 视图）
- 补全缺失数据组：`ResourceFlow` 加到 SV-2/SV-4/SV-6/OV-2/OV-3/DIV-2/DIV-3，`InformationPedigree` 加到 DIV-1/DIV-2
- `Foundation` 扩展到 AV-2（集成字典，定义所有术语）和 CV-1（能力愿景，高层概念建模）
- 不加入 Pedigree 和 Reification（全局横切组，加入会稀释区分度）
- 每视图的 `groups` 字段值确保与 DM2DataGroup 枚举名称精确一致

## Capabilities

### New Capabilities

- `view-group-alignment`: views.yaml 的 `groups` 字段命名与 DM2DataGroup 枚举（17 个标准数据组）完全对齐，确保 InstructionBuilder 的 `search_terms(group)` 精确命中对应数据组的 DM2 术语。

### Modified Capabilities

- `view-metadata-schema`: groups 字段的合法值集合从 14 个自造名变为 15 个 DM2DataGroup 枚举名（不含 Pedigree 和 Reification）

## Impact

- `dm2-reference/core/views.yaml` — 52 个视图的 `groups` 字段值更新
- `dm2-reference/core/groups/` — 不改动模板文件
- `src/dm2/` — 不改动任何 Python 代码（DM2DataGroup 枚举名已是正确的）
