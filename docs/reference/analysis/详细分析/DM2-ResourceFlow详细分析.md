---
tags:
  - dm2/analysis
---

> **操作模板** -> [[../11-ResourceFlow/README.md]]
> **所属数据组** -> [[../11-ResourceFlow]]

# DoDAF/DM2 Resource Flow 资源流详细分析

> 基于 resourceFlow.png 类图及 DoDAF v2.02 官方规范
> 分析日期：2026-04-17
> 版本：v1.0

---

## 一、Resource Flow 概述

### 1.1 核心定位

Resource Flow（资源流）是 DM2 元模型中描述 **"资源如何在活动之间流动"** 的核心机制。它连接了 Activity（活动）与 Resource（资源），揭示了企业架构中资源和活动的动态关系。

### 1.2 在元模型中的位置

```
┌──────────────────────────────────────────────────────────────┐
│                    DM2 元模型核心结构                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│   │  Performer  │◄──►│  Activity   │◄──►│   Rule     │      │
│   │  执行者     │    │   活动      │    │   规则      │      │
│   └─────────────┘    └──────┬──────┘    └─────────────┘      │
│                             │                                  │
│         ┌───────────────────┼───────────────────┐            │
│         │  consumes/produces │  consumes/produces │            │
│         ▼                   ▼                   ▼            │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│   │  Resource   │◄───┤    ↓        │───►│ Capability  │      │
│   │   资源      │    │ resourceFlow │    │    能力     │      │
│   └─────────────┘    │   资源流    │    └─────────────┘      │
│                       └─────────────┘                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 Resource Flow 的本质

> **核心原则**：资源流基于 **活动**，而非基于执行者。

- 资源由一个活动产生（Producing Activity）
- 资源被另一个活动消费（Consuming Activity）
- 两个活动之间存在时空重叠（Overlap）

---

## 二、资源类型体系

### 2.1 五种资源类型

| 资源类型 | 说明 | 示例 | 物理表示 |
|---------|------|------|---------|
| **Information** | 信息（语义层面） | 情报、指令、报告 | 电子文档、数据库记录 |
| **Data** | 数据（物理表示） | 原始数据、文件 | 比特流、存储介质 |
| **Materiel** | 物资（设备器材） | 武器、车辆、备件 | 实体物品 |
| **Personnel** | 人员 | 人员配置、技能 | 人员本身 |
| **Performers** | 执行者（作为资源） | 人员/组织/系统 | 实体或虚拟实体 |

### 2.2 资源类型层次结构

```
<<Type>>
   ResourceType
        │
        ├── InformationType
        │      │
        │      └── IndividualInformation
        │             │
        │             ├── StrategicInfo（战略信息）
        │             ├── TacticalInfo（战术信息）
        │             └── OperationalInfo（作战信息）
        │
        ├── DataType
        │      │
        │      └── IndividualData
        │
        ├── MaterielType
        │      │
        │      └── IndividualMateriel
        │             │
        │             ├── Weapon（武器）
        │             ├── Vehicle（车辆）
        │             ├── Equipment（设备）
        │             └── Supply（补给品）
        │
        ├── PersonnelType
        │      │
        │      └── IndividualPersonnel
        │
        └── PerformerType
               │
               ├── OrganizationType
               ├── SystemType
               └── ServiceType
```

---

## 三、Resource Flow 核心关系

### 3.1 关系一览

| 关系名称 | 关系类型 | 说明 | 方向 |
|---------|---------|------|------|
| `activityProducesResource` | Couple | 活动产生资源 | Activity → Resource |
| `activityConsumesResource` | Couple | 活动消耗资源 | Activity → Resource |
| `resourceFlow` | Tuple | 资源在执行者间流动 | Performer ↔ Performer |
| `resourcePartOfResource` | WholePart | 资源组成资源 | Resource → Resource |
| `resourceFlowSecurity` | Tuple | 资源流安全属性 | 资源流属性 |

### 3.2 活动-资源关系详解

```
┌─────────────────────────────────────────────────────────────┐
│                     活动资源关系                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐                        ┌──────────────┐   │
│  │   Producer    │                        │   Consumer   │   │
│  │   Activity     │                        │   Activity   │   │
│  │  （生产活动）   │                        │  （消费活动）  │   │
│  └───────┬───────┘                        └───────┬───────┘   │
│          │  produces                              │ consumes  │
│          ▼                                          ▼           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      Resource                          │   │
│  │                       资源                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                    │
│                          │ overlaps                           │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Temporal/ Spatial Overlap                    │   │
│  │              时间/空间 重叠                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、Resource Flow 三重叠机制

### 4.1 三重叠概念

Resource Flow 的核心是 **三重叠（Triple Overlap）**：

```
┌──────────────────────────────────────────────────────────────┐
│                   Resource Flow 三重叠                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐                                   ┌─────────┐│
│   │  Producer   │ ═══════════ Resource ════════════ │ Consumer││
│   │  Activity   │          （资源）                  │ Activity││
│   └──────┬──────┘                                   └────┬────┘│
│          │                                               │     │
│          │◄─────────── Temporal Overlap ───────────────►│     │
│          │              （时间重叠）                       │     │
│          │                                               │     │
│          │◄─────────── Spatial Overlap ────────────────►│     │
│          │              （空间重叠）                       │     │
│          │                                               │     │
│          └───────────── Resource Overlap ───────────────┘     │
│                         （资源重叠）                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 三重叠条件

| 重叠类型 | 说明 | 必须满足 |
|---------|------|---------|
| **Temporal Overlap** | 活动时间重叠 | 生产活动的产出时间 ≥ 消费活动的消费时间 |
| **Spatial Overlap** | 活动空间重叠 | 两个活动在地理位置上有交集 |
| **Resource Overlap** | 资源类型匹配 | 生产者产出的资源类型 = 消费者需求的资源类型 |

### 4.3 三重叠验证逻辑

```
资源流有效 当且仅当:
┌─────────────────────────────────────────────────────┐
│  T_produce_start ≤ T_consume_end                    │
│  AND                                            │
│  T_produce_end ≥ T_consume_start                  │
│  AND                                            │
│  Location_producer ∩ Location_consumer ≠ ∅       │
│  AND                                            │
│  ResourceType_match(producer, consumer)          │
└─────────────────────────────────────────────────────┘
```

---

## 五、资源流生命周期

### 5.1 资源状态转换

```
┌─────────┐    produces    ┌──────────┐   consumes   ┌─────────┐
│  潜在   │ ──────────────►│   存在   │ ────────────►│  消耗   │
│ Potential│                │ Existing │              │Consumed │
└─────────┘                 └─────┬────┘              └─────────┘
                                  │
                                  │ transforms
                                  ▼
                            ┌──────────┐
                            │  转换/存储 │
                            │Transform  │
                            └──────────┘
```

### 5.2 资源时序关系

| 关系 | 说明 | 示例 |
|------|------|------|
| `resourceProducedBeforeConsumed` | 先生产后消费 | 典型供应链 |
| `resourceProducedWhenConsumed` | 生产即消费 | 实时服务 |
| `resourceConsumedBeforeProduction` | 消费先于生产 | 订单驱动生产 |

---

## 六、Resource 与其他数据组的关系

### 6.1 资源-活动关系

| 关系 | 源 | 目标 | 说明 |
|------|---|------|------|
| `activityProducesResource` | Activity | Resource | 活动产出资源 |
| `activityConsumesResource` | Activity | Resource | 活动消耗资源 |
| `activityRequiresResource` | Activity | Resource | 活动需要资源（可选） |

### 6.2 资源-执行者关系

| 关系 | 源 | 目标 | 说明 |
|------|---|------|------|
| `resourceHeldByPerformer` | Resource | Performer | 资源由执行者持有 |
| `resourceOwnedByPerformer` | Resource | Performer | 资源由执行者拥有 |
| `performerTransfersResource` | Performer | Performer | 执行者之间转移资源 |

### 6.3 资源-位置关系

| 关系 | 源 | 目标 | 说明 |
|------|---|------|------|
| `resourceLocatedAtLocation` | Resource | Location | 资源位于某位置 |
| `resourceStoredAtLocation` | Resource | Location | 资源存储在某位置 |

### 6.4 资源-度量关系

| 关系 | 源 | 目标 | 说明 |
|------|---|------|------|
| `measureOfResource` | Measure | Resource | 资源的度量 |
| `resourceQuantity` | Resource | Measure | 资源数量 |
| `resourceQuality` | Resource | Measure | 资源质量 |

---

## 七、资源组成关系

### 7.1 Whole-Part 层次结构

```
┌─────────────────────────────────────────────────────────────┐
│                   资源组成关系（Whole-Part）                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────────────────────────────────────────┐       │
│   │              <<whole>>                           │       │
│   │           复合资源 (Composite Resource)          │       │
│   └────────────────────┬─────────────────────────────┘       │
│                        │ partOf                              │
│          ┌─────────────┼─────────────┐                       │
│          ▼             ▼             ▼                       │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐             │
│   │  <<part>>  │ │  <<part>>  │ │  <<part>>  │             │
│   │ 子资源 A   │ │ 子资源 B   │ │ 子资源 C   │             │
│   └────────────┘ └────────────┘ └────────────┘             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 示例：武器系统资源组成

```
Composite Materiel
│
├── Weapon System
│   ├── Platform（平台）
│   │    ├── Hull（船体）
│   │    ├── Turret（炮塔）
│   │    └── Propulsion（推进系统）
│   │
│   ├── Weapon（武器）
│   │    ├── Cannon（火炮）
│   │    └── Missile（导弹）
│   │
│   └── Support System（支援系统）
│        ├── Radar（雷达）
│        ├── Communication（通信）
│        └── Power Supply（电源）
```

---

## 八、资源流安全属性

### 8.1 resourceFlowSecurity 关系

Resource Flow 附带安全属性，用于描述资源在流转过程中的安全特性：

| 安全属性 | 说明 | 适用场景 |
|---------|------|---------|
| **Classification** | 密级分类 | 机密、秘密、机密 |
| **Caveats** | 限制说明 | 需要知道、同国籍等 |
| **Dissemination** | 发布控制 | 内部、公开、受限 |
| **Integrity** | 完整性 | 防篡改、防丢失 |
| **Availability** | 可用性 | 容错、冗余 |

### 8.2 安全流控模型

```
┌─────────────────────────────────────────────────────────────┐
│               资源流安全属性模型                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Producer                    Resource                   Consumer │
│   ┌────────┐                ┌─────────┐               ┌────────┐│
│   │ L1     │──produces──►│ [SEC]  │──consumes──►│ L2     ││
│   │ (低密) │                │ 资源    │               │ (高密) ││
│   └────────┘                └────┬────┘               └────────┘│
│                                   │                            │
│                          ┌────────▼────────┐                  │
│                          │  Need-to-Know   │                  │
│                          │    (知其所需)    │                  │
│                          └─────────────────┘                  │
│                                                              │
│   ⚠️ 注意：资源不能从低密级流向高密级，除非有特赦程序            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 九、Resource Flow 建模实践

### 9.1 OV-2 资源流视图要素

在 DoDAF OV-2（作战流线描述）中，Resource Flow 需要描述：

| 要素 | 说明 | 必选/可选 |
|------|------|----------|
| 资源标识 | 资源的唯一标识符 | 必选 |
| 资源类型 | Information/Data/Materiel等 | 必选 |
| 源活动 | 产出资源的活动 | 必选 |
| 目标活动 | 消费资源的活动 | 必选 |
| 流量规格 | 数量、频率、速率 | 必选 |
| 时序约束 | 时间窗口、同步要求 | 可选 |
| 位置约束 | 传输路径、存储位置 | 可选 |
| 安全属性 | 密级、访问控制 | 可选 |

### 9.2 资源流建模步骤

```
步骤 1：识别活动
   └─► 列出所有相关活动（Activity）

步骤 2：识别资源
   └─► 确定每个活动消耗和产生的资源

步骤 3：建立关系
   └─► 用 produces/consumes 连接活动与资源

步骤 4：验证三重叠
   └─► 确认时间、空间、类型三重合

步骤 5：添加约束
   └─► 补充时序、位置、安全等约束

步骤 6：文档化
   └─► 生成 OV-2 资源流视图
```

---

## 十、典型应用场景

### 10.1 供应链场景

```
┌─────────────┐     supplies      ┌─────────────┐    consumes    ┌─────────────┐
│  Supplier   │ ────────────────►│  Logistics  │ ──────────────►│  Factory    │
│  供应商      │                   │   物流       │                 │   工厂       │
└─────────────┘                   └─────────────┘                 └─────────────┘
       │                                                                  ▲
       │ produces                                                         │ consumes
       ▼                                                                  │
┌─────────────┐                                                            │
│   Parts    │────────────────────────────────────────────────────────────┘
│   零部件    │                            produces
└─────────────┘
```

### 10.2 情报系统场景

```
┌─────────────┐    produces      ┌─────────────┐    consumes    ┌─────────────┐
│  Sensor     │ ────────────────►│  Processor  │ ──────────────►│  Analyst    │
│   传感器     │                   │   处理器     │                 │   分析师     │
└─────────────┘                   └─────────────┘                 └─────────────┘
       │                                                                  ▲
       │ produces                                                         │ consumes
       ▼                                                                  │
┌─────────────┐                                                            │
│   Raw Data  │──────────────────────────────────────────────────────────┘
│   原始数据   │
└─────────────┘
```

---

## 十一、与旧版 DoDAF 的差异

### 11.1 DoDAF 1.5 vs DoDAF 2.0

| 方面 | DoDAF 1.5 | DoDAF 2.0 (DM2) |
|------|----------|-----------------|
| **资源定义** | 信息交换为主 | 五种资源类型 |
| **流描述** | OV-2 作战流线 | 活动-资源-活动 |
| **重叠机制** | 无明确机制 | 三重叠验证 |
| **安全属性** | 附加在交换上 | 内嵌在资源流 |

### 11.2 关键改进

1. **从交换到流的转变**：从描述"信息交换"转向描述"资源流"
2. **活动中心化**：资源流围绕活动而非执行者
3. **可验证性**：三重叠机制提供了形式化验证基础
4. **扩展性**：支持多种资源类型和安全属性

---

## 十二、关键洞察总结

### 12.1 核心要点

| # | 要点 | 说明 |
|---|------|------|
| 1 | **活动中心** | 资源流基于活动，不是基于执行者 |
| 2 | **三重叠验证** | 时间、空间、类型三重合才构成有效资源流 |
| 3 | **五种资源** | Information、Data、Materiel、Personnel、Performers |
| 4 | **状态转换** | 潜在 → 存在 → 消耗 |
| 5 | **安全内嵌** | 安全属性是资源流的固有属性 |

### 12.2 建模检查清单

```
□ 识别所有相关活动
□ 确定每个活动的资源输入/输出
□ 验证时间重叠
□ 验证空间重叠
□ 验证资源类型匹配
□ 添加时序约束
□ 添加安全属性
□ 文档化资源流规格
```

---

## 附录：关系速查表

| 关系名称                             | 源实体          | 目标实体         | 关系类型        |
| -------------------------------- | ------------ | ------------ | ----------- |
| `activityProducesResource`       | Activity     | Resource     | Couple      |
| `activityConsumesResource`       | Activity     | Resource     | Couple      |
| `resourceFlow`                   | Performer    | Performer    | Tuple       |
| `resourcePartOfResource`         | Resource     | Resource     | WholePart   |
| `resourceFlowSecurity`           | ResourceFlow | SecurityAttr | Tuple       |
| `resourceHeldByPerformer`        | Resource     | Performer    | Couple      |
| `resourceLocatedAtLocation`      | Resource     | Location     | Couple      |
| `measureOfResource`              | Measure      | Resource     | Couple      |
| `resourceProducedBeforeConsumed` | Resource     | Resource     | BeforeAfter |

---

*本分析基于 DoDAF v2.02 官方规范和 DM2 元模型类图整理*
