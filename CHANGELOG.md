# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- Initial release structure for GitHub

### Changed
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
- **数据组→视图映射修复与证据标注**（OpenSpec 变更 `repair-group-view-mapping`）：
  修复 `group-to-views.yaml` 的视图 ID 错误（SvcV-3）并补齐 SV 家族覆盖盲区，
  为每条映射添加 `basis` 证据标注；新增 `test/test_group_view_mapping.py`
  三类校验（视图 ID 有效性 / 数据组覆盖 / basis 完整性）
- `.gitignore` updated to allow `.claude/` directory

## [0.1.0] - YYYY-MM-DD

### Added
- dm2 CLI with 17 commands
- DoDAF Meta Model 2.02 knowledge base
- Pipeline orchestration for view generation
- Claude Code skill and command definitions