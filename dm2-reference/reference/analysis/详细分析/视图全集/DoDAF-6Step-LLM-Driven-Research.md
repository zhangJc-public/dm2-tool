---
title: DoDAF架构开发6步流程在LLM驱动下的演进研究
date: 2026-04-25
tags: [DoDAF, LLM, 方法论, AI驱动]
---

# DoDAF 架构开发 6 步流程在 LLM 驱动下的演进研究报告

> **研究时间**：2026-04-25
> **研究素材**：DoDAF v2.02 Vol.I pp.11-21（六步流程原文）+ Obsidian DM2 知识库（METHOD 方法论分析 / IDEAS 顶层本体 / 五大原子关联 / 视图生成协议 / Standard Interrogatives Matrix）

---

## 一、6 步流程原貌

| 步骤 | 名称 | 核心问题 |
|:---:|:---|:---|
| Step 1 | 确定架构的预期用途 | 为什么要做？给谁看？ |
| Step 2 | 确定架构的范围 | 做多宽？边界在哪？ |
| Step 3 | 确定支撑架构所需的数据 | 需要什么数据？ |
| Step 4 | 收集、整理、关联和存储架构数据 | 怎么获取和管理数据？ |
| Step 5 | 执行支撑架构目标的分析 | 数据能回答什么问题？ |
| Step 6 | 按决策者需求文档化结果 | 结论怎么呈现？ |

**核心哲学**：v2.0 的本质跃迁是**数据中心化**（data-centric）——视图是底层数据的可视化渲染，不是独立产物。这一哲学在 LLM 驱动下更加重要。

Step 1: Determine Intended Use of Architecture；

Step 2: Determine Scope of Architecture；

Step 3: Determine Data Required to Support Architecture Development；

Step 4: Collect, Organize, Correlate, and Store Architectural Data；

Step 5: Conduct Analyses in Support of Architecture Objectives；

Step 6: Document Results in Accordance with Decision-Maker Needs。

​	The high-level, 6-step architecture development process provides guidance to the architect and Architectural Description development team and emphasizes the guiding principles. The process is data-centric rather than product-centric (e.g., it emphasizes focus on data, and relationships among and between data, rather than DoDAF V1.0 or V1.5 products). This data-centric approach ensures concordance between views in the Architectural Description while ensuring that all essential data relationships are captured to support a wide variety of analysis tasks. The views created as a result of the architecture development process provide visual renderings of the underlying architectural data and convey information of interest from the Architectural Description needed by specific user communities or decision makers. The figure above depicts this 6-step process.

> [!NOTE]
>
> It is important to note that the development of Architectural Description is an iterative process and a unique one, in that every Architectural Description is: 
>
> - Different in that architecture creation serves a specific purpose, and is created from a particular viewpoint.
>
> - Serving differing requirements, necessitating different types of views to represent the collected data.
>
> - Representative of a 'snapshot in time' (e.g., the Architectural Description may represent the current view or baseline, or it may represent a desired view in some future time).
>
> - Changeable over time as requirements become more focused or additional knowledge about a process or requirement becomes known.

​	The methodology described below is designed to cover the broadest possible set of circumstances, and also to focus on the most commonly used steps by the architecture community.

**Step 1: Determine Intended Use of Architecture.** Defines the purpose and intended use of the architecture ("Fit-for-Purpose"); how the Architectural Description effort will be conducted; the methods to be used in architecture development; the data categories needed; the potential impact on others; and the process by which success of the effort will be measured in terms of performance and customer satisfaction. This information is generally provided by the process owner to support architecture development describing some aspect of their area of responsibility (process, activity, etc.).

A template for collection of high-level information relating to the purpose and scope of the Architectural Description, its glossary, and other information, has been developed for registration of that data in DARS.

**Step 2: Determine Scope of Architecture.** The scope defines the boundaries that establish the depth and breadth of the Architectural Description and establish the architecture's problem set, helps define its context and defines the level of detail required for the architectural content. While many architecture development efforts are similar in their approach, each effort is also unique in that the desired results or effect may be quite different. As an example, system development efforts generally focus first on process change, and then concentrate on those automated functions supporting work processes or activities. In addition to understanding the process, discovery of these 'system functions' is important in deciding how to proceed with development or purchase of automation support.

​	Information collected for Architectural Descriptions describing services is similar to information collected for Architectural Descriptions describing systems. For describing services, Architectural Description will collect additional information concerning subscriptions, directory services, distribution channels within the organization, and supporting systems/communications web requirements. 

​	Similar situations occur with Architectural Description development for joint operations. Joint capabilities are defined processes with expected results, and expected execution capability dates. The Architectural Descriptions supporting the development of these types of capabilities usually require the reuse of data already established by the military services and agencies, analyzed, and configured into a new or updated process that provides the desired capability. Included are the processes needed for military service and/or agency response, needed automation support, and a clear definition of both desired result and supporting performance measures (metrics). These types of data are presented in models. 

​	The important concept for this step is the clarity of scope of effort defined for the project that enables an expected result. Broad scoping or unclear definition of the problem can delay or prevent success. The process owner has the primary responsibility for ensuring that the scoping is correct, and that the project can be successfully completed.

​	Clarity of scope can better be determined by defining and describing the data to be used in the proposed Architectural Description in advance of the creation of views that present data about the Architectural Description itself, the subject-matter of the proposed Architectural Description, and a review of existing data from COIs, can provide a rich source for ensuring that Architectural Descriptions, when developed, are consistent with other existing Architectural Descriptions. It also ensures conformance with any data-sharing requirements within the Department or individual COIs, and conformant with the DM2.

​	An important consideration beginning with this and each subsequent step of the architecture

development process is the continual collection and recording of a consistent, harmonized,

and common vocabulary. The collection of terms should continue throughout the architecture

development process. As architectural data is identified to help clarify the appropriate scope

of the architecture effort, vocabulary terms and definitions should be disambiguated,

harmonized, and recorded in a consistent AV-2 process documented in the "DoDAF V2.0

Architecture Development Process for the DoDAF-described Models" Microsoft Project Plan.

Analysis of vocabularies across different Architectural Descriptions with similar scope may

help to clarify and determine appropriate Architectural Description scope. Specific examples

of data identification utilizing the AV-2 Data Dictionary construct are found in the DoDAF

Journal.

**Step 3: Determine Data Required to Support Architecture Development.** The required

level of detail to be captured for each of the data entities and attributes is determined

through the analysis of the process undergoing review conducted during the scoping in Step

2. This includes the data identified as needed for execution of the process, and other data

required to effect change in the current process, (e.g., administrative data required by the

organization to document the Architectural Description effort). These considerations establish

the type of data collected in Step 4, which relate to the architectural structure, and the depth

of detail required.

The initial type of architectural data content to be collected is determined by the established

scope of the Architectural Description, and recorded as attributes, associations, and concepts

as described in the DM2. A mapping from DM2 concepts, associations, and attributes to

architecture models suggests relevant architectural views the architect may develop (using

associated architecture techniques) during the more comprehensive and coherent data

collection of Step 4. This step is normally completed in conjunction with Step 4, a bottom-up

approach to organized data collection, and Architectural Description development typically

iterates over these two steps. As initial data content is scoped, additional data scope may be

suggested by the more comprehensive content of Architectural Views desired for

presentation or decision-making purposes.

This step can often be simplified through reuse of data previously collected by others, but

relevant to the current effort. Access to appropriate COI data and other architecture

information, discoverable via DARS and the DMR, can provide information on data and other

architectural views that may provide useful in a current effort.

Work is presently underway within the Department to ensure uniform representation for the

same semantic content within architecture modeling, called Architecture Modeling Primitives.

The Architecture Modeling Primitives, hereafter referred to as Primitives, will be a standard

set of modeling elements, and associated symbols mapped to DM2 concepts and applied to

modeling techniques. Using the Primitives to support the collection of architecture content

and, in concert with the PES, will aid in generating common understanding and

communication among architects in regard to architectural views. As the Primitives concepts

are applied to more modeling techniques, they will be updated in the DoDAF Journal and

details provided in subsequent releases of DoDAF. When creating an OV-6c in Business

Process Modeling Notation (BPMN), the Primitives notation may be used. DoD has created

the notation and it is in the DoDAF Journal. The full range of Primitives for views, as with the

current BPMN Primitives, will be coordinated for adoption by architecture tool vendors.

**Step 4: Collect, Organize, Correlate, and Store Architectural Data.** Architects typically

collect and organize data through the use of architecture techniques designed to use views

(e.g., activity, process, organization, and data models as views) for presentation and

decision-making purposes. The architectural data should be stored in a recognized

commercial or government architecture tool. Terms and definitions recorded are related to

elements of the (DM2).

Designation of a data structure for the Architectural Description effort involves creation of a

taxonomy to organize the collected data. This effort can be made considerably simpler by

leveraging existing, registered artifacts registered in DARS, to include data taxonomies and

data sets. Each COI maintains its registered data on DARS, either directly or through a

federated approach. In addition, some organizations, such as U.S. Joint Forces Command

(JFCOM), have developed templates, which provide the basis of a customizable solution to

common problems, or requirements, which includes datasets already described and

registered in the DMR. Examples of this template-based approach are in the DoDAF Journal.

DARS provides more information that is specific, and guidance on retrieving needed data

through a discovery process. Once registered data is discovered, the data can be cataloged

and organized within a focused taxonomy, facilitating a means to determine what new data

is required. New data is defined, registered in DARS, and incorporated into the taxonomy

structure to create a complete defined list of required data. The data is arranged for upload

to an automated repository to permit subsequent analysis and reuse. Discovery metadata

(i.e., the metadata that identifies a specific Architectural Description, its data, views, and

usage) should be registered in DARS as soon as it is available to support discovery and

enable federation. Architects and data managers should use the DoD EA Business Reference

Model (DoD EA BRM) taxonomy elements as the starting point for their registration efforts.

Additional discovery metadata, such as processes and services may be required later, and

should follow the same registration process.

**Step 5: Conduct Analyses in Support of Architecture Objectives.** Architectural data

analysis determines the level of adherence to process owner requirements. This step may

also identify additional process steps and data collection requirements needed to complete

the Architectural Description and better facilitate its intended use. Validation applies the

guiding principles, goals, and objectives to the process requirement, as defined by the

process owner, along with the published performance measures (metrics), to determine the

achieved level of success in the Architectural Description effort. Completion of this step

prepares the Architectural Description for approval by the process owner. Changes required

from the validation process, result in iteration of the architecture process (repeat steps 3

through 5 as necessary).

**Step 6: Document Results in Accordance with Decision-Maker Needs.** The final step

in the architecture development process involves creation of architectural views based on

queries of the underlying data. Presenting the architectural data to varied audiences requires

transforming the architectural data into meaningful presentations for decision-makers. This is

facilitated by the data requirements determined in Step 3, and the data collection methods

employed during Step 4.

DoDAF V2.0 provides for models and views. DoDAF-described Models are those models that

enable an architect and development team whose data has already been defined and

described consistent with the DM2. The models become views when they are populated with

architectural data. These models include those previously described in earlier versions of

DoDAF, along with new models incorporated from the MODAF, the NATO NAF, and TOGAF

that have relevance to DoD architecture development efforts.

Fit-for-Purpose Views are user-defined views that an architect and development team can

create to provide information necessary for decision-making in a format customarily used in

an agency. These views should be developed consistent with the DM2, but can be in formats

(e.g., dashboards, charts, graphical representations) that are normally used in an agency for

briefing and decision purposes. An Architectural Description development effort can result in

an Architectural Description that is a combination of DoDAF-described Models and Fit-for

Purpose Views.

DoDAF does not require specific models or views, but suggests that local organizational

presentation types that can utilize DoDAF-created data are preferred for management

presentation. A number of available architecture tools support the creation of views

described in this step. The PES provides the format for data sharing.

> [!NOTE]
>
> DoDAF V2.0 does NOT prescribe a Physical Data Model, leaving that task to the
>
> software developers who will implement the principles and practices of DoDAF in their
>
> own software offerings.

---

## 二、逐步再评估

### Step 1：确定用途 — 仍然必要，执行方式变了

- 从"Workshops + 访谈"变成"多轮对话中的意图收敛"
- LLM 可以主动追问，但"讨好本能"可能导致过早收敛
- **建议**：增加"反向质问"机制——LLM 在确认用途前必须显式提出 2-3 个根本性澄清问题

### Step 2：确定范围 — 更关键，上下文预算是硬约束

- 上下文窗口是 LLM 的硬约束，超出范围推理质量急剧下降
- Step 2 在 LLM 时代承担**上下文预算管理**的角色
- 范围界定本质是选择要使用哪些 DM2 数据组

### Step 3：数据定义 — 核心地位不变，且更显性化

- 从"人类架构师的规划活动"变成"LLM 的推理前置条件"
- DM2 五大原子关联（WholePart / BeforeAfter / Overlap / Couple / TemporalWholePart）覆盖 90%+ 的建模关联需求
- LLM 内化这 5 种模式后，能更准确判断关系类型

### Step 4：数据存储 — 变化最彻底的环节

```
传统模式：架构数据 → DARS/EA工具 → 人类架构师读取
LLM模式：  架构数据 → Obsidian知识库(DM2笔记)
                    ↓
              LLM工作记忆(MEMORY.md+每日日志)
                    ↓
              LLM直接推理 → 产出视图
```

IDEAS 的"Individual IS-A Type"公理使每条笔记既可以是 Individual（具体实例），也可以通过 wikilinks 声明其 Type 身份——天然支持 DM2 的概念-实例分离。

### Step 5：分析执行 — 从"阶段性产物"到"持续推理能力"

SE 四算子作为 LLM 的推理引擎：

| 算子          | 解决的问题   | 在 6 步中的位置   |
| :---------- | :------ | :---------- |
| **Cynefin** | 感知（看哪里） | Step 2 范围判定 |
| **溯因推理**    | 因果（为什么） | Step 3 数据选择 |
| **OODA 循环** | 韧性（会怎样） | Step 5 分析执行 |
| **TOC 约束**  | 落地（怎么做） | Step 5 分析执行 |

### Step 6：文档化 — 形式变了，内核没变

- 文档从"最终交付物"变成"LLM 的下一个输入"
- Composite Views（多 W 一图）比单视图更有推理价值
- LLM 产出的视图文档存入 Obsidian，通过 wikilinks 与 DM2 笔记建立双向关联

---

## 三、LLM 驱动的融合 6 步框架

```
Step 1+2：意图澄清 + 范围界定
  → Cynefin 判定复杂度 + 上下文预算

Step 3+4：数据定义 + 知识沉淀
  → 6W矩阵驱动采集 + DM2笔记网络

Step 5：分析执行（SE 四算子驱动）
  → 溯因补全 + OODA韧性 + TOC瓶颈

Step 6：文档化 + 知识回流
  → Composite View优先 + wikilinks双向关联
       ↓
  ← 回 Step 1（迭代）
```

---

## 四、核心结论

1. **6 步骨架保留**，但执行机制从"人类工作流"变成"LLM + 知识库协同"
2. **Step 3 是核心瓶颈**——LLM 推理质量取决于知识库的广度和精度，当前缺 GB/T → DM2 映射
3. **VIEW-GENERATION-PROTOCOL** 是 LLM 驱动 DoDAF 的最小可行实现
4. **SE 四算子**是 Step 5 从模糊变可操作的必要条件

---

## 五、后续研究建议

1. 建立 GB/T → DM2 映射（等保2.0 / 密评 / 关基 → DM2 数据组）
2. 扩展 VIEW-GENERATION-PROTOCOL 为 6 步全程约束协议
3. 选取实际安全体系项目进行实践验证
