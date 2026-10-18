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
| `scripts/` | 权威源 YAML → 派生 JSON 索引；技能模板 → 入库 agent 产物 | 开发者手动运行（无自动调用者） |
| `schemas/` | CLI JSON 输出形状声明 | `test/test_cli_output_schemas.py` |
| `test/` | 测试套件 | `pytest`、CI |
| `docs/` | 文档；`docs/reference/` 为源研究语料 | 人类读者；`docs/reference/` **无代码消费者** |
| `openspec/` | 变更与规范语料 | `openspec` CLI（validate / archive）、CI `spec` job |
| `.claude/` | 生成的 agent 指令（Claude Code 目标） | Claude Code；dm2 自产部分由 `test_generated_agent_config.py` 守护 |
| `.dsh/skills/` | 生成的 agent 指令（DSH 目标） | DSH 会话（source `project-dsh`）；dm2 自产部分由 `test_generated_agent_config.py` 守护 |
| `.agents/skills/` | openspec 的 SDD 技能（**第三方生成，不入库**） | DSH 会话（source `project-agents`）；openspec CLI 的 init/update 重建 |
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
| I9 | 生成物按**归属**决定入库与守护：dm2 自产的入库并由字节一致性测试守护；第三方工具产出的不入库，由该工具的 update 命令重建 | `test/test_generated_agent_config.py`（字节守护覆盖 `.claude` + `.dsh`；`.agents` 由 ignore 断言守护）、`.gitignore` |
| I10 | 视图溯源两层分离：事实层由 CLI 捕获（注册/转换/校验/内容哈希），理由层只由外部 AI Agent 声明且在审计中标注为未经验证；`verified` 受溯源完整性门控 | `openspec/specs/view-provenance`、`test/test_e2e_pedigree.py`、`test/test_view_lifecycle_pedigree.py` |

---

## 4. 当前态基线

以下数值可用所列命令复现，作为后续回归对比的基准（2026-09 地基变更后实测；2026-10-10 复核刷新）：

| 指标 | 数值 | 复现命令 |
|---|---|---|
| spec 数 | 38 | `ls -d openspec/specs/*/ \| wc -l` |
| requirement 总数 | 166 | `grep -rh '^### Requirement:' openspec/specs/*/spec.md \| wc -l` |
| spec 校验 | 38 项通过 / 0 失败（strict 无警告；openspec 1.14.1 的额外风格规则要求 requirement 正文 ≤500 字符，本仓库已满足） | `openspec validate --all --strict` |
| 测试 | 742 passed | `pytest test/` |
| 顶层命令 | 21 | `dm2 --help` |
| 命令 JSON 契约 | 34 flag 门控 + 3 豁免（`completion`/`__complete`/`uninstall`，共 37） | 见 §5 D2/D3/D4 |
| 知识库 | 279 术语 / 52 视图 / 17 数据组 | `dm2 knowledge stats --json` |
| 工作流技能 | 10 个工作流 × 2 个适配器目标（`.claude` + `.dsh` 均入库并由字节守护） | `dm2 init -t claude\|dsh` |
| Python 下限 | `>=3.9`，CI 矩阵 3.9–3.12 | `pyproject.toml`、`.github/workflows/test.yml` |
| 分发形态 | **editable-only**（`pip install -e .`），无 PyPI 发布 | 本节 §2、§5 D10 |

> 地基变更前的基线为 33 spec / 119 requirement / 194 测试 / 27 flag 门控 + 1 总是 JSON + 2 无 JSON；差异来自新增契约与守护测试，以及 `view register` 补上 `--json`。此后 `wire-cli-output-schemas`、`remove-llm-packaging-residuals`、`report-missing-knowledge-base` 等变更继续推高了这些数字——上表数值随时可用所列命令复现。
>
> 2026-10-10：开发环境切到 DSH + SDD（`.agents/skills` 承载 openspec 技能、`.dsh/skills` 承载 dm2 技能），
> 测试数 236 → 239（字节守护从 `.claude` 扩展到 `.dsh`）。
>
> 2026-10-10：`add-view-provenance` 归档（新增 `view-provenance`/`audit-report` 两个 spec，另更新 5 个），
> 数字变为 37 spec / 158 requirement / 366 测试 / 21 顶层命令（新增 `trace`、`audit`、`audit-report`）；
> 不变量新增 I10（视图溯源两层分离 + `verified` 门控）。
>
> 2026-10-10：`add-chinese-term-aliases` 归档（关闭 D9，只更新 `dm2-metamodel-knowledge` 一个 spec：
> +1 requirement / ~2 modified），数字变为 37 spec / 159 requirement / 389 测试；
> 术语检索新增中文别名与分词召回，来源为 `dm2-reference/dm2-term-zh-aliases.yaml`。
>
> 2026-10-12：`add-data-element-qualifier-model` 归档（新增 `dm2-element-vocabulary` spec，+3 requirement），
> 数字变为 38 spec / 162 requirement / 415 测试。术语名改按 GB/T 18391 的
> 「数据元 + 限定词 + 关系模板」建模（`dm2-element-vocabulary.yaml` + `src/dm2/kernel/elements.py`），
> 构建期强制词元全覆盖，组合结果与人工别名层对账（实体 100%、关联 96.2%，4 条分歧显式登记）。
> 这是 D9 之后的检索质量路线 **P1（模型与校验）**；P2 词元归一检索、P3 查询分解与命中理由、
> P4 新术语自动命名仍待做，P1 本身不改运行时行为。
>
> 2026-10-12：`wire-element-model-into-search` 归档（**P2**，只更新 `dm2-metamodel-knowledge`
> 两个 requirement，spec/requirement 总数不变），数字变为 38 spec / 162 requirement / 429 测试。
> `terms.json` 新增 `canonical_zh`；检索新增词元归一（`能力` → capability）与结构化命中分层，
> 实测 `能力 活动` 由关系术语领先（此前首条是 `Activity`），规范名可检索；无法归一的片段回退子串，
> 召回不回退。P3/P4 仍待做。
>
> 2026-10-12：`explain-search-matches` 归档（**P3**：`dm2-element-vocabulary` +2 requirement，
> `dm2-metamodel-knowledge` 原地更新），数字变为 38 spec / 164 requirement / 446 测试。
> 新增查询**反向分解**（`plan_query`）与**词元模式**层（顺序子序列匹配），排序扩为五层；
> `knowledge search --explain` 输出命中理由（`match`：tier/kind/pattern/segments），
> 默认输出不变。实测 `活动 属于 能力` 以词元模式命中 `activityPartOfCapability`，
> 反序查询退到结构化层。
>
> 2026-10-12：`auto-name-new-terms` 归档（**P4**，检索质量路线收官），
> 数字变为 38 spec / 166 requirement / 456 测试。中文名的强制来源从「人工别名」转为
> 「组合结果」（构建期校验 `canonical_zh` 非空）；按术语的策展别名降级为**可选补充**，
> 但数据组别名（17 组）转为**强制**。新增 `dm2 knowledge compose` 命名预检：
> 新术语由既有词元组成即自动命名（实测合成术语 `CapabilityPartOfProject` 零手写内容得到
> 「能力属于项目」并可检索），含未登记词元则构建失败并列出缺失词元。
>
> 2026-10-13：`comply-with-openspec-1-14-style` 归档——纯规范文本重构，无代码与行为变更；11 条 requirement 正文符合 1.14 风格规则，CI 与本地同版本同口径，strict 关口恢复 38/38。数字不变：38 spec / 166 requirement / 456 测试。
>
> 2026-10-14：**CI 首次全绿**（D12 修复，21 个积压提交推送 + `v0.2.0` 发版）。同一轮修掉 D13（模板 CLI 调用）并补其守护，测试 456 → **481**（+25 条模板调用可解析性用例）。同时订正本表两处滞后数字：requirement 164 → 166（`auto-name-new-terms` 归档时已变，表与 S2 未跟改）、测试 456 → 481。数字：38 spec / 166 requirement / 481 测试。
>
> 2026-10-14：**`engine/` 全层补测试（D14）**——这是该层第一次有覆盖。新增 9 个测试文件、**197 条用例**（`test_view_generator` / `test_step6_documentation` / `test_six_w_analyzer` / `test_consistency` / `test_step1_intent_scope` / `test_step3_data_requirements` / `test_step5_analysis` / `test_pipeline_state` / `test_pipeline_orchestrator`），测试 481 → **678**。其中 12 条缺陷按「先补网、后修复」的次序就地**钉住**（测试注释里以 `DEFECT-N` 标注 + 文件头说明），修复时测试转红即提醒改写期望；编排骨架经核实符合规格、直接锁死。数字：38 spec / 166 requirement / 678 测试。
>
> 2026-10-14：**D14 的 12 处缺陷全部修复**（变更 `fix-legacy-engine-defects`：proposal / 4 份 spec delta / design / 13 条 tasks，已归档前状态）。新增规格能力 `six-w-analysis`（6W 维度打分 + 七个实体桶，此前**完全无规格**），修改 `step1-intent-scope` / `step5-analysis` / `step6-documentation` 三份。端到端核验时发现并一并修掉 **D15**（视图输出目录与规格不符），其修正又暴露 `save_views` 的项目根解析缺陷。修复过程中把一处规格措辞收窄到关键词启发式**确实能保证**的范围（匹配到锚点为止、桶间不重复），而不是让规格承诺「解析出实体」。数字：38 spec / 166 requirement / **742 测试**。

> 2026-10-18：**`v0.3.0` 发版**（BREAKING）。`representation` 与 `format` 拆为正交两轴：载体由
> `views.formats` 决定（override → project default → 表征派生），`pictorial` 默认改为独立 SVG；
> `dm2 validate` 按「表征 + 载体」组合核对内容证据；移除旧键 `views.include_mermaid` 与
> `views.diagram_output`。另修三处工具缺陷：workflow 模板的 `--reasoning-file` 骨架不完整、
> 两条 prose-heuristic 提取器把语法当内容误报、R5「必要关联」跨视图聚合导致单视图 frontmatter
> 可使全项目告警消失。新增规格能力 `view-output-format`。数字：40 spec / 178 requirement / **803 测试**。

**已验证的强项**（本次不改其行为，仅用测试锁定）：

- **S1 分层干净**：见 §2，无反向依赖 → 已由 `test_architecture_boundaries.py` 守护。
- **S2 规范有规模**：38 spec / 166 requirement，strict 全量校验通过 → 已由 CI `spec` job 守护。
- **S3 质量关口存在**：742 测试绿、ruff 干净、CI 覆盖 3.9–3.12；代码经 3.9.6 实跑验证兼容。
- **S4 零 LLM 已规范化**：`dm2-no-llm-dependency` 覆盖源码、打包与用户可见面。
- **S5 适配缝已验证**：`ToolAdapter` 由 claude/dsh 两个目标证实可用。
- **S6 信封覆盖率高**：37 个命令中 34 个输出统一信封，另 3 个为显式豁免 → 已由 `test_cli_json_contract.py` 守护。

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
| D9 | `knowledge search` **中文召回为 0**（记录时以为只是内容层，实测连 `"resource flow"` 也 0：字典的定义/别名 279 条全英文） | `search "资源流"` → 0；`search Performer` → 10；`definition`/`aliases` 含中文的术语数 = 0 | 由 `add-chinese-term-aliases` 修复：新增策展源 `dm2-term-zh-aliases.yaml`（279 术语 + 17 数据组中文别名）→ `terms.json` 的 `zh_aliases`/`zh_groups`；检索分词（多 token AND）+ 三层排序；构建校验未知键/空别名/重复别名，测试守护「每术语必有别名」 |
| D11 | `openspec` 升级到 1.14.1 后，新风格规则（requirement 正文 >500 字符 → WARNING）让本地 strict 关口对 5 个既有 spec 判红，而 CI 因锁定 1.13.1 判绿——本地与 CI 口径不一致 | `openspec --version` → 1.14.1；`validate --all --strict` → 33/5 失败，失败项只有该警告 | 由 `comply-with-openspec-1-14-style` 修复：11 条 requirement 正文压到 ≤487 字符（表格/字段清单/示例移入场景，既有场景逐字保留、SHALL 语义不减），CI 同步升到 `@fission-ai/openspec@1.14.1`，两侧均为 38/38 |
| **D12** | **CI 从未绿过**——`Tests` 与 `Verify` 自初始提交起每一次运行都失败，而本地 macOS 全绿，故长期无人察觉 | 两个根因都只在 CI 环境成立：① `test/_cli.py` 在函数签名里用了 PEP 604（`str | None`）却没有 `from __future__ import annotations`——签名注解是定义期求值，3.9 直接 `TypeError`，且只有 2 个测试文件 import 它，于是 pytest 报 2 个 collection error 后**中止整个 3.9 作业**（一个测试都没跑）；② `test_cli_json_contract.py` 断言 `"--json" in result.stdout`，而 rich 在 `GITHUB_ACTIONS` 下判定环境支持颜色，把选项名拆成 `-\x1b[0m\x1b[1;36m-json`，字面量被转义序列打断，35 个命令全部误报 | ① 补 `from __future__ import annotations`；② 断言前剥离 ANSI SGR 序列。复现方法：`GITHUB_ACTIONS=true pytest` 暴露 ②，`uv python install 3.9` 建真 3.9 venv 暴露 ①（`ruff` 拦不住 ①——本仓库只选 `E/F/W/I`，未开 pyupgrade 的 `UP007`）。3.9.25 / 3.11.16 / 3.13.12 × GITHUB_ACTIONS 开与关共 6 组全绿 |
| **D13** | **工作流模板里的 CLI 调用无人校验**——模板是 `.claude/skills/` 与 `.dsh/skills/` 的源，一条 CLI 拒绝的命令会作为「坏指令」发给用户 | 实测 `analyze "<description>" --json`（该命令只接受 `--desc`/`-d`）出现在 ff 与 onboard 模板，渲染进 4 个入库 SKILL.md，运行即 exit 2「Got unexpected extra argument(s)」。另有两处同类：`verify.py` 让 agent 写 `dm2-changes/<name>/reports/verify.md`（`ChangeManager.create` 只建 `analysis`/`views`/`delta-specs`，从不建 `reports/`）；`onboard.py` 宣传 `/dm2:knowledge ...`（`.claude/commands/dm2/` 下无该斜杠命令） | 由本轮修复：`analyze -d`、报告改存 `analysis/`（与 `apply`/`ff` 写 trace 的目录一致）、`/dm2:knowledge` 改 `dm2 knowledge`（模板正文其余位置已在用该裸形式）。**新增守护** `test/test_workflow_templates.py::TestTemplateCliInvocations`：抽出模板里每条 `python3 -m dm2.cli.main …` 调用，用真实解析器验证可解析（不执行）。⚠️ 两个陷阱都踩过并已记入该测试注释：`make_context` 在根上因 `TyperGroup.allow_extra_args=True` 从不下降；`isinstance(cmd, click.Group)` 恒假，因 `TyperGroup` 派生自 `click.Command` |

### 显式判定为豁免（记录而非修复）

| # | 项 | 判定 |
|---|---|---|
| D8 | `uninstall` 交互式、无 JSON、无 `--yes` | **豁免**：它是带交互确认的人工维护命令。给 Agent 自动卸载能力与地基目标相悖。豁免写入 `cli-json-contract` 的豁免清单，避免成为「未判定的不一致」 |

### 已记录、明确延后

| # | 项 | 证据 | 为何延后 |
|---|---|---|---|
| D10（分发半边） | **`dm2-reference/` 不随包分发**：`package-data` 覆盖不到 `src/` 之外的路径（`dm2 = ["dm2-reference/core/**/*"]` 还指向 `src/dm2/` 下并不存在的路径），且代码靠从 `src/dm2/` 向上回溯定位知识库与 `concerns.yaml`——因此非 editable 安装拿不到运行时知识库 | 实测 `SOURCES.txt`：`dm2-reference/core/` 48 条；根 YAML、`scripts/`、`schemas/` 均 0 条 | 运行时半边已修（见上表），本项只剩**分发形态**决策：是否支持正式 wheel 分发。会显著改动打包布局，且文档与 CI 都只走 `pip install -e .`，当前无实际受害者。**2026-09-24 复核后判定：正式确立 editable-only**——隔离 venv 实测 sdist→wheel 会静默丢弃包外数据文件（wheel 的 `dm2/` 内零 json/yaml），非 editable 安装确定不可用（现在干净地报 `KB_NOT_FOUND` 而非空答案）；据此删除 MANIFEST.in 与 release.yml（后者会在打 tag 时把坏 wheel 发布到 PyPI）。待真实分发需求出现时，再以「运行时资产迁入 `src/dm2/`」的专门变更关闭本项 |
| **D14** | **legacy V1 引擎的 12 处缺陷**——`src/dm2/engine/` 全层 + `six_w_analyzer` / `consistency`。该层只经 `dm2 run` **不带 `--agent`** 到达（`src/dm2/cli/main.py:1391`），此前**零测试覆盖**，故长期无人发现。**2026-10-14 已全部补上表征测试并就地钉住**（每条缺陷在测试文件里以 `DEFECT-N` 标注，修复后该测试即失败，提醒改写期望） | **A 产出错误内容**：`D1` `view_generator._find_template_file` 用绝对 pattern 调 `Path.glob` 必抛 `NotImplementedError`（且它要找的 `dm2-reference/core/详细分析/` 目录根本不存在）；`D2` 该异常从 `fill()` 直接外抛；`D3` `step6` 的裸 `except Exception` 吞掉它，把 OV-1/OV-2/OV-5a 写成 `视图生成待 LLM 填充`——**该占位文案违反自家 `dm2-no-llm-dependency` 契约**；`D4` `six_w_analyzer` 声明 7 个实体桶只实现 3 个（`resource`/`capability`/`location`/`measure` 恒空，CLI 又过滤空桶，故用户看不到）；`D5` 中文正则贪心，匹配吞掉相邻整句。<br>**B 静默失效**：`D6` `consistency` 时序环检测不可达（`['prerequisite'] = []` 恒空 → `_find_cycles` 恒返回空；`_find_cycles` 本身正确，缺陷在调用方）——而 step5 规格明确要求 circular dependency detection；`D7` `step1` 的 `DM2_GROUP_TOKEN_ESTIMATES` 键（`"01-Performer"`）与调用方传入的裸名（`"Performer"`）**零重叠**，也与真实目录名（`00-foundation`）对不上，17 条估值全失效；`D8` `step1` 每个 6W 写了两条反问，只用 `templates[0]`；且 WHY 为主维度时回退分支重复追加同一问题。<br>**C 空占位**：`D9` `step3` `required_concepts` 恒 `[]`；`D10` `_build_taxonomy(…, concepts)` 的 `concepts` 参数函数体未用；`D11` `step5` 溯因推理端点恒为 `"未知"` / `"(从描述提取)"`；`D12` `step5` `TOCBottleneck.out_degree` 写死 `1` | **2026-10-14 已全部修复**（变更 `fix-legacy-engine-defects`：先补表征测试钉住，再逐处修复并把断言改写成正确行为）。守护文件：`test_view_generator.py`(D1/D2)、`test_step6_documentation.py`(D3)、`test_six_w_analyzer.py`(D4/D5)、`test_consistency.py`(D6)、`test_step1_intent_scope.py`(D7/D8)、`test_step3_data_requirements.py`(D9/D10)、`test_step5_analysis.py`(D11/D12)。编排骨架（`pipeline_orchestrator` / `state_manager`）经核实**符合规格**，已锁入 `test_pipeline_orchestrator.py` / `test_pipeline_state.py`。修复要点：D1 直接删掉永远失败的文件模板查找（规格只要求产出视图文档，`_fill_from_scratch` 本就能产出）；D3 改为「记录为未生成、不写文件」；D4/D7 两处都是**词汇漂移**，统一到单一来源并加可达性断言；D5 名词桶保留前缀类、动词桶不带前缀（动词的锚点是动词，任何不定长前缀都会吞主语）；D6 只修调用方，`_find_cycles` 本身正确；D9/D10 是无人读的 API，直接删除 |
| **D15** | **编排器把视图写到 `<项目>/output/`，而 step6 规格与 step6 自身都写 `.dm2/output/`**——修复 D14 的端到端核验时发现 | 证据 4:1 倒向 `.dm2/output/`：规格 `step6-documentation` §Documentation output 两处（沿用自归档变更 `complete-6step-pipeline` 任务 5.6）、`step6_documentation.py` 模块文档串、`DocumentationResult.output_dir` 字段；只有 `pipeline_orchestrator.py:77,153` 写 `output/`，`CLAUDE.md:54` 的四层图也跟着错 | **2026-10-14 已修复**：编排器改指 `.dm2/output/`；`CLAUDE.md` 四层图订正；守护 `test_pipeline_orchestrator.py::test_view_files_land_in_dot_dm2_output` + `test_no_bare_output_directory_is_created`。⚠️ **顺带暴露一个潜在缺陷**：`save_views` 用 `output_dir.parent` 当项目根去构造 `ViewManager`，一旦输出目录多一层（正是本次修正）就会把视图注册进 `.dm2/.dm2/`；已改为用 `get_project_root(output_dir)` 向上找项目标记。测试夹具 `tmp_project` 原先也建的是裸 `output/`，同步订正 |



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
| DSH 产品面原生化（agent preset、`@local/dsh-tool-dm2` 原生工具插件、多工具分发） | 2026-10-10 起**开发环境**已切到 DSH + SDD（`.agents/skills` 承载 openspec 技能、`.dsh/skills` 承载 dm2 技能，见 §2）；产品面原生化仍延后，待开发环境稳定后单独立项 |
| 非交互式 `uninstall` / `--yes` | 判定为豁免（D8） |
| 合并 `_require_project` 的多份拷贝 | 属重构，超出地基范围；本次仅补齐缺失的守卫并统一其语义，三份拷贝保持独立（不得下沉到 `utils`——那会形成向上依赖，破坏 I1） |
| 既有 spec 体系的全面审计 | 本次仅补 Purpose 与新增两条契约 |
| 视图/变更生命周期状态机、知识库索引生成逻辑 | 已有 spec 覆盖，无已知裂缝 |
