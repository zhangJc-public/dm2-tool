# dm2 propose 工作流 & 增强视图推荐 — 设计方案

> 版本: v0.1（讨论稿）
> 范围: 涵盖 `/dm2:propose` 工作流设计和视图推荐引擎增强

---

## 1. 问题定义

### 1.1 缺少 propose 环节

当前 dm2 工作流跳跃：

```
用户说"分析这个系统"
  → /dm2:new 直接跑 cynefin + 6W + 推荐 + 生成（太多）
  → /dm2:ff 一步生成全部视图（更重）
  → /dm2:continue 推进下一个（OK）
```

openspec 的三阶段（new → propose → apply）在 dm2 域里对应：

| openspec | dm2 映射 | 当前状态 |
|----------|---------|---------|
| `/opsx:new` | 创建 change 目录 + 初始状态 | `/dm2:new` 做得太多 |
| `/opsx:propose` | 做分析 + 生成规划产物 | **缺失** |
| `/opsx:apply` | 逐个生成视图 | `/dm2:continue` 承担 |
| `/opsx:ff` | 一键生成全部（跳过交互） | 已有（合理） |

### 1.2 视图推荐过于片面

当前 `ViewRecommender` 的评分公式：

```python
relevance = 0.5 (base) + 0.3 if 6W matches + 0.2 if concept matches
```

三维度评价：

| 问题 | 表现 | 根因 |
|------|------|------|
| **片面** | 推荐结果只依赖 6W 一个因子 | ViewRecommender 只有 2 个加性因子 |
| **重复推荐** | 已生成的视图下次还推 | 不从 ViewManager 读状态 |
| **无视依赖** | 推 SV-4 但不先推 OV-5a | 不用 ArtifactGraph 检查前置 |
| **无视合规** | 等保场景推的和普通场景一样 | 0 合规因子 |
| **无视角色** | 架构师和合规审计员得到相同推荐 | 0 用户角色因子 |

---

## 2. 设计方案：/dm2:propose

### 2.1 定位

```
/dm2:propose "某网络安全态势感知系统"
    ↓
做分析 + 出文档
    ↓
等待 /dm2:continue 逐个实施 或 /dm2:ff 一键全跑
```

### 2.2 工作流步骤

```
Step 1: 接收输入
  用户提供一个系统描述（必选）和可选参数（合规要求、利益相关方等）

Step 2: dm2 change new <name>
  创建变更目录和工作区

Step 3: dm2 cynefin --json
  复杂度评估 → 确定视图数量级

Step 4: dm2 analyze --json（增强版）
  多因子分析（详见第 3 节）→ 得到分层推荐方案

Step 5: 生成规划产物
  ├── proposal.md — 变更动机和范围（含用户原始描述、对话内容）
  ├── design.md — 技术方案（含分析推理过程）
  └── tasks.md — 实现任务清单（按依赖排序的视图生成任务）

Step 6: 展示结果
  分析摘要 + 分层推荐 + "运行 /dm2:continue 开始"
```

### 2.3 产物结构

```
dm2-changes/<name>/
  ├── proposal.md        ← 为什么、范围、用户提供的资料（纯人类可读）
  ├── design.md          ← 分析推理、决策记录、依赖图（人和 AI 可读）
  └── tasks.md           ← 可执行任务清单（被 /dm2:continue 消费）

.dm2/
  ├── view-state.yaml    ← 已有（ViewManager）
  └── analysis-state.yaml ← 已有（cynefin + 6W 结果）
```

### 2.4 和现有工作流的关系

```
/dm2:new (简化后)
  → 仅创建 change 目录，提示 /dm2:propose 或 /dm2:continue

/dm2:propose (新增)
  → 做完整分析 + 生成规划产物
  → 产物可继续由 continue 实施，也可由 ff 跳过

/dm2:continue (已有)
  → 读 tasks.md 取第一个未完成的任务并执行
  → 不改

/dm2:ff (已有)
  → 跳过交互，按 tasks 顺序依次执行
  → 不改
```

---

## 3. 设计方案：基于 DM2 数据组的视图推荐

### 3.1 核心认识

> **DM2 的 17 个数据组本身就是视图推荐的自然框架。**

当前 `ViewRecommender` 用 6W 和一个硬编码的 `CONCEPT_TO_VIEWS` 来映射。但 DM2 元模型定义了 17 个完整的数据组，每个组自带 relationships 和相应的 DoDAF 视图：

| # | 数据组 | 视点 | 驱动视图 | 用户描述中对应的话题 |
|---|--------|------|---------|-------------------|
| 01 | Performer | WHO | OV-4, PV-1, 所有视图的基础 | "谁来做"、"哪个部门负责" |
| 02 | Activity | HOW/DO | OV-5a/b | "流程是什么"、"步骤有哪些" |
| 03 | Capability | WHY | CV-1 ~ CV-7 | "需要什么能力"、"要达到什么目标" |
| 04 | Resource | WHAT flows | OV-2/3, SV-2/6, DIV-1/2/3 | "数据怎么流转"、"交换什么信息" |
| 05 | Guidance | WHAT rules (原文) | StdV-1, OV-6a | "要遵循什么标准"、"等保要求" |
| 06 | Measure | HOW WELL | SV-7, SvcV-7 | "性能指标"、"SLA" |
| 07 | Location | WHERE | OV-1, OV-2 上下文 | "部署在哪"、"节点位置" |
| 08 | Services | WHAT (服务态) | SvcV-1 ~ SvcV-10 | "微服务"、"API 网关" |
| 09 | Project | WHEN / PAYS | PV-1 ~ PV-3 | "项目时间线"、"里程碑" |
| 10 | Rules | WHAT rules (可执行) | SV-10a, SvcV-10a | "加密规则"、"密码策略" |
| 11 | ResourceFlow | HOW connected | SV-4, DIV-2/3 | "功能间数据流"、"接口关系" |
| 14 | OrgStructure | HOW organized | OV-4 | "组织架构"、"矩阵管理" |
| 16 | InformationData | WHAT data means | DIV-1 ~ DIV-3 | "数据模型"、"信息架构" |
| 00/12/13/15 | Meta | 所有视图的基础架构 | 抽象层次、溯源、血缘 | — |

### 3.2 新推荐流程

```
用户描述文本
    │
    ▼
┌──────────────────────────────────────────────────┐
│ 1. 数据组激活检测（替代 6W 分类）                    │
│    输入: 描述文本                                   │
│    输出: {(data_group_id, activation_score), ...}    │
│    方法: 关键词匹配 + KnowledgeAPI 语义关联         │
│          每个数据组有对应的 keywords 和 patterns     │
│          如 Performer: "谁|角色|组织|团队|部门|..."   │
│          如 Rules: "密码|加密|合规|标准|等保|..."    │
│          得分 = 命中关键词数 / 组关键词总数           │
└──────────────────────┬───────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────┐
│ 2. 数据组 → 视图映射                               │
│    输入: 活跃数据组列表                              │
│    输出: {(view_id, group_score), ...}              │
│    规则: 每个数据组对应一组 DoDAF 视图              │
│          视图得分 = 激活的数据组中与该视图相关的      │
│          数据组的最高 activation_score              │
│          一个视图可能对应多个数据组（取 max）        │
└──────────────────────┬───────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────┐
│ 3. 修正因子（不改变推荐框架，仅调整优先级）           │
│    依赖就绪度: 前置视图未完成 → 降权                │
│    已完成过滤: generated/verified 视图不重复推荐     │
│    Phase 分层: score 0.7+ → P1, 0.5+ → P2, 其余 P3│
└──────────────────────┬───────────────────────────┘
                       ▼
              分层推荐方案 (Phase 1/2/3)
```

### 3.3 与 6W 的关系

6W 分析不再作为唯一维度，而是作为数据组激活检测的**子模块**：

| 6W 维度 | 对应的 DM2 数据组 |
|---------|-----------------|
| WHO | 01-Performer, 14-OrgStructure |
| HOW | 02-Activity |
| WHERE | 07-Location |
| WHEN | 09-Project |
| WHY | 03-Capability, 05-Guidance, 10-Rules |
| WHAT | 04-Resource, 08-Services, 16-InformationData |

也就是说，6W 仍然是文本分析的入口，但它输出的是**数据组激活向量**（一个 17 维的稀疏向量），而不是一个单一的主维度。

### 3.4 对比

| 方面 | 当前（6W） | 原方案（加权多因子） | 新方案（DM2 数据组） |
|------|-----------|-------------------|-------------------|
| 推荐维度 | 1（主 6W） | 6 个因子 | 17 个数据组 |
| 权重调参 | 无需显式调参 | 需要 6 个权重参数 | 数据组自动加权（激活度） |
| 合规感知 | 无 | 人工 YAML 映射 | DM2 Guidance + Rules 组自带 |
| 依赖感知 | 无 | 外部因子 | 修正因子（不下沉） |
| 扩展性 | 加新维度需改代码 | 加新因子需加权重 | 加新数据组 = 加新 lens |
| 与 DM2 一致 | 低 | 中 | 高（元模型驱动） |

---

## 4. 数据组激活检测

### 4.1 如何判断用户描述激活了哪些数据组

每个 DM2 数据组定义一组 keyword patterns，用于从用户描述中检测该组是否"活跃"：

```python
# 示例（每个数据组已定义 keywords 在 dm2-reference 中）
DATA_GROUP_KEYWORDS = {
    "01-Performer":     ["谁", "角色", "组织", "团队", "部门", "人", "performer",
                        "operator", "admin", "user", "系统管理员"],
    "02-Activity":      ["流程", "步骤", "活动", "操作", "过程", "activity",
                        "process", "workflow", "procedure"],
    "03-Capability":    ["能力", "目标", "愿景", "mission", "capability",
                        "战略", "roadmap"],
    "04-Resource":      ["数据", "资源", "信息", "接口", "resource", "data",
                        "information", "flow", "交换"],
    "05-Guidance":      ["标准", "规范", "指南", "guidance", "standard",
                        "框架", "policy", "策略"],
    "06-Measure":       ["性能", "度量", "指标", "SLA", "measure", "KPI",
                        "metric", "可用性", "吞吐"],
    "07-Location":      ["位置", "部署", "节点", "location", "site",
                        "地域", "数据中心", "region"],
    "08-Services":      ["服务", "API", "微服务", "service", "SOA",
                        "endpoint", "gateway"],
    "09-Project":       ["项目", "计划", "阶段", "里程碑", "project",
                        "timeline", "milestone", "phase"],
    "10-Rules":         ["规则", "约束", "密码", "加密", "合规", "等保",
                        "rule", "constraint", "NIST", "GDPR"],
    "11-ResourceFlow":  ["数据流", "资源流", "依赖", "resource flow",
                        "data flow", "dependencies", "交互"],
    "14-OrgStructure":  ["组织结构", "汇报关系", "矩阵", "org chart",
                        "organization structure", "reporting"],
    "16-InformationData": ["数据模型", "信息架构", "概念模型", "data model",
                          "information model", "逻辑模型", "物理模型"],
}
```

```
activation_score(group) = matched_keywords / total_keywords_in_group

# 示例：用户描述 "我们需要建设一个安全态势感知系统，包含探针、分析和展示。系统管理员通过大屏监控。按等保三级要求设计。"
# → Performer: 0.6  (命中"系统管理员")
# → Activity: 0.4   (命中"监控"、"分析")
# → Rules: 0.5      (命中"等保"、"要求")
# → Guidance: 0.3   (命中"要求")
# → Others: <0.2    (弱激活)
```

### 4.2 检测准确度的渐进增强

| 阶段 | 方法 | 效果 |
|------|------|------|
| Phase 1 | 关键词覆盖 | 够用。现有 `SixWAnalyzer` 的 regex 引擎可直接复用 |
| Phase 2 | 加权关键词（TF-IDF 风格） | 降低高频停用词干扰 |
| Phase 3 | 知识库增强（KnowledgeAPI） | 用 DM2 概念定义扩展同义词和关联词 |
| Future | 语义匹配 | 向量嵌入相似度（如需要） |

当前 `SixWAnalyzer` 的 regex 引擎可以直接复用并扩展——它已经按 6W 维度做了关键词分组，只需把维度扩展为 17 个数据组即可。

---

## 5. 组件关系图

```
用户输入
  │
  ▼
┌──────────────────────────────────────────────────────┐
│ /dm2:propose                                          │
│  ├── 1. DM2 Data Group Activator  → 17 组激活向量    │
│  │      复用 SixWAnalyzer 的 regex 引擎，扩展到 17 组  │
│  │                                                     │
│  ├── 2. CynefinAnalyzer         → 复杂度域             │
│  │                                                     │
│  ├── 3. ViewRecommender (v2)    → 数据组 → 视图映射    │
│  │      ├── 数据组→视图映射表（GroupToViews）          │
│  │      ├── 读 ArtifactGraph    → 依赖就绪度修正      │
│  │      ├── 读 ViewManager      → 已完成视图过滤      │
│  │      └── KnowledgeAPI        → 关键词扩展         │
│  │                                                     │
│  └── 4. 产物生成器             → proposal/design/tasks │
└──────────────────┬───────────────────────────────────┘
                   ▼
      分层推荐方案 (Phase 1/2/3) + 规划产物
                   │
                   ▼
      /dm2:continue 或 /dm2:ff
```

---

## 6. 实施建议

### 6.1 实施路径

| 阶段 | 内容 | 工作量 |
|------|------|--------|
| **Phase 1**（P0） | /dm2:propose 技能 + 简化 /dm2:new | 小 |
| **Phase 2**（P0） | 数据组激活检测 + GroupToViews 映射表 | 中 |
| **Phase 3**（P1） | 依赖就绪度修正 + 已完成视图过滤 | 小 |
| **Phase 4**（P1） | Phase 分层 + 分层推荐输出 | 小 |
| **Phase 5**（P2） | 知识库增强的关键词扩展 + 同义词关联 | 中 |

### 6.2 不改变的内容

- 不改变现有 CLI 命令的结构（cynefin、analyze、generate 保持原样）
- 不改变 `ConsistencyChecker`
- 不改变 Pipeline 流程（run/continue/ff 沿用）
- 不改变 ViewManager 的存储格式
- 不改变 ArtifactGraph 的 DAG 结构
- **不改变 DM2 参考知识库** — 17 个数据组模板已存在，仅需补充每个组的 `keywords` 和 `related_views`

### 6.3 数据组 → 视图映射表（外部配置）

GroupToViews 映射表存放为**外部文件**，不硬编码在 Python 中：

```yaml
# dm2-reference/group-to-views.yaml
# CLI 运行期间加载，可随时调试和调整
01-Performer: [OV-4, PV-1]
02-Activity: [OV-5a, OV-5b, OV-6a, OV-6b, OV-6c]
03-Capability: [CV-1, CV-2, CV-3, CV-4, CV-5, CV-6, CV-7]
04-Resource: [OV-2, OV-3, SV-2, SV-6, DIV-1, DIV-2, DIV-3]
05-Guidance: [StdV-1, StdV-2, OV-6a]
06-Measure: [SV-7, SvcV-7]
07-Location: [OV-1]
08-Services: [SvcV-1, SvcV-2, SvcV-3a, SvcV-3b, SvcV-4, SvcV-5,
             SvcV-6, SvcV-7, SvcV-8, SvcV-9, SvcV-10a, SvcV-10b, SvcV-10c]
09-Project: [PV-1, PV-2, PV-3]
10-Rules: [SV-10a, SvcV-10a, OV-6a]
11-ResourceFlow: [SV-4, DIV-2, DIV-3]
14-OrgStructure: [OV-4]
16-InformationData: [DIV-1, DIV-2, DIV-3]
```

> **为什么不硬编码？** 调试期需要频繁调整映射关系。放到外部 YAML 里，修改后即刻生效，不需要改代码、不需要重装包。

### 6.4 CLI 输出到 AI Agent 的数据契约

`dm2 analyze --json` 的增强输出结构：

```json
{
  "status": "success",
  "data": {
    "data_group_activation": {
      "01-Performer": 0.6,
      "02-Activity": 0.4,
      "10-Rules": 0.5,
      "05-Guidance": 0.3
    },
    "data_group_keywords_matched": {
      "01-Performer": ["系统管理员", "监控"],
      "02-Activity": ["分析", "展示"],
      "10-Rules": ["等保", "要求"]
    },
    "group_to_views": {
      "01-Performer": ["OV-4", "PV-1"],
      "02-Activity": ["OV-5a", "OV-5b", "OV-6a", "OV-6b", "OV-6c"],
      "10-Rules": ["SV-10a", "SvcV-10a", "OV-6a"]
    },
    "views_completed": ["OV-1"],
    "view_dependencies": {
      "SV-4": ["OV-5a"],
      "OV-5a": []
    },
    "recommendation_candidates": {
      "OV-5a": {"activation_sources": ["02-Activity"], "dependencies_ready": true},
      "OV-4":  {"activation_sources": ["01-Performer"], "dependencies_ready": true},
      "SV-10a": {"activation_sources": ["10-Rules"], "dependencies_ready": false, "missing_deps": ["OV-5a"]}
    }
  }
}
```

**CLI 只做数据检测和映射，不做优先级排序**。最终的视图选择、排序、优先级判断由 AI Agent（LLM）结合与用户的对话上下文完成。符合"CLI 是大脑（提供结构化数据），AI 是手脚（做推理决策）"的核心模式。

---

## 7. 决策记录 & 开放问题

### 已确定

| 决策 | 结论 |
|------|------|
| GroupToViews 映射表存放位置 | **外部 YAML 文件**（如 `dm2-reference/group-to-views.yaml`），不硬编码，方便调试 |
| 多组映射的得分策略 | **CLI 不做聚合计算**。输出原始激活向量 + 映射关系给 AI Agent，由 LLM 结合对话上下文决策 |
| 合规感知 | **不创建额外映射文件**。Guidance(05) + Rules(10) 数据组天然覆盖 |
| 权重调参 | **不需要权重参数**。17 个数据组的激活度是自然权重 |

### 还需讨论

1. 数据组激活检测的关键词表应该内置硬编码，还是从 `dm2-reference/` 模板文件的 frontmatter 中自动提取？
2. Phase 分层后，`/dm2:continue` 是否应该先跑完 P1 再提示进入 P2？
3. `dm2-reference/` 的 17 个数据组模板是否需要补充 `keywords` 和 `related_views` 字段来作为外部配置的数据源？

