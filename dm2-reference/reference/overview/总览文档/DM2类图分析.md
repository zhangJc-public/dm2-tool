# DM2 类图完整分析

> 基于 18 张 DM2 元模型类图（IDEAS 格式）  
> 📅 **最后更新: 2026-04-18（重构完成 · 全部 18/18 已分析）**  
> ✅ 状态: 所有类图分析已完成，详见 [[详细分析]] 目录

---

## 一、类图概述

### 1.1 收集的类图清单 ✅ 全部完成

| 序号  | 类图                                 | 对应数据组/模式        | 详细分析                                         | 状态  |
| --- | ---------------------------------- | --------------- | -------------------------------------------- | --- |
| 1   | Capability.png                     | 03-Capability   | [[详细分析/DM2-Capability详细分析]]                  | ✅   |
| 2   | Common Patterns.png                | 00-基础模式         | [[详细分析/DM2-CommonPatterns详细分析]]              | ✅   |
| 3   | Foundation For Associations.png    | 00-基础模式         | [[详细分析/DM2-FoundationForAssociations详细分析]]   | ✅   |
| 4   | IDEAS TopLevel.png                 | 00-基础模式         | [[详细分析/DM2-IDEASTopLevel详细分析]]               | ✅   |
| 5   | Information and Data.png           | 16-InfoData     | [[详细分析/DM2-InformationAndData详细分析]]          | ✅   |
| 6   | Information Pedigree.png           | 13-InfoPedigree | [[详细分析/DM2-InformationPedigree详细分析]]         | ✅   |
| 7   | Location.png                       | 07-Location     | [[详细分析/DM2-Location详细分析]]                    | ✅   |
| 8   | Measure.png                        | 06-Measure      | [[详细分析/DM2-Measure详细分析]]                     | ✅   |
| 9   | Naming and Description Pattern.png | 00-基础模式         | [[详细分析/DM2-NamingAndDescriptionPattern详细分析]] | ✅   |
| 10  | Organizational Structure.png       | 14-OrgStructure | [[详细分析/DM2-OrgStructure详细分析]]                | ✅   |
| 11  | performer.png                      | 01-Performer    | [[详细分析/DM2-Performer详细分析]]                   | ✅   |
| 12  | project.png                        | 09-Project      | [[详细分析/DM2-Project详细分析]]                     | ✅   |
| 13  | Reification Levels.png             | 15-Reification  | [[详细分析/DM2-Reification详细分析]]                 | ✅   |
| 14  | resourceFlow.png                   | 11-ResourceFlow | [[详细分析/DM2-ResourceFlow详细分析]]                | ✅   |
| 15  | Rules.png                          | 10-Rules        | [[详细分析/DM2-Rules详细分析]]                       | ✅   |
| 16  | Services.png                       | 08-Services     | [[详细分析/DM2-Services详细分析]]                    | ✅   |
| 17  | Temporal Part and Boundaries.png   | 00-基础模式         | [[详细分析/DM2-TemporalPartAndBoundaries详细分析]]   | ✅   |
| 18  | Pedigree.png                       | 12-Pedigree     | [[详细分析/DM2-Pedigree详细分析]]                    | ✅   |

---

## 二、IDEAS Top Level（元模型根基）

### 2.1 顶层结构

根据 IDEAS Foundation 元模型：

```
Thing（万物）
│
├── Individual（实例层）
│   └── <<Individual>> - 具有时空扩展的具体实体
│       颜色：Grey(80%) - R40 G40 B40
│
├── Type（类型层）
│   ├── <<Type>> - 类型的规格定义
│   │   颜色：Pale Blue - R153 G204 B255
│   │
│   ├── <<IndividualType>> - 个体类型的规格
│   │   颜色：Light Orange - R255 G173 B91
│   │
│   └── <<Powertype>> - 幂类型（元类型的类型）
│       颜色：Lavender - R204 G153 B255
│
└── Tuple（元组/关系）
    └── <<TupleType>> - 元组类型的规格
        颜色：Light Green - R204 G255 B204
```

### 2.2 关键关系

| 关系 | 类型 | 说明 |
|------|------|------|
| <<typeInstance>> | 依赖 | 类型与实例的关系（红色） |
| <<powertypeInstance>> | 依赖 | 类型与幂类型的关系（红色） |
| <<super-subtype>> | 泛化 | 类型之间的继承关系（蓝色） |
| <<wholePart>> | 聚合 | 整体与部分关系（绿色） |
| <<tuple>>/<<couple>> | 关联 | 事物之间的关系（灰色） |
| <<namedBy>> | 关联 | 名称与事物的关系（黑色） |

---

## 三、Reification Levels（物化层次）

### 3.1 Type/Individual 分层机制

DM2 通过 Reification 实现从"通用"到"具体"的层次建模：

```
┌─────────────────────────────────────────────────────────────┐
│                    <<Powertype>>                            │
│                   ActivityType                              │
│              （活动类型的类型）                               │
└─────────────────────────┬───────────────────────────────────┘
                          │ <<powertypeInstance>>
┌─────────────────────────▼───────────────────────────────────┐
│                      <<Type>>                               │
│                     ActivityType                            │
│                （活动类型/模板）                             │
└─────────────────────────┬───────────────────────────────────┘
                          │ <<typeInstance>>
┌─────────────────────────▼───────────────────────────────────┐
│                   <<Individual>>                            │
│                  IndividualActivity                          │
│                  （具体活动实例）                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 各数据组的 Type/Individual 对应

| 数据组 | Type | Individual | 关系 |
|--------|------|------------|------|
| Performer | PerformerType | IndividualPerformer | performerTypeOfIndividual |
| Activity | ActivityType | IndividualActivity | activityTypeOfIndividual |
| Resource | ResourceType | IndividualResource | resourceTypeOfIndividual |
| Capability | CapabilityType | IndividualCapability | capabilityTypeOfIndividual |
| Location | LocationType | IndividualLocation | locationTypeOfIndividual |
| Condition | ConditionType | IndividualCondition | conditionTypeOfIndividual |
| Service | ServiceType | IndividualService | serviceTypeOfIndividual |
| Project | ProjectType | IndividualProject | projectTypeOfIndividual |
| System | SystemType | IndividualSystem | systemTypeOfIndividual |
| Measure | MeasureType | IndividualMeasure | measureTypeOfIndividual |

---

## 四、四种关系模式（Common Patterns）

### 4.1 Whole-Part（组成/整体-部分）

**用途**：表示实体之间的包含关系

**示例**：
- `materielPartOfPerformer` - 物资作为执行者的一部分
- `activityPartOfActivity` - 活动作为活动的一部分
- `resourcePartOfResource` - 资源作为资源的一部分
- `capabilityPartOfCapability` - 能力作为能力的一部分
- `servicePartOfService` - 服务作为服务的一部分

**图示**：
```
┌──────────────────┐
│    WholePart      │
│  (整体-部分关系)   │
└────────┬─────────┘
         │ wholePart
         ▼
┌──────────────────┐
│    Part          │
│    (部分)         │
└──────────────────┘
```

### 4.2 Overlap（重叠）

**用途**：表示实体之间的交叉/重叠关系

**示例**：
- `activityOverlapsActivity` - 活动间的时间/资源重叠
- `locationOverlapsLocation` - 空间重叠

**关键应用 - 资源流三重叠**：
```
┌─────────────────────────────────────┐
│                                     │
│  ProducerActivity ──Resource──→ ConsumerActivity
│       │                              │
│       └──────────Overlap─────────────┘
│              (时空重叠)
```

### 4.3 Before-After（时序/前后）

**用途**：表示实体之间的时间顺序关系

**示例**：
- `activityPrecedesActivity` - 活动先于活动
- `resourceConsumedBeforeProduction` - 消费先于生产

### 4.4 Couple（配对）

**用途**：表示实体之间的配对/耦合关系

**示例**：
- `activityPerformedByPerformer` - 活动与执行者的配对
- `activityConsumesResource` - 活动与资源的配对
- `activityProducesResource` - 活动与资源的配对

---

## 五、Performer 类图分析

### 5.1 执行者类型层次

```
<<IndividualType>>
     PerformerType
           │
           ├── OrganizationType
           │      │
           │      └── IndividualOrganization
           │
           ├── SystemType
           │      │
           │      └── IndividualSystem
           │
           ├── ServiceType
           │      │
           │      └── IndividualService
           │
           └── PersonRoleType
                  │
                  └── IndividualPersonRole
```

### 5.2 核心关系

| 关系 | 说明 |
|------|------|
| activityPerformedByPerformer | 执行者执行活动 |
| materielPartOfPerformer | 物资作为执行者的一部分 |
| personRoleTypePartOfPerformer | 人员角色作为执行者的一部分 |
| performerLocatedAtLocation | 执行者位于位置 |
| performerRealizesCapability | 执行者实现能力 |
| ruleConstrainsActivity | 规则约束活动 |

### 5.3 关键洞察

1. **Performer 是中心枢纽**：连接 Activity（谁做）、Capability（交付什么能力）
2. **多层次组成**：Performer 可以由 Materiel、PersonRole 等组成
3. **可度量**：Performer 的性能可通过 Measure 量化
4. **位置感知**：Performer 与 Location 关联

---

## 六、Capability 类图分析

### 6.1 能力层次结构

```
<<IndividualType>>
   CapabilityType
         │
         ├── IndividualCapability
         │
         └── capabilityComposedOfCapability
                │
                └── 子能力...
```

### 6.2 核心关系

| 关系 | 说明 |
|------|------|
| capabilityRealizedByActivity | 能力由活动实现 |
| capabilityDeliveredByPerformer | 能力由执行者交付 |
| capabilityDependsOnCapability | 能力依赖能力 |
| capabilityPartOfCapability | 能力包含能力 |
| measureOfEffect | 效果度量 (MOE) |
| measureOfPerformance | 性能度量 (MOP) |

### 6.3 能力愿景链

```
Vision（愿景）
     │
     └── Goal（目标）
           │
           └── Objective（具体目标）
                 │
                 └── DesiredEffect（预期效果）
                       │
                       └── Capability（能力）
                             │
                             └── Activity（活动）
                                   │
                                   └── Performer（执行者）
```

---

## 七、Activity 类图分析

### 7.1 活动作为核心枢纽

Activity 是 DM2 中连接所有其他概念的中心：

```
                    Resource（消耗）
                         ▲
                         │
┌──────────────┐    Activity    ┌──────────────┐
│   Performer  │◄──────────────┼─►   Rule    │
│   （谁做）   │   （做什么）   │  （约束）    │
└──────────────┘    activity   └──────────────┘
                    PerformedBy
                         │
                         ▼
                   Capability
                   （为什么做）
```

### 7.2 核心关系

| 关系 | 说明 |
|------|------|
| activityPerformedByPerformer | 执行活动的执行者 |
| activityConsumesResource | 活动消耗资源 |
| activityProducesResource | 活动产生资源 |
| activityPartOfCapability | 活动映射到能力 |
| ruleConstrainsActivity | 规则约束活动 |
| activityPerformableUnderCondition | 活动在条件下可执行 |
| activityPartOfActivity | 活动分解 |
| activityPrecedesActivity | 活动时序 |
| activityTriggersActivity | 活动触发活动 |

### 7.3 活动与资源流

根据 DoDAF v2.02：
- 资源流基于活动，不是基于执行者
- 三重叠：生产者活动、资源、消费者活动

---

## 八、Resource Flow 类图分析

### 8.1 资源流三重叠

```
┌─────────────────────────────────────────┐
│                                         │
│  ProducerActivity ──Resource──→ ConsumerActivity
│       │                              │
│       │      时空重叠                  │
│       └──────────Overlap───────────────┘
│              (三重叠)
```

### 8.2 资源类型

| 资源类型 | 说明 |
|---------|------|
| Information | 信息（语义层面） |
| Data | 数据（物理表示） |
| Materiel | 物资（设备、器材） |
| Personnel | 人员 |
| Performers | 执行者 |

### 8.3 核心关系

| 关系 | 说明 |
|------|------|
| activityProducesResource | 活动产生资源 |
| activityConsumesResource | 活动消耗资源 |
| resourceFlow | 资源在执行者间流动 |
| resourcePartOfResource | 资源组成资源 |
| resourceFlowSecurity | 资源流安全属性 |

---

## 九、Rules 类图分析

### 9.1 规则类型层次

```
<<IndividualType>>
    GuidanceType
         │
         ├── Rule（强制性规则）
         │    │
         │    ├── Policy（策略）
         │    ├── Constraint（约束）
         │    └── Regulation（法规）
         │
         ├── Standard（标准）
         │
         ├── Agreement（协议）
         │
         └── Guidance（指导性指南）
```

### 9.2 核心关系

| 关系 | 说明 |
|------|------|
| ruleConstrainsActivity | 规则约束活动 |
| guidanceGuidesActivity | 指南指导活动 |
| standardConstrainsSystem | 标准约束系统 |
| policyGovernsOrganization | 策略治理组织 |
| agreementConstrainsActivity | 协议约束活动 |

---

## 十、Services 类图分析

### 10.1 服务作为 Performer

Service 是 Performer 的一种特殊形式，提供能力访问机制：

```
ServiceType
     │
     ├── IndividualService
     │
     ├── ServicePort（服务端口）
     │      │
     │      └── ServiceInterface
     │
     └── ServiceDescription（服务描述）
            │
            └── ServiceContract（服务契约）
```

### 10.2 核心关系

| 关系 | 说明 |
|------|------|
| serviceEnablesAccessToResource | 服务启用资源访问 |
| serviceConsumesResource | 服务消耗资源 |
| serviceProducesResource | 服务产生资源 |
| serviceComposedOfService | 服务组成服务 |
| serviceDependsOnService | 服务依赖服务 |

---

## 十一、Project 类图分析

### 11.1 项目结构

```
<<IndividualType>>
    ProjectType
         │
         ├── IndividualProject
         │
         ├── Program（项目群）
         │      │
         │      └── Portfolio（项目组合）
         │
         ├── Milestone（里程碑）
         │
         └── Deliverable（交付物）
                │
                └── WorkPackage（工作包）
```

### 11.2 核心关系

| 关系 | 说明 |
|------|------|
| projectDeliversCapability | 项目交付能力 |
| projectComposedOfActivity | 项目由活动组成 |
| projectPerformedByPerformer | 项目由执行者执行 |
| projectHasMilestone | 项目有里程碑 |
| projectProducesDeliverable | 项目产生交付物 |
| projectBudget | 项目预算 |
| projectCost | 项目成本 |
| projectSchedule | 项目进度 |

---

## 十二、Measure 类图分析

### 12.1 度量类型

根据 DM2，Measure 贯穿所有实体：

```
MeasureType
     │
     ├── MeasureOfEffect (MOE) - 效果度量
     ├── MeasureOfPerformance (MOP) - 性能度量
     ├── MeasureOfSuitability - 适用性度量
     ├── MeasureOfWorth - 价值度量
     │
     └── measureOf[Entity] - 关联到各种实体
            │
            ├── measureOfCapability
            ├── measureOfActivity
            ├── measureOfResource
            ├── measureOfSystem
            ├── measureOfService
            ├── measureOfCondition
            ├── measureOfLocation
            └── measureOfProject
```

### 12.2 度量贯穿所有实体

| 度量关联 | 说明 |
|---------|------|
| measureOfCapability | 能力的度量 |
| measureOfActivity | 活动的度量 |
| measureOfResource | 资源的度量 |
| measureOfSystem | 系统的度量 |
| measureOfService | 服务的度量 |
| measureOfCondition | 条件的度量 |
| measureOfLocation | 位置的度量 |
| measureOfProject | 项目的度量 |

---

## 十三、Location 类图分析

### 13.1 位置类型

```
LocationType
     │
     ├── Facility（设施）
     │      │
     │      └── IndividualFacility
     │
     ├── Installation（安装设施）
     │
     ├── Region（区域）
     │
     ├── GeoPoliticalExtent（地缘政治范围）
     │
     ├── Point（点）
     │
     ├── Line（线）
     │
     ├── Volume（体积）
     │
     └── Address（地址）
            │
            ├── URL（网络地址）
            └── IPAddress（IP 地址）
```

### 13.2 核心关系

| 关系 | 说明 |
|------|------|
| performerLocatedAtLocation | 执行者位于位置 |
| systemLocatedAtLocation | 系统位于位置 |
| activityPerformedAtLocation | 活动在位置执行 |
| resourceLocatedAtLocation | 资源位于位置 |
| locationPartOfLocation | 位置组成位置 |
| locationAdjacentToLocation | 位置相邻 |

---

## 十四、Temporal 时间边界

### 14.1 时间扩展

DM2 通过 Temporal 处理时间相关建模：

```
TemporalExtent
     │
     ├── temporalWholePart - 时间整体-部分
     │
     └── beforeAfter - 前后关系
```

### 14.2 时间相关关系

| 关系 | 说明 |
|------|------|
| activityPrecedesActivity | 活动时序 |
| activityOverlapsActivity | 活动重叠 |
| resourceProducedBeforeConsumed | 资源产生与消费时序 |

---

## 十五、Organizational Structure 类图分析

### 15.1 组织结构

```
OrganizationType
     │
     ├── IndividualOrganization
     │
     ├── Post（岗位）
     │      │
     │      └── IndividualPost
     │
     └── PersonRoleType（人员角色类型）
            │
            ├── Skill（技能）
            │      │
            │      └── MeasureableSkill
            │
            └── IndividualPersonRole
```

### 15.2 核心关系

| 关系 | 说明 |
|------|------|
| postPartOfOrganization | 岗位属于组织 |
| postReportsToPost | 岗位汇报关系 |
| personRoleTypePartOfPost | 人员角色属于岗位 |
| postHasResponsibility | 岗位有责任 |
| postHasAuthority | 岗位有权限 |

---

## 十六、Pedigree 谱系

### 16.1 谱系信息

```
Pedigree
     │
     ├── Provenance（出处）
     ├── Author（作者）
     ├── CreationDate（创建日期）
     ├── ModificationDate（修改日期）
     ├── Version（版本）
     ├── ConfidenceLevel（可信度等级）
     ├── VerificationStatus（验证状态）
     └── ApprovalStatus（审批状态）
```

### 16.2 关键应用

- **信息可信度**：数据的来源和历史
- **版本追溯**：文档的版本演变
- **审批流程**：文档的审核状态

---

## 十七、关键洞察总结

### 17.1 IDEAS Top Level 是元模型根基

```
Thing（万物）
├── Individual（实例层）
├── Type（类型层）
│     ├── IndividualType
│     └── Powertype（元类型的类型）
└── Tuple（元组/关系）
```

### 17.2 Reification（物化）是核心机制

- **Type 层**：定义结构模板
- **Individual 层**：具体实例
- **Powertype**：类型的类型（如 ActivityType 本身是什么类型）

### 17.3 四种关系模式

| 关系类型 | 颜色 | 示例 |
|---------|------|------|
| WholePartType | 绿色 | materielPartOfPerformer |
| OverlapType | 绿色 | activityOverlapsActivity |
| CoupleType | 绿色 | activityPerformedByPerformer |
| BeforeAfterType | 绿色 | activityPrecedesActivity |

### 17.4 Activity 是核心枢纽

```
Activity
├── activityPerformedByPerformer → Performer（谁做）
├── activityConsumesResource → Resource（消耗什么）
├── activityProducesResource → Resource（产出什么）
├── activityPartOfCapability → Capability（为什么做）
└── ruleConstrainsActivity → Rule（在什么规则下）
```

### 17.5 Measure 无处不在

- 几乎所有实体都可以被度量
- 通过 `measureOfType` 和 `measureOfIndividual` 关联

### 17.6 Capability 支撑 Goal

```
Vision → Goal → Objective → DesiredEffect → Capability
                                                      ↓
                                              Activity
                                                      ↓
                                              Performer
```

### 17.7 颜色编码总结

| 颜色 | 含义 |
|------|------|
| 蓝色 | 属性/度量类 |
| 紫色 | Type 层（类型定义） |
| 橙色 | Individual 层（实例） |
| 绿色 | 关系/关联 |
| 灰色 | Individual 专用 |
| 红色 | typeInstance 关系 |
| 黄色 | NamingScheme |

---

## 十八、版本信息

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-04-16 | 初稿完成 |
| v2.0 | 2026-04-16 | 校准：与 DoDAF v2.02 官方 PDF 对应，补充关键洞察 |
| **v3.0** | **2026-04-18** | **重构完成：18/18 全部分析完毕 · 链接到详细分析目录 · 知识库结构重组为 16 数据组 + 5 基础模式** |

---

*本文档基于 18 张 DM2 类图和 DoDAF v2.02 官方规范分析整理*  
*📎 完整深度分析文档 → [[详细分析]]（每张类图 20~36KB）*  
*📎 快速导航 → [[DM2-REFERENCE]]（一站式索引）*
