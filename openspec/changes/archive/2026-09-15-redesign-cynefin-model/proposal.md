## Why

当前 Cynefin 复杂度评估模块在理论与工程上都已失效：加权分数量表为 1–3，域阈值却设在 3.5/5.0，导致 **Complex 与 Chaotic 域在数学上永不可达**（实测 5 个维度全部取 complex 仍判定 Complicated）；CLI 与 pipeline 各有一套关键词推导实现且已漂移，pipeline 侧存在「不确定」被子串「确定」覆盖成 simple 的语义反转 bug；生产路径从不传 evidence，置信度退化为 {0.5, 0.6, 0.7} 三个离散值且「全默认 medium」反而拿到最高置信。更深层的问题是现有 5 个维度度量的是**规模**（系统数、干系人数、时间跨度、法规条数），而 Cynefin 框架的分界轴是**因果关系的可知性**——等保三级这类规则完备的问题被错误推向 Complex，真正的复杂（需求涌现、无先例、目标冲突）反而测不出来。

## What Changes

- **BREAKING** 以 5 个语义维度替换旧维度：需求可知性、实践成熟度、环境动态性、目标一致性（冲突而非数量）、约束清晰度（矛盾而非条文数）
- 域判定机制从「加权平均+固定阈值」改为**维度域投票 + 硬触发**：危机信号一票进 Chaotic；≥3 维 Complex 倾向进 Complex；否则按加权带落 Clear/Complicated
- **新增第 5 域 Disorder（混乱/不明）**：证据覆盖不足且维度间跨域矛盾时不强行归类，转由澄清问题闭环处理；Disorder 不推荐视图集
- **新增规模剖面（scale profile）**：系统数、时间跨度、干系人数量从域评分中剥离，单独报告并作为视图广度/预算信号（供 ViewRecommender 未来消费，本次不接）
- 置信度重写：缺失维度**不投票**（不再默认 medium 且拿满分一致度）；推导命中的关键词原文作为 evidence 透传；允许输出低置信度
- 合并 `cli/main.py::_derive_cynefin_from_description` 与 `step1_intent_scope.py::_infer_cynefin_values` 为单一 `CynefinDeriver`，关键词表外部化 YAML，否定词语义安全（极性正则），CLI 与 pipeline 同输入必同结果
- **BREAKING** `dm2 cynefin` 参数面与 JSON 契约调整：`--json` 输出逐维度值、证据、置信度分解、规模剖面与 Disorder 状态；显式选项正确覆盖推导值（修复现有 spec 已要求但未实现的 override 场景）
- 清理：恒为 medium 的 time_span 死维度、零调用的 `get_dynamic_thresholds()`、return 处被套话覆盖的 reasoning 字段；`test_cynefin.py` 按新语义重写
- 域 → 视图深度档位（2-4 / P0 / P0+P1+行为三件套 / Fusion / 不推荐）保留并结构化输出；**域结果仍不直接驱动 ViewRecommender**，该「长牙」工作留作后续独立变更

## Capabilities

### New Capabilities
- `dm2-cynefin-model`: Cynefin 域模型本体——语义维度定义与三档锚点、投票+硬触发域聚合（含 Disorder）、置信度推导、规模剖面分离、域到视图深度档位的映射

### Modified Capabilities
- `dm2-cynefin-auto-derive`: 推导从「关键词计数」升级为统一 deriver（维度值+证据、极性安全）；CLI/pipeline 共用；`--json` 契约扩展为逐维度+证据+置信度分解；显式选项覆盖语义按新维度修正（旧 override 场景从未真正实现）

## Impact

- **代码**：
  - `src/dm2/cognitive/cynefin_analyzer.py` 重写（维度、聚合、置信度、`ComplexityAssessment` 契约扩展）
  - 新增 `src/dm2/cognitive/cynefin_deriver.py` 与外部化关键词配置（预计置于 `dm2-reference/core/`，随 init 复制）
  - `src/dm2/cli/main.py`（cynefin 命令选项/JSON/状态持久化、删除 `_derive_cynefin_from_description`）
  - `src/dm2/engine/pipeline/step1_intent_scope.py`（删除 `_infer_cynefin_values`，Disorder 联动澄清问题）
  - `src/dm2/engine/pipeline/pipeline_orchestrator.py`（展示层适配新字段）
- **测试**：`test/test_cynefin.py` 重写；新增 deriver 双入口一致性、否定词极性、Disorder 触发测试；三个真实语料锚点（等保三级医院→Complicated、需求不确定的 AI 系统→Complex、单一防火墙→Clear）
- **持久化**：`.dm2/analysis-state.yaml` 的 cynefin 节扩展（domain 取值新增 Disorder；新增 dimensions/scale 字段；旧文件向后兼容读取）
- **模板/文档**：`propose.py` 等 workflow 模板中「CLI JSON 太薄、AI 应自行重做分析」的说明反转；CLAUDE.md / docs/readme.md 命令说明同步
- **依赖**：无新增第三方依赖（零 LLM 依赖原则不变，全部本地规则匹配）
