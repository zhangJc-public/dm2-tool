# Common Patterns（元元模型）

> DM2 的建模规范总纲，所有 18 个数据组都遵循的通用模式。

## 概述

Common Patterns 定义了 DM2 中所有数据项的通用建模规则，是元元模型（Meta-Meta Model）层。

## 1. Type/Individual 具体化模式

### 层级结构
```
TypeType（类型之类型）
   ↓
Type（类型/模板）
   ↓
Individual（具体实例）
```

### 颜色编码
- **紫色** = Type 层（模板）
- **橙色** = Individual 层（实例）

### 示例
| Type | Individual |
|------|------------|
| SystemType | IndividualSystem |
| ActivityType | IndividualActivity |
| CapabilityType | IndividualCapability |
| OrganizationType | Organization |
| PersonRoleType | IndividualPersonRole |

## 2. 四元素建模模式

所有 DM2 数据项都围绕四个核心问题展开：

| 元素 | 维度 | 典型数据项 |
|------|------|-----------|
| **What** | 资源/信息 | Resource、Information |
| **Who** | 执行者 | Performer（System/Organization） |
| **When** | 时间 | Temporal、Project |
| **Why** | 规则 | Rules、Guidance |

### 价值链中的分布
```
Vision（为什么） → Project（何时） → Activity（做什么） → Capability → Performer（谁） → Resource（什么）
```

## 3. WholePartType 层级模式

整体-部分关系，用于表达包含/组成结构。

### 层级示例
- `capabilityPartOfCapabilityType` — 能力组成能力类型
- `capabilityPartOfCapability` — 能力组成能力
- `activityPartOfCapability` — 活动组成能力

### 核心规则
- Part → Whole 是 `partOf` 关系
- Whole → Part 是 `hasPart` 或直接包含
- 支持多层嵌套（TypeType → Type → Individual）

## 4. Association 通用关系模式

DM2 定义了四种标准关系类型：

### 4.1 WholePartType（整体-部分）
- **含义**：包含/组成关系
- **示例**：System hasPart Component
- **符号**：⊃（包含）、⊂（组成）

### 4.2 OverlapType（重叠）
- **含义**：共享/交叉关系
- **示例**：两个 Capability 共享同一个 Activity
- **符号**：⊙（重叠）

### 4.3 CoupleType（成对）
- **含义**：双向关联关系
- **示例**：System ↔ Service
- **符号**：↔（双向）

### 4.4 BeforeAfterType（前后）
- **含义**：时序/依赖关系
- **示例**：Activity A before Activity B
- **符号**：→（时序）

## 5. Temporal 建模模式

时间维度是 DM2 的核心跨领域机制。

### Temporal Part（时间切分）
- 每个实体可以有多个 Temporal Part
- 不同时间点的实例可以共存

### Temporal Boundary（时间边界）
- 定义实体的有效时间范围
- 支持版本管理和演进追踪

## 6. Naming & Description 模式

### 命名规范
- 使用标准化的命名模式
- 支持多语言（中文/英文）
- 可追溯的命名历史（Pedigree）

### 描述结构
```
Description
├── name（名称）
├── definition（定义）
├── note（备注）
└── source（来源）
```

## 7. Measure 通用量化模式

Measure 是跨数据组的通用度量机制。

### Measure 关联
- 任何实体都可以关联 Measure
- 支持 Performance（性能）、Metrics（指标）
- 形成量化分析基础

## 8. Location 空间建模模式

### 位置类型
- **地理位置**：Physical Location
- **逻辑位置**：Logical Location
- **虚拟位置**：Virtual Location

### 位置关系
- `locatedAt` — 定位于
- `hasLocation` — 拥有位置

## 9. Pedigree 信息血缘模式

记录信息的来源和演变历史。

### Pedigree 链
```
Source → Derived → Aggregated → ...
```

### 属性
- 来源（Source）
- 派生方式（Derivation）
- 置信度（Confidence）
- 时间戳（Timestamp）

## 10. 元元模型要素总结

| 要素 | 作用 | 适用范围 |
|------|------|----------|
| Type/Individual 分层 | 区分模板与实例 | 所有数据项 |
| 四元素 | 结构化问题域 | 所有分析 |
| WholePartType | 层级分解 | Capability、Activity、Performer |
| Association | 关系建模 | 所有数据项 |
| Temporal | 时间演进 | 所有数据项 |
| Naming/Description | 可追溯性 | 所有数据项 |
| Measure | 量化评估 | 性能/质量分析 |
| Location | 空间定位 | Performer、Resource |
| Pedigree | 血缘追踪 | Information、Data |

---

## 相关笔记

- [[DM2-REFERENCE]] — DM2 参考主页
- [[Performer]] — Performer 数据组
- [[Capability]] — Capability 数据组
