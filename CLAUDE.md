# dm2-tool

DoDAF Meta Model 2.02 系统工程辅助工具。

## 项目结构

```
~/workroot/dm2-tool/
├── .github/                  # GitHub 配置
│   ├── workflows/           # CI/CD (test, release, docs)
│   ├── ISSUE_TEMPLATE/      # Issue 模板
│   └── PULL_REQUEST_TEMPLATE.md
├── .claude/                  # AI Agent 接口定义
│   ├── settings.example.json
│   ├── skills/              # 17 个 skill 定义
│   └── commands/            # 命令定义
├── src/dm2/                  ← Python 包
│   ├── cli/                 ← CLI 入口 + 命令实现
│   ├── core/                ← 核心引擎（AI Agent 接口）
│   ├── kernel/              ← DM2 元模型和索引
│   ├── engine/              ← 视图生成、pipeline
│   ├── cognitive/           ← Cynefin/6W 分析
│   ├── reasoning/           ← 一致性检查
│   └── utils/               ← 路径、frontmatter 解析
├── dm2-reference/           ← 内置 DM2 参考知识库
│   └── core/                ← 打包发布的核心数据
├── docs/
├── test/
├── templates/               ← dm2 init 使用的项目模板
├── openspec/                ← 实验性 OpenSpec 工作流
└── pyproject.toml
```

## 架构：四层模型

```
Agent Interface Layer  ← CLI --json + Knowledge API
Core Engine Layer      ← Instructions Engine + Artifact Graph + Change Manager + Pipeline V2
Knowledge Base Layer   ← DM2KnowledgeIndexer + KnowledgeAPI
File System Layer      ← .dm2/ 项目 + dm2-changes/ + output/
```

**核心模式**: CLI 是大脑，AI 是手脚。CLI 管理状态、生成指令；AI Agent 根据指令执行任务。

**技能分发**: `dm2 init` 通过 Python 模板动态生成 `.claude/skills/` 和 `.claude/commands/`。`ToolAdapter` 协议支持未来扩展到其他 AI 工具。

## 开发

```bash
pip install -e .              # 可编辑模式安装
python3 -m dm2 version        # 验证安装
python3 -m dm2.cli.main --help  # 查看所有命令
pytest test/                  # 运行测试
ruff check src/               # Lint
```

## 源码关键映射

| 路径 | 职责 |
|------|------|
| `src/dm2/cli/main.py` | CLI 入口和命令路由 |
| `src/dm2/cli/commands/` | 各命令实现（`init/analyze/generate/validate/...`） |
| `src/dm2/core/` | 核心引擎：Instructions Engine、Artifact Graph、Change Manager、Pipeline V2 |
| `src/dm2/core/templates/workflows/` | 技能 Markdown 模板（from Python `.py` → `.claude/skills/`） |
| `src/dm2/kernel/` | DM2 元模型定义、视图 schema、术语索引 |
| `src/dm2/engine/` | 视图生成 pipeline 各步骤 |
| `src/dm2/cognitive/` | Cynefin 复杂度评估 + 6W 分析 |
| `src/dm2/reasoning/` | 一致性校验（R1-R5） |
| `dm2-reference/core/` | views.yaml、术语 JSON、数据组模板、group-to-views 映射 |
| `test/` | 测试套件 |
| `templates/` | `dm2 init` 的项目模板骨架 |

## 工作规则

- **零 LLM 依赖** — dm2-tool 完全不调用 LLM API。analyze/cynefin 纯本地执行，generate 输出结构化指令（AI Agent 消费），所有分析基于关键词匹配和模板填充。LLM 配置已被清除。
- **CLI 输出结构化 JSON** — `--json` / `-j` 标志输出 `{"status":"success","data":{...}}` 或 `{"status":"error","error":{"code":"...","message":"..."}}`。所有命令必须遵循此格式。
- **视图生命周期** — 每个视图经过 `pending → in_progress → generated → verified` 四个状态，由 `.dm2/view-state.yaml` 管理。
- **变更生命周期** — 每个变更在 `dm2-changes/<name>/` 下有 proposal、design、tasks 和 views/ 目录。
- **路径优先** — `get_reference_path()` 优先 `.dm2/reference/` 本地副本，回退到包内置 `dm2-reference/core/`。
- **约定优先于配置** — 文件名、目录结构是系统约定的接口，减少配置项。如需动态行为，走模板生成而非运行时配置。
- **测试风格** — 使用 pytest，测试放在 `test/` 目录，与 `src/dm2/` 结构对应。

## CLI 命令概要

完整参考见 `docs/readme.md`。常用命令分类：

- **项目管理**: `dm2 init` / `list` / `status` / `archive`
- **分析与生成**: `dm2 analyze` / `cynefin` / `generate` / `validate`
- **AI Agent 接口**: `dm2 knowledge` / `change` / `instructions` / `run --agent`
- **配置与工具**: `dm2 config` / `completion` / `version`

## 项目模式（.dm2/）

`dm2 init` 创建的项目含：
- `.claude/skills/` + `.claude/commands/` — 从 Python 模板动态生成
- `.dm2/reference/` — 知识库本地副本
- `.dm2/view-state.yaml` — 视图生命周期状态
- `.dm2/analysis-state.yaml` — cynefin/analyze 结果持久化
- 可选通过 `DM2_VAULT_PATH` 链接 Obsidian vault
