# dm2-tool

DoDAF Meta Model 2.02 系统工程辅助工具。

## 项目结构

```
~/workroot/dm2-tool/
├── .github/                  # GitHub 配置
│   ├── workflows/           # CI/CD (test, release, docs)
│   ├── ISSUE_TEMPLATE/      # Issue 模板
│   └── PULL_REQUEST_TEMPLATE.md
├── .claude/                  ← 生成物：手写文件仅 settings.example.json
│   ├── settings.example.json ← 手写：权限示例
│   ├── skills/              ← 22 个技能，全部生成：10 个 dm2-*（入库）+ 12 个 openspec-*（不入库）
│   └── commands/            ← 全部生成：10 个 dm2（入库）+ 12 个 opsx（不入库）
├── src/dm2/                  ← Python 包
│   ├── cli/                 ← CLI 入口 + 命令实现
│   ├── core/                ← 核心引擎（AI Agent 接口）
│   ├── kernel/              ← DM2 索引 + metamodel/ 派生索引加载器
│   ├── engine/              ← 视图生成、pipeline
│   ├── cognitive/           ← Cynefin/6W 分析
│   ├── reasoning/           ← 一致性检查 + 符合性校验
│   └── utils/               ← 路径、frontmatter 解析
├── scripts/                  ← 构建脚本（派生知识索引生成）
│   └── build_knowledge_indexes.py
├── dm2-reference/           ← 运行时 + 构建资产（权威源与派生索引）
│   ├── dm2-data-dictionary.yaml ← 权威源：DM2 数据字典（279 术语 + 怪物矩阵）
│   ├── dm2-metamodel-2.02.yaml  ← 权威源：DM2 逻辑数据模型（19 子模型）
│   ├── group-to-views.yaml  ← 数据组→视图映射（basis 证据标注）
│   ├── concerns.yaml        ← 关切模板库
│   └── core/                ← 派生索引 + views.yaml + groups/（打包发布）
├── schemas/                  ← CLI JSON 输出形状的 JSON Schema 声明（测试对照真实输出执行）
├── docs/                    ← 地基文档（foundation.md）+ 用户手册 + 专题
│   └── reference/           ← 源研究与分析语料；运行时不读取、不随包分发
├── test/
├── openspec/                ← 变更与规范（spec-driven）
└── pyproject.toml
```

> 各目录的**作用与消费者**声明见 `docs/foundation.md` §2（**试行中，暂未加守护测试**）。上方树中的行内注释只是摘要。

## 架构：四层模型

```
Agent Interface Layer  ← CLI --json + Knowledge API
Core Engine Layer      ← Instructions Engine + Artifact Graph + Change Manager + Pipeline V2
Knowledge Base Layer   ← DM2KnowledgeIndexer + KnowledgeAPI
File System Layer      ← .dm2/ 项目 + dm2-changes/ + output/
```

**核心模式**: CLI 是大脑，AI 是手脚。CLI 管理状态、生成指令；AI Agent 根据指令执行任务。

> 上面四层是**概念划分**；它在包级的可执行形式是五级依赖序，见「工作规则 → 架构边界」。

**技能分发**: `dm2 init` 通过 Python 模板动态生成 AI 工具配置，由 `ToolAdapter` 协议选择目标：
- `claude`（默认）：`.claude/skills/` + `.claude/commands/dm2/`
- `dsh`：`init --tool dsh` → `.dsh/skills/`（10 个 SKILL.md，`user-invocable: true`，无 commands；正文经 `DshAdapter.render_skill_body` 重写 `/dm2:*`、`AskUserQuestion`、`python3 -m dm2.cli.main`）
注册表入口：`dm2.core.adapters.get_adapter(tool_id)`。

## 开发

```bash
pip install -e .              # 可编辑模式安装
openspec update --force       # 首次克隆后重建未入库的 openspec 技能与 opsx 命令
python3 -m dm2 version        # 验证安装
python3 -m dm2.cli.main --help  # 查看所有命令
pytest test/                  # 运行测试
ruff check src/ test/         # Lint（与 CI 口径一致）
openspec validate --all --strict  # 规范关口（与 CI 的 spec job 一致；strict 会把警告也视为失败）
DM2_DEBUG=1 dm2 analyze ...   # 显示索引器诊断（默认静默，保证 --json 的 2>&1 流纯净）
```

## 源码关键映射

| 路径 | 职责 |
|------|------|
| `src/dm2/cli/main.py` | CLI 入口和命令路由 |
| `src/dm2/cli/commands/` | 各命令实现（`init/analyze/generate/validate/...`） |
| `src/dm2/core/` | 核心引擎：Instructions Engine、Artifact Graph、Change Manager、Pipeline V2 |
| `src/dm2/core/templates/workflows/` | 技能 Markdown 模板（from Python `.py` → 各 adapter 的 skills 目录） |
| `src/dm2/core/adapters/` | AI 工具适配器：`claude.py`（ClaudeCodeAdapter）、`dsh.py`（DshAdapter）+ `get_adapter()` 注册表 |
| `src/dm2/kernel/indexer.py` | 术语/概念/视图模板加载（术语源 = `core/terms.json`） |
| `src/dm2/kernel/metamodel/` | `MetamodelIndex`：关联目录/分类学/视图内容规范查询 |
| `src/dm2/engine/` | 视图生成 pipeline 各步骤 |
| `src/dm2/cognitive/` | Cynefin 复杂度评估（五维域投票+硬触发，含 Disorder；`cynefin_deriver.py` 外部化 YAML 词库，CLI/pipeline 共用）+ 6W 分析 |
| `src/dm2/reasoning/consistency.py` | 散文级正则一致性检查（prose-heuristic） |
| `src/dm2/reasoning/conformance.py` | 元模型符合性校验（metamodel-conformance，5 条规则） |
| `scripts/build_knowledge_indexes.py` | 权威源 YAML → 派生 JSON 索引 + 组模板 relationships 对账 |
| `dm2-reference/core/` | views.yaml、派生索引（terms/associations/taxonomy/view-content-spec.json）、数据组模板 |
| `schemas/` | 各命令 JSON 输出形状的 JSON Schema 声明；由 `test/test_cli_output_schemas.py` 对照真实输出执行 |
| `test/` | 测试套件 |
| `test/test_architecture_boundaries.py` | 分层依赖方向守护（五级依赖序、`utils` 为叶子） |
| `test/test_cli_json_contract.py` | JSON 信封契约守护（`--json` 覆盖面、守卫失败出信封、豁免清单） |
| `docs/foundation.md` | **地基文档**：架构边界、横切不变量、现状基线、已知裂缝、目标态 |

## 工作规则

- **零 LLM 依赖** — dm2-tool 完全不调用 LLM API。analyze/cynefin 纯本地执行，generate 输出结构化指令（AI Agent 消费），所有分析基于关键词匹配和模板填充。LLM 配置已被清除。契约见 `openspec/specs/dm2-no-llm-dependency`：源码不导入、打包不声明、文档不教学 LLM 依赖与 API key。
- **架构边界** — 包按五级依赖序组织，依赖只能**向下**：`utils`(L0) < `config`/`kernel`(L1) < `cognitive`/`reasoning`/`core`(L2) < `engine`(L3) < `cli`(L4)。`utils` 是叶子层，任何包都不得 import `cli`。契约见 `openspec/specs/dm2-architecture-boundaries`，由 `test/test_architecture_boundaries.py` 守护；**新增包必须显式登记层级**，否则测试失败。
- **生成物不可手改** — `.claude/skills/dm2-*`、`.claude/commands/dm2/`、`.dsh/skills/dm2-*` 由 `dm2 init` 从 `src/dm2/core/templates/workflows/` 生成；手改会在下次生成时被覆盖。改技能先改 Python 模板再重新生成。
- **生成物归属决定是否入库** — dm2 自己生成的 agent 指令**入库**（它是 dm2 的产品面），由 `test/test_generated_agent_config.py` 做字节一致性守护：改了模板却没重新生成即失败。第三方工具生成的（`.claude/skills/openspec-*`、`.claude/commands/opsx/`，将来还有 `.dsh/skills/speckit-*`）**不入库**——它们的生命周期不归 dm2，用各自工具的 update 命令重建（见「开发」）。
- **规范驱动** — 行为变更走 OpenSpec 变更：`openspec new change <name>` → proposal/design/tasks + delta spec → 实现 → `openspec archive`。规范（`openspec/specs/`）是行为的权威来源，实现与规范不符即为缺陷。
- **CLI 输出结构化 JSON** — 契约见 `openspec/specs/cli-json-contract`：读写项目/架构状态的命令接受 `--json`/`-j`，输出 `{"status":"success","data":{...}}` 或 `{"status":"error","error":{"code":"...","message":"..."}}`；JSON 模式下 stdout 只含信封（诊断走 stderr），项目守卫失败也必须返回信封。豁免（不得视为缺陷）：`completion`（输出 shell 脚本）、隐藏 `__complete`、`uninstall`（交互式人工维护）。
- **输出形状以 schema 声明** — `schemas/*.json` 声明各命令 JSON 输出的形状，由 `test/test_cli_output_schemas.py` 对照真实输出执行。改输出须同步改 schema；描述已移除能力的 schema 必须删除，不得留在树上腐烂。
- **视图生命周期** — 每个视图经过 `pending → in_progress → generated → verified` 四个状态，由 `.dm2/view-state.yaml` 管理。
- **变更生命周期** — 每个变更在 `dm2-changes/<name>/` 下有 proposal、design、tasks 和 views/ 目录。
- **路径优先** — `get_reference_path()` 优先 `.dm2/reference/` 本地副本，回退到包内置 `dm2-reference/core/`。
- **索引派生** — 改权威源 YAML（`dm2-data-dictionary.yaml` / `dm2-metamodel-2.02.yaml`）后必须重跑 `python3 scripts/build_knowledge_indexes.py` 再生成派生 JSON（快照测试 `test/test_knowledge_indexes.py` 会拦截未再生成的索引）；组模板 `relationships:` 槽位用 `--fix-templates` 从关联目录投影同步。运行时只加载紧凑 JSON，不解析 840KB 源 YAML。
- **约定优先于配置** — 文件名、目录结构是系统约定的接口，减少配置项。如需动态行为，走模板生成而非运行时配置。
- **测试风格** — 使用 pytest，测试放在 `test/` 目录，与 `src/dm2/` 结构对应。

## CLI 命令概要

完整参考见 `docs/readme.md`。常用命令分类：

- **项目管理**: `dm2 init` / `list` / `status` / `archive`
- **分析与生成**: `dm2 analyze` / `cynefin` / `generate` / `validate`
- **AI Agent 接口**: `dm2 knowledge` / `change` / `view` / `concern` / `instructions` / `run --agent`
- **配置与工具**: `dm2 config` / `completion` / `version`

## 项目模式（.dm2/）

`dm2 init` 创建的项目含：
- `.claude/skills/` + `.claude/commands/`（默认）或 `.dsh/skills/`（`--tool dsh`）— 从 Python 模板动态生成
- `.dm2/reference/` — 知识库本地副本
- `.dm2/view-state.yaml` — 视图生命周期状态
- `.dm2/analysis-state.yaml` — cynefin/analyze 结果持久化
- 可选通过 `DM2_VAULT_PATH` 链接 Obsidian vault
