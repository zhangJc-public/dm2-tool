---
tags:
  - dm2/analysis
  - dm2/governance
---

> **操作模板** → [[../00-基础模式]]  \n> **所属数据组** → [[..]]

# DM2 Working Group (WG) 治理结构分析

> 📄 来源：DoDAF v2.02 Volume II, pp.261-262 (CM Overview 章节)  
> 🔗 原始 PDF: `C:\Users\vanom\Desktop\dodaf_v2-02_web.pdf`

## 一、什么是 DM2 WG？

**DM2 Working Group（工作组）** 是 DM2 的**配置管理（Configuration Management, CM）执行体**。

### 核心定位

```
┌─────────────────────────────────────────────────┐
│              DoD CIO（配置管理权威）              │
│                    ↓                            │
│    Architecture & Standards Review Group (ASRG)  │ ← 决策层
│              （架构与标准审查组）                  │
│                    ↓                            │
│           DM2 Working Group (WG)                │ ← 执行层
│         （DM2 配置管理工作组）                    │
│          = DoD EA COI DMWG                      │ ← 兼职身份
└─────────────────────────────────────────────────┘
```

### 关键事实

| 属性 | 内容 |
|------|------|
| **CM 权威** | DoD CIO（国防部首席信息官） |
| **上级机构** | ASRG（Architecture and Standards Review Group） |
| **起源** | 在 DoDAF 2.0 开发期间建立 |
| **转型** | 从开发团队 → 转型为 CM 持续管理实体 |
| **兼职角色** | 同时担任 **DoD Enterprise Architecture COI Data Management Working Group (DMWG)** |

### 三大职责

1. **监督与审查** — 监督、审查 CM 计划的技术层面，向 ASRG 提出建议
2. **变更评审** — 受 ASRG 委托时，对拟议变更进行**详尽全面的技术评审**
3. **行动推荐** — 向 ASRG 推荐应采取的行动（基于变更建议的结果）

---

## 二、DM2 WG 组织生态（第262页原图）

![DM2 WG Organization Ecosystem](../DM2-WG-Page262-orgchart.png)

> ⬆️ 上图为 DM2 WG 与外部组织的交互关系全景（DoDAF v2.02 p.262）

### 10 类交互组织详解

| # | 组织类型 | 具体实体 | 关系性质 | 状态 |
|---|---------|---------|---------|------|
| **1** | **ASRG** | 架构与标准审查组 | 上级决策者，拥有所有 DM2 CI 变更的**批准权** | ✅ 已建立 |
| **2** | IDEAS Group | 国际国防企业架构规范组 | 标准对接 | TBS* |
| **3** | 工业顾问/标准组 | OMG、OASIS | 行业标准对齐 | TBS |
| **4** | 相关 COI | UCORE、C2 Core | 领域兴趣共同体 | TBS |
| **5** | 受控词汇组 | Controlled Vocabulary Groups | 术语标准化 | TBS |
| **6** | 试点/早期采用者 | Pilots and Early Adopters | 实践验证 | TBS |
| **7** | DoDAF WG | DoDAF 工作组 | 框架层面协调 | TBS |
| **8** | DARS TWG | 架构注册系统工作组 | 注册发现平台 | TBS |
| **9** | DoD MDR WG | 元数据注册工作组 | 元数据管理 | TBS |
| **10** | EA Tool Vendors | 企业架构工具厂商 | 工具链支持 | TBS |

> *TBS = To Be Specified（待确定/规划中）

---

## 三、DM2 WG 内部结构（第261页协作站点）

![DM2 Collaboration Site](../DM2-WG-Page261-diagram.png)

> ⬆️ DM2 协作站点主题区域截图（DoDAF v2.02 p.261）

### 协作站点的 6 大区域

| 区域 | 内容 |
|------|------|
| **① Current baseline** | 当前基线：CDM、LDM、PES 文件和文档 |
| **② Working copy** | 工作副本（活跃修改中的版本） |
| **③ IDEAS model and profile** | IDEAS 模型和 Profile 定义 |
| **④ Folders** | 信息/参考资料/Tutorials/Briefings 文件夹 |
| **⑤ Next meeting info** | 下次会议信息 |
| **⑥ Links** | 到 IDEAS & BORO 的外部链接 |

### DM2 WG 下属领域分组

从图中可见 DM2 WG 内部按领域分为多个子组：

```
DM2 WG
├── Govt   （政府）
├── Military（军方）
├── Industry（工业界）
├── Academia（学术界）
└── Vendors （供应商）
```

这体现了 DM2 治理的**多方利益相关者参与**原则——不仅是军方内部，还纳入了工业界、学术界的输入。

---

## 四、ASRG 详细职责（第262页补充）

由于 ASRG 是 DM2 WG 的直接上级，理解它有助于把握整个治理链条：

### ASRG 在 DoD CIO 治理框架中的位置

```
DoD CIO Enterprise Guidance Board（企业指导委员会）
                    ↓
        Architecture & Standards Review Group (ASRG)
                    ↓
    ┌───────┬───────┼───────┬──────────────┐
    ↓       ↓       ↓       ↓              ↓
  ITSC    GTG CMB   ARG    ERAC      Ad-hoc Tiger Teams
(标准委员会) (技术指导CMB) (架构审查组) (参考架构单元)
```

### ASRG 六大职能

1. 审查架构政策与指南
2. 识别 DoD IT 技术标准
3. 监督 IT 标准 管理
4. 审查架构并强制执行架构政策
5. 监督 DoD EA 联邦
6. 强制执行 DoD IEA（信息企业架构）合规

### ASRG 运作方式

- **常设秘书处** + **常设小组** + **临时特遣队(Tiger Teams)**
- 支援来自成员单位，现有小组将按需重新归入 ASRG
- **对所有 DM2 CI 变更行使批准权**

---

## 五、对中国 DoDAF实践的启示

### 🔑 关键洞察

1. **配置管理是元模型的命脉** — DM2 不是"写完就冻结"的标准，而是一个**持续演进的受控实体**
2. **双层治理结构** — ASRG（战略决策）+ WG（技术执行），分工明确
3. **多方参与** — 军方/政府/工业界/学术四方协同，避免闭门造车
4. **COI 兼任机制** — DM2 WG 同时是 EA COI 的数据管理工作组，实现**治理复用**
5. **工具生态整合** — EA Tool Vendors 作为第 10 类交互方，确保标准能落地到工具链

### 🇨🇳 中国适配思考

| 美国做法 | 中国对应/可借鉴点 |
|---------|----------------|
| DoD CIO as CM Authority | 国家标准化管理委员会 / 中央网信办？ |
| ASRG 双层决策 | 可参考等保/密评的"专家委+工作组"模式 |
| 多方利益相关者参与 | 引入高校/厂商/用户单位参与标准制定 |
| DARS 注册发现体系 | 对标国家政务信息系统登记备案制度 |
| 协作站点透明化 | 标准制定过程公开（草案征求意见机制） |

---

## 六、术语表

| 缩写 | 全称 | 含义 |
|------|------|------|
| CM | Configuration Management | 配置管理 |
| CI | Configuration Item | 配置项（受控对象） |
| ASRG | Architecture & Standards Review Group | 架构与标准审查组 |
| WG | Working Group | 工作组 |
| COI | Community of Interest | 利益共同体/兴趣社区 |
| DMWG | Data Management Working Group | 数据管理工作组 |
| DARS | DoD Architecture Registry System | DoD 架构注册系统 |
| MDR | Metadata Registry | 元数据注册库 |
| EA | Enterprise Architecture | 企业架构 |
| CDM | Conceptual Data Model | 概念数据模型 |
| LDM | Logical Data Model | 逻辑数据模型 |
| PES | Presentation Exchange Specification | 表示交换规范 |
| FAC | ? | （图中顶部节点，可能为 Federal Advisory Committee） |
| TBS | To Be Specified | 待确定 |

---

*分析完成: 2026-04-18 · 基于 DoDAF v2.02 PDF pp.261-262*
