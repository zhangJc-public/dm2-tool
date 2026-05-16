## Context

views.yaml 的 `groups` 字段当前使用 14 个自造短名称，与 `DM2DataGroup` 枚举（17 个标准值）不完全对应。`InstructionBuilder.build_view_instructions()` 中 `self.knowledge.search_terms(group)` 按组名检索术语时，组名不匹配导致只能靠定义文本模糊命中。`ViewTemplate.dm2_groups` 字段无校验，任意字符串均可存入。

## Goals / Non-Goals

**Goals:**
- views.yaml 中所有 `groups` 值精确匹配 `DM2DataGroup` 枚举名
- 命名统一：`InfoAndData` → `InformationAndData`，`OrgStructure` → `OrganizationalStructure`
- 补全：`ResourceFlow` 加到 7 个资源流相关视图，`InformationPedigree` 加到 2 个信息血缘视图
- `Foundation` 扩展到 AV-2, CV-1

**Non-Goals:**
- 不改 DM2DataGroup 枚举定义
- 不改 `_dm2_v202_extract.json` 术语分组
- 不改 InstructionBuilder 或 ViewRecommender 代码
- 不加入 Pedigree 和 Reification

## Decisions

### 1. groups 值使用 DM2DataGroup 的 `.name` 属性

DM2DataGroup 枚举定义在 `indexer.py`：

```python
class DM2DataGroup(str, Enum):
    FOUNDATION = "00-基础模式"
    PERFORMER = "01-Performer"
    ACTIVITY = "02-Activity"
    ...
    RESOURCE_FLOW = "11-ResourceFlow"
    PEDIGREE = "12-Pedigree"
    INFO_PEDIGREE = "13-InformationPedigree"
    ...
    INFO_AND_DATA = "16-InformationAndData"
```

枚举的 `.name` 属性（如 `RESOURCE_FLOW`, `INFO_AND_DATA`）是 Python 标识符，不适合直接暴露。枚举的 `.value` 属性是带编号的中文名（如 `"11-ResourceFlow"`），版本化但冗长。

**决定：使用枚举的简短英文名**，即去掉编号前缀的语义名。映射如下：

| DM2DataGroup | 简短名 |
|---|---|
| FOUNDATION | Foundation |
| PERFORMER | Performer |
| ACTIVITY | Activity |
| CAPABILITY | Capability |
| RESOURCE | Resource |
| GUIDANCE | Guidance |
| MEASURE | Measure |
| LOCATION | Location |
| SERVICES | Services |
| PROJECT | Project |
| RULES | Rules |
| RESOURCE_FLOW | ResourceFlow |
| PEDIGREE | Pedigree |
| INFO_PEDIGREE | InformationPedigree |
| ORG_STRUCTURE | OrganizationalStructure |
| REIFICATION | Reification |
| INFO_AND_DATA | InformationAndData |

这是当前 views.yaml 已在使用的方式（如 `Activity`, `Performer`），只是此前命名不完全一致。

### 2. 不加入 Pedigree 和 Reification

理由：两者在 group-to-views.yaml 中均映射到 `"All"`，标签为 `"Meta"`，是全局横切关注点。加入具体视图的 groups 会稀释语义区分度。这两个值保留在 DM2DataGroup 枚举中供 ViewRecommender 使用，但不出现在 views.yaml 的 groups 字段中。

## Risks / Trade-offs

- [Risk] 如果未来 `DM2DataGroup` 枚举 rename → views.yaml 需要同步更新。但枚举名是稳定的（基于 DM2 标准），风险极低。
