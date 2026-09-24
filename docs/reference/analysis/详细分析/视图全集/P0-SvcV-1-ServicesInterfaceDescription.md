---
tags:
  - dm2/view-analysis
  - dodaf/svcv
  - p0-core
---

> 📄 来源：DoDAF v2.02 Vol.II, pp.170-172
> 🎯 视点：Services Viewpoint（服务视点）
> 📊 优先级：P0 核心
> 🔗 关联 DM2 数据组：[[DM2-Performer]] / [[DM2-ResourceFlow]] / [[DM2-Activity]]
> 🖼️ 原图：[[images/SvcV-1-p170.png]]

# SvcV-1: Services Interface Description（服务接口描述）

## 一、定位与目的

### 1.1 这张图回答什么问题？

**一句话**：**服务**之间如何组合和交互来实现作战需求？

SvcV-1 是服务视点的**结构模型**——展示服务、资产和人员如何配置成满足特定能力的方案。

核心问题集：
| 问题 | 回答 |
|------|------|
| 有哪些服务及其子服务？ | 服务分解结构 |
| 服务之间如何交互？ | Service Resource Flows |
| 谁使用这些服务？ | 组织资源和人员类型 |
| 部署在哪些物理资产上？ | 平台/设施位置 |

### 1.2 在架构描述中的角色

```
┌──────────────────────────────────────────────────┐
│        SvcV-1: 服务接口描述                       │
│   （服务结构 / OV-2 Needlines 的服务实现）        │
├──────────────────────────────────────────────────┤
│                                                  │
│   OV-2 (Needline) ──实现(Realize)──→ SvcV-1     │
│                                                  │
│   ┌─────────┐   资源流    ┌─────────┐           │
│   │ Service A │ ─────────→ │ Service B │          │
│   │ (发布者)  │            │ (订阅者)  │          │
│   └────┬─────┘            └─────────┘           │
│        │                                         │
│   部署在:                                        │
│   ┌────┴────┐                                   │
│   │ Platform │ ← Physical Asset                 │
│   └─────────┘                                   │
│   使用者: Organization / Personnel Type           │
│                                                  │
│   与 SV-1 的关键差异:                             │
│   ├─ SvcV-1: 关注 Provider + Data (发布/订阅)     │
│   └─ SV-1:   关注 System-to-System 点对点接口      │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 二、核心内容解析

### 2.1 必要性说明

> SvcV-1 解决服务的**组成和交互**问题。DoDAF V2.0 中，SvcV-1 将**人类元素作为 Performer 类型**纳入——组织和人员类型。
>
> SvcV-1 通过描绘资源如何结构和交互来**实现 OV-2 中指定的逻辑架构**，将作战和服务架构模型连接起来。
>
> ⚠️ **SvcV-1 vs SV-1 的核心区别**：
> - **SvcV-1**: 聚焦 **Resource Flow 和提供的服务** → 适合 **发布/订阅模式**（以网络为中心的数据战略原则）
> - **SV-1**: 聚焦 **System-to-System 点对点接口** → Source System 和 Target System 之间的约定接口

预期用途：
1. 服务概念定义
2. 服务选项定义
3. 服务资源流需求捕获
4. 能力集成规划
5. 服务集成管理
6. 作战规划（能力和执行者定义）

### 2.2 两种互补使用方式

| 方式 | 内容 |
|------|------|
| **方式一** | 描述架构中资源间交换的 Resource Flows |
| **方式二** | 以能力组件及其在平台和其他设施上的物理集成为基础描述**解决方案或解决方案选项** |

### 2.3 关键数据元素

| 元素 | 说明 |
|------|------|
| **Services / Sub-services** | 服务及子服务（可任意深度分解） |
| **Performers（Services as）** | 服务作为执行者类型 |
| **Personnel Types** | 人员类型（V2.0 新增的人类因素） |
| **Organizational Resources** | 组织资源 |
| **Physical Assets / Platforms** | 部署资源的物理资产 |
| **Service Resource Flows** | 服务间的资源流动指示器 |
| **Service Functions（可选叠加）** | 来自 SvcV-4 的功能 |
| **Operational Activities/Locations（可选标注）** | 来自 OV-2 的追溯标注 |

### 2.4 完整细节

#### 2.4.1 物理资源的组成规则

> 贡献于能力的物理资源要么是组织资源，要么是**物理资产**——即**服务不能单独贡献**（它必须托管在由组织资源使用的物理资产上）。

#### 2.4.2 人类因素（V2.0 新增）

> DoDAF V2.0 包括**人类因素**（作为 Personnel Types 和一种 Performer 类型）。如果架构师希望描述具有人工元素的服务，应使用 Services、Personnel Types 和 Performers 的分组来将人工和服务元素包装在一起。

#### 2.4.3 从 OV-2 到 SvcV-1 的追溯

> SvcV-1 可以选择性地用 OV-2 中最初指定的 Operational Activities 和 Locations 标注。通过这种方式，可以建立从逻辑 OV 结构到物理 Service Model 结构的**追溯性**。
>
> 在许多情况下，OV-2 中描绘的作战活动和位置很可能是 SvcV-1 中显示的资源的**逻辑表示**。

#### 2.4.4 SvcV-1 与 SvcV-4 的互补关系

> SvcV-1 和 SvcV-4 提供**互补的表示（结构和功能）**。两者都可以先建模，但通常采用**迭代方法**逐步构建服务描述的详细程度。

#### 2.4.5 Needline 到 Service Resource Flow 的映射

> Service Resource Flows 提供了**OV-2 Needlines 中指定的资源流交换如何被服务实现的规范**。
>
> ⚠️ OV-2 中的单个 Needline 可能**转换为多个** Service Resource Flows。
>
> Service Resource Flow 的实际实现可能采取**多种形式**（如多条物理链路）。实现接口的物理路径或网络模式的详细信息记录在 SvcV-2 中。

---

## 三、关联视图

| 上游依赖（输入） | 下游支撑（输出） | 同级互补 |
|------------------|-----------------|---------|
| OV-2（Needlines → 实现） | → SvcV-2（Resource Flow 详情） | SV-1（系统接口对应物） |
| CV（能力需求） | → SvcV-3a/b（矩阵汇总） | SvcV-4（行为/功能对应物） |
| OV-5b（活动→服务追溯来源） | → SvcV-6（RF 矩阵） | |

---

## 四、待补充（第二阶段填入）

- [ ] 适用场景清单（基于 Architecture Interrogatives 矩阵）
- [ ] 不适用场景
- [ ] 常见误区
- [ ] 示例框架（最小化模板）
- [ ] 中国适配备注（独立第三阶段）

---

## 五、术语表

| 英文术语 | 中文翻译 | 说明 |
|---------|---------|------|
| Services Interface Description | 服务接口描述 | 服务组成与交互的结构化描述 |
| Publish/Subscribe Pattern | 发布/订阅模式 | 以网络为中心的数据分发模式 |
| Net-Centric Data Strategy | 以网络为中心的数据战略 | DoD 数据管理原则之一 |
| Physical Asset | 物理资产 | 托管系统/服务的硬件平台 |
| Personnel Type | 人员类型 | 人员分类（非具体个人） |
| Realization | 实现 | 逻辑需求到物理方案的映射关系 |
