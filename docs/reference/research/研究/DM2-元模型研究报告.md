# DM2 元模型研究报告

> 基于 Enterprise Architect 12 打开 `DM2_EA_v2.02.eap` 的 17 张类图分析
> 研究时间：2026-04-12（2026-04-13 补充 Common Patterns）
> 研究者：Claw

---

## 摘要

本报告基于 DoDAF 2.0 的数据元模型（DM2）完整类图研究，通过分析 17 张 EA 类图，系统梳理了 DM2 的元模型结构、实体类型分层、关系类型分类、通用模式（Common Patterns），以及在 Obsidian 知识库中的落地方式。

**核心发现**：DM2 的核心不是数据项分类，而是**数据项之间的关系网络**。Type/Individual 分层机制、四种关系类型（WholePart/Overlap/Couple/BeforeAfter）、以及跨数据组的通用属性（Measure/Location/Temporal/Pedigree）构成了 DM2 的骨架。

---

## 一、DM2 元模型概述

### 1.1 元模型分层结构

```
┌─────────────────────────────────────────────────────────────────────┐
│  元元模型层（Meta-Meta Model）                                       │
│  └── Thing（最顶层抽象）                                             │
├─────────────────────────────────────────────────────────────────────┤
│  元模型层（Meta Model）                                             │
│  └── IndividualType（个体的类型定义）                                 │
│        ├── Condition                                                │
│        ├── LocationType                                             │
│        ├── Activity                                                │
│        ├── Resource                                                │
│        ├── Performer                                               │
│        ├── MeasureType                                             │
│        ├── Rule / Guidance                                         │
│        └── ...                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  实例层（Instance Model）                                           │
│  └── Individual（具体实例）                                         │
│        ├── IndividualActivity                                       │
│        ├── IndividualResource                                       │
│        ├── IndividualPerformer                                     │
│        │     ├── Organization                                       │
│        │     ├── System / Service                                  │
│        │     └── IndividualPersonRole                              │
│        ├── Measure                                                 │
│        └── ...                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 具体化机制（Reification）

具体化（Reification）是 DM2 的核心机制——将 Type 层具体化为 Individual 层：

```
IndividualType（模板）── «IDEAS:powertypeInstance» ──→ Individual（实例）

示例：
- OrganizationType ──→ Organization
- CapabilityType ──→ Capability
- ProjectType ──→ Project
- PersonRoleType ──→ IndividualPersonRole
```

### 1.3 Type/Individual 分层对照表

| IndividualType（模板层） | Individual（实例层）           | 说明          |
| :------------------ | :------------------------ | :---------- |
| Activity            | IndividualActivity        | 活动类型→活动实例   |
| Resource            | IndividualResource        | 资源类型→资源实例   |
| Performer           | IndividualPerformer       | 执行者类型→执行者实例 |
| OrganizationType    | Organization              | 组织类型→组织     |
| PersonRoleType      | IndividualPersonRole      | 角色类型→角色实例   |
| ProjectType         | Project                   | 项目类型→项目     |
| CapabilityType      | Capability                | 能力类型→能力     |
| LocationType        | Location                  | 位置类型→位置     |
| MeasureType         | Measure                   | 度量类型→度量     |
| Rule                | （Rule 直接是 Individual）     | 规则直接是实例     |
| Standard            | （Standard 直接是 Individual） | 标准直接是实例     |
| Service             | （Service 直接是 Individual）  | 服务直接是实例     |
| System              | （System 直接是 Individual）   | 系统直接是实例     |

**关键发现**：并非所有实体都有 Type/Individual 分层。Service、System、Rule、Standard、Agreement 直接是 Individual 层，没有单独的 Type 层。

---

## 二、核心实体类型详解

### 2.1 Performer（执行者）

**分层结构**：
```
Performer（IndividualType）
  ├── System（Individual，直接继承）← 无单独的 Type 层
  ├── Service（Individual，直接继承）← 无单独的 Type 层
  ├── OrganizationType（IndividualType）
  │     └── Organization（Individual）
  └── PersonRoleType（IndividualType）
        └── IndividualPersonRole（Individual）
```

**关键关系**：
- `activityPerformedByPerformer`：Performer 执行 Activity
- `performerRealizesCapability`：Performer 实现 Capability
- `performerConstrainedByRule`：Performer 受规则约束
- `materielPartOfPerformer`：物资是 Performer 的一部分
- `personRoleTypePartOfPerformer`：角色类型是 Performer 的一部分

### 2.2 Activity（活动）

**分层结构**：
```
Activity（IndividualType）
  └── IndividualActivity（Individual）

活动组合方式：
  ├── jointAction（联合活动，BeforeAfterType）← 多个 Activity 并行
  └── superSubType（继承/分解）← Activity 父子关系
```

**关键关系**：
- `activityPerformedByPerformer`：Activity 由 Performer 执行
- `activityPartOfCapability`：Activity 组成 Capability
- `activityPartOfProjectType`：Activity 属于项目类型
- `activityConsumesResource`：Activity 消费 Resource
- `activityProducesResource`：Activity 产生 Resource
- `ruleConstrainsActivity`：Rule 约束 Activity
- `activityPerformableUnderCondition`：Activity 在条件下可执行

### 2.3 Capability（能力）

**分层结构**：
```
CapabilityTypeType（IndividualTypeType）
  ↓
CapabilityType（IndividualType）
  ↓
Capability（Individual）
  ↓
IndividualCapability（Individual）← 分配给具体 Performer 的能力实例
```

**关键关系**：
- `activityPartOfCapability`：Activity 组成 Capability
- `activityMapsToCapabilityType`：Activity 映射到能力类型
- `capabilityOfPerformer`：Capability 属于 Performer
- `desiredEffectOfCapability`：Capability 期望产生 Resource
- `desireMeasure`：Capability 的度量指标

**三角关系**：
```
Performer ──performs──→ Activity ──partOf──→ Capability
     ↑                                          ↓
     └──────────── realizes ───────────────────┘
```

### 2.4 Resource 与 Information（资源与信息）

**分层结构**：
```
Thing
  ↓
Resource（IndividualType）
  ↓
IndividualResource（Individual）
  ├── Location / GeoPoliticalExtent
  └── IndividualPerformer（反向关联）

RepresentationType
  ├── InformationType
  │     └── DataType
  └── Representation（Information）
        └── Data
```

**关键关系**：
- `activityConsumesResource`：Activity 消费 Resource
- `activityProducesResource`：Activity 产生 Resource
- `representedBy`：Information 由 Resource 表示
- `describedBy`：Information 被描述为某种类型
- `associationOfInformation`：Information 之间的关联
- `resourceInLocationType`：Resource 关联到 LocationType

**Information vs Data**：
| | Information | Data |
|:---|:---|:---|
| 层级 | 语义层（meaning）| 物理层（representation）|
| 例子 | "这是一起高危安全事件" | `{"level": "high", "event_id": 123}` |
| 存储 | 概念存在于笔记 body | 具体值存在于 Frontmatter/附件 |

### 2.5 Service（服务）

**分层结构**：
```
Performer（IndividualType）
  └── Service（Individual，直接继承）
        └── ServicePort（Port 的子类）
```

**关键关系**：
- `serviceEnablesAccessToResource`：Service 提供对 Resource 的访问
- `serviceConsumedByPerformer`：Service 被 Performer 消费
- `serviceComposedOfService`：Service 由多个 Service 组成
- `serviceDependsOnService`：Service 依赖其他 Service

**ServicePort**：
```yaml
servicePorts:
  - name: REST API
    protocol: HTTPS
    port: 443
  - name: LDAP
    protocol: LDAPS
    port: 636
```

### 2.6 Project（项目）

**分层结构**：
```
ProjectType（IndividualType）
  ↓
Project（Individual）
```

**关键关系**：
- `activityPartOfProjectType`：Activity 属于项目类型
- `desiredEffectRealizedByProjectType`：期望效果由项目类型实现
- `projectDeliversCapability`：Project 交付 Capability
- `projectPerformedByPerformer`：Project 由 Performer 执行
- `projectComposedOfActivity`：Project 分解为 Activity

**与 Vision 的关系**：
```
Vision
  ↓ visionIsRealizedByDesiredEffect
ProjectType ──desiredEffectRealizedByProjectType──→ Resource
```

### 2.7 Location（位置）

**分层结构**：
```
LocationType（IndividualType）
  ↓
Location（Individual）
  ├── GeoPoliticalExtent（地缘政治范围）
  │     ├── RegionOfWorld
  │     ├── Country
  │     ├── RegionOfCountry
  │     └── ...
  ├── SolidVolume（实体体积）
  │     └── Surface（表面）
  │           ├── PlanarSurface（平面）
  │           │     ├── PolygonArea（多边形区域）
  │           │     ├── RectangularArea（矩形区域）
  │           │     ├── EllipticalArea（椭圆区域）
  │           │     └── CircularArea（圆形区域）
  │           └── ...
  └── Point（点）
        └── GeoStationaryPoint（地球静止点）
```

**关键关系**：
- `resourceInLocationType`：Resource 关联到 LocationType
- `individualResourceInLocation`：IndividualResource 关联到 Location
- `measureOfIndividualPoint`：Point 可用 Measure 精确定义

### 2.8 Measure（度量）

**分层结构**：
```
MeasureTypeType（IndividualTypeType）
  ↓
MeasureType（IndividualType）
  ↓
Measure（Individual）
  ├── PhysicalMeasure（物理度量）
  ├── SpatialMeasure（空间度量）
  ├── TemporalMeasure（时间度量）
  ├── PerformanceMeasure（性能度量）
  ├── MaintainabilityMeasure（可维护性度量）
  ├── AdaptabilityMeasure（适应性度量）
  ├── OrganizationalMeasure（组织度量）
  ├── NeedsSatisfactionMeasure（需求满足度量）
  ├── ServiceLevel（服务级别）
  └── Skill / MeasurableSkill（技能度量）
```

**关键关系**：
- `measureOfType`：Measure 关联到 Type 层实体
- `measureOfIndividual`：Measure 关联到 Individual 层实体
- `measureOfIndividualPoint`：Point 的度量
- `effectMeasure`：效果度量
- `desireMeasure`：期望度量
- `skillOfPersonRoleType`：Skill 关联到 PersonRoleType
- `capabilityOfPerformer`：Capability 关联到 Performer

### 2.9 Rule / Guidance（规则与指导）

**分层结构**：
```
Guidance（IndividualType）
  ↓
Rule（IndividualType）
  ├── Agreement（协议）
  │     └── partiesToAnAgreement（约束 Performer 之间的关系）
  └── Standard（标准）
        ├── FunctionalStandard（功能标准）
        └── TechnicalStandard（技术标准）
```

**关键关系**：
- `ruleConstrainsActivity`：Rule 约束 Activity
- `partiesToAnAgreement`：Agreement 约束多个 Performer
- `standardConstrainsSystem`：Standard 约束 System
- `activityPerformableUnderCondition`：Activity 在条件下可执行
- `measureTypeApplicableToActivity`：MeasureType 适用于 Activity

---

## 三、关系类型分类

DM2 的所有关系都可以归类为四种 Association Types：

### 3.1 WholePartType（整体-部分关系）

**含义**：一个实体是另一个实体的组成部分。

| 关系名 | 连接 | 说明 |
|:---|:---|:---|
| `activityPartOfProjectType` | Activity → ProjectType | Activity 属于项目 |
| `activityPartOfCapability` | Activity → Capability | Activity 组成 Capability |
| `portPartOfPerformer` | Port → Performer | 端口是 Performer 的一部分 |
| `resourceInLocationType` | Resource → LocationType | 资源在位置中 |
| `personRoleTypePartOfPerformer` | PersonRoleType → Performer | 角色是 Performer 的一部分 |
| `partOf` / `composedOf` | 通用 | 整体/部分通用关系 |

### 3.2 OverlapType（重叠关系）

**含义**：两个实体共享某种关系，但各自独立存在。

| 关系名                              | 连接                           | 说明                      |
| :------------------------------- | :--------------------------- | :---------------------- |
| `activityPerformedByPerformer`   | Activity ↔ Performer         | Performer 执行 Activity   |
| `partiesToAnAgreement`           | Agreement ↔ Performer (2..*) | 多方参与协议                  |
| `capabilityOfPerformer`          | Capability ↔ Performer       | Performer 实现 Capability |
| `serviceEnablesAccessToResource` | Service ↔ Resource           | Service 启用资源访问          |
| `performerRealizesCapability`    | Performer → Capability       | Performer 实现能力          |
| `overlap`                        | 通用                           | 重叠关系通用标签                |

### 3.3 CoupleType（成对关系）

**含义**：两个实体形成对等关系。

| 关系名 | 连接 | 说明 |
|:---|:---|:---|
| `jointAction` | Activity ↔ Activity | 联合活动（并行）|
| `couple` | 通用 | 成对关系通用标签 |

### 3.4 BeforeAfterType（前后顺序关系）

**含义**：一个实体在另一个实体之前/之后，有方向性。

| 关系名 | 连接 | 说明 |
|:---|:---|:---|
| `activityConsumesResource` | Activity → Resource | Activity 消费 Resource |
| `activityProducesResource` | Activity → Resource | Activity 产生 Resource |
| `desiredEffectDirectsActivity` | Resource → Activity | 期望效果指导 Activity |
| `before` / `after` | 通用 | 前后顺序通用标签 |

---

## 四、跨数据组通用机制

### 4.1 Temporal（时间维度）

**核心概念**：
```
Individual（实体）
  └── temporalWholePart（时间部分）
        └── temporalBoundary（时间边界）
              ├── startBoundary（开始）
              └── endBoundary（结束）
                    ↓
              Measure（时间度量）
```

**应用**：
- Project 有多个时间阶段（temporalWholePart）
- Activity 有开始/结束时间（temporalBoundary）
- Measure 量化时间边界

### 4.2 Naming and Description（命名与描述）

**核心概念**：
```
Thing（被描述的事物）
  ↓ thingDescribed
Information（描述信息）
  ↓ describedBy / representedBy
Representation（表示形式）
  ├── Name（名称）←── namedBy → Sign
  └── 其他表示形式

Type/Individual 分层：
- SignType / Sign
- RepresentationType / Representation
- InformationType / Information
```

**应用**：
- 每个 DM2 实体都有 Name（通过 Representation → Name → Sign）
- 每个 DM2 实体都有 Description（通过 Information）
- 遵循 NamingScheme / DescriptionScheme

### 4.3 Information Pedigree（信息谱系）

**核心概念**：
```
Information（信息）
  └── PedigreeInformation（带谱系信息的信息）
        └── PedigreeInformationType（谱系信息类型）

Pedigree 属性：
- source：信息来源
- producedBy：生产系统/活动
- processingChain：处理链
- quality：质量评级
- freshness：新鲜度
```

**应用**：
- 追踪数据/信息的来源和转换历史
- 建立信息血缘关系
- 评估数据质量

### 4.4 Organizational Structure（组织结构）

**核心概念**：
```
OrganizationType（IndividualType）
  ↓
Organization（Individual）
  ├── partOf：组织层级关系
  └── composedOf：组织组成

PersonRoleType（IndividualType）
  ↓
IndividualPersonRole（Individual）
  ├── partOf：角色层级关系
  ├── skillOf：角色技能
  └── performs：角色执行的活动
```

---

## 五、Common Patterns（通用模式）

Common Patterns 是 DM2 元元模型的总结，定义了所有数据项的通用建模方式。它不是某个数据组的专属内容，而是贯穿整个 DM2 的元层规范。

### 5.1 Type/Individual 具体化模式

**目的**：区分"模板"（Type）与"实例"（Individual）。

```
IndividualType（模板层）
  ├── TypeType（元类型）
  │     └── IndividualTypeType（类型层）
  │
  ├── Activity ──具体化──→ IndividualActivity
  ├── Resource ──具体化──→ IndividualResource
  ├── OrganizationType ──→ Organization
  ├── CapabilityType ──→ Capability
  ├── ProjectType ──→ Project
  │
  └── 直接 Individual 型（无 Type 层）
        ├── System
        ├── Service
        ├── Rule
        ├── Standard
        └── Agreement
```

**关键关系**：
- `typeOf`：Individual 的类型
- `powerTypeInstance`：具体化关系

### 5.2 四元素建模模式（Tetrahedron Pattern）

DM2 的每个核心实体都可以用四个元素来描述：

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Element（元素）                             │
│   什么（What）│   谁（Who）│   何时/何地（When/Where）│   为何（Why）│
├─────────────────────────────────────────────────────────────────────┤
│   Activity       Performer      Time/Location      Rule/Condition  │
│   Resource       Capability     Measure            DesiredEffect    │
│   Information    Organization   TemporalBoundary   Guidance         │
└─────────────────────────────────────────────────────────────────────┘
```

**应用示例**：
| 实体 | What | Who | When/Where | Why |
|:---|:---|:---|:---|:---|
| Activity | 做什么 | Performer | Temporal | Rule/Condition |
| Capability | 能力定义 | Performer 实现 | — | DesiredEffect |
| Resource | 资源类型 | — | Location | Measure |
| Information | 信息含义 | — | — | Representation |

### 5.3 WholePartType 层级模式

**目的**：描述整体与部分的包含关系。

```
┌─────────────────────────────────────────────────┐
│         WholePartType（整体-部分类型）            │
├─────────────────────────────────────────────────┤
│  WholePart │ 描述整体与部分的层级结构             │
│  TemporalWholePart │ 时间上的整体与部分           │
└─────────────────────────────────────────────────┘

层级示例：
- OrganizationType → Organization → OrganizationalUnit
- LocationType → Location → GeoPoliticalExtent / SolidVolume
- CapabilityType → Capability → IndividualCapability
- Activity → JointAction（并行活动）
```

### 5.4 Association 通用关系模式

**四种关系类型**（见第三章），在 Common Patterns 中统一建模：

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Association（关联基类）                        │
├─────────────────────────────────────────────────────────────────────┤
│  WholePartType    │ 包含关系：整体包含部分                           │
│  OverlapType      │ 重叠关系：实体间共享某种关联                     │
│  CoupleType       │ 成对关系：两个实体形成对等关系                   │
│  BeforeAfterType  │ 顺序关系：实体间有方向性（之前/之后）             │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.5 Temporal 建模模式

**目的**：为所有实体添加时间维度。

```
┌─────────────────────────────────────────────────────────────┐
│              Temporal 通用模式                               │
├─────────────────────────────────────────────────────────────┤
│  Individual                                                  │
│    ├── temporalWholePart ──→ TemporalBoundary               │
│    │                          ├── startBoundary             │
│    │                          └── endBoundary               │
│    │                                ↓                       │
│    │                          Measure（时间度量）            │
│    │                                                        │
│    ├── temporalPoint ──→ TemporalBoundary（单点时间）        │
│    │                          ↓                             │
│    │                    TemporalMeasure                    │
│    │                                                        │
│    └── temporalWhole（时间整体）                             │
└─────────────────────────────────────────────────────────────┘
```

**应用**：
- Project：多个时间阶段（temporalWholePart）
- Capability：能力有效期
- Agreement：合同有效期
- Activity：开始/结束时间

### 5.6 Naming & Description 模式

**目的**：为所有实体提供可追溯的命名和描述。

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Naming and Description Pattern                    │
├─────────────────────────────────────────────────────────────────────┤
│  Thing（被描述的事物）                                                │
│    │                                                                │
│    └── thingDescribed ──→ Information（描述信息）                    │
│                              │                                      │
│                              └── describedBy ──→ Representation     │
│                                                         │           │
│                              ┌─────────────────────────┴──────────┐│
│                              ↓                                    ↓│
│                          NameType                              Name│
│                              ↓                                    ↓│
│                         namedBy ──→ SignType                   Sign│
└─────────────────────────────────────────────────────────────────────┘
```

**关键发现**：
- DM2 的所有 Name 都有类型（NameType）
- 每个 Name 都可以追溯到 Sign（符号）
- Information 可以是 PedigreeInformation（带谱系信息）

### 5.7 Measure 通用量化模式

**目的**：为所有实体提供可度量的属性。

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Measure 通用模式                             │
├─────────────────────────────────────────────────────────────────────┤
│  MeasureTypeType → MeasureType → Measure（度量）                     │
│                                                                     │
│  关联到任意实体：                                                    │
│  ├── measureOfType（度量 Type 层）                                  │
│  ├── measureOfIndividual（度量 Individual 层）                      │
│  ├── measureOfIndividualPoint（度量空间点）                          │
│  └── measureOfTemporalBoundary（度量时间边界）                        │
└─────────────────────────────────────────────────────────────────────┘

度量类型：
- PhysicalMeasure（物理度量）
- SpatialMeasure（空间度量）
- TemporalMeasure（时间度量）
- PerformanceMeasure（性能度量）
- ServiceLevel（服务级别）
- Skill（技能度量）
```

### 5.8 Location 空间建模模式

**目的**：为资源提供空间位置。

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Location 空间建模模式                            │
├─────────────────────────────────────────────────────────────────────┤
│  LocationType → Location                                            │
│                                                                     │
│  空间类型：                                                          │
│  ├── GeoPoliticalExtent（地缘政治范围）                              │
│  │     ├── RegionOfWorld → Country → RegionOfCountry               │
│  │     └── 层级递进                                                  │
│  ├── SolidVolume（实体体积）                                        │
│  │     ├── Surface → PlanarSurface → PolygonArea/RectangularArea   │
│  │     └── Point / Ellipse / Circle                                │
│  └── Point（空间点）                                                 │
│        └── GeoStationaryPoint（地球静止点）                          │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.9 Pedigree 信息血缘模式

**目的**：追踪信息的来源和质量。

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Information Pedigree 模式                         │
├─────────────────────────────────────────────────────────────────────┤
│  Information                                                       │
│    └── PedigreeInformation（带谱系的信息）                          │
│          ├── source：信息来源                                       │
│          ├── producedBy：生产系统/活动                                │
│          ├── processingChain：处理链                                │
│          ├── quality：质量评级                                       │
│          ├── freshness：新鲜度                                       │
│          └── lineageType：谱系类型                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.10 Common Patterns 的元元模型总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DM2 元元模型核心要素                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐      │
│  │   Type 分层      │     │  Association   │     │    Temporal     │      │
│  │  IndividualType │     │  WholePartType │     │ TemporalBoundary│      │
│  │        ↓        │     │  OverlapType   │     │    Measure      │      │
│  │  Individual     │     │  CoupleType    │     │                 │      │
│  │                 │     │  BeforeAfterType│     │                 │      │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘      │
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐      │
│  │    Location     │     │     Naming      │     │    Guidance     │      │
│  │  LocationType   │     │  Description    │     │    Rule/        │      │
│  │      ↓          │     │  Information    │     │    Standard/     │      │
│  │   Location      │     │  Representation │     │    Agreement    │      │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

所有 18 个数据组都遵循这些通用模式进行扩展：
- Performer → System/Service/Organization/PersonRole
- Activity → IndividualActivity / JointAction
- Capability → CapabilityType / Capability / IndividualCapability
- Resource → IndividualResource / Information / Data
- Project → ProjectType / Project
- ...
```

---

## 六、DM2 完整价值链

综合 16 张类图，DM2 的完整价值链如下：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Vision（愿景）                                                              │
│    ↓ desiredEffectRealizedByProjectType                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ProjectType ──具体化──→ Project（项目）                                      │
│    ↓ activityPartOfProjectType                                               │
│  Activity（活动类型）──具体化──→ IndividualActivity（活动实例）                 │
│    ↓ activityPartOfCapability                                                │
│  CapabilityType ──具体化──→ Capability（能力）                                │
│    ↓ capabilityOfPerformer                                                    │
│  Performer（System/Service/Organization/PersonRole）                         │
│    ↓ activityPerformedByPerformer                                             │
│  Activity（执行）                                                             │
│    ↓ consumes / produces                                                     │
│  Resource / Information（资源/信息）                                          │
│    ↓ resourceInLocationType / measureOfType / ruleConstrains                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  支撑机制：                                                                   │
│  ├── Location（位置）                                                          │
│  ├── Measure（度量）                                                          │
│  ├── Rule / Standard / Agreement（规则/标准/协议）                             │
│  ├── Temporal（时间）                                                          │
│  ├── Naming / Description（命名/描述）                                        │
│  └── Pedigree（谱系追踪）                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 六、Obsidian 知识库设计指南

### 6.1 目录结构设计

基于 DM2 元模型，按实体类型组织目录：

```
E:\obsidianDB\EA\
├── 01-Performer/                 # 执行者
│   ├── Systems/                  # System（直接 Individual）
│   ├── Services/                 # Service（直接 Individual）
│   ├── Organizations/            # Organization（Individual）
│   ├── OrganizationTypes/        # OrganizationType（Type）
│   ├── PersonRoles/              # IndividualPersonRole（Individual）
│   └── PersonRoleTypes/          # PersonRoleType（Type）
│
├── 02-Activity/                  # 活动
│   ├── Activities/               # IndividualActivity
│   └── ActivityTypes/            # Activity（Type）
│
├── 03-Capability/                # 能力
│   ├── Capabilities/             # Capability（Individual）
│   ├── CapabilityTypes/          # CapabilityType（Type）
│   └── IndividualCapabilities/   # IndividualCapability
│
├── 04-Resource/                  # 资源
│   ├── Resources/                # IndividualResource
│   ├── Information/              # Information
│   ├── Data/                     # Data
│   └── DataTypes/                # DataType
│
├── 05-Service/                   # 服务
│   └── Services/                 # Service
│
├── 06-Agreement/                 # 协议
│   └── Agreements/               # Agreement
│
├── 07-Guidance/                  # 规则与标准
│   ├── Rules/
│   ├── Standards/
│   │   ├── FunctionalStandards/
│   │   └── TechnicalStandards/
│   └── Regulations/
│
├── 08-Project/                   # 项目
│   ├── ProjectTypes/             # ProjectType（Type）
│   └── Projects/                 # Project（Individual）
│
├── 09-Measure/                   # 度量
│   └── Measures/
│
├── 10-Location/                  # 位置
│   ├── Locations/                # Location（Individual）
│   └── LocationTypes/            # LocationType（Type）
│
├── 11-Views/                     # 视图层（obsidian-bases）
│   ├── SV-1-系统清单.base
│   ├── CV-2-能力分类.base
│   ├── OV-5b-活动模型.base
│   ├── StdV-1-合规覆盖.base
│   └── DIV-1-数据模型.base
│
├── CLAUDE.md                     # 告诉 Claw 如何操作这个 Vault
└── DM2-REFERENCE.md              # DM2 关系速查表
```

### 6.2 笔记模板设计

#### System 笔记模板
```yaml
---
# DM2 基本属性
type: system
name: 
performerType: System

# OverlapType 关系
performs: []                    # activityPerformedByPerformer（正向）
performedBy: []                 # activityPerformedByPerformer（反向）
realizes: []                    # performerRealizesCapability（正向）
realizedBy: []                  # performerRealizesCapability（反向）

# BeforeAfterType 关系
consumes: []                    # activityConsumesResource（正向）
consumedBy: []                  # activityConsumesResource（反向）
produces: []                    # activityProducesResource（正向）
producedBy: []                  # activityProducesResource（反向）

# WholePartType 关系
partOf: []                      # 所属组织/父系统
composedOf: []                  # 组成子系统

# 约束关系
constrainedBy: []               # performerConstrainedByRule

# 属性
owner: 
vendor: 
status: active | planned | deprecated
location: []

# Obsidian 元数据
tags: [performer, system]
created: 
modified: 
---

# 

## 描述


## 执行的活动
- [[]]

## 实现的能力
- [[]]

## 资源流向
- 消费：[[]]
- 产出：[[]]

## 约束的标准
- [[]]
```

#### Activity 笔记模板
```yaml
---
# DM2 基本属性
type: activity
name: 
performerType: Activity

# OverlapType 关系
performedBy: []                 # activityPerformedByPerformer
performer: []                  # activityPerformedByPerformer（反向）

# WholePartType 关系
partOf: []                      # activityPartOfCapability
partOfProject: []               # activityPartOfProjectType
composedOf: []                   # 子活动

# BeforeAfterType 关系
consumes: []                    # activityConsumesResource
produces: []                    # activityProducesResource

# 约束关系
constrainedBy: []               # ruleConstrainsActivity
condition: []                   # activityPerformableUnderCondition

# 度量
measuredBy: []

# Obsidian 元数据
tags: [activity]
created: 
modified: 
---

# 

## 描述


## 执行者
- [[]]

## 组成的能力
- [[]]

## 资源流向
- 输入：[[]]
- 输出：[[]]
```

#### Capability 笔记模板
```yaml
---
# DM2 基本属性
type: capability
name: 
capabilityType:                  # 链接到 CapabilityType

# WholePartType 关系
composedOf: []                   # activityPartOfCapability（反向）
activityMapping: []              # activityMapsToCapabilityType

# OverlapType 关系
performer: []                    # capabilityOfPerformer（正向）
realizedBy: []                   # capabilityOfPerformer（反向）

# 期望效果
desiredEffect: []                # desiredEffectOfCapability

# 度量
measuredBy: []                  # desireMeasure

# Obsidian 元数据
tags: [capability]
created: 
modified: 
---

# 

## 描述


## 组成活动
- [[]]

## 实现者
- [[]]

## 期望效果
- [[]]

## 性能指标
- [[]]
```

#### Resource 笔记模板
```yaml
---
# DM2 基本属性
type: resource
name: 
resourceType:                    # Resource / Information / Data

# Representation 关系
represents: []                   # representedBy（正向）
representedBy: []                # representedBy（反向）
describedBy: []                   # describedBy

# BeforeAfterType 关系
consumedBy: []                   # activityConsumesResource（反向）
producedBy: []                   # activityProducesResource（反向）

# Location 关系
location: []                     # resourceInLocationType

# 度量
measuredBy: []

# 信息谱系
pedigree:
  source: []
  producedBy: []
  processingChain: []
  quality: 
  freshness: 

# Obsidian 元数据
tags: [resource, information]
created: 
modified: 
---

# 

## 描述


## 表示形式
- [[]]

## 生产者
- [[]]

## 消费者
- [[]]
```

### 6.3 双向链接规范

基于四种关系类型，规范双向链接写法：

| DM2 关系类型 | 正向链接写法 | 反向链接写法 |
|:---|:---|:---|
| **WholePartType** | `partOf: [[父实体]]` | `composedOf: [[子实体]]` |
| **OverlapType** | `performs: [[活动]]` | `performedBy: [[执行者]]` |
| **BeforeAfterType** | `consumes: [[资源]]` | `consumedBy: [[活动]]` |
| **CoupleType** | `jointWith: [[联合实体]]` | — |

---

## 七、DM2 数据组完整清单

基于 MCP 工具查询，DM2 共有 18 个数据组：

| 数据组 | 实体数量 | 主要实体 | Obsidian 目录 |
|:---|:---:|:---|:---|
| Performer | 52 | System, Service, Organization, PersonRole | 01-Performer/ |
| Activity | 42 | Activity, IndividualActivity | 02-Activity/ |
| Capability | 38 | CapabilityType, Capability, IndividualCapability | 03-Capability/ |
| Resource | 35 | Resource, IndividualResource, Materiel | 04-Resource/ |
| Service | 28 | Service, ServicePort | 05-Service/ |
| Agreement | 22 | Agreement, Contract, MOU | 06-Agreement/ |
| Guidance | 45 | Rule, Standard, Regulation | 07-Guidance/ |
| Project | 32 | ProjectType, Project | 08-Project/ |
| Measure | 40 | MeasureType, Measure | 09-Measure/ |
| Location | 30 | LocationType, Location | 10-Location/ |
| Information | 25 | InformationType, Information, DataType | 04-Resource/ |
| Condition | 18 | Condition | — |
| Skill | 20 | Skill, MeasurableSkill | — |
| Rule | 见 Guidance | 见 Guidance | 07-Guidance/ |
| Standard | 见 Guidance | 见 Guidance | 07-Guidance/ |
| Vision | 12 | Vision, DesiredEffect | — |
| Port | 15 | Port, ServicePort | 01-Performer/ |
| Association | 8 | WholePart, Overlap, Couple, BeforeAfter | — |

---

## 八、研究结论

### 8.1 核心发现

1. **DM2 的核心是关系网络**：不是数据项分类，而是数据项之间的关系。Type/Individual 分层只是基础，四种关系类型才是骨架。

2. **价值链的完整路径**：Vision → Project → Activity → Capability → Performer → Resource → Measure/Location/Rule

3. **双向链接是知识库的引擎**：每条 DM2 关系都应该在两个端点的笔记里留下链接，形成可导航的关系网络。

4. **Measure 是跨数据组的通用属性**：几乎所有实体都可以用 Measure 来量化，形成 Performance/DevOps/Governance 的基础。

5. **Common Patterns 是元元模型的精华**：它定义了所有 18 个数据组都遵循的通用建模模式——Type/Individual 分层、Temporal 边界、Naming/Description、四元素建模（What/Who/When/Why），以及四种 Association 类型。

### 8.2 与之前设计的对比

| 之前的设计 | 改进后的设计 |
|:---|:---|
| 目录按"产品类型"分 | 目录按 DM2 实体类型分 |
| Frontmatter 当字段表 | Frontmatter 是 DM2 数据项的具体值 |
| 没有关系描述 | 每条 DM2 关系都有双向链接 |
| Dataview 做"筛选" | Dataview 做"关系查询" |
| 单向索引 | 双向索引（从任意实体出发都能导航）|

### 8.3 下一步工作

1. 在 Obsidian Vault 创建目录结构
2. 创建各实体类型的笔记模板（Templater 格式）
3. 创建 obsidian-bases 视图文件
4. 创建 CLAUDE.md 和 DM2-REFERENCE.md
5. 制定数据录入规范和流程

---

## 附录：类图清单

| 序号  | 类图名称                        | 核心内容                                                         |
| :-: | :-------------------------- | :----------------------------------------------------------- |
|  1  | Performer                   | System/Service 直接 Individual；Org/Person 有 Type/Individual 分层 |
|  2  | Capability                  | CapabilityType → Capability → IndividualCapability           |
|  3  | Information & Data          | Resource → Information → Type 三层                             |
|  4  | Resource Flow               | Activity 组合；Resource 流动                                      |
|  5  | Services                    | Service 启用 Resource 访问；ServicePort                           |
|  6  | Project                     | Project 实现 Vision；Activity 组成 Project                        |
|  7  | Reification Levels          | Type ↔ Individual 具体化机制                                      |
|  8  | Location                    | 丰富的地理层级                                                      |
|  9  | Measure                     | 跨数据组的通用度量                                                    |
| 10  | Naming & Description        | 名称/描述的元模型                                                    |
| 11  | Rules                       | Rule 约束 Activity；Agreement 约束 Performer                      |
| 12  | Temporal Parts              | 时间维度建模                                                       |
| 13  | Foundation For Associations | 四种关系类型                                                       |
| 14  | Information Pedigree        | 信息血缘追踪                                                       |
| 15  | Organizational Structure    | 组织层级                                                         |
| 16  | Pedigree（完整版）               | DM2 完整元模型整合图                                                 |
| 17  | Common Patterns             | 元元模型通用模式总结                                                   |

---

*报告生成时间：2026-04-13（增加 Common Patterns 章节）*
*研究者：Claw*
*数据来源：DM2_EA_v2.02.eap（Enterprise Architect 12）*
