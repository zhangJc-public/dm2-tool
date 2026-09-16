# Design: Cynefin 语境规则 + 量表评估 + 裁定

## Context

`redesign-cynefin-model` 建立了五维投票/硬触发/Disorder 模型，但输入端仍是子串关键词匹配。
2026-09-15 实测：危机一票否决被规划语境大面积误触（「应急预案」「应急演练」「业务中断风险」
全部判 Chaotic；workNow 语料抽样 应急×62、中断×58）。收窄词表能堵具体词，但子串匹配无法
处理时态（正在/预案）、情态（风险/防止）、范围（单机/全站），打地鼠无终点。

同时 CLI 把启发式结果当确定域输出，违背 Cynefin「结构化提问引导人判断」的本义。本变更把
工具重构为三层：规则只做证据提取（A），rubric 量表是规范评估路径，Agent/人裁定才落确定域（B）。
约束不变：CLI 零 LLM、无新依赖、--json 流纯净。

## Goals / Non-Goals

**Goals:**

1. v2 语境规则引擎：候选词 + 窗口门控 + 排除复合词；排除/弱信号全部留痕（signal_report）。
2. rubric 量表外部化：五维三档锚点 + 引导问题；启发式结果降级为 prefill，量表随 JSON 输出。
3. heuristic/adjudicated 两态：显式选项或 `--domain` 终裁才是 adjudicated；状态与 status 区分。
4. 工作流模板把「读卷宗 → 必要时提问 → 显式裁定」变成标准动作。
5. 9 个 workNow 工程的 v1 本地词库同步为 v2。

**Non-Goals:**

- 不引入分词器/句法分析/统计 NLP/LLM；窗口是字符级的。
- 不实现澄清答案回流的完整闭环（step1 仅预留字段与文案）。
- 不做模糊隶属度分布、CBR 案例库、基于 DM2 产物的结构度量（后续变更候选）。
- 不改五维定义、投票/硬触发/加权带/Disorder 算法常量。
- 不重新生成工程内 .claude/.dsh skills 以外的工程数据（views/groups 不动）。

## Decisions

### D1. 三层职责切分

```
描述文本
  │
  ▼ CynefinDeriver（规则层，纯机械）
 信号卷宗：维度 prefill + 证据 / crisis signals（fired|excluded|weak）/ scale / warnings
  │
  ▼ CynefinAnalyzer（规则层，纯计算）
 suggested_domain + depth tier，resolution=heuristic
  │
  ▼ Rubric（量表层，外部化 YAML）
 五维问题 + 三档锚点 + prefill 建议
  │
  ▼ Agent/人（裁定层，语义判断发生在 CLI 之外）
 显式维度选项 或 --domain 终裁 → resolution=adjudicated，落 analysis-state
```

CLI 对语义只陈述「看到了什么、按机械规则意味着什么」，不声称知道现实状态。

### D2. v2 词库 schema

```yaml
version: 2

crisis:
  signals:
    - id: response-in-progress
      candidates: [应急处置, 应急响应, 应急指挥, 抢修]
      require_near: [正在, 中, 已启动, 已进入]
      window: 8
      exclude: [应急预案, 应急演练, 应急体系, 应急能力, 应急机制,
                应急流程, 应急规划, 响应流程, 应急制度]
    - id: large-scale-outage
      candidates: [中断, 宕机]
      require_near: [全站, 全网, 全线, 大面积, 核心系统, 核心业务, 多个关键]
      window: 6
      exclude: [中断风险, 中断处置流程, 防止中断, 宕机风险, 业务中断风险]
    - id: spreading
      candidates: [蔓延]
      require_near: [正在, 仍在, 持续, 事态]
      window: 4
      exclude: [防止蔓延]
    - id: loss-of-control
      candidates: [失控]
      require_near: [正在, 已, 完全, 濒于]
      window: 4
      exclude: [失控风险, 防止失控, 防失控]
  # 既有强短语可直接作为门控恒成立的信号保留（fired phrases）
  direct: [战时状态, 紧急抢修中, major outage, system is down, ongoing emergency, active crisis]

dimensions:
  requirement_knowability:
    rubric:
      question: "需求现在能说清吗？是冻结的、需要调研收敛的、还是在持续涌现？"
      anchors:
        clear: "需求明确且已冻结，范围不再变化"
        complicated: "部分明确，经调研/分阶段可以收敛"
        complex: "需求模糊或持续涌现，行动前无法完整定义"
    clear: [...]        # v1 词表保留，作为 prefill 词
    complicated: [...]
    complex: [...]
    exclude: {}         # 预留：本变更只在发现具体误判时填
  # 其余四维同构
```

loader 行为：顶层 `version` 缺失或 < 2 → `CynefinKeywordsError`，信息指明文件路径与
「请重新同步参考库（重新运行 dm2 init 或覆盖词库）」。v1 扁平 `crisis:` 列表是明确的
版本判据。

### D3. 信号引擎匹配算法

复用现有最长匹配/去重叠引擎，新增三步（先全部用最长匹配收集跨度）：

1. **排除跨度**：匹配所有 signal 的 `exclude` 复合词 + `direct` 短语，各成跨度集合。
2. **候选评估**（每个 candidate 命中跨度）：
   - 与任一排除跨度重叠 → verdict `excluded`，reason 记录排除词；不计危机、不回流维度。
   - 否则取跨度左右各 `window` 字符的文本窗，命中任一 `require_near` → `fired`
     （evidence 记录候选词 + 门控词）。
   - 无门控 → `weak`；默认不计危机。
3. `direct` 短语命中即 fired。
任一 fired → `crisis=True`。全部 signal 的判定写入 `signal_report`
（含未命中的规则不需要报告；只报告实际发生候选评估的条目）。

边界情形：

- 「全站中断，启动应急预案，应急处置中」：中断与全站门控成立；应急预案进排除跨度；
  应急处置 + 中成立 → crisis=true，卷宗同时保留「应急预案 excluded」。
- 中文没有词边界，窗口是字符级，会有偶发误伤；排除/弱信号全部留痕且可 `--domain` 推翻，
  错误成本从「静默错杀」降为「可审计提示」。
- 维度侧机制同构（prefill 词 + 可选 exclude/require_near），本变更只移植极性安全，
  不批量加规则。

### D4. Rubric 数据结构与输出

```python
@dataclass
class RubricDimension:
    dimension_id: str
    question: str
    anchors: dict[str, str]      # clear/complicated/complex 三档描述
    prefill: str | None          # 启发式倾向
    prefill_evidence: list[str]

@dataclass
class Rubric:
    dimensions: list[RubricDimension]
```

YAML 的 `dimensions.<id>.rubric` 是权威内容；加载时缺失 question/anchors 的维度用代码内
兜底文案（保证老词库结构损坏不炸，配合 version 2 校验实际上不触发）。

`dm2 cynefin -d ... --json` 的 data 增字段（不删既有字段）：

```json
{
  "domain": "Complicated", "suggested_domain": "Complicated",
  "resolution": "heuristic",
  "warnings": ["..."],
  "signal_report": [
    {"rule": "large-scale-outage", "matched": "中断",
     "verdict": "excluded", "reason": "业务中断风险", "gate": null}
  ],
  "rubric": [ {"id": "...", "question": "...", "anchors": {...},
               "prefill": "complicated", "prefill_evidence": ["分阶段明确"]} ]
}
```

`--rubric-only`：不做文本推导，输出空白量表 + depth tier 说明，exit 0。

### D5. Adjudication 契约

- 无 `--domain`、无显式维度选项 → `resolution: "heuristic"`。
- 任一显式维度选项（含显式值与 prefill 相同）→ `resolution: "adjudicated"`，
  该维 source=user。
- `--domain X`：跳过 analyzer 的三级解析直接取裁定域；但 deriver 照跑（有描述时），
  卷宗、rubric、scale 全部保留；payload 额外带
  `mechanical_suggestion: "<heuristic domain>"`；crisis 标志仍如实报告但不决定终局域。
- persistence：analysis-state 的 cynefin 节存完整 payload；旧记录缺 resolution 时
  status 按「历史记录（无裁定标记）」展示，不崩。
- `dm2 status`：`Complicated ~草案` / `Complex ✓已裁定`。

### D6. step1 与工作流

- `IntentScopeResult` 增加 `cynefin_resolution: str`、`cynefin_warnings: list[str]`；
  format_output 在评估块标注「启发式草案，未经裁定」并列 warnings；Disorder 文案保留。
- 模板：
  - **propose**：新增「Adjudicate Cynefin」步骤——读 signal_report/warnings；
    全部 fired 且无排除争议、接受建议 → 带显式维度选项（或接受的域）重跑落 adjudicated；
    有 weak/excluded 且用户语境显示真危机 → `--domain` 终裁并写理由；Disorder → 先提问。
  - **ff**：heuristic 可继续但输出必须标注未裁定；遇到危机弱信号要向用户确认。
  - **onboard**：展示 rubric 锚点，引导用户逐维确认后再继续。

### D7. 测试策略

- 规则引擎：预案/演练/体系/能力/风险/防止 → excluded；裸候选无门控 → weak；
  正在应急处置/全站中断/事态蔓延/濒于失控 → fired；真危机与预案同句共存。
- 金标语料回归（现有 5 条 + 3 条规划类非危机）。
- rubric：-d 输出含完整量表与 prefill；--rubric-only 空白量表；YAML 锚点可改。
- 裁定：heuristic 默认；显式选项升 adjudicated；--domain 绕过危机但保留卷宗与
  mechanical_suggestion；非法域 INVALID_ARG。
- v1 词库错误信息；CLI↔pipeline 一致性测试补 warnings/resolution 断言。
- status 新旧状态格式。

### D8. 工程副本同步与未提交改动处置

- 9 个 workNow 工程的 `.dm2/reference/cynefin-keywords.yaml`（本会话刚分发的 v1）
  在实现完成后统一覆盖为 v2，并在其中 3 个代表性工程冒烟。
- 工作区现存未提交的 crisis 收窄改动（YAML 白名单、3 条回归测试、auto-derive spec 措辞）
  被本变更取代：实现时以 v2 schema 重写该 YAML 节，保留并迁移那 3 条规划类回归用例
  （它们正好成为 excluded 语义的测试），主 spec 的措辞修订并入 delta。

## Risks / Trade-offs

- **[字符窗口误伤/漏伤]** → 排除与 weak 全留痕、warnings 显式提示、`--domain` 可推翻；
  规则在 YAML 里可调，不需要发版。
- **[Agent 不遵守裁定步骤，heuristic 仍被当结论]** → 模板用命令式步骤约束；
  status 与 JSON 字段让未裁定状态可见；后续可用 /dm2:verify 检查 change 目录是否有
  adjudicated 记录。
- **[v1 本地副本导致升级即报错]** → 错误信息指明同步方法；本变更直接覆盖 9 个已知工程。
- **[rubric 锚点文案主观]** → 锚点外部化且可按项目改；锚点不参与机械判定，只引导人。
- **[--domain 绕过规则让结果"想填啥填啥"]** → mechanical_suggestion 与卷宗同时落盘，
  审计时分歧可见；这是刻意把语义权交给有语境的一方。

## Migration Plan

1. v2 YAML（signals + rubric）与 loader 版本校验。
2. deriver 规则引擎 + signal_report/warnings；迁移规划类回归用例。
3. analyzer/CLI resolution 状态 + --domain + --rubric-only + 持久化/status。
4. step1 透传；模板更新并重生成 3 个 skill。
5. 测试、docs、CHANGELOG（BREAKING 标注）。
6. 覆盖同步 9 工程副本并冒烟；全量 pytest/ruff；openspec strict validate。

回滚：单特性提交序列，revert 恢复 v1 行为；工程副本可用 git 历史中的 v1 YAML 覆盖回。

## Open Questions

1. 危机门控窗口默认 4/6/8 字符是否合适 → 用金标语料实现时校准，常量写进 YAML 可继续调。
2. 是否需要 `dm2 cynefin` 交互式逐项提问（而非只输出量表由 Agent 问）→ 本变更不做，
   Agent 是提问主体；纯 CLI 用户可直接用维度选项。
3. 归档时自动重评（域迁移轨迹）→ 后续变更。
