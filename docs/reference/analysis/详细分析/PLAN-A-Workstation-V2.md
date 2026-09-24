# 方向 A：DoDAF 架构师工作台（工具化）规划方案 V2

> **日期**: 2026-04-19
> **状态**: 📋 待评审
> **版本**: V2 — 从"静态文档集"升级为 **SKILL + 工程生命周期体系**
> **前置**: DoDAF 标准研究阶段已完成（18类图+52视图+127关系+DIV全链条）
> **修订说明**: V1→V2 新增两大架构决策：① 形式化为 SKILL+Agent 三层架构；② 每次使用定义为完整的工程生命周期（启动→研究→编制→验证→归档）

---

## 一、定位与目标

### 核心问题
当前知识库是"读的"——架构师要自己翻 48 份报告 + 关系矩阵 + DIV 链条才能拼出答案。我们把它变成"用的"——**一个可执行的工程体系**，每次项目启动时自动引导完成从需求到归档的全流程。

### 目标用户画像
| 维度 | 描述 |
|------|------|
| 谁 | 安全架构师（雷及同行） |
| 在哪 | 做等保三级/国密合规/政务数据安全项目时 |
| 做什么 | 用 DoDAF 方法论产出架构交付物 |
| 痛点 | 不知道该画哪些视图 / 每个视图怎么填 / 生成后怎么验证 / 产出怎么管理 |

### 一句话定义
> **DoDAF 架构师工作台 = 一个 SKILL（工作流引擎）+ 项目工程体系（生命周期管理）+ 四类工具资产（模板/路径/检查/决策）**
>
> 不是"参考书"，是**建筑队**。

---

## 二、形式化架构：三层递进模型

### 2.1 总体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    DoDAF 工作台架构                          │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│                                                             │
│   Layer 1: SKILL 封装（★ 标准入场形态 ★）                    │
│   ════════════════                                         │
│   ┌─────────────────────────────────────────────┐           │
│   │        doaf-workstation SKILL               │           │
│   │                                             │           │
│   │  SKILL.md:                                  │           │
│   │    ├── 触发词: "DoDAF架构"/"视图生成"/...    │           │
│   │    ├── SOP: Phase0~4 完整工作流              │           │
│   │    ├── Input/Output Contract                │           │
│   │    └── 错误处理协议                         │           │
│   │                                             │           │
│   │  scripts/ (可选自动化):                     │           │
│   │    ├── query-template.py                   │           │
│   │    ├── check-consistency.py                │           │
│   │    └── init-project.py                    │           │
│   │                                             │           │
│   │  references/: → 现有知识库的软链接/引用      │           │
│   └──────────────────┬─────────────────────────┘           │
│                      │                                      │
│   Layer 2: 单 Agent 执行（默认运行模式）                     │
│   ═══════════════════════                                 │
│   ┌──────────────────▼─────────────────────────┐           │
│   │         WorkBuddy 主 Agent                  │           │
│   │         (加载 SKILL 后执行)                 │           │
│   │                                             │           │
│   │  接收你的自然语言需求                        │           │
│   │       ↓                                    │           │
│   │  按 SOP 步骤引导你:                         │           │
│   │  选视图集 → 创建工程 → 研究 → 编制 → 验证   │           │
│   │       ↓                                    │           │
│   │  产出归档到 projects/                       │           │
│   └─────────────────────────────────────────────┘           │
│                                                             │
│   Layer 3: Team Agent 并行（大型 Max 级项目按需启用）        │
│   ═════════════════════════════════                      │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│   │Orchestr.│  │ViewSet  │  │PathNav  │  │Validator│     │
│   │ 调度员   │  │选择器   │  │导航引擎 │  │验证引擎  │     │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘     │
│        └────────────┴────────────┴────────────┘           │
│                        │                                   │
│              并行推进 ≥20 个视图的生成与验证                 │
│                                                             │
│  ═══════════════════════════════════════════════════════    │
│            底层资产（四类工具，SKILL 和 Agent 共享）          │
│  ═══════════════════════════════════════════════════════    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │模块A模板库│ │模块B路径  │ │模块C检查  │ │模块D决策  │      │
│  │ 52+4     │ │ 4+1      │ │ R~G 18项 │ │ 3项      │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 为什么必须是 SKILL？（vs 纯 Markdown 文档集）

| 维度 | V1 纯文档集 | V2 SKILL 封装 |
|------|-----------|--------------|
| **触发方式** | 你自己去打开 INDEX.md | 自然语言："帮我做等保三级的 CV-1" |
| **上下文注入** | AI 每次都要重新读文件，可能遗漏 | SKILL.md 自动完整加载到 system prompt |
| **工作流强制执行** | 靠自觉，容易跳过检查步骤 | SOP 步骤硬编码在 SKILL.md 中，AI 必须顺序执行 |
| **参数传递** | 手动复制字段值 | 步骤间自动传递（视图清单→模板选择→字段预填） |
| **错误恢复** | 没有 — 出错了你自己查 | SKILL 定义了每步的异常处理和回退策略 |
| **跨会话一致性** | 取决于你是否记得上次的约定 | SKILL 是持久的，每次加载都相同 |
| **可扩展性** | 改文件即可 | 可挂载脚本（scripts/）实现部分自动化 |

### 2.3 三层何时使用？

| 条件 | 推荐模式 | 说明 |
|------|---------|------|
| 日常单视图 / 小型 Min/Avg 集（≤15 视图） | **Layer 1 + 2** | SKILL 加载，主 Agent 引导完成 |
| 中型 Avg+/Max 集（16~35 视图） | **Layer 1 + 2** + 脚本辅助 | 同上，但 consistency check 用脚本跑 |
| 大型 Max+ 集（≥36 视图）或并行赶工期 | **Layer 3** | 启动 Team Agent 并行 |

---

## 三、工程生命周期模型（每次使用 = 一次工程）

> **核心设计原则**：每次使用工作台不是"打开几个模板填一下"，而是一次**有始有终的工程项目**。
> 有明确的阶段划分、状态管理、产物归档和知识库索引建立。

### 3.1 完整生命周期流程

```
Phase 0: 项目启动（初始化）
╔════════════════════════════════════════════════════════════╗
║                                                              ║
║  输入: "我要做 XX项目的 DoDAF 架构"                           ║
║       ↓                                                      ║
║  ① arch-q 问题分类                                           ║
║     → 项目类型(新建/改造/合规)? 复杂度? 领域? 技术特征?      ║
║       ↓                                                      ║
║  ② 视图集推荐 (Min / Avg / Max)                               ║
║     → 产出本次工程的视图清单                                   ║
║       ↓                                                      ║
║  ③ OV-1 场景分解 (R1: CV-1:OV-1 = 1:N)                       ║
║     → 几个场景? 每个场景的范围?                               ║
║       ↓                                                      ║
║  ④ 创建工程目录 + 初始化 project.yaml                        ║
║                                                              ║
║  产出:                                                       ║
║    📁 projects/2026-XXXX-[项目简称]/                         ║
║    ├── project.yaml          ← 工程元数据（见下文 schema）    ║
║    └── .gitignore           ← 排除 drafts/临时文件          ║
╚════════════════════════════════════════════════════════════╝
                              ↓
Phase 1: 领域知识研究
╔════════════════════════════════════════════════════════════╗
║  在正式编制视图前，先搞清楚"这个领域是什么样子的"             ║
║                                                              ║
║  ① 业务背景调研                                             ║
║     → 干系人清单 / 组织结构 / 业务边界                       ║
║       ↓                                                      ║
║  ② 领域标准收集 → StdV-1 条目预填                            ║
║     → 等保等级? 国密算法行标? 行业规范? 数据安全法?         ║
║       ↓                                                      ║
║  ③ 现状盘点 (As-Is)                                          ║
║     → 已有系统清单 / 已有接口 / 已有数据资源                 ║
║       ↓                                                      ║
║  ④ 约束识别                                                 ║
║     → 合规约束 / 技术约束 / 组织约束 / 时间约束             ║
║                                                              ║
║  产出: research/ 目录下的调研笔记                             ║
║    📁 research/                                              ║
║    ├── stakeholders.md                                      ║
║    ├── standards-survey.md  ← StdV-1 预填稿                 ║
║    ├── as-is-inventory.md                                   ║
║    └── constraints.md                                       ║
╚════════════════════════════════════════════════════════════╝
                              ↓
Phase 2: 视图编制（迭代循环，按路径导航器走）
╔════════════════════════════════════════════════════════════╗
║  按 Path Navigator 的步骤顺序逐视图生成                      ║
║                                                              ║
║  对每个视图:                                                 ║
║    ① 从 templates/ 读取对应的输出模板                        ║
║    ② 查上游依赖 → 确认上游已就绪 / 取输入字段               ║
║    ③ 填充内容（AI 辅助 + 人工确认）                          ║
║    ④ 写入 drafts/[ID]-[name].md（带 frontmatter）           ║
║    ⑤ 标记下游消费者"等待此输入"                             ║
║                                                              ║
║  迭代直到所有视图清单中的视图都完成                           ║
║                                                              ║
║  产出: drafts/ 目录（可反复修改的草稿）                       ║
║    📁 drafts/                                                ║
║    ├── CV-1-Vision.md                                       ║
║    ├── OV-1-Scenario-A.md                                   ║
║    ├── OV-1-Scenario-B.md                                   ║
║    ├── ...                                                  ║
║    └── (每份都有标准 YAML frontmatter)                       ║
╚════════════════════════════════════════════════════════════╝
                              ↓
Phase 3: 一致性验证
╔════════════════════════════════════════════════════════════╗
║  所有视图草稿完成后，统一跑一遍质量门禁                       ║
║                                                              ║
║  ① 硬约束检查 (R1 ~ R10)                                    ║
║     → CV-1:OV-1=1:N? OV-5b→SV-4 全映射? StdV-1 法理终点?  ║
║       ↓                                                      ║
║  ② DIV 链条验证 (G1 ~ G8)                                   ║
║     → Info→Data 分界线? Type/Individual 物化? 端到端追溯?  ║
║       ↓                                                      ║
║  ③ 交叉引用完整性扫描                                        ║
║     → 上游是否全部就绪? 下游是否被正确通知?                  ║
║     → StdV-1 引用是否都已登记? AV-2 术语是否一致?           ║
║       ↓                                                      ║
║  ④ SV ↔ SvcV 双轨对称检查                                   ║
║     → 是否漏了 SvcV 入口/出口? 规则是否有服务独有扩展?      ║
║                                                              ║
║  产出: ConsistencyReport.md                                  ║
║    - ✅ 通过项                                               ║
║    - ⚠️ 警告项（缺可选输入，建议补全）                        ║
║    - ❌ 阻塞项（缺必须输入 / 硬约束违反 → 必须修复）          ║
║    - 📝 改进建议                                             ║
║                                                              ║
║  如有 ❌ → 回到 Phase 2 修复 → 重新验证                      ║
╚════════════════════════════════════════════════════════════╝
                              ↓
Phase 4: 正式归档
╔════════════════════════════════════════════════════════════╗
║  验证通过后，将草稿提升为正式产出并归档                       ║
║                                                              ║
║  ① drafts/ → outputs/ （复制为正式版，status 改为 final）    ║
║       ↓                                                      ║
║  ② 每份产出确认 YAML frontmatter 完整                        ║
║       ↓                                                      ║
║  ③ 建立 Obsidian 索引                                        ║
║     - wikilink 反向链接到知识库（模板/报告/关系矩阵/DIV链）   ║
║     - tag 标记: dodaf/[视点]/[优先级] / project/[项目名]     ║
║       ↓                                                      ║
║  ④ 更新 project.yaml（标记 COMPLETED + 产出清单 + 统计）     ║
║       ↓                                                      ║
║  ⑤ 更新 REFERENCE 索引（新增本项目条目）                      ║
║                                                              ║
║  最终目录结构:                                                ║
║  📁 projects/2026-XXXX-[项目简称]/                          ║
║  ├── project.yaml           ← 工程元数据（COMPLETED）        ║
║  ├── research/              ← 领域调研笔记（归档）           ║
║  ├── drafts/                ← 草稿留存（历史记录）            ║
║  ├── outputs/               ← ★ 正式产出 ★                  ║
║  │   ├── CV-1-Vision.md     ← 带 frontmatter + wikilink     ║
║  │   ├── OV-1-Scenario-A.md                                ║
║  │   ├── ...                                                ║
║  │   └── _INDEX.md           ← 本项目产出索引页              ║
║  └── ConsistencyReport.md    ← 一致性报告（归档）            ║
╚════════════════════════════════════════════════════════════╝
```

### 3.2 project.yaml Schema（工程元数据）

```yaml
# === DoDAF 工程元数据 v1 ===
project:
  id: "2026-gov-data-share"
  name: "某市政务数据共享交换平台 DoDAF 架构"
  domain: "政务数据安全"
  created_date: 2026-04-19
  status: "in-progress"  # planning / in-progress / review / completed / archived
  completed_date: null

# === arch-q 分类结果 ===
classification:
  project_type: "新建系统"        # 新建系统/现有系统改造/纯研究
  complexity: "高"                 # 低/中/高
  scale: "大型"                    # 小型/中型/大型
  technology: ["云原生", "微服务", "国密"]
  compliance: ["等保三级", "国密", "数据安全法"]
  recommended_viewset: "Max"       # Min / Avg / Max
  recommended_views: 38             # 具体数量

# === OV-1 场景分解 (R1: CV-1:OV-1 = 1:N) ===
scenarios:
  - id: "S1"
    name: "市民互联网办证"
    ov1_ref: "outputs/OV-1-Scenario-S1.md"
    scope:
      included: ["市民", "互联网区", "政务外网", "办事窗口"]
      excluded: ["涉密网", "内部办公网"]
    specific_constraints: ["GB/T 22239 二级", "实名认证"]
  - id: "S2"
    name: "公务员审批流转"
    ov1_ref: "outputs/OV-1-Scenario-S2.md"
    scope: {...}
  # ... 更多场景

# === 视图清单 ===
views:
  planned:
    - id: "CV-1"
      name: "愿景"
      priority: "P0"
      status: "completed"
      output_file: "outputs/CV-1-Vision.md"
      scenario: null  # CV-1 跨场景
    - id: "OV-1"
      name: "高层作战概念图"
      priority: "P0"
      status: "completed"
      scenarios:  # 多场景
        - scenario_id: "S1"
          output_file: "outputs/OV-1-Scenario-S1.md"
          status: "final"
        - scenario_id: "S2"
          output_file: "outputs/OV-1-Scenario-S2.md"
          status: "review"
    - id: "SV-4"
      name: "系统功能描述"
      priority: "P0"
      status: "in-progress"
      output_file: "drafts/SV-4-SystemFunctions.md"
      # ...
  completed_count: 12
  total_count: 38
  progress_pct: 31.6

# === 验证结果 ===
validation:
  last_check_date: null
  consistency_report: "ConsistencyReport.md"
  hard_constraints_pass: false
  blocking_issues: 0
  warnings: 3

# === 归档索引 ===
archive:
  obsidian_tags:
    - "project/gov-data-share"
    - "domain/gov-data-security"
    - "compliance/dengbao-level3"
    - "compliance/guomi"
  knowledge_base_links:
    - "[[REFERENCE#gov-data-share]]"
```

### 3.3 视图产出 YAML Frontmatter Schema

```yaml
---
# === DoDAF 视图产出属性 v1 ===
dodaf_view_id: CV-1
dodaf_view_name: "愿景"

# === 工程归属 ===
project: "2026-gov-data-share"
project_name: "某市政务数据共享交换平台架构"
created_date: 2026-04-19
modified_date: 2026-04-19
author: "雷"
status: final  # draft → review → final → archived

# === 表达等级 ===
expression_level: Avg  # Min / Avg / Max
scenario: null  # 跨场景视图为 null；场景相关视图填写场景 ID

# === 一致性追踪 ===
upstream_deps:
  - ref: "AV-1"
    status: "satisfied"
    note: "AV-1 概览已完成"
downstream_consumers:
  - ref: "CV-2"
    status: "pending"
    note: "等待 CV-1 能力范围定义"
  - ref: "OV-1"
    status: "pending"
    note: "R1: 1个CV-1 → N个OV-1，需3个场景"

# === 硬约束验证快照 ===
constraint_checks:
  R1_cv1_ov1_1n:
    result: "pass"
    note: "CV-1 映射到 3 个 OV-1 场景 (S1/S2/S3)"

# === 知识库反链（自动生成，手动维护）===
template_ref: "[[templates/P0/CV-1-Vision-OT]]"
view_report_ref: "[[视图全集/P0/CV-1-Vision]]"
relation_ref: "[[VIEW-RELATIONS-FULL-MAP#section-cv-1]]"
div_chain_ref: "[[VIEW-DIV-CHAIN#CV-1]]"
mcp_definition: "get_view_definition('CV-1')"
mcp_template: "get_output_template('CV-1')"

# === Obsidian 索引 ===
tags:
  - dodaf/cv
  - dodaf/p0
  - project/gov-data-share
  - expression/avg
---
```

---

## 四、四类工具资产（SKILL / Agent 共享底层）

### 模块 A：视图模板库（View Template Library）

#### A1. 核心视图输出模板 × 52

**现状**: 每份视图报告是"参考阅读型"（描述这个视图是什么），不是"操作输出型"（给你一个框架让你填内容）。

**目标**: 为每个视图产出一个 **`[ID]-OutputTemplate.md`**，结构统一为：

```markdown
# [视图ID] [中文名] 输出模板

> 视图元信息: 视点 | 优先级(P0/P1/P2) | 表达等级(Min/Avg/Max) | 上游依赖 | 下游消费者
> 对应 MCP: get_view_definition / get_output_template

---
## 1. 本视图目的（一句话）
[来自视图报告的核心定义]

## 2. 必填字段表
| # | 字段名 | 类型 | 是否必填 | 示例/提示 | 数据来源指引 |
|---|--------|------|---------|----------|------------|
| 1 | ... | text/select/table/... | ⭐ | ... | 来自哪个上游视图 |

## 3. 固定结构骨架（Mermaid/UML）
[该视图的标准图形表示法]

## 4. 输入检查清单
- [ ] 上游视图 X 已完成 → 取 Y 字段作为输入
- [ ] AV-2 中已定义术语: ...
- [ ] StdV-1 中已引用标准: ...

## 5. 输出质量门禁
- [ ] 字段完整度 ≥ X%
- [ ] 与上游视图的一致性: ...
- [ ] 下游消费者就绪检查: ...

## 6. 参考
- 完整视图报告: `[[P0/P1/P2-xxx]]`
- DM2 映射: `[[VIEW-DIV-CHAIN#section]]`
- 关系矩阵: `[[VIEW-RELATIONS-FULL-MAP#section]]`
```

**存放位置**: `详细分析/视图全集/templates/` （与现有报告分离）

#### A2. 场景包（Scenario Packs）

针对常见场景提供**预选视图集 + 预填示例**：

| 场景包名称 | 适用场景 | 包含视图数 | 预置内容 |
|-----------|---------|-----------|---------|
| `pack-min-security` | 小型安全合规（等保测评） | ~12 | OV-1/CV-1/SV-1/DIV-1/StdV-1 等，带安全领域示例 |
| `pack-gov-data-share` | 政务数据共享交换平台 | ~20 | 全 CV/OV/DIV/SV 核心 + PV 时间线 |
| `pack-soc-design` | 安全运营中心(SOC)设计 | ~18 | SV-10规则链 + DIV-3物理模型 + StdV-1安全标准 |
| `pack-system-evolution` | 系统演进规划 | ~15 | SV-8/9 + PV-2 + StdV-2 + CV-3/5 |

每个场景包 = 视图清单 + 各视图的关键字段预填值 + Mermaid 示例图。

---

### 模块 B：路径导航器（Path Navigator）

#### B1. 四路径交互式导航卡

将 VIEW-RELATIONS-FULL-MAP §一 的 4 条路径转化为**每步操作的导航卡**：

以 **路径① 主追溯链**为例：

```
╔════════════════════════════════════════════════════════════╗
║  路径①：主追溯链 — 从能力到系统                              ║
║  用途："证明某个能力有系统支撑"                               ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Step 0 → CV-1 愿景                                       ║
║     ✏️ 写一句话: 这个架构解决什么战略问题?                    ║
║     🔗 输出→ Step 1 (CV-2) + Step 1' (OV-1)               ║
║                                                            ║
║  Step 1 → CV-2 能力分类法                                  ║
║     ✏️ 列出能力树 (层级结构)                                ║
║     🔗 输入← CV-1 的愿景范围                               ║
║     🔗 输出→ Step 2 (CV-6) + Step 2' (OV-5b)              ║
║                                                            ║
║  Step 1' → ★OV-1 场景 (并行!) ★                            ║
║     ✏️ 画概念图: 干系人/节点/连接                            ║
║     ⚠️  R1约束: 1个CV-1 → N个OV-1                          ║
║     🔗 输出→ 所有后续步骤的场景上下文                        ║
║                                                            ║
║  Step 2 → OV-5b 作战活动模型                               ║
║     ✏️ 分解活动 (在OV-1场景内)                             ║
║     ✏️ 分配执行者 (OV-4组织)                               ║
║     🔗 输入← CV-2(能力) + CV-6(映射目标) + OV-1(场景)      ║
║     🔗 输出→ Step 3a(SV-4) + Step 3b(SvcV-4) ← R3核心跳转  ║
║                                                            ║
║  Step 3a → SV-4 系统功能 (系统轨)                          ║
║     ✏️ 映射: 每个活动 → 哪些系统功能                       ║
║     ⚠️  R3约束: OV-5b→SV-4 是最关键的实现映射              ║
║     🔗 输出→ Step 4 (SV-5a 反向追溯验证)                    ║
║                                                            ║
║  Step 3b → SvcV-4 服务功能 (服务轨)                        ║
║     ✏️ 映射: 每个活动 → 哪些服务操作                      ║
║     💡 与SV-4的区别: 松耦合/可跨系统/SLA策略                ║
║     🔗 输出→ Step 4' (SvcV-5 反向追溯)                     ║
║                                                            ║
║  Step 4 → SV-5a / SvcV-5 追溯验证                         ║
║     ✔️ 检查: 每个活动都有≥1个系统/服务支撑?                 ║
║     ✔️ 检查: 有无孤立能力(有CV-2但无OV-5b)?                ║
║     ✔️ 检查: 有无孤立活动(有OV-5b但无SV/SvcV)?            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

另外 3 条路径同理制作。

#### B2. "我该走哪条路？"快速路由表

| 你的问题             | 推荐路径              | 额外建议                 |
| ---------------- | ----------------- | -------------------- |
| "领导要我证明系统满足业务需求" | ① 主追溯链            | 同时跑一遍 ③ 约束传播         |
| "我要设计数据库/接口格式"   | ② 数据细化链           | 先看 VIEW-DIV-CHAIN    |
| "我要做合规性论证（如等保）"  | ③ 约束传播链           | 结合 StdV-1 标准配置模板     |
| "我要规划明年IT建设路线图"  | ④ 演进闭环链           | PV-2 是核心             |
| "我不知道该画哪些视图"     | → 先用 **模块D: 决策树** | arch-q 问题分类法         |
| "改了一个视图怕影响别的"    | → 查 **关系矩阵下游**    | VIEW-RELATIONS §五热力图 |

---

### 模块 C：一致性检查清单（Consistency Checklist）

#### C1. 硬约束检查器（R1~R10）

把 VIEW-RELATIONS §三 的 10 条约束变成**逐项打勾表**：

```markdown
# DoDAF 架构一致性检查清单 v1

## Phase 1: 生成前（防错于未然）
- [ ] R1: CV-1:OV-1 = 1:N — 几个愿景对应几个场景？是否 1:N？
- [ ] R2: AV-1:OV-1 = 1:N — 几份概览对应几张概念图？
- [ ] R6: OV-2 Needline ≠ SV-1 RF — 有没有错误地 1:1 对应？（应为 M:N）

## Phase 2: 生成中（过程校验）
- [ ] R3: OV-5b→SV-4 — 每个作战活动都映射到≥1个系统功能？
- [ ] R4: OV-6a→SV-10a→SvcV-10a — 规则的三层 What→How 都有？
- [ ] R7: SvcV 全能桥 — 每个 OV 视图都有 SvcV 入口/出口？

## Phase 3: 生成后（交叉验证）
- [ ] R5: StdV 法理终点 — 所有技术视图引用的标准都在 StdV-1 里？
- [ ] R8: DIV 三层单向 — 没有 DIV-3→DIV-2 或 DIV-2→DIV-1 的逆向？
- [ ] R9: PV-2 时间中枢 — 能力阶段/系统演进/标准预测都对齐到时间线了？
- [ ] R10: SV-4↔SvcV-4 双路径 — OV-5b 同时驱动了两条实现路？还是漏了一条？

## Phase 4: DIV 链条专项（G1~G8）
- [ ] G1: 端到端追溯 — 任取一个数据元素，能否从 OV 追踪到 DIV-3？
- [ ] G2: DM2→DIV 映射 — Information/Data/System 分别落在哪一层？
- [ ] G5: Info→Data 分界线 — DIV-1 只有语义信息，DIV-2 才引入物理数据？
- [ ] G6: Type/Individual 物化 — Type 概念在 C/L 层，Individual 在 L/P 层？
```

#### C2. 交叉引用完整性扫描

基于 127 条关系的扫描逻辑（可由脚本辅助或人工执行）：

```
对每个已生成的视图 X:
  1. 从 VIEW-RELATIONS 取 X 的所有上游 → 检查这些上游视图是否都已生成
  2. 从 VIEW-RELATIONS 取 X 的所有下游 → 标记这些下游视图"等待X输入"
  3. 从 VIEW-DIV-CHAIN 取 X 涉及的 DM2 概念 → 检查 DIV-1/2/3 对应实体是否存在
  4. 从 StdV-1 引用列表 → 检查 X 引用的每个标准是否已在 StdV-1 中登记
```

产出一份 **`ConsistencyReport.md`**：✅ 通过 / ⚠️ 警告 / ❌ 阻塞 / 📋 建议

---

### 模块 D：场景选择决策树（Decision Tree）

#### D1. arch-q 集成版视图集推荐器

```
开始
  │
  ▼
你的项目类型是什么？
  │
  ├── 新建系统（绿地）
  │    │
  │    ├── 复杂度高（多部门/多系统）
  │    │    └── → Max 集 (~35-40 视图)
  │    │         推荐: CV全量 + OV全量 + SV+SvcV双轨 + DIV三层 + PV闭环
  │    │
  │    └── 复杂度低（单部门/单系统）
  │         └── → Avg 集 (~20-25 视图)
  │              推荐: CV核心 + OV-1/2/4/5 + SV单轨 + DIV-1/2 + StdV-1
  │
  ├── 现有系统改造（棕地）
  │    │
  │    ├── 仅加安全合规层
  │    │    └── → Min 合规集 (~12-15 视图)
  │    │         推荐: OV-1 + SV-1 + DIV-3 + StdV-1 + OV-6a/SV-10a
  │    │
  │    └── 全面重构
  │         └── → Avg+ 演进集 (~25-30 视图)
  │              含 SV-8/9 演进 + PV-2 时间线
  │
  └── 纯研究/对标分析
       └── → 精简集 (~8-10 视图)
            推荐: CV-1/2 + OV-1 + StdV-1 + AV-1/2
```

#### D2. OV-1 多场景分解指南（R1 实操方法）

基于 R1 (`CV-1:OV-1 = 1:N`) 的实操方法：

```markdown
# OV-1 场景分解工作坊

## 输入
- CV-1 愿景陈述 (1份)
- 干系人名单
- 业务边界描述

## 步骤

### Step 1: 识别场景维度
常用维度:
  - 📍 地理位置（市本级 / 区县 / 街道 / 村居）
  - 👥 用户角色（市民 / 公务员 / 管理员 / 审计方）
  - 🔐 安全域（互联网区 / 政务外网 / 政务内网 / 涉密网）
  - ⏱️ 时间阶段（现状 As-Is / 近期 To-Be v1 / 远期 To-Be v2）

### Step 2: 笛卡尔积筛选
列出维度组合 → 排除不合理组合 → 得到 N 个有效场景
⚠️ 每个场景 = 1 个独立的 OV-1

### Step 3: 每个场景确定范围
对每个 OV-1 填写:
  - 场景名称 (如 "市民互联网办证")
  - 边界内: (涉及哪些组织/系统/数据)
  - 边界外: (明确排除什么)
  - 特殊约束: (本场景独有的规则/标准)

### Step 4: 场景间差异矩阵
| 维度 | 场景A | 场景B | 场景C |
|------|-------|-------|-------|
| 用户角色 | 市民 | 公务员 | 审计方 |
| 核心能力 | 在线申报 | 审批流转 | 监督审计 |
| 关键标准 | GB/T 22239 二级 | GB/T 22239 三级 | 审计署规范 |

## 产出
N 份 OV-1 + 1 份差异矩阵 → 后续所有 OV/SV/SvcV 视图按场景分别填充
```

---

## 五、目录结构与文件总览

```
文学/领域知识/DM2/
│
├── 详细分析/
│   ├── 视图全集/                          ← (已有, 不动)
│   │   ├── P0/ P1/ P2/                    ← 48份视图报告 (只读参考)
│   │   │
│   │   ├── templates/                     ← 【新建】模块A: 视图模板库
│   │   │   ├── README.md                  ← 模板使用说明
│   │   │   ├── P0/                        ← 17个P0视图输出模板
│   │   │   │   ├── CV-1-Vision-OT.md
│   │   │   │   ├── OV-1-HighLevelOpConceptGraphic-OT.md
│   │   │   │   └── ...
│   │   │   ├── P1/                        ← 22个P1视图模板
│   │   │   └── P2/                        ← 8个P2视图模板
│   │   │
│   │   └── packs/                         ← 【新建】模块A2: 场景包
│   │       ├── pack-min-security/
│   │       ├── pack-gov-data-share/
│   │       ├── pack-soc-design/
│   │       └── pack-system-evolution/
│   │
│   ├── WORKSTATION/                       ← 【新建】工作台主入口
│   │   ├── AGENT.md                       ← 工作台协议(AI读取)
│   │   ├── INDEX.md                       ← 工作台主页(人类阅读)
│   │   │
│   │   ├── paths/                         ← 【新建】模块B: 路径导航器
│   │   │   ├── path-01-main-trace.md
│   │   │   ├── path-02-data-refine.md
│   │   │   ├── path-03-constraint-prop.md
│   │   │   ├── path-04-evolution-loop.md
│   │   │   └── route-quick-decision.md
│   │   │
│   │   ├── checklists/                    ← 【新建】模块C: 检查清单
│   │   │   ├── cl-hard-constraints-R1to10.md
│   │   │   ├── cl-div-chain-G1toG8.md
│   │   │   ├── cl-cross-ref-scanner.md
│   │   │   └── ConsistencyReport-template.md
│   │   │
│   │   └── decisions/                     ← 【新建】模块D: 决策树
│   │       ├── dt-viewset-selector.md
│   │       ├── dt-ov1-scenario-workshop.md
│   │       └── dt-sv-vs-svcV-chooser.md
│   │
│   ├── VIEW-RELATIONS-FULL-MAP.md         ← (已有 V2.0, 只读)
│   ├── VIEW-DIV-CHAIN.md                  ← (已有, 只读)
│   └── DM2-*详细分析.md ×18                ← (已有, 只读参考)
│
├── projects/                               ← 【新建】工程目录（每次使用创建一个子目录）
│   ├── .TEMPLATE/                          ← 工程目录模板（复制即用）
│   │   ├── project.yaml.template
│   │   └── .gitignore
│   │
│   ├── 2026-XXXX-project-alpha/            ← 示例: 第一个实际项目
│   │   ├── project.yaml
│   │   ├── research/
│   │   ├── drafts/
│   │   ├── outputs/
│   │   └── ConsistencyReport.md
│   │
│   └── 2026-YYYY-project-beta/             ← 第二个项目...
│
├── skills/                                 ← 【新建】SKILL 定义（WorkBuddy 层面）
│   └── doaf-workstation/
│       ├── SKILL.md                        ← ★ 核心：工作流 SOP + I/O 协议
│       ├── scripts/                        ← 自动化辅助脚本（可选）
│       │   ├── init-project.py
│       │   ├── query-template.py
│       │   └── check-consistency.py
│       └── references/                     → 软链接到 ../详细分析/
│
├── REFERENCE                               ← (已有, 更新索引)
│   └── (新增 projects/ 下的索引条目)
│
└── PLAN-A-Workstation-V2.md                ← 本文件
```

---

## 六、SKILL.md 核心结构设计（预览）

以下是 SKILL 的骨架设计，实际编写时会展开每个 phase 的详细指令：

```markdown
---
name: doaf-workstation
description: >
  DoDAF 架构图师工作台。用于基于 DoDAF 2.0 方法论产出企业架构交付物。
  支持：视图集推荐(arch-q)、视图模板填充、路径导航(4条核心路径)、
  一致性检查(R1~R10硬约束+G1~G8 DIV链条)、工程全生命周期管理。
  触发词：DoDAF架构、视图生成、架构追溯、合规映射、DoDAF工程、架构交付物
version: "1.0.0"
---

# DoDAF 架构师工作台 — SKILL 协议

## 触发条件
当用户提出以下任一意图时加载本 SKILL：
- 要用 DoDAF 方法论做架构设计/分析
- 需要生成/审查 DoDAF 视图
- 要做架构追溯（能力→活动→系统）
- 要做合规映射（等保/国密→DoDAF视图证明）
- 明确提到"DoDAF"、"架构工作台"、"视图模板"

## 工作流 SOP

### Phase 0: 项目初始化
1. 收集基本信息 → 执行 arch-q 分类 → 推荐 Min/Avg/Max 视图集
2. 执行 OV-1 场景分解 (R1: 1:N)
3. 调用 init-project.py 或手动创建 projects/ 子目录 + project.yaml
4. 向用户展示工程概况并确认

### Phase 1: 领域研究
1. 引导用户完成业务背景调研
2. 收集领域标准 → 预填 StdV-1
3. 记录约束条件
4. 产出 research/ 笔记

### Phase 2: 视图编制（核心循环）
对视图清单中的每个视图（按路径导航器的拓扑序）：
1. 读取对应 template
2. 检查 upstream_deps 就绪状态
3. 从上游取出输入字段值
4. 引导用户/AI 填充内容
5. 写入 drafts/ (带完整 frontmatter)
6. 标记 downstream_consumers

### Phase 3: 一致性验证
1. 跑 R1~R10 硬约束检查
2. 跑 G1~G8 DIV 链条验证
3. 跑交叉引用完整性扫描
4. 产出 ConsistencyReport.md
5. 如有阻塞项 → 回到 Phase 2 修复

### Phase 4: 归档
1. drafts/ → outputs/ (status: final)
2. 确认 frontmatter 完整
3. 建立 Obsidian wikilink 和 tags
4. 更新 project.yaml (status: COMPLETED)
5. 更新 REFERENCE 索引

## Input/Output Contract

### 输入（用户提供）
- 项目基本描述（一句话~几段话均可）
- 领域/行业/合规要求
- 现有资料（如有）

### 输出（工作台承诺产出）
- projects/[id]/ 完整工程目录
- outputs/ 下 N 份正式视图（带属性和反链）
- ConsistencyReport.md 验证报告
- project.yaml 工程元数据

## 错误处理协议
- 上游未就绪 → 暂停当前视图，先提示完成上游
- 硬约束违反 → 阻塞归档，给出具体修复建议
- 用户中途取消 → 保存当前进度到 project.yaml (status: in-progress)，下次可断点续传
- 模板缺失 → 使用 MCP get_output_template 动态获取兜底
```

---

## 七、实施计划（分三期）

### 第一期：SKILL + MVP 工程闭环

**目标**: 能用 SKILL 触发 → 走通一个小型项目的完整生命周期

| 任务 | 产物 | 优先级 | 说明 |
|------|------|--------|------|
| **SKILL.md 编写** | `skills/doaf-workstation/SKILL.md` | 🔴 最高 | SOP + I/O Contract + 错误处理 |
| **工程目录模板** | `projects/.TEMPLATE/` + init 脚本 | 🔴 最高 | project.yaml.template + .gitignore |
| **17 个 P0 模板** | `templates/P0/*.md` × 17 | 🔴 最高 | 最常用视图的"答题纸" |
| **路径① 导航卡** | `paths/path-01-main-trace.md` | 🔴 最高 | 最常走的路的完整导航 |
| **R1~R5 检查清单** | `checklists/cl-hard-R1to5.md` | 🟡 高 | 前5条最常触发的硬约束 |
| **决策树 V1** | `decisions/dt-viewset-selector.md` | 🟡 高 | Min/Avg/Max 推荐 |
| **仪表盘入口** | `WORKSTATION/INDEX.md` + `AGENT.md` | 🔴 最高 | 串起一切 |

**一期验收标准**: 
- 说一句"帮我做一个等保三级的小型安全合规 DoDAF 架构"→ SKILL 自动触发 → 走通 Phase 0~4 → 产出完整工程目录

### 第二期：全覆盖 + 场景包

| 任务 | 产物 | 说明 |
|------|------|------|
| A1-full | P1(22)+P2(8) 视图模板补全 | 52 个视图模板全集 |
| A2 | 4 个场景包 | 每个含预填示例 |
| B1-full | 路径②③④ 导航卡 | 4 条路径齐全 |
| C1-full | R6~R10 + G1~G8 补充 | 全量 18 项检查 |
| D2 | OV-1 场景分解工作坊 + SV/SvcV 选择器 | 深层决策支持 |
| scripts | check-consistency.py 脚本 | 半自动一致性扫描 |

### 第三期：智能化增强

| 任务 | 产物 | 说明 |
|------|------|------|
| C2-auto | 交叉引用自动扫描 | 输入视图清单 → 自动生成报告 |
| D3-deep | arch-q 深度集成 | 自然语言提问 → 自动路由 |
| A3-obsidian | Dataview/Templates 集成 | Obsidian 内一键创建 |
| L3-team | Team Agent 协作模式 | ≥20 视图项目并行推进 |

---

## 八、成功标准

| 指标 | 一期后 | 二期后 | 三期后 |
|------|-------|-------|-------|
| **SKILL 可用** | ✅ 可触发、可走通完整闭环 | ✅ | ✅ |
| 视图模板覆盖率 | 17/52 (33%) | 52/52 (100%) | 100% + 场景包 |
| 路径导航覆盖 | 1/4 | 4/4 | 4/4 + 智能路由 |
| 硬约束可检查项 | 5/10 | 10/10 + G1~G8 (18项) | 18项 + 自动扫描 |
| **工程闭环** | ✅ 1个项目走通 Phase 0~4 | ✅ 多项目 | ✅ 断点续传 |
| **归档质量** | ✅ frontmatter + wikilink | ✅ | ✅ Dataview 可查询 |
| 从"不知道画什么"到"开填"的时间 | < 5 分钟 | < 3 分钟 | < 1 分钟（自然语言） |
| 新手独立完成的门槛 | 需读少量文档 | 基本不需额外阅读 | 对话式引导完成 |

---

## 九、风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| SKILL SOP 过于复杂导致 AI 执行偏离 | 中 | 高 | 一期只做核心路径，快速验证迭代；每个 Phase 有明确的 gate 检查 |
| 模板与实际项目需求差距大 | 中 | 高 | 一期只做 P0 + 1个场景包，用真实案例验证 |
| 工程目录结构后期调整成本 | 中 | 低 | projects/ 独立于知识库目录，结构调整不影响已有资产 |
| 过度工程化（做了用不上的东西） | 中 | 高 | 严格"先有真实使用场景再建"原则，不预建抽象能力 |
| frontmatter schema 后续演化不兼容 | 低 | 中 | schema 版本号化，旧工程保持原 schema 不强制迁移 |
| SKILL 与 WorkBuddy 平台能力耦合变化 | 低 | 中 | SKILL 核心逻辑在 markdown，脚本为可选增强，降级时可纯手工执行 |

---

*方案完毕。请审阅。*
