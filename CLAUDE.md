# dm2-tool

DoDAF Meta Model 2.02 系统工程辅助工具。

## 项目结构

```
~/workroot/dm2-tool/
├── src/dm2/                    ← Python 包
│   ├── cli/                    ← CLI 入口
│   │   ├── main.py             ← 主入口（17 个命令）
│   │   ├── json_output.py      ← 统一 JSON 响应 helper
│   │   └── commands/           ← 子命令模块
│   │       ├── knowledge.py    ← dm2 knowledge * (5 个子命令)
│   │       ├── change.py       ← dm2 change * (4 个子命令)
│   │       └── view.py         ← dm2 view * (1 个子命令)
│   ├── core/                   ← 核心引擎（AI Agent 接口）
│   │   ├── knowledge/api.py    ← KnowledgeAPI（结构化知识查询）
│   │   ├── artifacts/graph.py  ← ArtifactGraph（视图依赖管理）
│   │   ├── agent/instructions.py ← InstructionBuilder（Agent 指令生成）
│   │   ├── changes/manager.py  ← ChangeManager（变更生命周期）
│   │   ├── views/manager.py    ← ViewManager（视图生命周期状态）
│   │   ├── pipeline/orchestrator.py ← PipelineOrchestratorV2（Agent 驱动）
│   │   ├── templates/          ← 工作流模板（7 个 dm2 workflow 的 Python 定义）
│   │   │   ├── __init__.py     ← WorkflowTemplate / SkillTemplate / CommandTemplate dataclass + WORKFLOWS 注册表
│   │   │   ├── generator.py    ← generate_agent_config() 模板→文件生成引擎
│   │   │   └── workflows/      ← 每个 workflow 的 Python 模板（propose, continue, new, ff, verify, onboard, bulk-archive）
│   │   └── adapters/           ← 工具适配器（输出路径 + frontmatter 格式）
│   │       ├── __init__.py     ← ToolAdapter ABC（tool_id, get_skills_dir, get_commands_dir, format_*_frontmatter）
│   │       └── claude.py       ← ClaudeCodeAdapter（.claude/skills/, .claude/commands/dm2/）
│   ├── kernel/                 ← DM2 元模型和索引
│   ├── engine/                 ← 视图生成、pipeline 各步骤
│   ├── cognitive/              ← Cynefin/6W 分析
│   ├── llm/                    ← RAG 检索、配置管理
│   ├── reasoning/              ← 一致性检查
│   └── utils/                  ← 路径、frontmatter 解析
├── dm2-reference/              ← 内置 DM2 参考知识库
│   └── core/                   ← 打包发布的核心数据（296 KB）
├── templates/init/             ← 项目模板（dm2 init 使用）
└── pyproject.toml              ← 包配置
```

## 架构：四层模型

```
Agent Interface Layer  ← CLI --json + Knowledge API
Core Engine Layer      ← Instructions Engine + Artifact Graph + Change Manager + Pipeline V2
Knowledge Base Layer   ← DM2KnowledgeIndexer + KnowledgeAPI
File System Layer      ← .dm2/ 项目 (config/view-state/analysis-state) + dm2-changes/ + output/
```

**核心模式**: CLI 是大脑，AI 是手脚。CLI 管理状态、生成指令；AI Agent 根据指令执行任务。

**技能分发**: `dm2 init` 通过 `generate_agent_config()` 从 Python 模板动态生成 `.claude/skills/` 和 `.claude/commands/`，不复制开发者自己的 `.claude/` 目录。`ToolAdapter` 协议支持未来扩展到其他 AI 编码工具。

## 开发

```bash
pip install -e .              # 安装为可编辑模式
python3 -m dm2 version        # 验证安装
python3 -m dm2.cli.main --help  # 查看所有命令
```

## CLI 命令

### 项目管理
| 命令 | 说明 |
|------|------|
| `dm2 init <name>` | 创建 .dm2 项目 |
| `dm2 list` | 列出项目中的变更 |
| `dm2 status` | 项目状态（知识库 + 分析 + 视图进度） |
| `dm2 archive <change>` | 归档变更 |

### 分析与生成
| 命令 | 说明 |
|------|------|
| `dm2 analyze -d "..."` | 6W 分析 + 视图推荐 |
| `dm2 cynefin` | Cynefin 复杂度评估 |
| `dm2 generate <view> -d "..."` | 生成 DoDAF 视图 |
| `dm2 validate <view>` | 一致性校验（支持 --all） |
| `dm2 run -d "..."` | 运行 6 步融合流程 |

### AI Agent 接口（新增）
| 命令 | 说明 |
|------|------|
| `dm2 knowledge search <q>` | 搜索 DM2 术语 |
| `dm2 knowledge concept <n>` | 查看概念详情 |
| `dm2 knowledge views` | 列出所有视图 |
| `dm2 knowledge view <id>` | 查看视图元数据 |
| `dm2 knowledge stats` | 知识库统计 |
| `dm2 change new <name>` | 创建变更 |
| `dm2 change status` | 查看变更状态 |
| `dm2 change list` | 列出活跃变更 |
| `dm2 change archive <name>` | 归档变更 |
| `dm2 instructions <type> -d "..."` | 生成 Agent 指令 |
| `dm2 run --agent -d "..."` | Agent 驱动 pipeline |
| `dm2 run --status` | Pipeline 状态 |
| `dm2 run --instructions <step>` | 步骤指令 |
| `dm2 run --complete-step <step>` | 标记步骤完成 |
| `dm2 view list` | 列出视图及生成状态 |

### 配置与工具
| 命令 | 说明 |
|------|------|
| `dm2 config` | 查看/设置配置 |
| `dm2 completion` | Shell 补全 |
| `dm2 uninstall` | 卸载/清理 |
| `dm2 version` | 版本信息 |

所有命令支持 `--json` / `-j` 标志，输出 `{"status":"success","data":{...}}` 或 `{"status":"error","error":{"code":"...","message":"..."}}`。

## Agent 驱动 Pipeline 流程

```
dm2 run --agent -d "描述"
→ 初始化 pipeline，返回状态 + 第一步指令

dm2 run --instructions step1-intent-scope
→ 获取指定步骤的 Agent 指令（上下文 + 规则 + 模板）

dm2 run --complete-step step1-intent-scope
→ 标记完成，自动推进到下一步

dm2 run --status
→ 查询当前 pipeline 状态
```

## 项目模式

- `dm2 init` 在任何目录创建 `.dm2/` 项目，含：
  - `.claude/skills/` + `.claude/commands/` — 从 Python 模板动态生成（非文件复制），含 `generatedBy` 版本元数据
  - `.dm2/reference/` — 参考知识库本地副本（views.yaml、术语、数据组模板）
- `.dm2/view-state.yaml` — 视图生命周期状态（pending/in_progress/generated/verified）
- `.dm2/analysis-state.yaml` — 最近一次 cynefin/analyze 结果持久化
- 每个项目独立管理自己的变更和输出
- `get_reference_path()` 优先使用项目本地 `.dm2/reference/`，回退到包内置 `dm2-reference/core/`
- 不主动调用 LLM 模型
- 可选通过 `DM2_VAULT_PATH` 环境变量连接 Obsidian vault
