---
tags:
  - dm2/view-analysis
  - index
---

# 📚 P1 重要视图报告索引 (21 份) ✅

> **完成时间**: 2026-04-18 23:12 ~ 23:35
> **产出**: 21 份完整分析报告 + 22 张 PDF 原图
> **位置**: `文学/领域知识/DM2/详细分析/视图全集/`

## A 组：能力 + 作战 (7 份)

| # | 视图 | 报告 | 核心发现 |
|---|------|------|---------|
| 19 | **CV-4** | [[P1-CV-4-CapabilityDependencies]] | CV-4≠CV-2: 前者=任意依赖网, 后者=IS-A分类树; 支持自定义依赖类型 |
| 20 | **CV-5** | [[P1-CV-5-CapabilityToOrgMapping]] | 每阶段一张; 本质属PV视点; ⚠️应在方案确定后制作(不限制解空间) |
| 21 | **CV-6** | [[P1-CV-6-CapabilityToOpActivitiesMapping]] | CV↔OV桥梁; 类比SV-5a; 支持完全/部分满足两种状态 |
| 22 | **CV-7** | [[P1-CV-7-CapabilityServicesMapping]] | CV-6的镜像(一个对活动一个对服务); 与SvcV-5形成完整追溯链 |
| 23 | **OV-3** | [[P1-OV-3-OperationalResourceFlowMatrix]] | OV-2的属性深化(非替代); Needline:ResourceFlow = 1:N; 安全架构须穷举 |
| 24 | **OV-6abc** | [[P1-OV-6abc-OperationalRulesStateEventTrace]] | 规则(What)+状态机+时序(How)三件套; OV-6a=What vs SV-10a=How |

## B 组：项目 + 标准 + 系统 (9 份)

| # | 视图 | 报告 | 核心发现 |
|---|------|------|---------|
| 25 | **PV-1** | [[P1-PV-1-ProjectPortfolio]] | 能力需求→项目投资的转化入口 |
| 26 | **PV-2** | [[P1-PV-2-ProjectTimeline]] | 多数据源时间协调器(CV-5/SV-8/SvcV-8均引用) |
| 27 | **PV-3** | [[P1-PV-3-ProjectToCapabilityMapping]] | 双向追溯审计表: 缺口/冗余检测 |
| 28 | **StdV-2** | [[P1-StdV-2-StandardsForecast]] | StdV-1的时间延伸; 技术→标准→演进的因果链; 可与SV-9组合为Fit-for-Purpose视图 |
| 29 | **SV-3** | [[P1-SV-3-SystemsSystemsMatrix]] | SV-1的表格摘要; 支持多种编码(状态/类别/密级); 可按域/阶段/方案组织多份 |
| 30 | **SV-5ab** | [[P1-SV-5ab-SystemsFunctionToOpActivityTraceability]] | SV-5a=函数粒度, SV-5b=系统粒度(可隐藏系统只显示Performer); 🔴🟡🟢交通灯状态 |
| 31 | **SV-6** | [[P1-SV-6-SystemsResourceFlowMatrix]] | OV-3的物理等价物; 跨系统边界流; SV-4逻辑vs SV-6物理(不必1:1); 追溯链OV-2→OV-3→SV-6 |
| 32 | **SV-9** | [[P1-SV-9-SystemsTechnologyForecast]] | 技术前瞻雷达; 短中长6/12/18月框架; 技术使能标准采纳(SV-9→StdV-2) |
| 33 | **SV-10a** | [[P1-SV-10a-SystemsRulesModel]] | 技术实现级规则库; OV-6a What vs SV-10a How; 引用StdV-1作为权威来源 |

## C 组：服务剩余 (6 份)

| # | 视图 | 报告 | 核心发现 |
|---|------|------|---------|
| 34 | **SvcV-2** | [[P1-SvcV-2-ServicesResourceFlowDescription]] | 服务接口规格(端口+协议栈); 支持非IT服务(SAR); 网络=服务; 协议需在StdV-1定义 |
| 35 | **SvcV-3a** | [[P1-SvcV-3a-SystemsServicesMatrix]] | 系统×服务交互摘要; 特别适合遗留系统服务化迁移场景 |
| 36 | **SvcV-3b** | [[P1-SvcV-3b-ServicesServicesMatrix]] | 服务协作拓扑; SOA编排的输入(SvcV-10a/b/c); 可按服务分类法组织 |
| 37 | **SvcV-5** | [[P1-SvcV-5-OpActivityToServicesTraceability]] | 活动→服务追溯桥梁; 交通灯状态; CV-7/SV-5a/SvcV-5形成活动追溯三胞胎 |
| 38 | **SvcV-6** | [[P1-SvcV-6-ServicesResourceFlowMatrix]] | OV-3/SV-6的服务侧物理等价; Net-Centric背景(生产者聚焦); SvcV-4逻辑vs SvcV-6物理 |
| 39 | **SvcV-9** | [[P1-SvcV-9-ServicesTechnologyForecast]] | SV-9的服务侧镜像; 服务技术路线(REST→gRPC→...); HR技能规划 |
| 40 | **SvcV-10a** | [[P1-SvcV-10a-ServicesRulesModel]] | 服务契约级规则; SLA/熔断/降级/重试/编排约束; SvcV-3b→SvcV-10编排输入 |

---

## P1 关键发现汇总

| 发现                                  | 影响范围               |
| ----------------------------------- | ------------------ |
| **CV-5 应在方案确定后制作**                  | 不限制解空间的实践原则        |
| **OV-3: Needline:RF = 1:N**         | 资源流细化时的关键映射关系      |
| **安全架构必须穷举所有交换**                    | OV-3 的特殊要求         |
| **OV-6a = What, SV/SvcV-10a = How** | 规则体系的三层分工          |
| **StdV-2 ← SV-9 使能**                | 技术预测驱动标准采纳的因果链     |
| **SV-4 逻辑 ≠ SV-6 物理** (不必1:1)       | 数据流建模的重要灵活性        |
| **SvcV-3b → SvcV-10 编排**            | 服务矩阵是规则/状态/时序的前置输入 |
| **CV-6 / SV-5a / SvcV-5 活动追溯三胞胎**   | 能力→系统→服务的完整活动覆盖    |

---

*与 [[00-INDEX-P0核心视图全集]] 配合使用，共覆盖 38/52 视图 (73%)*
