# DoDAF 2.02 DM2 元模型完整定义

> **参考来源**：DoDAF Architecture Framework Version 2.02（2010年8月）
> **文档路径**：`E:\03-PublicWorkSpace\政\01-主线\01-标准\03-美国标准\02-USAarmy\12-DoDAF\dodaf_v2-02_web.pdf`
> **编制日期**：2026-04-16
> **版本**：v2.0（基于 DoDAF v2.02 官方规范）

---

## 一、DM2 概述

### 1.1 什么是 DM2

**DM2（DoDAF Meta-Model）** 是 DoDAF 2.0 的核心基础，从"产品（视图）驱动"转向**"数据驱动"**。

### 1.2 DM2 的三大目的

1. **统一词汇**：为 DoD 架构工作提供标准术语表
2. **数据互操作**：使不同架构工具生产的数据能够被比较、集成和分析
3. **语义基础**：为所有 DoDAF 视图提供共同的语义层

> **核心原则**：**数据是架构资产的核心，视图只是数据的可视化表达。**

### 1.3 DM2 三层模型结构

| 层级 | 对应视图 | 抽象层次 | 用途 |
|------|---------|---------|------|
| **CDM**（概念数据模型） | DIV-1 | 最高，与技术无关 | 核心业务概念，与利益相关者沟通 |
| **LDM**（逻辑数据模型） | DIV-2 | 中等，结构精确 | 驱动系统设计，支持数据库设计 |
| **PDM**（物理数据模型） | DIV-3 | 最低，与实现相关 | 数据格式、接口标准（XML/JSON Schema） |

---

## 二、DM2 核心概念（CDM 层）

DoDAF v2.02 官方定义的 12 个核心概念：

### 2.1 Activity（活动）

> **定义**：Work, not specific to a single organization, weapon system or individual that transforms inputs (Resources) into outputs (Resources) or changes their state.

**关键特性**：
- **与 Performer 分离定义**（DoDAF V2.0 重要变化）
- Activity 描述"做什么"，Performer 描述"谁来做"
- 同一 Activity 可由多种类型的 Performer 执行

### 2.2 Resource（资源）

> **定义**：Data, Information, Performers, Materiel, or Personnel Types that are produced or consumed.

**包含类型**：
- **Information**：信息的语义层面
- **Data**：信息的物理表示
- **Materiel**：设备、器材或补给品
- **Personnel**：人力资源
- **Performers**：执行者本身

### 2.3 Performer（执行者）

> **定义**：Any entity - human, automated, or any aggregation of human and/or automated - that performs an activity and provides a capability.

**类型**：
- **Person Type**：人员角色类型（如军事职业专业代码 MOS）
- **Organization**：组织（如 FBI，有特定使命）
- **System**：系统（如武器系统、IT 系统）
- **Service**：服务（从软件服务到业务服务）

### 2.4 Capability（能力）

> **定义**：The ability to achieve a Desired Effect under specified [performance] standards and conditions through combinations of ways and means [activities and resources] to perform a set of activities.

### 2.5 Condition（条件）

> **定义**：The state of an environment or situation in which a Performer performs.

### 2.6 Desired Effect（预期效果）

> **定义**：A desired state of a Resource.

### 2.7 Measure / Measure Type（度量）

> **定义**：The magnitude of some attribute of an individual / A category of Measures.

### 2.8 Location（位置）

> **定义**：A point or extent in space that may be referred to physically or logically.

### 2.9 Guidance / Rule / Agreement / Standard（规则/指南）

| 概念 | 定义 |
|------|------|
| **Guidance** | An authoritative statement intended to lead or steer the execution of actions. |
| **Rule** | A principle or condition that governs behavior; a prescribed guide for conduct or action. |
| **Agreement** | A consent among parties regarding the terms and conditions of activities that said parties participate in. |
| **Standard** | A formal agreement documenting generally accepted specifications or criteria for products, processes, procedures, policies, systems, and/or personnel. |

### 2.10 Project（项目）

> **定义**：A temporary endeavor undertaken to create Resources or Desired Effects.

### 2.11 Vision（愿景）

> **定义**：An end that describes the future state of the enterprise, without regard to how it is to be achieved; a mental image of what the future will or could be like.

### 2.12 Skill（技能）

> **定义**：The ability, coming from one's knowledge, practice, aptitude, etc., to do something well.

---

## 三、DM2 数据组（LDM 层）

### 3.1 分类概览

根据 DoDAF v2.02，DM2 LDM 将概念分为两组：

#### Principal Architectural Constructs（核心架构构造）

| 序号  | 数据组                  | 核心概念            |
| --- | -------------------- | --------------- |
| 1   | Performers           | 执行者（人/组织/系统/服务） |
| 2   | Resource Flows       | 资源流（活动间的交互）     |
| 3   | Information and Data | 信息与数据           |
| 4   | Rules                | 规则/标准/协议/约束     |
| 5   | Goals                | 目标/愿景/效果        |
| 6   | Capability           | 能力              |
| 7   | Services             | 服务              |
| 8   | Project              | 项目              |

#### Supporting Architectural Constructs（支撑架构构造）

| 序号  | 数据组                      | 核心概念        |
| --- | ------------------------ | ----------- |
| 9   | Reification              | 物化（类型/个体分层） |
| 10  | Organizational Structure | 组织结构        |
| 11  | Measures                 | 度量          |
| 12  | Locations                | 位置          |
| 13  | Pedigree                 | 谱系          |

---

## 四、IDEAS 顶层本体

DM2 基于 IDEAS（Integrated DEFENSE Architecture System）基础本体构建。

### 4.1 顶层元素

```
Thing（万物）
├── Individual（实例）
│   └── 具有时空扩展的具体实体
├── Type（类型）
│   ├── IndividualType（个体类型）
│   └── Powertype（幂类型，类型的类型）
└── Tuple（元组/关系）
```

### 4.2 IDEA 颜色编码

| 立体类型 | 颜色 | RGB |
|----------|------|-----|
| <<Individual>> | Grey(80%) | R40 G40 B40 |
| <<Type>> | Pale Blue | R153 G204 B255 |
| <<IndividualType>> | Light Orange | R255 G173 B91 |
| <<TupleType>> | Light Green | R204 G255 B204 |
| <<Powertype>> | Lavender | R204 G153 B255 |
| <<Name>> | Tan | R255 G254 B153 |
| <<NamingScheme>> | Yellow | R255 G255 B0 |

---

## 五、四种关系模式

DM2 复用的四种通用模式：

### 5.1 Whole-Part（组成/整体-部分）

```yaml
关系: <<wholePart>>
说明: 表示整体与部分的关系
示例: materielPartOfPerformer（物资作为执行者的一部分）
```

### 5.2 Super-Subtype（泛化/特殊化）

```yaml
关系: <<super-subtype>>
说明: 表示类型之间的继承关系
示例: System → WeaponSystem → Tank
```

### 5.3 Before-After（时序/前后）

```yaml
关系: 时序相关
说明: 表示事物之间的时间关系
示例: activityPrecedesActivity（活动先于活动）
```

### 5.4 Overlap（重叠）

```yaml
关系: 重叠
说明: 表示事物之间的重叠/交叉关系
示例: activityOverlapsActivity（活动重叠）、资源流中的三重叠
```

### 5.5 Couple/Tuple（配对/元组）

```yaml
关系: <<tuple>>/<<couple>>
说明: 表示事物之间的关系
示例: activityPerformedByPerformer（活动与执行者的配对）
```

---

## 六、关键关系模式

### 6.1 能力-活动-执行者三角

```
                    Vision（愿景）
                          ↑
                          │ (支撑)
                    Goal（目标）
                          ↑
                    Capability（能力）
                          ↑
                    (activityMapsToCapabilityType)
                          │
    Resource ───────→ Activity ←────── Performer
   (消耗/产生)     (执行)      (activityPerformedByPerformer)
```

### 6.2 资源流三重叠

```
资源流由三个重叠组成：
┌────────────────────────────────┐
│                                │
↓                                │
Activity(生产者) ──Resource──→ Activity(消费者)
│                                │
└─────────── 时空重叠 ───────────┘
```

### 6.3 目标链

```
Vision → Goal → Objective → DesiredEffect → Capability → Activity → Performer
```

---

## 七、数据组详细定义

### 7.1 Performers（执行者）

**核心定义**：Who in the Architectural Development Process

**包含类型**：
- Person Type（人员角色类型）
- Organization（组织）
- System（系统）
- Service（服务）

**核心关系**：
| 关系 | 说明 |
|------|------|
| activityPerformedByPerformer | 执行者执行活动 |
| materielPartOfPerformer | 物资作为执行者的一部分 |
| performerLocatedAtLocation | 执行者位于位置 |

**主要视图**：OV-4, SV-1

### 7.2 Resource Flows（资源流）

**核心定义**：活动间资源的流动或交换

**关键特性**：
- 资源流基于活动，不是基于执行者
- 三重叠：生产者活动、资源、消费者活动

**包含类型**：
- Information Flow（信息流）
- Materiel Flow（物资流）
- Personnel Flow（人员流）
- Performers Flow（执行者流）

**主要视图**：OV-3, SV-6

### 7.3 Information and Data（信息与数据）

**核心定义**：
- **Information**：信息的语义层面（State of something-of-interest）
- **Data**：信息的物理表示（Formalized representation）

**关系**：
- Information 是 Resource 的一种
- Data 描述 Information

**主要视图**：DIV-1, DIV-2, DIV-3

### 7.4 Rules（规则）

**包含类型**：
- **Rule**：强制性规则
- **Guidance**：指导性指南
- **Agreement**：协议
- **Standard**：标准
- **Policy**：策略
- **Constraint**：约束

**核心关系**：
| 关系 | 说明 |
|------|------|
| ruleConstrainsActivity | 规则约束活动 |
| guidanceGuidesActivity | 指南指导活动 |
| standardConstrainsSystem | 标准约束系统 |

**主要视图**：OV-6a, SV-10a, StdV-1

### 7.5 Goals（目标）

**包含类型**：
- Vision（愿景）
- Goal（目标）
- Objective（具体目标）
- Desired Effect（预期效果）
- End State（终态）

**核心关系**：
| 关系 | 说明 |
|------|------|
| goalAchievedByCapability | 目标由能力实现 |
| desiredEffectProducedByActivity | 效果由活动产生 |

**主要视图**：CV-1, PV-1

### 7.6 Capability（能力）

**核心定义**：The ability to achieve a Desired Effect under specified standards and conditions through combinations of ways and means to perform a set of activities.

**核心关系**：
| 关系 | 说明 |
|------|------|
| capabilityRealizedByActivity | 能力由活动实现 |
| capabilityDeliveredByPerformer | 能力由执行者交付 |
| capabilityDependsOnCapability | 能力依赖能力 |

**主要视图**：CV-1, CV-2, CV-3, CV-6

### 7.7 Services（服务）

**核心定义**：A mechanism to enable access to a set of one or more capabilities, where the access is provided using a prescribed interface.

**关键概念**：
- Service 作为 Performer 的一种
- ServicePort（服务端口）
- ServiceDescription（服务描述）
- ServiceContract（服务契约）

**主要视图**：SvcV-1 ~ SvcV-10c

### 7.8 Project（项目）

**核心定义**：A temporary endeavor undertaken to create Resources or Desired Effects.

**包含类型**：
- Project（项目）
- Program（项目群）
- Portfolio（项目组合）
- Milestone（里程碑）
- Deliverable（交付物）

**核心关系**：
| 关系 | 说明 |
|------|------|
| projectDeliversCapability | 项目交付能力 |
| projectComposedOfActivity | 项目由活动组成 |
| projectPerformedByPerformer | 项目由执行者执行 |

**主要视图**：PV-1, PV-2, PV-3

### 7.9 Reification（物化）

**核心定义**：The process of reifying or to regard (something abstract) as a material or concrete thing.

**核心概念**：
| 概念 | 说明 |
|------|------|
| **Type** | 通用规格、设计定义 |
| **Individual** | 具体实例、部署节点 |
| **Powertype** | 类型的类型 |

**关系**：
| 关系 | 说明 |
|------|------|
| <<typeInstance>> | 类型与实例的关系 |
| <<powertypeInstance>> | 类型与幂类型的关系 |

### 7.10 Organizational Structure（组织结构）

**包含类型**：
- Organization Type
- Organization（Individual）
- Post（岗位）
- PersonRoleType（人员角色类型）

**核心关系**：
| 关系 | 说明 |
|------|------|
| postPartOfOrganization | 岗位属于组织 |
| postReportsToPost | 岗位汇报至岗位 |
| personRoleTypePartOfPost | 人员角色属于岗位 |

### 7.11 Measures（度量）

**核心定义**：The magnitude of some attribute of an individual.

**包含类型**：
- Measure Of Effect (MOE)
- Measure Of Performance (MOP)
- Measure Of Suitability
- Measure Of Worth

**核心关系**：Measure 可关联到几乎所有 DM2 实体

**主要视图**：SV-7

### 7.12 Locations（位置）

**核心定义**：A point or extent in space that may be referred to physically or logically.

**包含类型**：
- Facility（设施）
- Installation（安装设施）
- Region（区域）
- Point（点）
- Line（线）
- Volume（体积）
- Address（地址）
- GeoPoliticalExtent（地缘政治范围）

**核心关系**：
| 关系 | 说明 |
|------|------|
| performerLocatedAtLocation | 执行者位于位置 |
| activityPerformedAtLocation | 活动在位置执行 |

**主要视图**：OV-2, SV-1

### 7.13 Pedigree（谱系）

**核心定义**：The origin and the history of something; broadly: background, history.

**包含类型**：
- Provenance（出处）
- Author（作者）
- CreationDate（创建日期）
- ModificationDate（修改日期）
- Version（版本）
- ConfidenceLevel（可信度等级）
- VerificationStatus（验证状态）
- ApprovalStatus（审批状态）

---

## 八、视图映射速查

| 数据组 | 主要视图 | 次要视图 |
|--------|---------|---------|
| Performers | OV-4, SV-1 | OV-2, SvcV-1 |
| Resource Flows | OV-3, SV-6 | OV-2, DIV-1/2/3 |
| Information and Data | DIV-1/2/3 | OV-3 |
| Rules | OV-6a, SV-10a | StdV-1, AV-1 |
| Goals | CV-1, PV-1 | 跨视图 |
| Capability | CV-1~7 | PV-3, SV-5 |
| Services | SvcV-1~10c | SV-1 |
| Project | PV-1/2/3 | CV-3 |
| Reification | 跨视图 | SV-7, SV-1 |
| Organizational Structure | OV-4 | SV-1 |
| Measures | SV-7 | CV-1, OV-6a |
| Locations | OV-2, SV-1 | OV-1, OV-4 |
| Pedigree | AV-1 | 跨视图 |

---

## 九、DoDAF 2.02 与早期版本的关键变化

1. **Activity 与 Performer 分离**：Activity 描述"做什么"，Performer 描述"谁来做"
2. **Resource 泛化**：不仅包含信息和数据，还包括物资、人员、执行者
3. **Service 作为 Performer**：服务被视为一种特殊的执行者
4. **资源流基于活动**：资源流由活动产生和消耗，而不是由执行者
5. **数据驱动**：视图只是数据的可视化表达

---

## 十、版本信息

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-04-16 | 初稿完成 |
| v2.0 | 2026-04-16 | 校准：基于 DoDAF v2.02 官方 PDF 原文重构 |

---

*本文档基于 DoDAF Architecture Framework Version 2.02（2010年8月）官方规范编制*
