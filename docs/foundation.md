# dm2-tool 地基

> 本文论证两件事：**当前 dm2 是什么**（附可复现证据），以及**改进后的 dm2 应该是什么**。
> 它是 dm2 的地基文档：架构边界、横切不变量、现状基线、已知裂缝与目标态。
>
> 读者分工：本文谈**地基**（为什么这样划界）；`docs/readme.md` 谈**用法**；`CLAUDE.md` 谈**Agent 约定**。
> 规范性要求以 `openspec/specs/` 为准，本文只做论证与索引。

---

## 1. 定位与边界

**dm2 是什么**：DoDAF Meta Model 2.02 的系统工程辅助工具。它提供 DM2 知识、视图规范、符合性规则和结构化指令，**由外部 AI Agent 执行具体内容生成**。

**dm2 不是什么**（这些边界是有意的，改动它们等于改产品定位）：

| 不是 | 原因 |
|---|---|
| 不是 LLM 应用 | 不调用任何 LLM API，不持有 API key。分析和生成都是本地规则/模板 |
| 不是视图渲染器 | 不产出视图正文。`generate`/`instructions` 产出的是给 Agent 的**指令载荷** |
| 不是流程引擎 | `run --agent` 是**步进状态机**，每一步都由 Agent 执行后回执推进，dm2 不自行推进 |
| 不是配置中心 | 项目行为由文件名与目录约定决定，不靠运行时配置项开关 |

核心模式一句话：**CLI 是大脑，AI 是手脚**。CLI 管状态、出指令；Agent 执行。

---

## 2. 四层架构

```
Agent Interface Layer  ← CLI --json + Knowledge API
Core Engine Layer      ← Instructions Engine / Artifact Graph / Change Manager / Pipeline V2
Knowledge Base Layer   ← DM2KnowledgeIndexer + MetamodelIndex（加载派生 JSON）
File System Layer      ← .dm2/ 项目 + dm2-changes/ + dm2-archive/
```

### 实测依赖方向

对 `src/dm2/**` 做 import 静态扫描得到的层间依赖边（数字为该方向的引用处数）：

| 上层 | 依赖的下层 |
|---|---|
| `cli` | `cognitive`(1)、`config`(1)、`core`(4)、`engine`(1)、`kernel`(1)、`reasoning`(1)、`utils`(2) |
| `engine` | `cognitive`(3)、`core`(2)、`kernel`(5)、`reasoning`(1)、`utils`(1) |
| `cognitive` | `kernel`(1)、`utils`(2) |
| `reasoning` | `kernel`(1)、`utils`(1) |
| `core` | `kernel`(1) |
| `kernel` | `utils`(2) |
| `config` | `utils`(1) |
| `utils` | —（**纯叶子层**，不依赖任何内部层） |

**关键结论：无反向依赖边。** 依赖方向严格自上而下，`utils` 是真叶子。这条架构原则在代码里是被真实遵守的，不是文档口号——因此值得用测试锁定（见 §3）。

### 允许与禁止的依赖

**允许**：上层依赖下层。`cli` 作为最上层可依赖全部；`engine` 作为编排层可依赖能力层与知识层。

**禁止**（下述边在实测中均不存在，须由测试保持）：

- `kernel` → `core` / `engine` / `cli`
- `utils` → 任何内部层
- `cognitive` / `reasoning` → `engine` / `cli`
- `config` → `cli` / `engine`
- 任何层 → `cli`（CLI 是入口，不是被依赖的库）

### 顶层目录的声明（试行）

一个顶层目录只承担一种角色，并**声明**自己的**作用**与**消费者**——它是干什么的、谁在读它。

之所以需要这份声明：`dm2-reference/reference/` 正是因为**没有任何地方写明它的消费者是谁**，才能零引用地存在很久，直到一次专门审计才发现它。`dm2-reference/` 原先还同时承担三种角色（运行时知识库、构建输入、源研究语料），于是打包配置也自相矛盾。

**本约定尚在试行：以声明为准，暂不加守护测试。** 先让它跑一段时间，等声明稳定、并确认它真能防住问题（而不是退化成填空作业），再考虑升格为「必须」。

| 目录 | 作用 | 消费者 |
|---|---|---|
| `src/dm2/` | 运行时 Python 包 | pip 入口 `dm2`；包内各层互引 |
| `dm2-reference/core/` | 运行时知识库：派生索引 + `views.yaml` + 组模板 | `kernel/indexer.py`（经 `get_reference_path()`）；`dm2 init` 复制到项目 |
| `dm2-reference/` 根 YAML | 权威源（数据字典 / 元模型 / 视图映射）＝构建输入；`concerns.yaml`＝运行时关切模板 | `scripts/build_knowledge_indexes.py`（前三者，仅构建）；`cli/commands/concern.py` 与 propose 技能模板（`concerns.yaml`） |
| `scripts/` | 权威源 YAML → 派生 JSON 索引 | 开发者手动运行（无自动调用者） |
| `schemas/` | CLI JSON 输出形状声明 | `test/test_cli_output_schemas.py` |
| `test/` | 测试套件 | `pytest`、CI |
| `docs/` | 文档；`docs/reference/` 为源研究语料 | 人类读者；`docs/reference/` **无代码消费者** |
| `openspec/` | 变更与规范语料 | `openspec` CLI（validate / archive）、CI `spec` job |
| `.claude/` | 生成的 agent 指令 | Claude Code；dm2 自产部分由 `test_generated_agent_config.py` 守护 |
| `.github/` | CI 工作流 | GitHub Actions |

> 分发不在本表之列，但它揭示了一个相关事实（D10）：项目的安装形态是 **editable / 源码检出**（文档也只写 `pip install -e .`）——2026-09-24 起这是**唯一正式支持**的形态：不发布 wheel/sdist 到 PyPI，非 editable 安装以 `KB_NOT_FOUND` 明确失败。

---

## 3. 横切不变量

每条不变量都必须有**守护锚点**（spec 或 test）。无锚点者视为「已声称但未守护」，属于地基缺口。

| # | 不变量 | 守护锚点 |
|---|---|---|
| I1 | 分层依赖方向自上而下，`utils` 为叶子 | `test/test_architecture_boundaries.py` |
| I2 | 所有读写项目/架构状态的命令接受 `--json` 并输出统一信封 | `openspec/specs/cli-json-contract`、`test/test_cli_json_contract.py` |
| I3 | JSON 模式下 stdout 只含单个信封（诊断走 stderr） | 同上 |
| I4 | 分发不声明 LLM 依赖、源码不导入 LLM 客户端 | `openspec/specs/dm2-no-llm-dependency` |
| I5 | 视图生命周期 `pending → in_progress → generated → verified` | `openspec/specs/view-lifecycle` |
| I6 | 变更生命周期：`dm2-changes/<name>/` 下 proposal/design/tasks/views | `openspec/specs/dm2-project-init` |
| I7 | 知识库权威源为 YAML，运行时只加载派生 JSON | `openspec/specs/dm2-metamodel-knowledge` |
| I8 | 技能由 Python 模板 + `ToolAdapter` 生成，不从开发者目录复制 | `openspec/specs/skill-template-generation`、`tool-command-adapter` |
| I9 | 生成物按**归属**决定入库与守护：dm2 自产的入库并由字节一致性测试守护；第三方工具产出的不入库，由该工具的 update 命令重建 | `test/test_generated_agent_config.py`、`.gitignore` |

---

## 4. 当前态基线

以下数值可用所列命令复现，作为后续回归对比的基准（2026-09 实测，**已含本次地基变更**）：

| 指标 | 数值 | 复现命令 |
|---|---|---|
| spec 数 | 35 | `ls -d openspec/specs/*/ \| wc -l` |
| requirement 总数 | 135 | `grep -rh '^### Requirement:' openspec/specs/*/spec.md \| wc -l` |
| spec 校验 | 36 项通过 / 0 失败（strict 无警告） | `openspec validate --all --strict` |
| 测试 | 236 passed | `pytest test/` |
| 顶层命令 | 18 | `dm2 --help` |
| 命令 JSON 契约 | 28 flag 门控 + 2 无 JSON（均属豁免，共 30） | 见 §5 D2/D3/D4 |
| 知识库 | 279 术语 / 52 视图 / 17 数据组 | `dm2 knowledge stats --json` |
| 工作流技能 | 10 个工作流 × 2 个适配器目标 | `dm2 init -t claude\|dsh` |
| Python 下限 | `>=3.9`，CI 矩阵 3.9–3.12 | `pyproject.toml`、`.github/workflows/test.yml` |
| 分发形态 | **editable-only**（`pip install -e .`），无 PyPI 发布 | 本节 §2、§5 D10 |

> 地基变更前的基线为 33 spec / 119 requirement / 194 测试 / 27 flag 门控 + 1 总是 JSON + 2 无 JSON；差异来自新增契约与守护测试，以及 `view register` 补上 `--json`。此后 `wire-cli-output-schemas`、`remove-llm-packaging-residuals`、`report-missing-knowledge-base` 等变更继续推高了这些数字——上表数值随时可用所列命令复现。

**已验证的强项**（本次不改其行为，仅用测试锁定）：

- **S1 分层干净**：见 §2，无反向依赖 → 已由 `test_architecture_boundaries.py` 守护。
- **S2 规范有规模**：35 spec / 135 requirement，strict 全量校验通过 → 已由 CI `spec` job 守护。
- **S3 质量关口存在**：236 测试绿、ruff 干净、CI 覆盖 3.9–3.12；代码经 3.9.6 实跑验证兼容。
- **S4 零 LLM 已规范化**：`dm2-no-llm-dependency` 覆盖源码、打包与用户可见面。
- **S5 适配缝已验证**：`ToolAdapter` 由 claude/dsh 两个目标证实可用。
- **S6 信封覆盖率高**：30 个命令中 28 个输出统一信封，另 2 个为显式豁免 → 已由 `test_cli_json_contract.py` 守护。

---

## 5. 已识别裂缝

按处置状态分三类。**严重度**：高 = 破坏 Agent 机器可读契约或造成规范失真；中 = 元数据/文档失真；低 = 需判定。

### 已修复

| # | 裂缝 | 证据 | 修复 |
|---|---|---|---|
| D1 | 无架构/地基专文 | `docs/` 原本仅 4 文件，无架构文档 | 本文 |
| D2 | JSON 信封契约**无 spec、无测试守护** | `openspec/specs/**` 无信封契约；`test/` 无 `json_output` 引用 | `openspec/specs/cli-json-contract` + `test/test_cli_json_contract.py` |
| D3 | **项目守卫覆盖不全**（一个缺陷族，见下） | — | 全局修复：守卫感知 JSON；补齐缺失守卫；写入前置守卫 |
| D3a | 守卫失败时 stdout 被污染，信封破裂 | `dm2 list --json` 在非 `.dm2` 目录：exit 1 但 stdout 为纯文本 `错误: 当前目录不在 .dm2 项目中…` | 守卫在 JSON 模式输出 `NOT_IN_PROJECT` 信封 |
| D3b | **`view list` / `view register` 完全没有守卫**，静默在任意 CWD 创建 `.dm2/` | 实测在 `/tmp` 执行 `view register` 后生成 `/tmp/.dm2/view-state.yaml` 且返回 `status: success`（`ViewManager.__init__` 以 `Path.cwd()` 回退） | 两命令补守卫 |
| D3c | **`run` 没有守卫**，项目外静默创建 `.dm2/state.yaml` 并返回成功 | 实测项目外 `run --agent` 返回 `status: success` 并生成 `.dm2/state.yaml` | 补守卫；Agent 子模式输出信封 |
| D3d | **`validate` 没有守卫**，项目外返回**误导性成功** | 实测项目外 `validate --all --json` 返回 `status: success`、`issues: []`，Agent 会误判为校验通过 | 补守卫 |
| D3e | `config -s` 的守卫在写入**之后**执行 | 项目外 `config -s k=v` 先落盘用户配置再报错 | 守卫前置到写入之前 |
| D4 | **`view register` 拒绝 `--json`，而 5 个技能模板要求「总是传 `--json`」**——同一模板内部自相矛盾 | 实测 `No such option: --json`；`apply`/`archive`/`continue`/`ff`/`onboard` 各含 "Always pass `--json`"，而 6 处 `view register` 示例都不敢加该 flag | 命令接受 `--json/-j` |
| D5 | 4 个 spec 的 Purpose 是归档占位符 | `TBD - created by archiving change …`：`dm2-explore-workflow`、`dm2-metamodel-knowledge`、`no-new-capability`、`view-register` | 逐一补全为真实 Purpose |
| D5b | `dm2-data-group-activation` 标题层级不合约定（`## 标题` + `### Purpose`） | 该 spec 仍能通过校验，但结构与其他 21 个不一致 | 规范化为 `# 标题` / `## Purpose` |
| D6 | `templates/` 是**死目录**（却被 git 跟踪），`CLAUDE.md` 称其被 `dm2 init` 使用 | `templates/init/.dm2/config.yaml` 已跟踪；全仓无代码引用；`init` 在 `main.py` 内联构造 `template_config` | 删除目录并修正 `CLAUDE.md` |
| D7 | **CI 不校验 spec**——这是历史上 17 个 spec 烂掉的根因 | `test.yml` 仅有 `pytest` + `ruff check src/ test/` | CI 增加 `openspec validate --all` |
| D10（运行时半边） | **知识库缺失时静默给空答案**：`get_reference_path()` 在两条候选都不存在时仍返回 `base`，索引器 glob 空目录后报成功 | 隔离 venv 中 `pip install .`：`dm2 knowledge stats` → 全 0、`dm2 concern list` → 空，**均 exit 0** | 由 `report-missing-knowledge-base` 修复：抛 `KnowledgeBaseNotFound`，中央报错输出 `KB_NOT_FOUND` 信封（人类模式给可操作提示）；`concerns.yaml` 同样处理；`test/test_missing_knowledge_base.py` 守护 |

### 显式判定为豁免（记录而非修复）

| # | 项 | 判定 |
|---|---|---|
| D8 | `uninstall` 交互式、无 JSON、无 `--yes` | **豁免**：它是带交互确认的人工维护命令。给 Agent 自动卸载能力与地基目标相悖。豁免写入 `cli-json-contract` 的豁免清单，避免成为「未判定的不一致」 |

### 已记录、明确延后

| # | 项 | 证据 | 为何延后 |
|---|---|---|---|
| D9 | `knowledge search` 中文召回为 0 | `search "资源流"` → 0；`search Performer` → 10 | 属知识库**内容层**（需中文别名索引），与契约地基不同类，单独变更更清晰 |
| D10（分发半边） | **`dm2-reference/` 不随包分发**：`package-data` 覆盖不到 `src/` 之外的路径（`dm2 = ["dm2-reference/core/**/*"]` 还指向 `src/dm2/` 下并不存在的路径），且代码靠从 `src/dm2/` 向上回溯定位知识库与 `concerns.yaml`——因此非 editable 安装拿不到运行时知识库 | 实测 `SOURCES.txt`：`dm2-reference/core/` 48 条；根 YAML、`scripts/`、`schemas/` 均 0 条 | 运行时半边已修（见上表），本项只剩**分发形态**决策：是否支持正式 wheel 分发。会显著改动打包布局，且文档与 CI 都只走 `pip install -e .`，当前无实际受害者。**2026-09-24 复核后判定：正式确立 editable-only**——隔离 venv 实测 sdist→wheel 会静默丢弃包外数据文件（wheel 的 `dm2/` 内零 json/yaml），非 editable 安装确定不可用（现在干净地报 `KB_NOT_FOUND` 而非空答案）；据此删除 MANIFEST.in 与 release.yml（后者会在打 tag 时把坏 wheel 发布到 PyPI）。待真实分发需求出现时，再以「运行时资产迁入 `src/dm2/`」的专门变更关闭本项 |

---

## 6. 目标态：改进后的 dm2

**一句话**：一个**契约明确、可自我校验**的纯 CLI 知识工具——它的每一条承诺都有 spec 与测试守护，且这些守护在 CI 中自动执行。

### 五条原则

1. **CLI 是大脑，AI 是手脚**——dm2 管状态与指令，不接管内容生成。新增功能先问：这是大脑的职责还是手脚的职责？
2. **零 LLM**——不导入、不声明、不文档化 LLM 依赖。LLM 配置属于 Agent 层。
3. **约定优先于配置**——文件名与目录结构就是接口。需要动态行为时走模板生成，而非引入运行时开关。
4. **spec 驱动**——行为变更走 OpenSpec 变更（proposal → delta spec → 实现 → 归档），spec 是行为的权威来源。
5. **知识库接地**——涉及 DM2 的论断必须能在 `views.yaml` / 派生索引中找到依据，不凭印象。

### 从当前态到目标态的差距

目标态与当前态的主要差距**不在功能，而在「承诺的守护强度」**：

- 架构原则已遵守（S1）→ 但无测试守护 → 补 I1
- 信封契约已大范围实践（S6）→ 但无 spec、无测试、且有破例（D2/D3/D4）→ 补 I2/I3
- 规范体系已成规模（S2）→ 但无 CI 关口、元数据有残缺（D5/D7）→ 补关口与元数据

因此改进路径 = **把已经做对的事，变成不会被悄悄做错的事**。

---

## 7. 非目标

以下明确不在本次地基范围，且各有理由：

| 非目标 | 理由 |
|---|---|
| 环境适配（DSH 原生工具、agent preset、多工具分发） | 按用户决定延后；地基稳后再谈 |
| 中文检索召回（D9） | 知识库内容层问题，独立变更 |
| 非交互式 `uninstall` / `--yes` | 判定为豁免（D8） |
| 合并 `_require_project` 的多份拷贝 | 属重构，超出地基范围；本次仅补齐缺失的守卫并统一其语义，三份拷贝保持独立（不得下沉到 `utils`——那会形成向上依赖，破坏 I1） |
| 既有 spec 体系的全面审计 | 本次仅补 Purpose 与新增两条契约 |
| 视图/变更生命周期状态机、知识库索引生成逻辑 | 已有 spec 覆盖，无已知裂缝 |
