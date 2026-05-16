# dm2-tool 使用说明

**dm2-tool** 是基于 DoDAF Meta Model 2.02 (DM2) 的系统工程辅助工具，帮助系统工程团队进行架构分析、DoDAF 视图生成和知识管理。

---

## 安装

```bash
cd dm2-tool                     # 进入项目目录
pip install -e .                # 基础安装
pip install -e ".[dev]"         # 含测试和 lint 工具
```

`dm2` 命令会被安装到 Python 的 user bin 目录（macOS 通常为 `~/Library/Python/<version>/bin`）。**确保该目录在 PATH 中**：

```bash
# 将 Python user bin 加入 PATH（写入 ~/.zshrc 永久生效）
echo 'export PATH="$HOME/Library/Python/$(python3 -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")")/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

验证安装：

```bash
dm2 version                     # 显示版本信息
dm2 --help                      # 显示所有可用命令
```

### 卸载

```bash
dm2 uninstall --self            # 卸载 dm2-tool 程序包（pip uninstall）
dm2 uninstall --project         # 删除当前目录的 .dm2/ 项目
dm2 uninstall --user-config     # 删除用户配置文件 ~/.config/dm2/config.yaml
dm2 uninstall                   # 显示卸载选项帮助
```

所有卸载操作执行前均有确认提示。

---

## 核心概念

### 项目结构

`dm2 init` 创建的 `.dm2` 项目目录如下：

```
my-project/
  .dm2/
    config.yaml           ← 项目配置
    reference/            ← 参考知识库本地副本（dm2 init 自动复制）
      views.yaml          ← 52 个 DoDAF 视图定义（含依赖关系）
      _dm2_v202_extract.json ← ~277 个 DM2 术语定义
      group-to-views.yaml ← 数据组到视图的映射
      groups/             ← 17 个数据组 Markdown 模板
    view-state.yaml       ← 视图生命周期状态（ViewManager 管理）
    analysis-state.yaml   ← 分析结果持久化（cynefin/analyze）
  .claude/
    skills/               ← Claude Code AI 技能（dm2 init 从 Python 模板动态生成）
    commands/             ← Claude Code 斜杠命令（含 generatedBy 版本元数据）
  dm2-changes/            ← 架构变更（每个变更一个子目录）
    <name>/
      analysis/           ← AI Agent 分析产物（可选，用于审计）
      views/              ← 生成的 DoDAF 视图
      proposal.md         ← 变更提案
      design.md           ← 技术设计
      tasks.md            ← 实施任务清单
  dm2-archive/            ← 已归档的变更
```

### 配置层次

配置支持三层覆盖（后者覆盖前者）：

| 层级 | 路径 | 用途 |
|------|------|------|
| 内置默认 | 代码内 | 开箱即用的默认值 |
| 用户配置 | `~/.config/dm2/config.yaml` | 跨项目共享（用户偏好） |
| 项目配置 | `.dm2/config.yaml` | 项目特定的视图和检查设置 |

---

## 架构概览

dm2-tool 采用四层架构，核心模式为 **"CLI 是大脑，AI 是手脚"**：

```
Agent Interface Layer  ← CLI --json + Knowledge API（供 AI Agent 消费）
Core Engine Layer      ← Instructions Engine + Artifact Graph + Change Manager + Pipeline V2
Knowledge Base Layer   ← DM2KnowledgeIndexer + KnowledgeAPI（277 术语、11 概念、52 视图）
File System Layer      ← .dm2/ 项目 + dm2-changes/ + dm2-archive/
```

CLI 管理状态、生成结构化指令；AI Agent 根据指令执行具体任务（分析、生成视图、检查一致性等）。

**技能分发**：`dm2 init` 通过 Python 模板系统（`core/templates/`）和工具适配器（`core/adapters/`）动态生成 `.claude/` 配置，不依赖开发者环境的 `.claude/` 目录。

### AI Agent 接口

所有命令支持 `--json` / `-j` 标志，输出统一的 JSON 响应：

```json
{"status": "success", "data": {...}}
{"status": "error", "error": {"code": "ERROR_CODE", "message": "..."}}
```

### Agent 驱动 Pipeline

```
dm2 run --agent -d "系统描述"
→ 初始化 pipeline，返回状态 + 第一步指令（JSON）

dm2 run --instructions step1-intent-scope
→ 获取指定步骤的 Agent 指令（上下文 + DoDAF 规则 + 模板）

dm2 run --complete-step step1-intent-scope
→ 标记完成，自动推进到下一步

dm2 run --status
→ 查询当前 pipeline 状态
```

---

## AI Agent 工作流

`dm2 init` 从 Python 模板自动生成 10 个 Claude Code 斜杠命令（`.claude/commands/dm2/`）和对应的技能文件（`.claude/skills/`）：

### 核心工作流（规划→实施→归档）

```
/dm2:explore  ──→  /dm2:propose  ──→  /dm2:apply  ──→  /dm2:verify  ──→  /dm2:archive
  (只读探索)        (分析规划)        (任务驱动实施)     (一致性检查)       (归档)
```

| 命令 | 说明 | 模式 |
|------|------|------|
| `/dm2:explore` | DoDAF 架构探索与讨论，只读思考模式。可查询知识库、对比视图、讨论架构决策，不生成任何文件 | 只读 |
| `/dm2:propose` | 全流程分析——Cynefin 评估 + 数据组激活 + 关注点匹配 + 生成 proposal/design/tasks | 分析 |
| `/dm2:apply` | 任务驱动实施——读取 tasks.md，按依赖顺序生成全部视图，勾选 checkbox（区别于分析驱动的 continue/ff） | 实施 |
| `/dm2:verify` | 验证已生成视图的完整性、正确性和跨视图一致性 | 检查 |
| `/dm2:archive` | 归档单个已完成的架构变更（含验证、确认步骤） | 归档 |

### 扩展命令

| 命令 | 说明 |
|------|------|
| `/dm2:new` | 创建新的架构变更目录（脚手架） |
| `/dm2:continue` | 逐步生成视图——每次生成一个视图（分析驱动，非 tasks.md 驱动） |
| `/dm2:ff` | 全自动一键生成所有推荐视图（分析驱动，跳过规划阶段） |
| `/dm2:bulk-archive` | 批量归档多个已完成的架构变更 |
| `/dm2:onboard` | 交互式引导——完整走一遍 DoDAF 架构建模流程 |

### 工作原理

每个工作流由 Python 模板定义（`src/dm2/core/templates/workflows/`），`dm2 init` 时通过 `ClaudeCodeAdapter` 生成带版本元数据的 Markdown 文件：

```
src/dm2/core/templates/workflows/
├── explore.py          →  .claude/skills/dm2-explore-workflow/SKILL.md
│                           .claude/commands/dm2/explore.md
├── propose.py          →  .claude/skills/dm2-propose-workflow/SKILL.md
│                           .claude/commands/dm2/propose.md
├── apply.py            →  .claude/skills/dm2-apply-workflow/SKILL.md
│                           .claude/commands/dm2/apply.md
├── archive.py          →  .claude/skills/dm2-archive-workflow/SKILL.md
│                           .claude/commands/dm2/archive.md
├── continue_workflow.py
├── new_workflow.py
├── ff.py
├── verify.py
├── onboard.py
└── bulk_archive.py
```

---

## 命令参考

### `dm2 init` — 创建项目

```bash
dm2 init [名称]                # 在当前目录下创建项目
dm2 init my-arch -v ~/vault   # 创建项目并关联 Obsidian vault
```

### `dm2 list` — 列出架构变更

```bash
dm2 list                       # 列出 dm2-changes/ 中的变更，显示任务进度
```

输出示例：

```
项目变更 (3):
  防火墙升级方案           [5/8]
  等保三级整改             [0/12]
  安全态势感知平台         未开始

已归档: 2 项
```

### `dm2 status` — 项目状态

```bash
dm2 status                     # 显示知识库状态 + 分析结果 + 视图进度
dm2 status --json              # 结构化输出（供 AI Agent 使用）
```

输出示例：

```
DM2 知识库状态:
  术语: 277
  概念: 35
  视图模板: 52

分析状态:
  Cynefin 域: 繁杂（Complicated） (置信度 85%)
  6W 分析: What (置信度 92%)
  推荐视图: 4 个

视图进度:
  待处理: 2
  进行中: 1
  已生成: 3
  已验证: 1

  OV-2        [generated]
  OV-5a       [generated]
  SV-4        [in_progress]
```

### `dm2 archive` — 归档变更

```bash
dm2 archive <变更名称>         # 将完成的变更移入 dm2-archive/
```

### `dm2 cynefin` — 复杂度评估

基于 Cynefin 框架评估系统复杂度，帮助确定合适的方法论（Clear → Complicated → Complex → Chaotic）。

```bash
dm2 cynefin                                    # 使用默认参数
dm2 cynefin -s 5 --uncertainty high --rules complex
```

参数：

| 参数 | 简写 | 取值 | 默认值 |
|------|------|------|--------|
| `--systems` | `-s` | 整数（自动映射到 simple/medium/complex） | 3 |
| `--stakeholders` | — | `simple` / `medium` / `complex` | medium |
| `--uncertainty` | — | `simple` / `medium` / `complex` | medium |
| `--rules` | `-r` | `simple` / `medium` / `complex` | medium |

### `dm2 analyze` — 架构分析（无需 LLM）

对系统描述文本执行 6W 分析（What/How/Where/Who/When/Why），识别焦点维度，提取实体，推荐 DoDAF 视图。

```bash
dm2 analyze -d "构建一个安全态势感知平台，包括数据采集、威胁分析和大屏展示"
dm2 analyze -d "等保三级整改，涉及边界防护、访问控制、审计日志"
```

输出包括：

- **主要 6W** 和次要维度（含置信度）
- **提取的实体**（系统、组织、活动等）
- **推荐视图列表**

### `dm2 generate` — 生成 DoDAF 视图

根据指定视图 ID 和系统描述，生成符合 DM2 规范的视图文档。

```bash
dm2 generate --list                                      # 列出所有可用视图
dm2 generate OV-1 -d "态势感知系统：探针→分析→展示"            # 生成 OV-1 视图
dm2 generate SV-4 -d "防火墙系统功能分解" --no-rag              # 禁用 RAG 增强
```

参数：

| 参数 | 简写 | 说明 |
|------|------|------|
| `--list` | `-l` | 列出全部 52 个 DoDAF 视图 |
| `--desc` | `-d` | 系统或架构描述文本 |
| `--no-rag` | — | 禁用 RAG（不检索 DM2 参考知识） |

### `dm2 validate` — 视图一致性校验

对已生成的 DoDAF 视图运行一致性检查（Activity-Performer 绑定、Resource Flow 完整性、Capability-Activity 映射、Temporal 一致性），校验通过自动更新视图状态为 `verified`。

```bash
dm2 validate OV-2              # 校验单个视图
dm2 validate --all             # 校验所有已生成视图
dm2 validate OV-2 --json       # JSON 格式输出（供 AI Agent 使用）
```

输出按 severity（ERROR/WARNING/INFO）分组，每项含 issue 类型、消息、建议和关联视图。

### `dm2 view` — 视图生命周期管理

```bash
dm2 view list                  # 列出所有视图及生成状态
dm2 view list --status verified # 按状态过滤（pending/in_progress/generated/verified）
dm2 view list --json           # JSON 格式输出（供 AI Agent 使用）
```

### `dm2 run` — 运行 DoDAF 6步融合流程

执行完整的 DoDAF 架构开发流程（融合 6 步框架）：

```
Step 1+2: 意图澄清 + 范围界定 → Cynefin + 反向质问 + 上下文预算
Step 3+4: 数据定义 + 知识沉淀 → 6W矩阵 + RAG检索 + 缺口检测
Step 5:   分析执行             → 溯因推理 + OODA + TOC + 一致性
Step 6:   文档化 + 知识回流     → Composite View + wikilinks → 可迭代回 Step 1
```

```bash
dm2 run -d "某云原生微服务系统的安全架构：包含API网关、SIEM、IDS..."
dm2 run --resume                           # 从上次中断处继续
dm2 run --step step5-analysis               # 单独执行某一步骤
dm2 run --progress                          # 查看当前 pipeline 进度
dm2 run --iterate                           # 触发迭代循环（重置所有步骤）
```

参数：

| 参数 | 简写 | 说明 |
|------|------|------|
| `--desc` | `-d` | 系统/架构描述文本（必填，首次启动时） |
| `--resume` | `-r` | 从上次中断的步骤继续执行 |
| `--step` | `-s` | 单独执行指定步骤（step1-intent-scope / step3-data-requirements / step5-analysis / step6-documentation） |
| `--progress` | `-p` | 显示当前 pipeline 各步骤完成状态 |
| `--iterate` | `-i` | 重置所有步骤，准备新一轮迭代 |
| `--agent` | — | Agent 驱动模式（输出 JSON 指令） |
| `--status` | — | 输出 pipeline 状态 JSON |
| `--instructions` | — | 获取指定步骤的 Agent 指令 |
| `--complete-step` | — | 标记步骤完成并推进 |
| `--json` | `-j` | 输出结构化 JSON |

产物输出到 `.dm2/steps/`（各步骤中间产物）和 `dm2-changes/<name>/views/`（生成的视图文件）。

### `dm2 config` — 查看和设置配置

```bash
dm2 config                        # 显示合并后的最终配置（三层解析）
dm2 config -u                     # 仅显示用户级配置
dm2 config -p                     # 仅显示项目级配置
dm2 config -r                     # 显示合并结果（同默认）
```

支持嵌套键（点分隔）：`views.include_mermaid` 等。

### `dm2 completion` — Shell 自动补全

```bash
dm2 completion                    # 自动检测 shell 并打印补全脚本
dm2 completion bash               # 指定 shell 类型
dm2 completion zsh --install      # 生成并自动安装到 ~/.zshrc
```

### `dm2 version` — 版本信息

```bash
dm2 version                       # 显示版本号
dm2 version --json                # JSON 格式
```

### `dm2 knowledge` — DM2 知识库查询（AI Agent 接口）

提供对 DM2 参考知识库的结构化查询，供 AI Agent 在生成和分析时检索 DM2 术语、概念和视图。

```bash
dm2 knowledge search "capability"       # 搜索术语
dm2 knowledge concept Capability        # 查看概念详情
dm2 knowledge views                     # 列出所有 52 个视图
dm2 knowledge views --type OV           # 按视点过滤
dm2 knowledge view OV-1                 # 查看单个视图元数据
dm2 knowledge stats                     # 知识库统计
```

所有子命令支持 `--json` 输出。

### `dm2 change` — 架构变更管理（AI Agent 接口）

管理变更的完整生命周期：创建 → 分析 → 生成 → 验证 → 完成。

```bash
dm2 change new "防火墙HA升级"           # 创建变更（含 .change.yaml 状态文件）
dm2 change status                       # 列出所有活跃变更
dm2 change status -c "防火墙HA升级"      # 查看单个变更详情
dm2 change list                         # 列出活跃变更（同 status）
dm2 change archive "防火墙HA升级"        # 归档变更
```

所有子命令支持 `--json` 输出。

### `dm2 instructions` — 生成 Agent 指令

为 AI Agent 生成结构化的任务执行指令，包含 DM2 上下文、DoDAF 合规规则和输出模板。

```bash
# 视图生成指令（含 DM2 术语、依赖视图、DoDAF 规则）
dm2 instructions view/OV-1 -d "云原生安全系统" --json

# Pipeline 步骤指令（含章节模板、输出路径）
dm2 instructions step/step1-intent-scope -d "系统描述" --json

# 结合变更上下文生成指令
dm2 instructions view/OV-2 -c "防火墙HA升级" -d "..." --json
```

### `dm2 run --agent` — Agent 驱动 Pipeline

启动 AI Agent 驱动的 6 步流程。与传统的 `dm2 run` 不同，`--agent` 模式输出结构化 JSON 指令而非直接执行。

```bash
dm2 run --agent -d "系统描述"                       # 初始化 Agent pipeline
dm2 run --status                                    # 查询当前状态
dm2 run --instructions step1-intent-scope            # 获取步骤指令
dm2 run --complete-step step1-intent-scope           # 标记完成，推进
```

---

## 典型工作流

### 场景 1：新建架构项目

```bash
# 1. 创建项目
dm2 init 安全态势感知平台

# 2. 排查可用视图
dm2 generate --list

# 3. 分析系统描述，获取推荐视图
dm2 analyze -d "
我们需要建设一个安全态势感知系统：
- 数据采集层：在网络各节点部署探针，采集流量和日志
- 分析层：使用大数据平台和 AI 模型进行威胁检测
- 展示层：可视化大屏实时呈现安全态势
- 响应层：自动化编排处置流程
"

# 4. 生成视图
dm2 generate OV-1 -d "态势感知系统概览"
dm2 generate OV-2 -d "资源流分析"
dm2 generate DIV-1 -d "数据模型"
```

### 场景 2：渐进式架构变更管理

```bash
# 1. 在 dm2-changes/ 下创建变更目录
mkdir -p dm2-changes/防火墙HA升级
echo "# 防火墙 HA 升级" > dm2-changes/防火墙HA升级/proposal.md

# 2. 查看项目中的变更
dm2 list

# 3. 编写变更任务
cat > dm2-changes/防火墙HA升级/tasks.md << 'EOF'
## 任务
- [x] 现状分析 (OV-1)
- [x] 资源流梳理 (OV-2)
- [ ] 系统功能影响 (SV-4)
- [ ] 数据模型变更 (DIV-1)
- [ ] 标准合规检查 (StdV-1)
EOF

# 4. 完成后归档
dm2 archive 防火墙HA升级
```

### 场景 3：Cynefin 驱动的分析策略

```bash
# 1. 评估场景复杂度
dm2 cynefin -s 8 --stakeholders complex --uncertainty high --rules complex

# 2. 根据输出（Chaotic 域 → 全量视图集）运行分析
dm2 analyze -d "多部门协同的安全运营中心，跨三个数据中心"

# 3. 按优先级生成视图
```

### 场景 4：AI Agent 协作工作流（新）

```bash
# 1. AI Agent 查询知识库获取上下文
dm2 knowledge view OV-1 --json
dm2 knowledge search "资源流" --json

# 2. AI Agent 获取生成指令
dm2 instructions view/OV-2 -d "云原生安全系统" --json

# 3. AI Agent 根据指令生成视图内容，写入文件

# 4. 创建变更跟踪
dm2 change new "安全架构OV视图" --json

# 5. 运行 Agent 驱动 Pipeline
dm2 run --agent -d "云原生安全系统" --json
dm2 run --instructions step1-intent-scope
# ... Agent 执行步骤 ...
dm2 run --complete-step step1-intent-scope
dm2 run --status  # 查看进度
```

### 场景 5：DoDAF 6步流程完整执行

```bash
# 1. 创建项目
dm2 init 安全架构项目

# 2. 一键运行完整 6 步流程
dm2 run -d "
某云原生微服务系统的安全架构：
- API网关、SIEM平台、IDS探针、微服务集群
- 核心流程：采集日志 → 实时分析 → 自动化响应 → 安全报表
- 涉及 SOC团队、运维团队、开发团队
- 需满足等保2.0三级要求
"

# 3. 查看进度
dm2 run --progress

# 4. 基于 Step 6 的迭代建议，重置并重新运行
dm2 run --iterate
dm2 run --resume

# 5. 如只需重新分析，单独执行 Step 5
dm2 run --step step5-analysis
```

产物查看：
```bash
ls .dm2/steps/          # 各步骤中间产物
# step1-intent-scope.md    ← 意图、Cynefin、数据组
# step3-data-requirements.md ← 6W映射、RAG检索、缺口
# step5-analysis.md        ← 溯因推断、OODA、TOC、一致性
# step6-documentation.md   ← Composite View、wikilinks、迭代建议

ls dm2-changes/<name>/views/   # 生成的视图文件
# composite-view.md, OV-1.md, OV-2.md, OV-5a.md
```

---

## 可用 DoDAF 视图一览

### 全视点 (AV) — 2 个
| ID | 名称 | 说明 |
|----|------|------|
| AV-1 | 概述与摘要信息 | 系统概述和关键业务目标 |
| AV-2 | 集成字典 | 关键术语定义和缩写 |

### 能力视点 (CV) — 7 个
| ID | 名称 | 说明 |
|----|------|------|
| CV-1 | 能力愿景 | 能力开发愿景和目标 |
| CV-2 | 能力分类法 | 能力分类和层级结构 |
| CV-3 | 能力阶段化 | 能力发展阶段和里程碑 |
| CV-4 | 能力依赖 | 能力间依赖关系 |
| CV-5 | 能力-组织映射 | 能力到组织的阶段映射 |
| CV-6 | 能力-作战活动映射 | CV↔OV 桥梁 |
| CV-7 | 能力-服务映射 | CV↔SvcV 桥梁 |

### 数据与信息视点 (DIV) — 3 个
| ID | 名称 | 说明 |
|----|------|------|
| DIV-1 | 概念数据模型 | 顶层语义概念和关系 |
| DIV-2 | 逻辑数据模型 | 数据结构定义 |
| DIV-3 | 物理数据模型 | 物理实现和数据格式 |

### 作战视点 (OV) — 9 个
| ID | 名称 | 说明 |
|----|------|------|
| OV-1 | 高层作战概念图 | 作战概念和活动概览 |
| OV-2 | 作战资源流描述 | 资源在活动间流动 |
| OV-3 | 作战资源流矩阵 | 资源流信息交换矩阵 |
| OV-4 | 组织关系图 | 组织结构和职责 |
| OV-5a | 作战活动分解 | 活动层级分解 |
| OV-5b | 作战活动分解（追踪） | 活动到执行者的追踪 |
| OV-6a | 作战规则追踪 | 活动遵循的规则 |
| OV-6b | 作战状态追踪 | 状态转换和事件追踪 |
| OV-6c | 作战事件追踪 | 事件序列和时间线 |

### 项目视点 (PV) — 3 个
| ID | 名称 | 说明 |
|----|------|------|
| PV-1 | 项目组合 | 项目组合概览 |
| PV-2 | 项目时间线 | 项目计划和里程碑 |
| PV-3 | 项目-能力映射 | 项目与能力对应关系 |

### 系统视点 (SV) — 14 个
| ID | 名称 | 说明 |
|----|------|------|
| SV-1 | 系统接口描述 | 系统间接口 |
| SV-2 | 系统资源流描述 | 系统间资源流 |
| SV-3 | 系统-系统矩阵 | 系统间交互关系 |
| SV-4 | 系统功能描述 | 系统功能分解 |
| SV-5a | 系统功能-作战活动追溯 | 系统功能到活动的映射 |
| SV-5b | 系统功能-作战活动追溯（追踪） | 双向追溯矩阵 |
| SV-6 | 系统资源流矩阵 | 系统资源流详细矩阵 |
| SV-7 | 系统度量矩阵 | 系统性能度量 |
| SV-8 | 系统演进描述 | IT 现代化/信创替代路线图 |
| SV-9 | 系统技术预测 | 技术前瞻雷达 |
| SV-10a | 系统规则模型 | OV-6a 的技术实现 |
| SV-10b | 系统状态转换描述 | HA/DR/AI 降级状态机 |
| SV-10c | 系统事件追踪描述 | 系统交互序列图 |

### 服务视点 (SvcV) — 13 个
| ID | 名称 | 说明 |
|----|------|------|
| SvcV-1 | 服务接口描述 | 服务接口定义 |
| SvcV-2 | 服务资源流描述 | 服务间资源流 |
| SvcV-3a | 服务-服务矩阵 | 服务间交互矩阵 |
| SvcV-3b | 服务-服务矩阵 | SOA 编排拓扑 |
| SvcV-4 | 服务功能描述 | 服务功能分解 |
| SvcV-5 | 服务功能-作战活动追溯 | 服务到活动的映射 |
| SvcV-6 | 服务资源流矩阵 | 服务资源流矩阵 |
| SvcV-7 | 服务度量矩阵 | SLA 管理 |
| SvcV-8 | 服务演进描述 | SOA 转型路线图 |
| SvcV-9 | 服务技术预测 | 技术成熟度预测 |
| SvcV-10a | 服务规则模型 | SLA/熔断/降级契约 |
| SvcV-10b | 服务状态转换描述 | 编排器/Saga 状态机 |
| SvcV-10c | 服务事件追踪描述 | API 调用链序列图 |

### 标准视点 (StdV) — 2 个
| ID | 名称 | 说明 |
|----|------|------|
| StdV-1 | 标准轮廓 | 适用的标准和规范 |
| StdV-2 | 标准预测 | 未来标准趋势 |

---

## 配置参考

### 内置默认值

```yaml
views:
  include_mermaid: true       # 生成视图中包含 Mermaid 图表
  include_timestamps: true    # 生成视图中包含时间戳

consistency:
  check_enabled: true         # 启用手动一致性检查
  strict_mode: false          # 严格模式（警告 → 错误）

dm2:
  language: zh                # 界面语言
```

### 环境变量

| 变量 | 说明 |
|------|------|
| `DM2_VAULT_PATH` | Obsidian vault 路径（补充参考源） |

---

## 内置知识库

`dm2-reference/` 目录包含 DM2 2.02 规范的参考数据：

- `_dm2_v202_extract.json` — ~277 个 DM2 术语定义
- `views.yaml` — 52 个 DoDAF 视图的完整定义（含依赖关系、优先级、所需数据）
- `00-基础模式/` ~ `16-InformationAndData/` — 17 个数据组的 Markdown 参考文档
- `详细分析/` — 深度分析报告和视图全集映射

运行 `dm2 init` 时，参考知识库会自动复制到项目的 `.dm2/reference/` 目录，Claude Code 技能和命令从 Python 模板动态生成到 `.claude/`。项目完全自包含——AI Agent 可直接读取本地副本，无需通过 CLI 查询。用户也可按项目自定义 `views.yaml` 中的视图依赖关系。CLI 命令会优先使用项目本地副本，不存在时回退到包内置版本。
