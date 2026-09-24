## Why

关键词匹配把语义判断焊死在词条上：crisis 一票否决曾被「应急预案」「应急演练」「业务中断风险」
等规划语境大面积误触（workNow 工程产物抽样：应急×62、中断×58、应急预案×15、应急演练×12），
收窄白名单只是打地鼠——子串匹配给不出时态（正在/预案）、情态（风险/防止）、范围（单机/全站）。
同时 CLI 把启发式推导结果当作确定域输出，而 Cynefin 在真实实践中本就是**结构化提问引导人判断**
的意义建构工具，不是文本分类器。需要把工具从「分类器」重构为「证据提取 + 量表评估 + 裁定」
三层，让语义判断归位给在环的 Agent/人，CLI 保持零 LLM 且输出诚实。

## What Changes

- **三层评估架构**：
  1. **语境规则引擎（A）**：词库升级为 v2 schema。危机信号 = 候选词 ∧ 窗口内门控词
     （正在/中/全站/已…）∧ 不落入排除复合词（应急预案/演练/风险/流程/防止…）；被排除与
     门控不足的候选不沉默丢弃，写入 `signal_report` 与 `warnings`。维度侧 schema 预留同款
     规则能力，本次仅为已确认误判配规则
  2. **量表评估（主路径）**：YAML 定义五维三档**行为锚点量表（rubric）+ 引导问题**；
     启发式推导结果只作为量表的预填（prefill）；Agent/人按量表回答后才产出确定评估。
     量表随 `-d` JSON 一并输出（含每维 prefill 与证据），另支持无描述时输出空白量表
  3. **裁定状态（B）**：评估结果区分 `heuristic`（纯推导草案）与 `adjudicated`
     （显式维度选项或新增 `--domain` 终局裁定）；analysis-state 与 `dm2 status` 区分展示；
     危机候选被排除等情形以 warnings 显式提示裁定者
- **BREAKING** 词库 `version: 1 → 2`，crisis 节从词列表改为 signals 规则结构；
  `dm2 cynefin -d` 的 JSON 契约扩展（`suggested_domain`、`resolution`、`signal_report`、
  `warnings`、`rubric`），`domain` 字段保留为建议域以兼容基本读取
- 新增 `--domain <域>` 终局裁定选项（跳过投票/触发，证据卷宗保留）；任一显式维度选项
  即使结果与草案一致也标记 `adjudicated`
- step1 pipeline 透传 warnings 并把域标注为 heuristic；Disorder 澄清答案回流的接口预留
  （澄清问答闭环本体留作后续变更）
- 工作流模板（propose/ff/onboard）改为「读证据卷宗与量表 → 必要时向用户提问 →
  显式裁定」的标准动作
- v1 本地词库副本（9 个 workNow 工程）随本次重新同步为 v2

## Capabilities

### New Capabilities
（无）

### Modified Capabilities
- `dm2-cynefin-model`：新增评估解析状态（heuristic/adjudicated）、量表裁定为规范路径、
  `--domain` 终局裁定语义；危机否决的输入从「词命中」改为「语境规则成立的信号」
- `dm2-cynefin-auto-derive`：推导器从关键词计数升级为 v2 语境规则引擎（门控/排除/窗口、
  signal_report/warnings）；CLI JSON 输出量表与裁定状态；纯推导结果明确为 heuristic

## Impact

- **代码**：
  - `dm2-reference/core/cynefin-keywords.yaml`：v2 schema（crisis signals 全套规则；
    五维 rubric 锚点与引导问题；维度排除规则少量）
  - `src/dm2/cognitive/cynefin_deriver.py`：规则引擎（排除跨度、门控窗口、signal_report）、
    v1/v2 版本校验
  - `src/dm2/cognitive/cynefin_analyzer.py`：resolution 字段、domain 终裁入口、to_dict 扩展
  - `src/dm2/cli/main.py`：`--domain`、量表输出、`--rubric-only`、持久化与 status 展示
  - `src/dm2/engine/pipeline/step1_intent_scope.py`：warnings/heuristic 透传
  - `src/dm2/core/templates/workflows/{propose,ff,onboard}.py` + 重生成 skills
- **测试**：门控正反例（预案/演练/风险 vs 处置中/全站中断）、排除留痕、量表预填与裁定、
  `--domain`、v1 词库报错信息、CLI JSON 契约；golden 语料补规划类非危机语料
- **工程数据**：覆盖同步 9 个 workNow 工程的 `.dm2/reference/cynefin-keywords.yaml`
- **文档**：docs/readme.md 命令参考、CHANGELOG（BREAKING）
- **依赖**：无新增（零 LLM 原则不变）
- **吸收未提交改动**：工作区中 crisis 收窄与 3 条非危机回归测试被本变更的规则化实现取代
