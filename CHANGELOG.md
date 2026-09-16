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
- Initial release structure for GitHub

### Changed
- **BREAKING** `dm2 cynefin` 选项：`--uncertainty/--rules/--stakeholders` 替换为
  `--knowability/--constraints/--alignment`（取值 `clear|complicated|complex`），
  新增 `--maturity/--dynamics/--stakeholder-count/--time-span`；`--systems` 改为纯规模
  信号不再影响域；显式选项现在正确覆盖 `-d` 推导的对应维度（旧版该场景从未生效）
- **BREAKING** `dm2 cynefin --json` 契约：输出五维投票+证据、置信度分解、
  scale_profile、depth_tier、needs_clarification；旧 analysis-state 读取保持兼容
- 裸跑 `dm2 cynefin`（无描述无选项）不再产出虚假的中庸判定，改为 Disorder 成功响应
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