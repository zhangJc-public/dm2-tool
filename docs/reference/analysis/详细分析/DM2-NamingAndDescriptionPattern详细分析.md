---
tags:
  - dm2/analysis
---

> **操作模板** -> [[../00-基础模式/NamingAndDescriptionPattern.md]]
> **所属数据组** -> [[../00-基础模式]]

# DM2 Naming and Description Pattern（命名与描述模式）详细分析

> **来源**：`Naming and Description Pattern.png` + DoDAF v2.02 PDF (IDEAS Foundation 相关章节)
> **日期**：2026-04-18
> **性质**：DM2 的"语义基础模式"——定义事物如何被命名和描述的完整元模型

---

## 一、概述

### 1.1 什么是 Naming and Description Pattern？

**Naming and Description Pattern（命名与描述模式）** 是 DM2 中关于**事物如何被标识、命名、描述和分类**的基础元模型。它回答了架构建模中最基本的问题：

> - 这个东西叫什么？(**Name**)
> - 它用什么方式表示？(**Representation**)
> - 它有什么属性描述？(**Description**)
> - 这些名称和描述遵循什么规范？(**Scheme**)

### 1.2 核心定位

```
IDEAS Top Level (本体: Thing/Individual/Type/Tuple)
    │
    ▼
Foundation For Associations (关联模式)
    │
    ▼
★ Naming & Description Pattern ★  ← 本文档
    (事物的"身份卡"系统)
    │
    ├── Name (名字)        → "它叫什么"
    ├── Description (描述) → "它是什么"
    ├── Representation (表示) → "它长什么样"
    └── Scheme (方案)      → "遵循什么规范"
```

### 1.3 与其他图的关系

| 关系 | 目标图 | 说明 |
|------|--------|------|
| **使用来自** | Foundation For Associations | couple/typeinstance/superSubtype 模式 |
| **扩展了** | Information Pedigree | Sign/Representation 的详细展开 |
| **服务于** | 所有 17 个数据组 | 每个实体都需要名字和描述 |
| **被 Location 使用** | Address 命名模式 | URL/邮址都是 Name 的实例 |

---

## 二、类图解析

### 2.1 整体布局

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Thing                                       │
│  ┌──────────────────────────────────────────┐                      │
│  │         tuple / couple                   │ thingDescribed       │
│  │  place1[subsets]  place2[subsets]        │◄──────────────┐     │
│  └──────────────────┬───────────────────────┘               │     │
│                     │ «IDEAS:superSubtype»                    │     │
│                     ▼                                          │     │
│  ┌──────────────────────────────────────────┐   ┌────────────┴───┐  │
│  │           representedBy                  │   │  describedBy   │  │
│  │  (浅绿色大框)                             │   │  (浅绿)        │  │
│  └────────┬─────────────────────────────────┘   └───────┬────────┘  │
│           │ «IDEAS:powertypeInstance»                 │            │
│           ▼                                         ▼            │
│  ┌────────────────┐                    ┌────────────────────┐      │
│  │ IndividualType │                    │ IndividualType     │      │
│  │ SignType       │ thingDescribed     │ (place1Type)       │      │
│  └───────┬────────┘                    └─────────┬──────────┘      │
│          │ «IDEAS:                                      │            │
│          │  superSubtype»                                │ description │
│          ▼                                              │ place2Type   │
│  ┌──────────────┐                              ┌────────▼────────┐   │
│  │ Representation│  exemplar:variant             │   Information   │   │
│  │  (蓝色大框)   │ ◄────────────┐               │    (蓝色)       │   │
│  └──────┬────────┘              │               └────────┬────────┘   │
│         │                       │                        │             │
│         │ «IDEAS:               │                        │             │
│         │ powertypeInstance»    │                        │             │
│         ▼                       │                        │             │
│  ┌──────────────┐               │               ┌────────▼────────┐   │
│  │RepresenType  │               │               │SecurityAttrGroup│   │
│  │(紫色)        │               │               │ArchDescription  │   │
│  └──────┬───────┘               │               └─────────────────┘   │
│         │                       │                                     │
│         │ «IDEAS:               │  ═════════ NAME 区域 ════════      │
│         │ superSubtype»         │                                     │
│         ▼                       │  ┌──────────────┐                   │
│  ┌──────────────┐               │  │NameType(紫色)│                   │
│  │InformationType│              │  └──────┬───────┘                   │
│  │(紫色)         │              │         │                           │
│  └───────────────┘              │         │ instance                  │
│                                 │         ▼                           │
│  ═══ SCHEME 区域 ═══            │  ┌──────────────┐                   │
│                                 │  │   Name       │                   │
│  ┌──────────────┐              │  │  (蓝色大框)   │                   │
│  │NamingScheme  │              │  └──────┬───────┘                   │
│  │(蓝色)        │nameSpace      │         │ namedBy                  │
│  └──────┬───────┘◄─────────────│─────────┤ place2Type                │
│         │                       │         ▼                           │
│         │ namingSchemeInst.     │  [Thing 被命名]                     │
│         ▼                       │                                     │
│  ┌──────────────┐              │  ═══ DESCRIPTION 区域 ════          │
│  │DescrScheme   │              │                                     │
│  │(蓝色)        │scheme         │  ┌──────────────────────┐          │
│  └──────────────┘├────────────►│  │descriptionSchemeInst │          │
│                          place1Type  │  (浅绿色)            │          │
│                                  └──────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 颜色编码

| 颜色 | 元素类别 | 图中元素 |
|------|---------|---------|
| 🔵 **浅蓝** | 核心实体 | Thing, Representation, Information, Name, NamingScheme, DescScheme |
| 🟩 **浅绿** | Instance 层关系 | representedBy, describedBy, namedBy, descriptionSchemeInstance |
| 🟣 **紫色** | Type 层分类 | IndividualType/SignType, RepType, InfoType, NameType, SecurityAttributesGroup, ArchDescription |
| 🟠 **橙色** | Individual 实体 | Individual/Sign |

### 2.3 四大功能区域

| 区域 | 核心元素 | 功能 |
|------|---------|------|
| **📛 名称区 (Name)** | Name, NameType, namedBy, NamingScheme | "这个东西叫什么" |
| **📝 描述区 (Description)** | Information, describedBy, DescriptionScheme | "这个东西是什么" |
| **🎨 表示区 (Representation)** | Representation, Sign, representedBy, RepType | "这个东西如何呈现" |
| **📋 方案区 (Scheme)** | NamingScheme, DescriptionScheme, RepresentationScheme | "遵循什么规范" |

---

## 三、四大核心概念详解

### 3.1 Name（名称）—— 身份标识

#### 3.1.1 定义与结构

**namedBy 关系**：
> *A couple that asserts that a Name describes a Thing.*

```mermaid
graph LR
    T[Thing] --|"namedBy<br/>(couple)"| N[Name]
    N --|"typeinstance"| NT[NameType]
    NT -.->|"«IDEAS:superSubtype»"| RT[RepresentationType]
    
    N --|"namingSchemeInstance"| NS[NamingScheme]
    NS --|"nameSpace"| NS2[NamingScheme]
    
    style N fill:#87CEEB
    style NT fill:#DDA0DD
    style NS fill:#87CEEB
```

#### 3.1.2 Name 的关键特性

| 特性 | 说明 |
|------|------|
| **是 Representation 的子类** | Name 是一种特殊的"表示形式"——用语言符号来指称事物 |
| **通过 namedBy 连接 Thing** | 断言"这个名称指的是那个事物" |
| **有 NameType 分类** | 区分不同种类的名称（正式名、别名、代码名...）|
| **属于 NamingScheme** | 遵循特定的命名规范/方案 |
| **有 nameSpace** | 命名空间避免冲突 |

#### 3.1.3 NameType

> *A RepresentationType that is the Powertype of Name.*

Name 的幂类型分类——对名称的种类进行划分：

| NameType 示例 | 含义 | SOC 示例 |
|--------------|------|---------|
| 正式名称 | 组织/系统官方名 | "安全管理中心(SOC)" |
| 别名/俗称 | 非正式称呼 | "安全大脑"、"SOC" |
| 编码/标识符 | 系统内部ID | "SOC-BJ-001" |
| URL/URI | 网络可寻址名 | "soc.internal.army.mil" |
| 军事代号 | 作战代号 | "铁盾行动" |
| 型号/版本 | 产品型号 | "SIEM-Enterprise-v4.2" |

### 3.2 Description（描述）—— 属性说明

#### 3.2.1 describedBy 关系

```mermaid
graph TB
    T[Thing] --|"thingDescribed<br/>place1Type"| DB["describedBy<br/>(couple)"]
    DB --|"description<br/>place2Type"| I[Information]
    I --|"instance"| IT[IndividualType]
    
    I --|"«IDEAS:superSubtype»"| SAG[SecurityAttributesGroup]
    I --|"«IDEAS:superSubtype»"| AD[ArchitecturalDescription]
    
    I --|"descriptionSchemeInstance"| DSI["descriptionSchemeInstance"]
    DSI --|"scheme<br/>place1Type"| DS[DescriptionScheme]
    
    style I fill:#87CEEB
    style DS fill:#87CEEB
    style SAG fill:#DDA0DD
    style AD fill:#DDA0DD
```

#### 3.2.2 Information 的两个重要子类型

**ArchitecturalDescription（架构描述）**：
> *Information describing an architecture such as an OV-5 Activity Model document.*

- 架构文档本身就是一种 Information
- 出现在 **InfoData, Reification, Services** 数据组中
- 典型实例：OV-1 高层概览图、SV-4 系统功能描述等

**SecurityAttributesGroup（安全属性组）**：
> *The group of Information Security Marking attributes in which use of 'classification' and 'ownerProducer' is required.*

- DoD 信息安全标记体系
- 必须包含 `classification`(密级) 和 `ownerProducer`(生产者) 属性
- 对比：SecurityAttributesOptionGroup 中这两个属性可选

### 3.3 Representation（表示）—— 外观形式

#### 3.3.1 表示层级

```
Thing (被表示的对象)
  │
  ├── representedBy → Sign (符号/标记个体)
  │     │
  │     └── is-a → Individual (Sign is an Individual!)
  │     
  └── representedBy → Representation (具体表示实例)
        │
        ├── has exemplar: variant (有变体/范例)
        │
        └── type → RepresentationType (表示的类型分类)
              │
              ├── superSubtype → NameType (名称是一种表示)
              ├── superSubtype → InformationType (信息也是一种表示)
              └── ...
```

#### 3.3.2 Sign vs Representation vs Name 的关系

这是本图最精妙的三分法：

| 概念 | 性质 | 示例 | 抽象级别 |
|------|------|------|---------|
| **Sign** | 符号**个体**（具体的标记实例）| 写在纸上的"BOSTON"这串字符 | 最具体 |
| **Representation** | 表示**实例**（某种形式的呈现）| 地图上波士顿的位置标记 | 具体 |
| **Name** | 名称（**Representation 的子类**）| "Boston"这个字符串 | 较抽象 |
| **SignType** | 符号**类型**（符号的分类）| "城市名称"类型 | 抽象 |
| **RepresentationType** | 表示**类型** | "地图标记"、"文本标签" | 更抽象 |

**关键区分**：
> **Sign = 具体的标记事件**（如某次说出"波士顿"的声音）
> **Name = 标记的模式/模板**（如"波斯顿"这个词本身）

### 3.4 Scheme（方案/规范）—— 命名的治理

#### 3.4.1 三种 Scheme

| Scheme | 定义 | 用途 |
|--------|------|------|
| **NamingScheme** | *"A Type whose members are Names. What kind of name the name is."* | 管理名称的命名空间和规则 |
| **DescriptionScheme** | *"A RepresentationScheme whose members are intentionally descriptions"* | 管理描述的格式和内容要求 |
| **RepresentationScheme** | *"A RepresentationType that is a collection of Representations that are intended to be the preferred Representations in certain contexts."* | 在特定上下文中推荐使用的表示方式 |

#### 3.4.2 Scheme 的层次关系

```
RepresentationScheme (最通用 - 推荐表示集合)
  ├── extends/is-related-to → NamingScheme (名称专用)
  └── extends/is-related-to → DescriptionScheme (描述专用)

NamingScheme
  ├── nameSpace → NamingScheme (嵌套命名空间)
  └── namingSchemeInstance → Name (成员断言)

DescriptionScheme  
  └── descriptionSchemeInstance → Description (成员断言)
```

#### 3.4.3 实际案例：DoD 的命名方案

| Scheme 类型 | DoD 示例 | 规则 |
|-------------|---------|------|
| **NamingScheme** | 军事编号系统 | 如 "M1A2 Abrams Tank" 的编号规范 |
| **DescriptionScheme** | Data Item Description (DID) | MIL-STD-961 文档格式要求 |
| **RepresentationScheme** | UI/UX 设计规范 | DoD 交互设计标准 |

---

## 四、核心关系详解

### 4.1 图中的所有关系一览

| # | 关系名 | 从 | 到 | 类型 | 多重性 |
|---|-------|----|----|------|--------|
| 1 | **tuple/couple** | Thing | — | Tuple/Couple | places: 2..* |
| 2 | **representedBy** | Thing | Representation | Couple | — |
| 3 | **describedBy** | Thing | Information | Couple | thingDescribed/place1Type, description/place2Type |
| 4 | **namedBy** | Thing | Name | Couple | place2Type |
| 5 | **typeinstance** | NameType → Name | — | typeInstance | — |
| 6 | **namingSchemeInstance** | NamingScheme → Name | — | repSchemeInstance | nameSpace |
| 7 | **descriptionSchemeInstance** | DescriptionScheme → Description | repSchemeInstance | scheme/place1Type |
| 8 | **exemplar: variant** | Representation → ? | — | powertypeInstance | — |
| 9 | **superSubtype** | (多处) | — | — | IDEAS 继承 |

### 4.2 三个 "By" 关系的区别 ⚡

这是本图最重要的区分：

```mermaid
graph LR
    subgraph "三个 By 关系"
        direction TB
        T[Thing]
        
        T --|"representedBy"| R["Representation<br/>(表示形式)"]
        T --|"describedBy"| I["Information<br/>(结构化描述)"]
        T --|"namedBy"| N["Name<br/>(名称标识)"]
        
        R ---|"是一种特殊的<br/>Representation"| N
        I ---|"包含更多细节<br/>than Name"| N
    end
    
    style R fill:#87CEEB
    style I fill:#87CEEB
    style N fill:#87CEEB
```

| 维度 | **representedBy** | **describedBy** | **namedBy** |
|------|-------------------|-----------------|-------------|
| **连接到** | Representation | Information | Name |
| **回答问题** | "它怎么被呈现？" | "它有什么属性？" | "它叫什么？" |
| **内容量** | 视觉/符号形式 | 丰富的文本/数据 | 简短标识符 |
| **示例** | 图标、模型形状、URI | 文档段落、属性表 | ID、标题、代码 |
| **基数** | 一个事物可有多种表示 | 一个事物可有多个描述 | 一个事物可有多个名字 |
| **包含关系** | — | 包含 namedBy | 是 Representation 的子类 |

---

## 五、在 DM2 全局中的作用

### 5.1 每个实体都有"身份卡"

DM2 中的每个实体，通过此模式获得完整的身份定义：

```
任意实体 (Thing)
  ├── namedBy → Name (可以是多个)
  │     ├── NameType = "正式名称" → "SOC 安全管理中心"
  │     ├── NameType = "缩写"      → "SOC"  
  │     └── NameType = "内部代码"  → "SYS-SOC-001"
  │
  ├── describedBy → Information (可以是多个)
  │     ├── ArchitecturalDescription → OV-1 视图文档
  │     └── 一般描述 → 文本说明
  │
  └── representedBy → Representation (可以是多个)
        ├── Sign → 图形图标
        └── Representation → EA 模型元素
```

### 5.2 与 Location 的 Address 命名模式的联系

在 Location 分析中我们学到：

> **Address = Location 的 Name**

这意味着：
- URL (`http://soc.example.com`) 是一种 **Name**
- 邮政地址 ("北京市海淀区XX路XX号") 也是一种 **Name**
- URN (`urn:doD:soc:beijing:01`) 还是 **Name**

它们都通过 **namedBy** 关系连接到 Location 这个 Thing，并通过不同的 **NamingScheme** 管理。

### 5.3 与 SecurityAttributesGroup 的联系

**SecurityAttributesGroup** 作为 Information 的子类型，使得每个实体的描述都可以附带安全标记：

```xml
<!-- 概念示例 -->
<Thing name="SOC Architecture">
  <describedBy>
    <Information type="SecurityAttributesGroup">
      <classification>UNCLASSIFIED//FOUO</classification>
      <ownerProducer>USA</ownerProducer>
    </Information>
  </describedBy>
</Thing>
```

---

## 六、典型应用场景

### 6.1 SOC 资产的完整身份卡

以 SIEM 子系统为例，展示完整的命名+描述+表示：

| 维度 | 内容 | Scheme |
|------|------|--------|
| **Name (正式)** | "企业级安全信息与事件管理系统" | NamingScheme: 项目正式命名规范 |
| **Name (缩写)** | "SIEM" | NamingScheme: 缩写规范 |
| **Name (内部)** | "SYS-SIEM-PRD-01" | NamingScheme: CMDB 编码规范 |
| **Name (URL)** | "siem.soc.internal" | NamingScheme: DNS 命名规范 |
| **Description (架构)** | SV-4 功能描述文档 | DescriptionScheme: DoDAF SV-4 模板 |
| **Description (接口)** | REST API OpenAPI 3.0 规格书 | DescriptionScheme: API 文档规范 |
| **Description (安全)** | 密级: 内部使用 | SecurityAttributesGroup |
| **Representation (图形)** | OV-3 遵图中的圆角矩形 | RepresentationScheme: DoDAF 图形规范 |
| **Representation (模型)** | Enterprise Archiect 中的 Class 元素 | RepresentationScheme: EA 建模规范 |
| **Representation (数据)** | CMDB 中的 ConfigurationItem 记录 | RepresentationScheme: CMDB Schema |

### 6.2 命名冲突解决

当同一个 Thing 有多个 Name 时，通过 **NamingScheme + nameSpace** 解决冲突：

```
Thing: 北京基地的安全运营中心

Name#1: "SOC"          (NamingScheme: 内部简称, nameSpace: 全球)
Name#2: "Beijing SOC"  (NamingScheme: 地点前缀, nameSpace: 全球)
Name#3: "NOSC-CN-BJ"   (NamingScheme: NATO 编码, nameSpace: NATO)
Name#4: "安全管理中心"  (NamingScheme: 中文正式名, nameSpace: 中国)

→ 通过 (Name, NamingScheme, nameSpace) 三元组唯一确定
```

### 6.3 架构文档的可追溯命名

每份 ArchitecturalDescription 都应该有标准化的命名：

```
ArchitecturalDescription: 
  name: "OV-5b-SOC-ActivityModel-v2.1"
  namingScheme: "DoDAF_View-ID_Version"
  descriptionScheme: "DoDAF_OV5_Template_v2.0"
  securityGroup: {classification: "U//FOUO", ownerProducer: "USA"}
  pedigree: "基于 2026-04-10 工作坊产出修订"
```

---

## 七、版本差异

### v1.5 → v2.0 变化

| 方面 | v1.5 | v2.0 |
|------|------|------|
| **命名建模** | ad-hoc，依赖工具 | **统一的 Name/NameType/NamingScheme** |
| **描述管理** | 自由文本 | **DescriptionScheme + 模板约束** |
| **表示区分** | 不区分 Sign/Representation/Name | **三层清晰分离** |
| **安全标记** | 未纳入元模型 | **SecurityAttributesGroup 一等公民** |
| **方案治理** | 无 | **三种 Scheme 显式建模** |
| **ArchitecturalDescription** | 未显式定义 | **作为 Information 的子类型** |

### v2.0 新增的核心能力

1. **NamingScheme + nameSpace** —— 企业级命名的 governance 基础
2. **DescriptionScheme** —— 描述内容的标准化和模板化
3. **SecurityAttributesGroup** —— 信息安全的内建支持
4. **ArchitecturalDescription** —— 架构文档作为一等建模对象
5. **exemplar: variant** —— 支持同一表示的多种变体

---

## 八、关键洞察

### 🔑 从 Naming & Description Pattern 中发现的 7 个关键洞察

| # | 发现 | 说明 | 架构意义 |
|---|------|------|---------|
| **1** | **Name ⊂ Representation ⊂ Sign 层级链** 🔗 | 名称是最狭义的表示，符号是最广义的标记 | 建模时根据精度需求选择合适的层级 |
| **2** | **三个 "By" 回答三个不同问题** ❓ | representedBy=外观, describedBy=内涵, namedBy=标识 | 不要混淆——它们不可互相替代 |
| **3** | **Scheme = 命名的 Governance** 📋 | NamingScheme/DescScheme 不是技术细节而是治理工具 | 大型架构项目必须建立命名规范 |
| **4** | **SecurityAttributesGroup 内建于描述层** 🔒 | 安全密级不是外部标注而是元模型原生支持 | DoD 信息安全的底层保障 |
| **5** | **ArchitecturalDescription IS Information** 📄 | 架构图/文档也是一种信息资源 | 可以被追溯、度量、版本管理 |
| **6** | **nameSpace 支持分布式命名** 🌐 | 嵌套的 NamingScheme 避免全局名称冲突 | 多团队协作时的命名基础 |
| **7** | **最容易被忽视但最常用** 👻 | 每个 DM2 实体都隐式使用此模式 | 理解它可以提升所有架构描述的质量 |

---

## 九、速查卡

```
┌──────────────────────────────────────────────────────────────────┐
│             NAMING & DESCRIPTION PATTERN 速查卡                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  【三问三答】                                                    │
│  ──────────                                                     │
│  Q: 它叫什么？    A: namedBy → Name (via NamingScheme)           │
│  Q: 它是什么？    A: describedBy → Information (via DescScheme)  │
│  Q: 它长什么样？  A: representedBy → Representation/Sign        │
│                                                                  │
│  【层级关系】                                                    │
│  ──────────                                                     │
│  Sign (符号个体 - 最具体)                                        │
│    └── Representation (表示实例)                                 │
│          ├── Name (名称 - 一种特殊表示)                          │
│          └── Information (描述 - 更丰富的表示)                    │
│                ├── ArchitecturalDescription (架构文档)            │
│                └── SecurityAttributesGroup (安全标记)            │
│                                                                  │
│  【三种 Scheme】                                                │
│  ────────────                                                   │
│  NamingScheme        → 管理名称的命名空间和规则                   │
│  DescriptionScheme   → 管理描述的格式和内容模板                   │
│  RepresentationScheme → 在特定上下文中推荐表示方式                │
│                                                                  │
│  【实践检查清单】                                                │
│  ────────────                                                   │
│  ✓ 每个实体至少有一个正式 Name                                    │
│  ✓ Name 属于某个 NamingScheme                                    │
│  ✓ 关键实体有 ArchitecturalDescription                            │
│  ✓ 敏感信息附有 SecurityAttributesGroup                           │
│  ✓ 命名冲突通过 nameSpace 解决                                    │
│                                                                  │
│  【金句】                                                        │
│  ───────                                                        │
│  "A well-named architecture is half-understood."                │
│  "Names are the handles by which we grasp concepts."           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 十、与其他已分析数据组的关系

```
┌─────────────────────────────────────────────────────────────┐
│                  DM2 元模式依赖图谱                           │
│                                                             │
│  IDEAS TopLevel (本体公理)                                   │
│       │                                                     │
│       ▼                                                     │
│  Foundation For Associations (关联语法)                       │
│       │                                                     │
│       ├──► Common Patterns (模式总览)                        │
│       │                                                     │
│       ├──► Naming & Description (★本文档★)                  │
│       │      │                                             │
│       │      ├── 被 Location 使用 (Address=Name)            │
│       │      ├── 被 InfoPedigree 使用 (Sign/Rep)            │
│       │      └── 被所有数据组使用 (每个实体都要命名)          │
│       │                                                     │
│       ├──► Temporal Part & Boundaries (时间模式)             │
│       │                                                     │
│       └──► 其他 13 张业务数据组图                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

> **本文档完成于 DM2 类图系列分析的第 17 张。**
> 最后一张：Temporal Part and Boundaries
