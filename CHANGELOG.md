# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **视图载体格式成为一等概念（`views.formats`）**：`representation`（传达什么信息结构）与
  `format`（用什么载体）拆为两个正交轴，二者由**兼容矩阵**关联，而不是一对一映射。
  - `views.formats.overrides.<View-ID>` 按视图指定载体；`views.formats.default` 平移
    图类视图的默认载体（不影响 table/text）
  - `dm2 instructions` 的 `template` 新增 `representation` / `format` / `format_source`；
    段落与规则按载体分派（markdown / mermaid / svg / png / html / xlsx / csv / mp4）
  - 外部载体（html / xlsx / csv / mp4）由外部产出并在视图中引用，规则中明确说明
  - 视频是**载体**而非表征：`pictorial` × `mp4` 可声明，`table` × `mp4` 不可
- **视图表征一致性检查**：`dm2 validate` 新增 `RepresentationChecker`，比对视图在
  `views.yaml` 中声明的 `representation` 与实际内容（Mermaid 图型 / 外部图引用 / 无图）。
  默认 WARNING，`consistency.strict_mode: true` 时升级为 ERROR。外部图引用
  （`.svg` / `.png` / `.jpg`）视为满足图示要求，因此以独立图绘制的项目不会被误报。

### Changed
- **`dm2 validate` 改为按「表征 + 载体」组合校验视图**：`RepresentationChecker` 不再只看 Mermaid，
  而是先解析每个视图的载体格式，再核对内容证据。
  - `markdown` → 不得含 Mermaid（作为插图引用的图文件允许）
  - `mermaid` → 图型须与表征匹配；声明 mermaid 却只放了独立图文件也算不匹配
  - `svg` / `png` / `html` / `xlsx` / `csv` / `mp4` → 正文须引用对应扩展名的产物
  - 新增问题类型 `representation_missing_artifact`；其余沿用既有类型名
  - 既有项目中「画了独立图但未声明载体」的视图会收到新的 WARNING（默认不阻断，
    `consistency.strict_mode` 下升级为 ERROR），提示补 `views.formats.overrides`
- **解析逻辑下沉**：`resolve_view_format` / `MERMAID_TYPE_BY_REPRESENTATION` /
  `ARTEFACT_EXTENSIONS` 移入 `dm2.kernel.formats`，`instructions.py` 与校验器共用同一实现
- **BREAKING（行为）**：`pictorial` 视图（如 OV-1）的默认载体由内联 Mermaid 改为独立 SVG ——
  概念图的语义在版面本身，Mermaid 节点图会把它压平成关系网络。需要旧行为的项目配置
  `views.formats.overrides.OV-1: mermaid` 即可。
- **BREAKING：移除 `views.include_mermaid` 与 `views.diagram_output`**，由 `views.formats` 取代：
  - `include_mermaid: false` → `formats.default: svg`，个别视图用 `formats.overrides` 指定
  - `diagram_output: svg` → `formats.default: svg`
  - `diagram_output: mermaid` → 直接删除（本来就是默认）
  - 残留的旧键不再被读取，会被静默忽略
- `dm2 init` 的配置骨架改为从 `config.manager.DEFAULTS` 派生，不再手抄一份默认值
  （原手抄字典已漏掉 `trace.enabled`）。新项目会显式写入 `views.formats`。

### Fixed
- **R5「必要关联」跨视图聚合**：`check_view_required` 从**所有笔记**累计已声明关联，再按视图比对 ——
  于是任意一个视图的 frontmatter 会让**全项目**的 R5 告警消失。实测：给一个无关视图声明全部槽位后，
  SV-6 与 CV-1 的问题数由 1 变成 0。该缺陷在「全项目都没有 frontmatter」时不显现，一旦某个视图补了
  frontmatter 就会静默失效。现改为**只读取目标视图自己的笔记**；vault 笔记以文件名 stem 为键时按
  分隔符前缀容错（`OV-5b 作战活动分解` 命中 `OV-5b`，`OV-20` 不会命中 `OV-2`）。
- **删除死代码** `ConsistencyChecker._extract_performers`：定义后从未被调用。
- **两条 prose-heuristic 检查的活动 / 资源提取器误报**：
  - `unbound_activity`（ERROR）报出「123 个未分配执行者的活动」。`_extract_activities` 用
    `A\d+[:\s]+` 抓取，把 Mermaid 语法与表格单元格一并吞入；`_extract_bound_activities` 对
    `| A1 | … |` 行 `split('|')` 后取 `parts[0]`（首格恒为空串）—— 两个提取器口径互不相容。
    现改为读取 OV-5b 的两种书写形态（Mermaid 节点标签 / 活动表），取**非空**执行者；
    检查范围收敛为「OV-5b 声称建模的活动」，不再要求 OV-5a 的分解叶子逐一出现。
  - `orphan_resource`（INFO）把 OV-2 一级标题里的英文 `Resource` 当成资源名，建议中因此出现
    `Flow Description）`。现跳过一级标题行（标题是视图名，不是资源清单）。
  - 效果：一个 26 视图项目的校验由 19 项（1 ERROR + 17 WARNING + 1 INFO）降为 17 项
    （全部为结构性 WARNING）；ERROR 清零后视图可正常进入 `verified`。
- **`views.include_mermaid` 是无效果的开关**：该键在 `README.md` / `docs/readme.md` 中被
  当作可用特性记录，也存在于 `DEFAULTS`，但**没有任何代码读取它** —— 指令生成器无条件注入
  Mermaid 段落，因此设为 `false` 毫无作用。现已在 `InstructionBuilder` 中接入。
- **workflow 模板的 `--reasoning-file` 骨架不完整**：`propose` 模板只给出 `reasoning:` 三个字段，
  `apply` 用点号记法（`source.standard`）却未说明 `source` 是 `reasoning:` 的**同级**而非子级，
  且两者都未提及 `author`。按模板执行的 Agent 会写出 `pedigree_status: incomplete` 的记录——
  `trace record` 仍以退出码 0 写入，但该视图永远无法进入 `verified`，变更无法归档。
  （实测于一个 26 视图的架构：全部 26 条 pedigree 均被卡住）
  - `propose.py` / `apply.py` 补全完整骨架，并显式标注 `source` / `author` /
    `known_limitations` 为**顶层键**；规范结构直接取自 `test_cli_trace.py::REASONING_YAML`
  - 新增两条守卫测试（修复前红、修复后绿）：
    `test_reasoning_file_skeleton_covers_top_level_provenance`、
    `test_reasoning_file_nesting_is_explicit`
  - 重新生成 `.claude/skills/` 与 `.dsh/skills/` 产物
  - **不改运行时行为**：`_merge_payload` 的读取位置与 `trace record` 的退出码语义保持不变

## [0.2.0] - 2026-10-13

### Added
- **新术语自动命名**（OpenSpec 变更 `auto-name-new-terms`，P4，检索质量路线收官）：
  - **解除「每个术语必须手写别名」**：`dm2-term-zh-aliases.yaml` 允许按术语部分覆盖；
    中文名的强制来源改为组合结果 `canonical_zh`（构建期校验非空），别名层降级为可选同义词补充
  - **数据组别名转为强制**：`groups:` 段必须存在且覆盖 17 个数据组（组级中文召回无法由组合替代）
  - 新增 `dm2 knowledge compose <术语名>`：命名预检——输出词元分解、各词元中文、
    组合结果与**未登记词元**清单（无法组合时 `composed` 为空、退出码仍为 0，因为那是诊断答案）
  - 构建报告新增「策展别名覆盖 X/279」与「组合覆盖」，缺口可见但不致命
  - 实测：合成新术语 `CapabilityPartOfProject`（零手写内容）自动得到 `能力属于项目`，
    可被「能力属于项目」与「能力 属于 项目」（词元模式）检索到；含 `zzz` 这类未登记词元则构建失败
- **检索可解释与顺序敏感匹配**（OpenSpec 变更 `explain-search-matches`，P3）：
  - `ElementVocabulary.plan_query()` 把中文查询**反向分解**为「数据元 + 限定词」序列
    （`活动 属于 能力` → element/qualifier/element），产出词元模式候选
  - 新增最高优先级结构层**词元模式**：查询词元按序出现在术语词元中即命中
    （顺序子序列，允许夹结构词）——`活动 属于 能力` 由 `activityPartOfCapability` 领先；
    反序查询 `能力 属于 活动` 不判为模式，退到结构化层
  - 排序扩为五层：整串精确 → 词元模式 → 结构化 → 名称/别名子串 → 仅文本
  - 新增 `dm2 knowledge search --explain`（`-e`）：JSON 结果项附加 `match`
    （`tier`/`kind`/`pattern`/`segments`），人类模式打印一行命中理由；
    **不加该 flag 时输出与之前完全一致**（`match` 不出现）
  - `DM2KnowledgeIndexer.match_terms()` 提供「术语 + 解释」，`search_terms` 保持原签名
- **检索接入数据元模型**（OpenSpec 变更 `wire-element-model-into-search`，P2）：
  - 派生索引 `terms.json` 新增 `canonical_zh`（组合器产出的规范中文名，279/279 全部组合成功），
    构建期生成、快照测试守护
  - 检索新增**词元归一**：查询片段经 `ElementVocabulary.tokens_for()` 映射为候选词元
    （`能力` → capability、`区域` → {area, region}），一对多按「段内 OR」处理
  - 排序改为四层：**整串**精确命中 → **结构化命中**（含候选词元的段全部由词元命中）→
    名称/别名子串 → 仅定义/数据组/规范名；无法归一的片段仍走子串，**召回不回退**
  - 实测：`能力 活动` 由 `activityMapsToCapabilityType` / `activityPartOfCapability` 领先
    （此前首条是 `Activity`）；`activity capability` 同样受益；规范名可检索
    （`结束边界类型的度量` → `measureOfTypeEndBoundaryType`）
  - `knowledge search --json` 结果项新增 `canonical_zh`（既有字段不变）
- **数据元 / 限定词模型**（OpenSpec 变更 `add-data-element-qualifier-model`，P1：模型与校验）：
  - 新增策展权威源 `dm2-reference/dm2-element-vocabulary.yaml`：95 个数据元 + 36 个限定词 +
    10 个复合数据元 + 39 条关系模板，按 GB/T 18391（ISO/IEC 11179）对象类 + 特性 + 表示建模
  - 新增组合器 `src/dm2/kernel/elements.py`：整串/前缀复合数据元 → 最长连接词模板 → 结构规则
    （`XTypeType` → 「XType的类型」）→ 逐词元拼接；纯函数、零 LLM，未登记词元返回 `None`
  - 构建期强校验：术语名分解出的每个词元都必须登记，模板必须良构，违规即构建失败
  - 对账测试 `test/test_element_vocabulary.py`：组合名复现人工别名，实体 173/173 = 100%、
    关联 102/106 = 96.2%；4 条有意保留的分歧显式登记，新增分歧会让测试失败
  - 7 条别名首选名对齐规范组合名（`desireMeasure` → 期望度量 等），旧写法保留为同义词
  - P1 不改运行时检索行为
- **中文术语检索召回**（OpenSpec 变更 `add-chinese-term-aliases`，关闭地基缺口 D9）：
  - 新增策展权威源 `dm2-reference/dm2-term-zh-aliases.yaml`：279 个术语 + 17 个数据组的中文别名；
    构建时校验未知术语键、未知数据组键、空别名、重复别名与遗漏术语，违规即失败
  - 派生索引 `terms.json` 增加 `zh_aliases` / `zh_groups`；`dm2 knowledge search` 命中中文别名，
    查询按空白与中英文标点分词（多 token 要求**全部命中**），排序改为
    「术语名/完整别名 → 名称别名内子串 → 仅定义或数据组」
  - `dm2 knowledge search --json` 结果项新增 `zh_aliases`（标准 `aliases` 语义不变）；人类输出显示中文别名
  - 实测：`search "资源流"`、`"能力"`、`"执行者"`、`"活动属于能力"` 均有正确召回（变更前恒为 0）
- **视图溯源（DM2 Pedigree）**（OpenSpec 变更 `add-view-provenance`）：
  - **事实层**由 CLI 自动捕获（视图注册、状态转换、校验结果、视图文件内容哈希变化），
    **理由层**由外部 AI Agent 经 `dm2 trace record` 主动声明；两层在存储与呈现上严格分离
  - 新命令：`dm2 trace record/show/lineage/migrate`、`dm2 audit <view>`、`dm2 audit-report`
  - `.dm2/view-state.yaml` 增加每个视图的 `pedigree_status`/`pedigree_missing`；
    `dm2 view list --pedigree-status complete|incomplete|absent` 可过滤
  - `dm2 validate` 把本轮结果写回已有溯源记录（`ran_R1`–`ran_R5`、带 `suggested_fix` 的问题、
    `last_validated`），并以溯源完整性门控 `verified`；新增 `--force-pedigree` 覆盖（在修改历史中留痕），
    项目配置 `trace.enabled: false` 作为整体逃生阀
  - `.dm2/pedigree/<view_id>.yaml` 随项目提交（工程审计证据）；审计输出一律把理由层标注为
    「Agent 自述、未经验证」；无自动修复的问题显示 `No automated fix available`
  - `KnowledgeAPI` 新增 `get_pedigree`/`list_pedigrees`/`pedigree_summary`；
    `dm2 knowledge view --json` 与 `dm2 instructions` 的 context 带上溯源状态
  - propose/apply 技能模板要求 `## Trace Plan` 与每视图 `dm2 trace record`（含 reasoning-file 格式、
    失败处置）；视图生成后的人工修改由内容哈希自动识别并记为 `actor=human`
  - `dm2 init` 创建 `.dm2/pedigree/` 并写入 `trace.enabled: true`
- **开发环境切到 DSH + SDD**（仓库工具链调整，不改变 dm2 对外行为，故无 OpenSpec 变更）：
  - 接入 OpenSpec 的厂商中立目标 `agents`：12 个 `openspec-*` SDD 技能写入 `.agents/skills/`，
    DSH 以 `project-agents` 发现；这批第三方技能不入库，由 `openspec init/update` 重建
  - dm2 自产的 DSH 技能面 `.dsh/skills/dm2-*`（10 个）入库；字节一致性守护
    （`test/test_generated_agent_config.py`）扩展为 `.claude` + `.dsh` 双适配器
  - 新增 `scripts/render_agent_config.py`：一条命令幂等重建全部入库 agent 产物
  - `.gitignore` 与归属守护补 `.agents/skills/openspec-*`、`.agents/skills/.openspec-target`
- **Cynefin 复杂度模块按理论重构**（OpenSpec 变更 `redesign-cynefin-model`）：
  - 五个语义维度（需求可知性/实践成熟度/环境动态性/目标一致性/约束清晰度），
    度量因果可知性而非规模；规模信号（系统数/时间跨度/干系人数）拆入独立 scale profile
  - 新增第五域 **Disorder**：证据为零、或低证据且跨域矛盾时不强行归类，
    输出 `needs_clarification` 联动澄清问题；危机信号（应急/中断/失控）一票判 Chaotic
  - 域聚合改为「维度投票 + 硬触发（≥3 complex）+ 加权带」，修复旧量表下
    Complex/Chaotic 数学上永不可达的问题
  - 统一 `CynefinDeriver`（CLI 与 pipeline 共用，同输入同结果），词库外部化到
    `dm2-reference/core/cynefin-keywords.yaml`，否定词极性安全
    （修复「不确定」被子串「确定」反判为 simple 的语义反转 bug），命中词作为证据透传
  - 置信度重写：缺失维度不投票，公式输出 0.20–0.95 并暴露 coverage/agreement 分解；
    域 → depth_tier 视图深度档位（minimal/core/extended/full/none）
- **知识库扎根 DM2 元模型**（OpenSpec 变更 `ground-kb-in-dm2-metamodel`）：
  - 权威源入库：`dm2-reference/dm2-data-dictionary.yaml`（279 术语 + 怪物矩阵）、
    `dm2-metamodel-2.02.yaml`（19 子模型 / 621 类 / 242 Tuple）
  - `scripts/build_knowledge_indexes.py` 派生 4 个紧凑 JSON 索引
    （terms/associations/taxonomy/view-content-spec），运行时只加载 JSON，不解析 840KB 源 YAML
  - `src/dm2/kernel/metamodel/` 新增 `MetamodelIndex`（关联目录/分类学/视图内容规范查询）；
    `dm2 knowledge` 新增 `term/taxonomy/associations/content` 四个子命令
  - `dm2 validate` 接入元模型符合性校验（`src/dm2/reasoning/conformance.py`，5 条规则），
    与散文级启发式检查分层报告（metamodel-conformance / prose-heuristic）
  - 17 个数据组模板 `relationships:` 槽位按关联目录权威名再生成
- **Cynefin 评估量表与裁定**（OpenSpec 变更 `cynefin-rubric-assessment`）：
  - `dm2 cynefin --rubric-only` 输出空白量表（五维引导问题 + 三档行为锚点）与档位说明
  - 新增 `--domain <域>` 终裁：跳过机械解析直接取域，机械建议保留在
    `suggested_domain` / `mechanical_suggestion` 留痕；非法域报 `INVALID_ARG`
  - 评估量表（`rubric`）与证据卷宗（`signal_report` / `warnings`）随 CLI JSON 与
    analysis-state 输出；`dm2 status` 以 `～草案` / `✓已裁定` 标注解析状态
  - propose/ff/onboard 工作流改为「读证据卷宗与量表 → 向用户提问 → 显式裁定」标准动作
- **地基文档与治理**（OpenSpec 变更 `establish-dm2-foundation`，及配套
  `remove-llm-packaging-residuals` / `report-missing-knowledge-base` /
  `wire-cli-output-schemas`，均已归档）：
  - 新增 `docs/foundation.md`：定位边界、实测分层依赖边、9 条横切不变量
    （每条带守护锚点）、可复现现状基线、裂缝 D1–D10 清单与目标态
  - 新增守护测试：架构分层边界（`test_architecture_boundaries.py`）、
    JSON 信封契约（`test_cli_json_contract.py`）、输出 schema 对照真实输出
    （`test_cli_output_schemas.py`）、生成物字节一致性
    （`test_generated_agent_config.py`）、知识库缺失报错
    （`test_missing_knowledge_base.py`）
  - 研究语料从 `dm2-reference/reference/` 整体迁至 `docs/reference/`
    （运行时不读取、不随包分发）；删除死目录 `templates/` 与
    `dm2-reference/view-representations.yaml`
- Initial release structure for GitHub

### Changed
- **规范文本重构以符合 OpenSpec 1.14 风格规则**（OpenSpec 变更 `comply-with-openspec-1-14-style`）：
  5 个 spec 的 11 条 requirement 正文从 503–1550 字符压到 262–487 字符——只把表格、字段清单
  与示例移入场景（既有场景逐字保留，被移出内容以新增场景承载），SHALL 语义一条不减。
  CI 的 openspec 版本从 `1.13.1` 对齐到 `1.14.1`，本地与 CI 的 strict 关口恢复同口径
  （此前本地 1.14.1 判红 5 个 spec、CI 锁 1.13.1 判绿）。无代码与行为变更。
- **BREAKING** `dm2 validate` 不再无条件把视图置为 `verified`：溯源缺核心字段
  （`author`/`creation_date`/`source`）时保持 `generated` 并报 `rule: pedigree` 错误。
  旧项目可选：跑 `dm2 trace migrate` 后用 `dm2 trace record` 补核心字段，
  或设 `trace.enabled: false` 关闭门控与溯源写入
- `dm2 view list` 的表格与 `--json` 增加 `pedigree_status`/`pedigree_missing`；
  非法的 `--pedigree-status` 值现在以非零退出码返回错误信封
- **BREAKING** `dm2 cynefin` 选项：`--uncertainty/--rules/--stakeholders` 替换为
  `--knowability/--constraints/--alignment`（取值 `clear|complicated|complex`），
  新增 `--maturity/--dynamics/--stakeholder-count/--time-span`；`--systems` 改为纯规模
  信号不再影响域；显式选项现在正确覆盖 `-d` 推导的对应维度（旧版该场景从未生效）
- **BREAKING** `dm2 cynefin --json` 契约：输出五维投票+证据、置信度分解、
  scale_profile、depth_tier、needs_clarification；旧 analysis-state 读取保持兼容
- 裸跑 `dm2 cynefin`（无描述无选项）不再产出虚假的中庸判定，改为 Disorder 成功响应
- **BREAKING** 词库 `cynefin-keywords.yaml` 升级 v2：危机判定从子串词列表改为语境规则
  （候选词 + 窗口内门控词 + 排除复合词，产出 fired/excluded/weak 三态 `signal_report`），
  五维各带 rubric 引导问题与行为锚点；旧 v1 词库副本会报版本错误，需用包内置副本覆盖同步
- **BREAKING** `dm2 cynefin --json` 契约新增 `resolution`（heuristic|adjudicated）、
  `warnings`、`signal_report`、`rubric`、`suggested_domain` 字段；显式维度选项现在使
  结果标记为已裁定（adjudicated），纯 `-d` 推导标记为草案（heuristic）
- `dm2 init --tool/-t claude|dsh`: target-AI-tool selection. New `DshAdapter`
  emits 10 project skills under `.dsh/skills/<skill>/SKILL.md` (DeepSeek
  Harness discovery, `user-invocable: true`, no command files) and rewrites
  Claude-specific body references (`/dm2:<id>` → skill references,
  `AskUserQuestion` → `ask_user_question`, `python3 -m dm2.cli.main` → `dm2`).
  `ToolAdapter.get_adapter(tool_id)` is the adapter registry.

### Changed
- `dm2 init --json` field `claude_config` (boolean) replaced by structured
  `agent_config` (`tool`, `files_generated`, `skills_dir`, `commands_dir`,
  `commands`). The default (`claude`) generation is otherwise unchanged.
- `.claude/` directory added to version control
- `settings.local.json` renamed to `settings.example.json` as template

### Fixed
- **项目守卫族与 JSON 信封**：`view list/register`、`run`、`validate`
  补项目守卫；所有守卫在 `--json` 模式下输出 `NOT_IN_PROJECT` 错误信封
  （此前守卫失败会往 stdout 写纯文本、或在任意目录静默创建 `.dm2/`）；
  `config -s` 守卫前置到写入之前；`view register` 补接受 `--json`
- **知识库缺失从「静默空答案」改为明确失败**：`get_reference_path()` 在两条
  候选路径都不存在时抛 `KnowledgeBaseNotFound`，CLI 中央转为 `KB_NOT_FOUND`
  信封（人类模式给可操作提示）；`concerns.yaml` 同样处理
- **分发形态正式确立为 editable-only**：sdist→wheel 实测确认包外数据文件被
  静默丢弃（wheel 的 `dm2/` 内零 json/yaml），非 editable 安装确定不可用——
  现在会干净地报 `KB_NOT_FOUND` 而非静默空答案。删除 MANIFEST.in、删除会向
  PyPI 发布坏 wheel 的 release.yml，并清理指向不存在路径的死 package-data；
  正式 wheel 分发为 foundation D10 延后项
- **数据组→视图映射修复与证据标注**（OpenSpec 变更 `repair-group-view-mapping`）：
  修复 `group-to-views.yaml` 的视图 ID 错误（SvcV-3）并补齐 SV 家族覆盖盲区，
  为每条映射添加 `basis` 证据标注；新增 `test/test_group_view_mapping.py`
  三类校验（视图 ID 有效性 / 数据组覆盖 / basis 完整性）
- `.gitignore` updated to allow `.claude/` directory

## [0.1.0] - 2026-05-16

### Added
- dm2 CLI with 17 commands
- DoDAF Meta Model 2.02 knowledge base
- Pipeline orchestration for view generation
- Claude Code skill and command definitions