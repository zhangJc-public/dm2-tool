---
tags:
  - dm2/analysis
---

> **操作模板** -> [[../01-Performer/Performer-Template.md]]
> **所属数据组** -> [[../01-Performer]]

# DoDAF/DM2 Performer 执行者详细分析

> 基于 performer.png 类图 + DoDAF v2.02 官方规范（PDF pp.42-45）
> 分析日期：2026-04-18
> 版本：v1.0

---

## 一、Performer 概述

### 1.1 核心定位

**Performer（执行者）** 是 DM2 元模型中最核心的概念之一。它是架构描述的 **"Who"** —— 回答"谁来做"的问题。

> **官方定义**（DoDAF v2.02）：
> *"Any entity - human, automated, or any aggregation of human and/or automated - that performs an activity and provides a capability."*
>
> **中文定义**：任何实体——人、自动化系统，或人与自动化系统的聚合体——执行活动并提供能力。

### 1.2 在元模型中的位置

```
┌──────────────────────────────────────────────────────────────┐
│                    DM2 元模型核心结构                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│   │  Performer  │◄──►│  Activity   │◄──►│    Rule     │      │
│   │  ★执行者★   │    │   活动      │    │   规则      │      │
│   └──────┬──────┘    └──────┬──────┘    └─────────────┘      │
│          │                  │                                │
│          │ performs        │ produces/consumes               │
│          ▼                  ▼                                │
│   ┌─────────────┐    ┌─────────────┐                         │
│   │ Capability  │    │  Resource   │                         │
│   │   能力      │    │   资源      │                         │
│   └─────────────┘    └─────────────┘                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 Performer 的本质特征

根据 PDF p.42 官方说明，Performer 可以代表：

| # | 类型 | 说明 | 示例 |
|---|------|------|------|
| **1** | **Person Type（人员类型）** | 由角色定义的人员类别，如 MOS 军事职业专业代码 | 士兵、飞行员、情报分析师 |
| **2** | **Organization（组织）** | 有使命授权的组织，非仅人员或地点集合 | FBI、国防部、作战部队 |
| **3** | **System（系统）** | 功能上/物理上/行为相关的组件集合 | 武器系统、IT系统、SoS |
| **4** | **Service（服务）** | 从软件服务到业务服务 | 搜索救援服务、认证服务 |

---

## 二、类图详细解析

### 2.1 类图完整结构

基于 `performer.png` 的类图解析：

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           DM2 Performer 元模型类图                             │
│                              （performer.png）                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ═══════════════════════ 顶层概念 ════════════════════════                    │
│                                                                              │
│  <<IndividualType>>              <<IndividualType>>                           │
│       Location                        Resource                                │
│  (LocationType)                   (ResourceType)                              │
│        │                                │                                     │
│        │ wholePart                      │ superSubtype                        │
│        ▼                                ▼                                     │
│  resourceInLocationType           Materiel                                    │
│                                  (IndividualResource)                        │
│                                        │                                     │
│                                        │ wholePart                           │
│                                        ▼                                     │
│                                   materielPartOfPerformer                     │
│                                        │                                     │
│                                        ▼                                     │
│                                                                              │
│  ═══════════════════════ 核心：Performer ═══════════════════════             │
│                                                                              │
│                       <<IndividualType>>                                     │
│                            Performer                                         │
│                       (PerformerType)                                       │
│                            │                                                 │
│         ┌────────────────┼────────────────┐                                │
│         │                │                │                                │
│    superSubtype     superSubtype    personRoleTypePartOfPerformer            │
│         │                │                │                                │
│         ▼                ▼                ▼                                │
│  <<Type>>         <<IndividualType>>  <<IndividualType>>                    │
│    System          IndividualResource  PersonRoleType                         │
│ (SystemType)     IndividualPerformer  (PersonRoleTypeType)                    │
│         │                 │                │                               │
│         │                 │                │ propertyOfType                 │
│         ▼                 ▼                ▼                               │
│  <<Type>>           <<IndividualType>>   Skill                              │
│    Service          IndividualPersonRole (MeasurableSkill)                   │
│ (ServiceType)                                                          [Property]│
│         │                                                                 │
│         │ powertypeInstance                                               │
│         ▼                                                                 │
│  <<IndividualType>>                                                      │
│  IndividualService                                                        │
│                                                                              │
│  ═══════════════════════ 组织层次 ═══════════════════════                   │
│                                                                              │
│                       OrganizationType                                      │
│                       <<IndividualType>>                                   │
│                            │                                                │
│                            │ powertypeInstance                              │
│                            ▼                                                │
│                       <<Individual>>                                       │
│                       Organization                                          │
│                                                                              │
│  ═══════════════════════ 活动关系 ═══════════════════════                   │
│                                                                              │
│  <<OverlapType>>                                                           │
│    activityPerformedByPerformer                                             │
│         │                                                                  │
│         ▲                                                                  │
│         │ place1Type                                                       │
│         │                                                                  │
│  <<IndividualType>>                                                       │
│       Activity                                                            │
│    (ActivityType)                                                         │
│         │                                                                  │
│         ├── superSubtype ──────────► ruleConstrainsActivity                │
│         │                                  │                              │
│         │                                  ▼                              │
│         │                          <<IndividualType>>                    │
│         │                              Guidance                         │
│         │                                  │ superSubtype                │
│         │                                  ▼                              │
│         │                          <<IndividualType>>                    │
│         │                              Rule                             │
│         │                                  │ superSubtype                │
│         │                                  ▼                              │
│         │                          <<IndividualType>>                    │
│         │                              Agreement                        │
│         │                                                                  │
│         │ place2Type ◄────────── activityPerformableUnderCondition         │
│         │                                  │ place1Type                   │
│         │                                  ▼                              │
│         │                          <<IndividualType>>                    │
│         │                              Condition                        │
│         │                          (ConditionType)                      │
│         │                                                                  │
│         │ place2Type ◄────────── measureOfTypeCondition                    │
│         │                                                                  │
│  <<Property/Measure>>                                                     │
│       Measure                                                             │
│   + numericValue: string                                                  │
│         │                                                                  │
│         │ measureOfType                                                    │
│         ├──────── measureOfResource ──────────► Resource                   │
│         │                                                                  │
│         └──────── measureOfActivity ──────────► Activity                   │
│                                                                              │
│  ═══════════════════════ 技能体系 ═══════════════════════                   │
│                                                                              │
│  <<Individual>>                                                             │
│    MeasureableSkill                                                         │
│         │                                                                  │
│         │ superSubtype                                                     │
│         ▼                                                                  │
│       Skill                                                               │
│    [Property]                                                              │
│         │                                                                  │
│         │ skillOfPersonRoleType                                            │
│         ▼                                                                  │
│    PersonRoleType                                                          │
│         │                                                                  │
│         │ measureableSkillOfPersonRoleType                                  │
│         ▼                                                                  │
│    Measure                                                                │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 类图中关键注释解读

图中包含两个重要的文本注释框：

#### 注释框 1：关于 System

```
"A functionally, physically, and/or behaviorally related group 
 of regularly interacting or interdependent elements."
```
> **翻译**：功能上、物理上和/或行为上相关的一组定期交互或相互依赖的元素。
> **来源**：DoDAF/CADM System 定义
> **含义**：System 是组件的有机组合，强调元素间的交互性和依赖性。

#### 注释框 2：关于 Person Type

```
"When a Person is part of another Person Type, that 
 Person refers to a role within a Person Type."
```
> **翻译**：当一个 Person 属于另一个 Person Type 时，
> 该 Person 指的是在某个 Person Type 内的角色。
> **含义**：PersonRole 支持嵌套角色关系——一个人可以在不同上下文中承担不同角色。

---

## 三、Performer 四种类型详解

### 3.1 PersonRoleType（人员角色类型）

> **官方定义**（DoDAF/CADM）：
> *"A category of person roles defined by the role or roles they share that are relevant to an architecture. Includes assigned materiel."*

**多来源定义**：

| 来源 | 定义 |
|------|------|
| DoDAF/CADM | 一类人员类别 |
| JC3IEDM | 表示需要保存信息的人类对象项 |
| JCS 1-02 | 在军事或文职能力下完成指派任务所需的人员 |
| Zachman | 一个人类个体 |
| Webster | 组织、企业或业务中雇佣或活跃的人员群体 |

**关键特性**：
- 描述角色的**类别**，而非具体个人
- 包含分配给该角色的**物资（Materiel）**
- 有**时间整体部分关系**——如驻扎状态 vs 部署状态
- 不同状态可能有不同的物资组成和规则关联

**示例**：

```
PersonRoleType 层次：
├── MilitaryPersonnel（军事人员）
│    ├── InfantrySoldier（步兵）
│    ├── Pilot（飞行员）
│    ├── IntelligenceAnalyst（情报分析师）
│    └── CyberOperator（网络操作员）
│
├── CivilianPersonnel（文职人员）
│    ├── SystemAdministrator（系统管理员）
│    ├── SecurityOfficer（安全官）
│    └── DataAnalyst（数据分析师）
│
└── Contractor（承包商）
     └── SecurityConsultant（安全顾问）
```

### 3.2 Organization（组织）

> **官方定义**（DoDAF/CADM）：
> *"A specific real-world assemblage of people and other resources organized for an on-going purpose."*
> **别名**：Department, Agency, Enterprise

**多来源定义**：

| 来源 | 定义 |
|------|------|
| DoDAF/CADM | 有使命的行政结构 |
| JC3IEDM | 行政或功能性结构的对象项 |
| NAF | 实际的具体组织实例，如 "美国国防部" |
| Zachman | 为特定目的聚集的一组人员 |
| Webster | 为某种目的组织的人群；有序的整体 |

**关键洞察**：
- 组织是**有使命的实体**，不是简单的人员集合
- 组织自己选择位置、人员等来完成使命
- 例如 FBI 有特许使命，它自主决定如何完成

### 3.3 System（系统）

> **官方定义**（DoDAF）：
> *"A functionally, physically, and/or behaviorally related group of regularly interacting or interdependent elements."*

**多来源定义**：

| 来源 | 定义 |
|------|------|
| DoDAF | 资源和程序的有组织的组合，通过交互或相互依赖统一和调节以完成一组特定功能 |
| DoDAF/CADM | 交互式组件和程序的有组织的组合，形成单元 |
| MODAF | 与 DoDAF 相同的定义 |
| IEEE | 为完成一个或多个特定功能而组织的组件集合 |
| JCS 1-02 | 功能上、物理上和/或行为上的...（同图注） |

**关键特性**：
- 系统由 **Materiel**（设备、飞机、舰船）组成
- 系统也由 **Personnel Types** 和组织要素组成
- 范围从小型装备到 **FoS**（Family of Systems）和 **SoS**（System of Systems）

### 3.4 Service（服务）

> **官方定义**：
> *"A mechanism to enable access to a set of one or more capabilities, where the access is provided using a prescribed interface and is exercised consistent with constraints and policies as specified by the service description."*

**关键特性**：
- Service 是一种 **Performer**（特殊形式的执行者）
- 通过**规定接口**提供对能力的访问
- 受约束和政策的限制
- 范围从软件服务到业务服务（如 Search and Rescue）

---

## 四、Performer 核心关系

### 4.1 关系一览（基于类图）

| 关系名称 | IDEAS 类型 | 源 | 目标 | 说明 |
|---------|-----------|----|------|------|
| `activityPerformedByPerformer` | OverlapType | Performer | Activity | **核心关系**：活动由执行者执行 |
| `activityPerformableUnderCondition` | OverlapType | Condition | Activity | 活动在条件下可执行 |
| `materielPartOfPerformer` | WholePartType | Materiel | Performer | 物资作为执行者的一部分 |
| `personRoleTypePartOfPerformer` | WholePartType | PersonRoleType | Performer | 角色作为执行者的一部分 |
| `resourceInLocationType` | WholePartType | Location | Resource | 资源位于某位置 |
| `ruleConstrainsActivity` | superSubtype | Guidance → Rule → Agreement | Activity | 规则约束活动 |
| `skillOfPersonRoleType` | Property | Skill | PersonRoleType | 技能是角色的属性 |
| `measureableSkillOfPersonRoleType` | couple | Measure | PersonRoleType | 可度量技能关联 |
| `measureOfResource` | Property | Measure | Resource | 资源的度量 |
| `measureOfActivity` | Property | Measure | Activity | 活动的度量 |
| `measureOfCondition` | Property | Measure | Condition | 条件的度量 |

### 4.2 activityPerformedByPerformer（核心关系）

这是 Performer 最核心的关系——连接 Performer 和 Activity。

**官方语义**（PDF p.43）：
> An overlap between a Performer and an Activity that is **non-specific** as to whether:
> 1. the Activity is solely performed by the Performer
> 2. the Activity is performed by several Performers
> 3. the Performer performs only this Activity
> 4. the Performer performs other Activities

**关键理解**：
- 这是一个 **Overlap（重叠）** 关系，不是简单的归属关系
- 不指定"唯一性"——支持一对多、多对一、多对多关系
- 这种灵活性支持架构建模的各种场景

```
activityPerformedByPerformer 的四种模式：

┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  模式 1: 一对一（专属）                                      │
│  Performer A ──solely performs──► Activity X                 │
│                                                              │
│  模式 2: 多个 Performer 执行同一 Activity                     │
│  Performer B ─┐                                              │
│  Performer C ─┼── performs ──────► Activity Y                │
│  Performer D ─┘                                              │
│                                                              │
│  模式 3: 一个 Performer 只做这个 Activity                    │
│  Performer E ──performs ONLY──► Activity Z                   │
│                                                              │
│  模式 4: 一个 Performer 做多个 Activities                    │
│  Performer F ─┬── performs ──► Activity M                    │
│              └── performs ──► Activity N                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 组成关系

#### materielPartOfPerformer

> 物资（Materiel）作为执行者（Performer）的一部分。

**应用场景**：
- 士兵携带武器（Materiel 是 Performer 的一部分）
- 飞机配备雷达系统
- IT系统包含服务器硬件

**注意**：Materiel 本身也是一种 Resource，这里体现了 Resource → Performer 的组成路径。

#### personRoleTypePartOfPerformer

> 人员角色（PersonRoleType）作为执行者的一部分。

**应用场景**：
- 组织中包含多个岗位角色
- 团队由不同角色的人员组成
- 系统操作员角色嵌入到系统中

---

## 五、条件与度量子系统

### 5.1 条件机制

类图中展示了完整的条件-活动-执行者三角关系：

```
┌─────────────────────────────────────────────────────────────┐
│                    条件-活动-执行者 三角                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Condition（条件）                                           │
│   ┌─────────────┐                                           │
│   │   条件      │ ── activityPerformableUnderCondition ──►   │
│   │ (环境/状态)  │               Activity                   │
│   └─────────────┘               ┌─────────────┐             │
│          │                      │   活动      │             │
│          │ measureOf            └──────┬──────┘             │
│          ▼                             │                     │
│   ┌─────────────┐               activityPerformedByPerformer│
│   │   Measure    │                     │                     │
│   │   度量值     │                     ▼                     │
│   └─────────────┘               ┌─────────────┐             │
│                                  │  Performer  │             │
│                                  │   执行者    │             │
│                                  └─────────────┘             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**关键逻辑链**：
1. **Condition** 定义活动的可执行前提
2. **Measure** 对条件进行量化（如温度范围、密级要求）
3. **Activity** 在满足条件时可被执行
4. **Performer** 执行该活动

### 5.2 Measure（度量）贯穿所有实体

从类图可见，Measure 作为 Property 出现在三个地方：

| 度量目标 | 关系 | 说明 |
|---------|------|------|
| Activity | `measureOfActivity` | 活动的性能度量（如耗时、频率） |
| Resource | `measureOfResource` | 资源的属性度量（如数量、质量） |
| Condition | `measureOfCondition` | 条件的参数度量（如阈值、范围） |

**Measure 结构**：
```
<<Property>>
   Measure
   └── + numericValue : string（数值属性）
```

---

## 六、技能体系

### 6.1 Skill 与 PersonRoleType

类图底部展示了技能与角色的关系：

```
┌─────────────────────────────────────────────────────────────┐
│                      技能体系                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────────────┐                                   │
│   │  MeasureableSkill   │◄── superSubtype ───┐              │
│   │  （可度量技能）       │                    │              │
│   └──────────┬──────────┘                    │              │
│              │ superSubtype                  │              │
│              ▼                                │              │
│   ┌─────────────────────┐                   │              │
│   │       Skill          │                   │              │
│   │    [Property]        │                   │              │
│   └──────────┬──────────┘                   │              │
│              │ skillOfPersonRoleType          │              │
│              ▼                                │              │
│   ┌─────────────────────┐                   │              │
│   │   PersonRoleType     │                   │              │
│   │   （人员角色类型）    │                   │              │
│   └──────────┬──────────┘                   │              │
│              │ measureableSkillOfPersonRoleType              │
│              └──────────────────────────────────────────────┘│
│                                              │               │
│                                              ▼               │
│                                    ┌─────────────────┐      │
│                                    │     Measure      │      │
│                                    │ + numericValue   │      │
│                                    └─────────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**关键点**：
- **Skill** 是 PersonRoleType 的 **Property**（属性）
- **Skill** 有子类型 **MeasureableSkill**（可度量技能）
- **MeasureableSkill** 可通过 `measureableSkillOfPersonRoleType` 关联到 Measure
- 这意味着**人员的技能可以被量化评估**

---

## 七、规则与指导体系

### 7.1 Guidance → Rule → Agreement 层次

类图右侧展示了规则体系的层次：

```
Guidance（指导）
   │
   └── superSubtype ──► Rule（规则）
                           │
                           └── superSubtype ──► Agreement（协议）
                                
这三者共同通过 ruleConstrainsActivity 约束 Activity
```

**与 Performer 的关联**：
- Guidance/Rule/Agreement 通过约束 Activity 来间接影响 Performer
- 因为 Activity 必须由 Performer 执行，所以规则最终作用于 Performer

---

## 八、物化层次（Reification Levels）

### 8.1 Performer 的 Type ↔ Individual 映射

| Type 层（类型定义） | Individual 层（实例） | 关系 |
|-------------------|---------------------|------|
| PerformerType | Performer | powertypeInstance |
| OrganizationType | Organization | powertypeInstance |
| PersonRoleType | IndividualPersonRole | powertypeInstance |
| SystemType | System | powertypeInstance |
| ServiceType | IndividualService | powertypeInstance |

### 8.2 实例示例

| Type | Individual 示例 |
|------|-----------------|
| OrganizationType | 美国国防部、FBI、海军陆战队第1师 |
| PersonRoleType | 步兵班长、网络安全分析师、系统管理员 |
| SystemType | F-35战斗机、宙斯盾驱逐舰、IDS入侵检测系统 |
| ServiceType | 身份认证服务、威胁情报共享服务 |

---

## 九、Performer 在架构开发中的应用

### 9.1 各阶段用途（来自 PDF p.42-44）

#### 架构设计（AD）

1. **任务/活动/流程**被分配给 Performers 以实现期望的结果
2. Performers 进一步细分并分配给组织、人员和机械化
3. Rules、Locations 和 Measures 应用于组织、人员和机械化
4. 分配过程中存在大量**权衡机会**：
   - 自动化 vs 人工
   - 性能与成本效益

#### 系统工程（SE）

1. **Activities 分配给 Performers**（组织型、人力型、物资型或其组合）
2. Capabilities、 Measures、Conditions、Constraints 分配给 Performer 的各层 Reification
3. **Allocation**（分配）= 跨结构/层次的映射，不限于特定方法

#### 运筹规划（Ops Planning）

1. 确定**谁**将完成任务（Activities）、**在哪**、**在什么条件下**、达到**什么指标**
2. Performers 是需要管理和优化的主要项目

### 9.2 配置管理（CI）

某些类型的 Performer 处于配置控制之下，称为**配置项（Configuration Items, CIs）**：
- 软件 CI → CSCIs / SCIs（按 MIL-HDBK-881A）
- 硬件 CI → 按 Mil-STD-196E 分类法（Central → Center → System → Subsystem → Set → Group → Unit）

### 9.3 WBS 工作分解结构

WBS、规格说明、SOW 都要求识别 **Performers 及其组成部分** 作为基本要素。

---

## 十、Performer 主要视图映射

| 数据组 | 主要视图 | 次要视图 |
|--------|---------|---------|
| Performer | **OV-4**, **SV-1** | OV-2, SvcV-1, StdV-1 |

### OV-4 组织关系图

- 描述组织结构和关系
- 展示 Performer 之间的层级和协作关系
- 重点：Organization、PersonRole

### SV-1 系统接口描述

- 描述系统及其接口
- 展示 System、Service 之间的数据交换
- 重点：System、Service 接口

---

## 十一、与其他数据组的关键关系总结

```
Performer
├── activityPerformedByPerformer ──► Activity
├── capabilityDeliveredByPerformer ──► Capability
├── materielPartOfPerformer ──► Materiel (Resource)
├── personRoleTypePartOfPerformer ──► PersonRoleType
├── performerLocatedAtLocation ──► Location
├── measureOfPerformer ──► Measure
└── serviceComposedOfService ──► Service (as Performer)
```

---

## 十二、关键洞察总结

### 12.1 核心要点

| # | 要点 | 说明 |
|---|------|------|
| 1 | **Performer 是"Who"** | 架构开发的中心问题之一："谁来做" |
| 2 | **四种类别** | PersonRole / Organization / System / Service |
| 3 | **Activity 重叠关系** | activityPerformedByPerformer 支持 1:1, 1:N, N:1, N:N |
| 4 | **组成关系丰富** | Materiel 和 PersonRole 都可以是 Performer 的一部分 |
| 5 | **条件-活动-执行者三角** | Condition → Activity → Performer 形成完整的执行链条 |
| 6 | **技能可量化** | Skill → MeasureableSkill → Measure 形成技能评估体系 |
| 7 | **规则间接作用** | Guidance/Rule/Agreement 通过约束 Activity 间接影响 Performer |
| 8 | **度量无处不在** | Measure 贯穿 Activity、Resource、Condition |

### 12.2 建模检查清单

```
□ 识别所有 Performer 类型（人/组织/系统/服务）
□ 建立 Performer 层次结构（Type → Individual）
□ 定义每个 Performer 的 Activity（谁做什么）
□ 建立活动-执行者的重叠关系
□ 识别 Performer 的组成部分（Materiel、PersonRole）
□ 定义活动执行的条件（Condition）
□ 为条件和活动添加度量（Measure）
□ 定义角色所需的技能（Skill）及度量方式
□ 应用规则约束（Rule/Guidance/Agreement）
□ 文档化到 OV-4 / SV-1 视图
```

---

## 附录 A：术语对照表

| 英文术语 | 中文翻译 | 定义 |
|---------|---------|------|
| Performer | 执行者 | 执行活动并提供能力的任何实体 |
| PersonRoleType | 人员角色类型 | 由角色定义的人员类别，含分配物资 |
| Organization | 组织 | 有使命的资源集合 |
| System | 系统 | 功能/物理/行为相关的组件集合 |
| Service | 服务 | 通过规定接口提供能力访问的机制 |
| Materiel | 物资 | 设备、器材、补给品 |
| Skill | 技能 | 人员角色的属性 |
| MeasureableSkill | 可度量技能 | 可被量化的技能子类型 |
| Condition | 条件 | 活动/执行的环境状态 |
| activityPerformedByPerformer | 活动由执行者执行 | Performer-Activity 核心重叠关系 |

## 附录 B：关系速查表

| 关系名称 | 源 | 目标 | IDEAS 类型 |
|---------|-----|------|-----------|
| `activityPerformedByPerformer` | Performer | Activity | OverlapType |
| `activityPerformableUnderCondition` | Condition | Activity | OverlapType |
| `materielPartOfPerformer` | Materiel | Performer | WholePartType |
| `personRoleTypePartOfPerformer` | PersonRoleType | Performer | WholePartType |
| `resourceInLocationType` | Location | Resource | WholePartType |
| `ruleConstrainsActivity` | Rule/Guidance/Agreement | Activity | superSubtype |
| `skillOfPersonRoleType` | Skill | PersonRoleType | Property |
| `measureableSkillOfPersonRoleType` | Measure | PersonRoleType | Couple |
| `measureOfActivity` | Measure | Activity | Property |
| `measureOfResource` | Measure | Resource | Property |
| `measureOfCondition` | Measure | Condition | Property |

## 附录 C：参考来源

| 来源 | 页码/链接 | 内容 |
|------|----------|------|
| DoDAF v2.02 Web PDF | p.42-44 | Performer 官方定义和解释 |
| DoDAF Meta Model | performers.html | Performer 元模型在线文档 |
| DM2 JSON Extract | _dm2_v202_extract.json | 所有术语的结构化提取 |

---

*本分析基于 DoDAF v2.02 官方规范（dodaf_v2-02_web.pdf pp.42-45）和 performer.png 类图整理*
