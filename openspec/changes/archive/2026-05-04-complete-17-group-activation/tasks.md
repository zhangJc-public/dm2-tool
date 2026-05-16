## 1. 创建 7 个缺失的数据组模板

- [x] 1.1 创建 `dm2-reference/core/groups/00-foundation/Foundation-Template.md`（抽象层，keywords 含基础/本体/抽象/关联/时态/ontology）
- [x] 1.2 创建 `dm2-reference/core/groups/11-resource-flow/ResourceFlow-Template.md`（keywords 含资源流/数据流/接口/连接/拓扑/flow/interface）
- [x] 1.3 创建 `dm2-reference/core/groups/12-pedigree/Pedigree-Template.md`（抽象层，keywords 含谱系/溯源/推导/置信度/provenance/derivation）
- [x] 1.4 创建 `dm2-reference/core/groups/13-information-pedigree/InformationPedigree-Template.md`（keywords 含信息谱系/衍生/聚合/变换/血缘/lineage）
- [x] 1.5 创建 `dm2-reference/core/groups/14-org-structure/OrgStructure-Template.md`（keywords 含组织结构/层级/汇报/干系人/hierarchy/stakeholder）
- [x] 1.6 创建 `dm2-reference/core/groups/15-reification/Reification-Template.md`（抽象层，keywords 含具体化/抽象层次/类型/实例/桥接/abstraction）
- [x] 1.7 创建 `dm2-reference/core/groups/16-information-data/InformationData-Template.md`（keywords 含信息/数据/模型/结构/元素/data model/structure）

## 2. DataGroupActivator 覆盖全部 17 组

- [x] 2.1 修改 `_scan_templates()`：从 `group-to-views.yaml` 加载全部 17 个 group ID，确保无模板的组也出现在激活向量中
- [x] 2.2 修改 `activate()`：返回全部 17 组的 `DataGroupActivation`（无模板的组 score=0.0）

## 3. analyze --json 输出增强

- [x] 3.1 在 `analyze --json` 输出中增加 `group_to_views` 字段（group_id → name/label/description/mapped_views）
- [x] 3.2 在 `analyze --json` 输出中增加 `views_completed` 字段（已生成视图 ID 列表）
- [x] 3.3 在 `analyze --json` 输出中增加 `view_dependencies` 字段（候选视图 → 依赖列表）
- [x] 3.4 从 `recommended_views` 中移除 `priority` 字段，输出不排序

## 4. 验证

- [x] 4.1 `dm2 analyze -d "test" --json` 输出包含 17 个 group 的 `data_group_activation`
- [x] 4.2 `dm2 analyze -d "test" --json` 输出包含 `group_to_views` 字段
- [x] 4.3 `dm2 analyze -d "test" --json` 输出包含 `views_completed` 和 `view_dependencies`
- [x] 4.4 `recommended_views` 无 `priority` 字段且未排序
- [x] 4.5 `dm2 cynefin --json -d "..."` + `dm2 analyze --json -d "..."` 正常（propose workflow 链路）
- [x] 4.6 全 17 组模板的 `related_dm2_views` 与 `group-to-views.yaml` 一致
