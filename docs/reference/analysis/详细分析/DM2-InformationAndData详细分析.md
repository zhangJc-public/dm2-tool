---
tags:
  - dm2/analysis
---

> **操作模板** -> [[../16-InformationAndData/README.md]]
> **所属数据组** -> [[../16-InformationAndData]]

# DoDAF/DM2 Information and Data 信息与数据详细分析

> 基于 Information and Data.png 类图及 DoDAF v2.02 官方规范
> 分析日期：2026-04-17
> 版本：v1.0

---

## 一、Information and Data 概述

### 1.1 核心定位

Information and Data 是 DM2 元模型中描述 **"信息的语义层面与物理表示"** 的核心数据组。它位于 Resource Flow 之下，是企业架构中数据建模的基础。

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
│   ┌─────────────────────────────────────────────────────┐   │
│   │              Resource Flow 资源流                    │   │
│   │   ┌────────────────┐    ┌────────────────┐          │   │
│   │   │  Information   │    │      Data      │          │   │
│   │   │   信息(语义)    │    │   数据(物理)    │          │   │
│   │   └────────────────┘    └────────────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 Information vs Data 的本质区别

| 维度 | Information（信息） | Data（数据） |
|------|-------------------|--------------|
| **层次** | 语义层面（Semantic） | 物理表示层面（Physical） |
| **定义** | "某物的状态" | "信息的正式化表示" |
| **特性** | 与意义相关，依赖语境 | 独立于意义，可被机器处理 |
| **示例** | "敌人位置在X坐标" | 1010110101（比特流） |
| **关系** | Information 是 Data 所表达的内涵 | Data 是 Information 的外延 |

---

## 二、核心概念定义

### 2.1 Information（信息）

> **官方定义**（DoDAF/CADM）：
> *"Information is the state of a something of interest that is materialized -- in any medium or form -- and communicated or received."*

**关键解读**：
- Information 是"感兴趣事物"的状态
- 必须以某种媒介或形式具体化（materialized）
- 可以被通信或接收

**多来源定义对照**：

| 来源       | 定义                                          |
| -------- | ------------------------------------------- |
| NAF      | 关于对象（事实、事件、事物、过程、想法）的知识，在特定语境中具有特定意义        |
| JCS 1-02 | 1. 以任何媒介或形式存在的事实、数据或指令 2. 人类通过已知表示约定赋予数据的意义 |
| IDEAS    | 信息的实例（如一次话语、一封电子邮件、一份文档实例、一个电子文件实例）         |
| Webster  | 通过交流或研究获得的知识或情报                             |

### 2.2 Data（数据）

> **官方定义**：
> *"Representation of information in a formalized manner suitable for communication, interpretation, or processing by humans or by automatic means."*

**关键解读**：
- Data 是信息的**正式化表示**
- 适合人类或机器的通信、解释或处理
- 可以是模型、包、实体、属性、类、域值、枚举值、记录、表、行、列、字段等

**多来源定义对照**：

| 来源 | 定义 |
|------|------|
| NAF | 可重新解释的信息表示，适合人类或自动处理 |
| Zachman | 企业架构框架中关注"对哪些事物足够重要需要保存信息"的列 |
| DoD Net-Centric Data Strategy | 支撑数据战略的概念 |

### 2.3 InformationType（信息类型）

> **定义**：Category or type of information（信息的类别或类型）

**用途**：
- 对 Information 进行分类
- 如：战略信息、战术信息、作战信息等

### 2.4 DataType（数据类型）

> **定义**：Powertype of Data（Data 的幂类型）

**用途**：
- 定义 Data 的类型层次
- 如：字符串、整数、日期、布尔等基础类型
- 支持复杂数据结构定义

---

## 三、类型层次结构

### 3.1 Information 层次

```
<<Type>>
   InformationType
        │
        ├── IndividualInformation
        │      │
        │      ├── StrategicInfo（战略信息）
        │      │    │
        │      │    ├── ThreatAssessment（威胁评估）
        │      │    └── CapabilityAnalysis（能力分析）
        │      │
        │      ├── TacticalInfo（战术信息）
        │      │    │
        │      │    ├── MissionOrder（任务命令）
        │      │    └── SituationReport（态势报告）
        │      │
        │      ├── OperationalInfo（作战信息）
        │      │    │
        │      │    ├── IntelligenceReport（情报报告）
        │      │    └── StatusUpdate（状态更新）
        │      │
        │      └── AdministrativeInfo（行政信息）
        │           │
        │           ├── Policy（政策）
        │           └── Procedure（程序）
        │
        └── InformationType hierarchies...
```

### 3.2 Data 层次

```
<<Powertype>>
   DataType
        │
        ├── PrimitiveType（基础类型）
        │    │
        │    ├── String（字符串）
        │    ├── Integer（整数）
        │    ├── Real（实数）
        │    ├── Boolean（布尔）
        │    ├── Date（日期）
        │    ├── Time（时间）
        │    └── Binary（二进制）
        │
        ├── StructuredType（结构化类型）
        │    │
        │    ├── Record（记录）
        │    ├── Table（表）
        │    ├── Array（数组）
        │    └── ComplexType（复杂类型）
        │
        └── DomainSpecificType（领域特定类型）
             │
             ├── Coordinate（坐标）
             ├── ClassificationLevel（密级）
             └── GeoLocation（地理位置）
```

---

## 四、核心关系

### 4.1 Information 与 Thing 的关系

| 关系 | 说明 | 方向 |
|------|------|------|
| `describedBy` | Information 描述 Thing（核心关系） | Information → Thing |

> **定义**：A tuple that asserts that Information describes a Thing.

**语义解读**：
- Information 附着于某个实体（Thing）
- 表示该实体的"状态"
- 是语义层面的关联

### 4.2 Information 内部关系

| 关系 | 说明 | 类型 |
|------|------|------|
| `associationOfInformation` | Information 之间的关联 | Whole-part |

> **定义**：A relationship or association between two elements of information.

**用途**：
- 表示信息元素之间的关系
- 如：订单与客户的关系、产品与供应商的关系

### 4.3 Information 与活动的关联

| 关系 | 说明 |
|------|------|
| `activityProducesResource` | 活动产生 Information（作为 Resource） |
| `activityConsumesResource` | 活动消耗 Information（作为 Resource） |
| `activityPerformedByPerformer` | 活动执行（与 Information 相关） |

### 4.4 Data 与 Information 的关联

```
┌─────────────────────────────────────────────────────────────┐
│                   Data 与 Information 关系                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────────────┐                                   │
│   │        Data         │                                   │
│   │   (数据的物理表示)   │                                   │
│   └──────────┬──────────┘                                   │
│              │                                               │
│              │ represents                                   │
│              │ (表示)                                        │
│              ▼                                               │
│   ┌─────────────────────┐                                   │
│   │     Information      │                                   │
│   │    (信息的语义内涵)   │                                   │
│   └──────────┬──────────┘                                   │
│              │                                               │
│              │ describes                                     │
│              │ (描述)                                         │
│              ▼                                               │
│   ┌─────────────────────┐                                   │
│   │       Thing          │                                   │
│   │    (被描述的实体)     │                                   │
│   └─────────────────────┘                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 五、Information 的物化层次

### 5.1 Reification 在 Information 上的应用

根据 DM2 的 Reification 机制，Information 同样分为 Type/Individual 层：

```
┌─────────────────────────────────────────────────────────────┐
│                   Information 物化层次                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                   <<Powertype>>                       │   │
│   │                  InformationType                     │   │
│   │                   （信息类型）                         │   │
│   └─────────────────────────┬───────────────────────────┘   │
│                             │ <<powertypeInstance>>          │
│   ┌─────────────────────────▼───────────────────────────┐   │
│   │                      <<Type>>                         │   │
│   │                   Information                        │   │
│   │                   （信息类型定义）                      │   │
│   └─────────────────────────┬───────────────────────────┘   │
│                             │ <<typeInstance>>                │
│   ┌─────────────────────────▼───────────────────────────┐   │
│   │                    <<Individual>>                     │   │
│   │                IndividualInformation                  │   │
│   │                   （信息实例）                         │   │
│   │                                                             │
│   │  例如：一份具体的作战命令、一个特定的情报报告               │
│   └─────────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Type vs Individual 示例

| Type（类型） | Individual（实例） |
|------------|------------------|
| IntelligenceReport（情报报告） | 2026-04-17 14:00的朝鲜半岛态势情报 |
| MissionOrder（任务命令） | "攻击X目标"的第123号作战命令 |
| StatusUpdate（状态更新） | 某部队"已完成集结"的状态报告 |

---

## 六、Information 的分类体系

### 6.1 按用途分类

```
Information
     │
     ├── Strategic Information（战略信息）
     │    │
     │    ├── 长期规划信息
     │    ├── 战略目标信息
     │    └── 威胁评估信息
     │
     ├── Tactical Information（战术信息）
     │    │
     │    ├── 作战计划信息
     │    ├── 战场态势信息
     │    └── 火力协调信息
     │
     ├── Operational Information（作战信息）
     │    │
     │    ├── 实时情报
     │    ├── 作战指令
     │    └── 行动反馈
     │
     └── Administrative Information（行政信息）
          │
          ├── 人事信息
          ├── 财务信息
          └── 后勤信息
```

### 6.2 按领域分类

根据 DM2 的 DomainInformationType：

```
DomainInformation
     │
     ├── MilitaryOperations（军事行动领域）
     │    │
     │    ├── Combat（作战）
     │    ├── Intelligence（情报）
     │    └── Logistics（后勤）
     │
     ├── BusinessOperations（业务运营领域）
     │    │
     │    ├── Finance（财务）
     │    ├── HR（人力资源）
     │    └── Procurement（采购）
     │
     └── ITOperations（IT运维领域）
          │
          ├── Network（网络）
          ├── Security（安全）
          └── Application（应用）
```

---

## 七、Information 与其他数据组的关系

### 7.1 关系网络图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Information 关系网络                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐                                              │
│   │    Thing     │◄────────── describedBy ──────────┐            │
│   │   (实体)     │                                  │            │
│   └──────────────┘                                  │            │
│                                                      │            │
│   ┌──────────────┐     produces/consumes     ┌──────────────┐   │
│   │   Activity   │◄──────────────────────────┤ Information  │   │
│   │   (活动)     │                            │   (信息)     │   │
│   └──────────────┘                            └───────┬──────┘   │
│         │                                             │           │
│         │ performs                              represents │           │
│         ▼                                             ▼           │
│   ┌──────────────┐                            ┌──────────────┐   │
│   │  Performer   │                            │    Data      │   │
│   │   (执行者)   │                            │   (数据)     │   │
│   └──────────────┘                            └──────────────┘   │
│         │                                             │           │
│         │ locatedAt                               measuredBy │           │
│         ▼                                             ▼           │
│   ┌──────────────┐                            ┌──────────────┐   │
│   │   Location   │                            │   Measure    │   │
│   │   (位置)     │                            │   (度量)     │   │
│   └──────────────┘                            └──────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 7.2 关系详解

| 关系 | 源 | 目标 | 说明 |
|------|---|------|------|
| `describedBy` | Thing | Information | 实体被信息描述 |
| `activityProducesResource` | Activity | Information | 活动产生信息 |
| `activityConsumesResource` | Activity | Information | 活动消耗信息 |
| `represents` | Data | Information | 数据表示信息 |
| `associationOfInformation` | Information | Information | 信息之间关联 |
| `locatedAt` | Information | Location | 信息位于某位置 |
| `informationPedigree` | Information | Pedigree | 信息谱系 |

---

## 八、Information 建模实践

### 8.1 DIV-1 数据与信息概念模型

在 DoDAF DIV-1（数据与信息概念模型）中，Information 建模需要描述：

| 要素 | 说明 | 必选/可选 |
|------|------|----------|
| Information 标识 | 信息的唯一标识符 | 必选 |
| Information 类型 | InformationType | 必选 |
| 语义描述 | 信息的含义 | 必选 |
| 关系 | 与其他 Information/Thing 的关系 | 必选 |
| Data 表示 | 表示该信息的数据格式 | 可选 |
| 位置 | 信息存储/传输位置 | 可选 |
| 生命周期 | 信息的创建、修改、销毁 | 可选 |

### 8.2 Information 建模步骤

```
步骤 1：识别业务对象
   └─► 确定需要描述的实体（Thing）

步骤 2：定义 Information
   └─► 为每个实体定义描述性的 Information

步骤 3：分类 Information
   └─► 归类到适当的 InformationType

步骤 4：建立关系
   └─► 用 describedBy 连接 Thing 与 Information
   └─► 用 associationOfInformation 建立信息间关系

步骤 5：定义 Data 表示
   └─► 为每个 Information 定义 Data 格式

步骤 6：添加约束
   └─► 补充完整性约束、访问控制等

步骤 7：文档化
   └─► 生成 DIV-1 数据与信息概念模型
```

---

## 九、典型应用场景

### 9.1 情报系统场景

```
┌─────────────────────────────────────────────────────────────┐
│                   情报系统 Information 建模                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Thing                              Information              │
│   ┌─────────────┐                   ┌─────────────────┐      │
│   │  EnemyForce │◄──describedBy───│ ThreatAssessment │      │
│   │   敌军      │                   │   威胁评估       │      │
│   └─────────────┘                   └────────┬────────┘      │
│                                               │ represents     │
│                                               ▼                │
│   Data                                       ┌─────────────────┐│
│   ┌─────────────────────────────┐            │  DataFormat     ││
│   │ XML Document:               │            │  (数据格式)     ││
│   │ <threat level="HIGH"/>      │            └─────────────────┘│
│   └─────────────────────────────┘                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 作战命令场景

```
┌─────────────────────────────────────────────────────────────┐
│                   作战命令 Information 建模                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Thing                              Information              │
│   ┌─────────────┐                   ┌─────────────────┐      │
│   │   Target     │◄──describedBy───│  MissionOrder    │      │
│   │   目标       │                   │   任务命令       │      │
│   └─────────────┘                   └────────┬────────┘      │
│                                               │ represents     │
│                                               ▼                │
│   Data                                       ┌─────────────────┐│
│   ┌─────────────────────────────┐            │ JSON Message    ││
│   │ {                          │            │ (JSON消息)      ││
│   │   "target_id": "X",        │            └─────────────────┘│
│   │   "action": "attack"       │                               │
│   │ }                          │                               │
│   └─────────────────────────────┘                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 十、与 DoDAF 1.5 的差异

### 10.1 信息建模的演进

| 方面       | DoDAF 1.5    | DoDAF 2.0 (DM2)                |
| -------- | ------------ | ------------------------------ |
| **信息定义** | 模糊，主要是"信息交换" | 精确区分 Information（语义）和 Data（表示） |
| **建模粒度** | 系统/功能导向      | 实体/语义导向                        |
| **关系描述** | 隐含在交换中       | 显式的关系建模                        |
| **类型层次** | 扁平           | 层次化（Type/Individual）           |

### 10.2 关键改进

1. **语义与表示分离**：Information（语义）≠ Data（表示）
2. **实体描述机制**：通过 describedBy 显式描述 Thing
3. **类型层次支持**：Type → Individual 的物化机制
4. **信息关联建模**：associationOfInformation 支持复杂信息关系

---

## 十一、关键洞察总结

### 11.1 核心要点

| # | 要点 | 说明 |
|---|------|------|
| 1 | **Information 是语义** | Information 描述"某物的状态" |
| 2 | **Data 是表示** | Data 是信息的"正式化表示" |
| 3 | **describedBy 是核心** | Information 通过 describedBy 描述 Thing |
| 4 | **Type/Individual 分层** | Information 有完整的物化层次 |
| 5 | **信息分类** | 按用途（战略/战术/作战/行政）和按领域分类 |

### 11.2 建模检查清单

```
□ 识别需要描述的业务实体（Thing）
□ 为每个实体定义 Information
□ 确定 Information 的 InformationType
□ 建立 Information 与 Thing 的 describedBy 关系
□ 定义 Information 的 Data 表示
□ 建立 Information 之间的 associationOfInformation 关系
□ 添加位置、生命周期等约束
□ 文档化到 DIV-1 视图
```

---

## 附录 A：术语对照表

| 英文术语                     | 中文翻译   | 定义                   |
| ------------------------ | ------ | -------------------- |
| Information              | 信息     | 某感兴趣事物的状态            |
| Data                     | 数据     | 信息的正式化表示             |
| InformationType          | 信息类型   | Information 的类别      |
| DataType                 | 数据类型   | Data 的幂类型            |
| IndividualInformation    | 信息实例   | Information 的具体化     |
| describedBy              | 被...描述 | Information 描述 Thing |
| associationOfInformation | 信息关联   | Information 之间的关系    |
| DomainInformation        | 领域信息   | 特定领域的信息类型            |
| Pedigree                 | 谱系     | 信息的出处和历史             |

## 附录 B：关系速查表

| 关系名称                       | 源实体         | 目标实体        | 关系类型      |
| -------------------------- | ----------- | ----------- | --------- |
| `describedBy`              | Thing       | Information | Tuple     |
| `associationOfInformation` | Information | Information | WholePart |
| `activityProducesResource` | Activity    | Information | Couple    |
| `activityConsumesResource` | Activity    | Information | Couple    |
| `represents`               | Data        | Information | Couple    |
| `informationPedigree`      | Information | Pedigree    | Couple    |

---

*本分析基于 DoDAF v2.02 官方规范和 DM2 元模型类图整理*
