# Tasks: cynefin-rubric-assessment

## 1. v2 词库（dm2-reference/core/cynefin-keywords.yaml）

- [x] 1.1 顶层 `version: 2`；crisis 节改为 `signals` 四规则（response-in-progress / large-scale-outage / spreading / loss-of-control：candidates/require_near/window/exclude）+ `direct` 强短语
- [x] 1.2 五维度各补 `rubric` 节：question（中文引导问题）+ anchors 三档行为锚点
- [x] 1.3 维度词表与 scale 节保持 v1 内容；顶部注释更新为 v2 语义（规则只是 prefill，裁定走量表）
- [x] 1.4 吸收工作区未提交的危机收窄改动：v1 白名单中的有效强短语迁入 direct，其余由规则取代

## 2. 语境规则引擎（cynefin_deriver.py）

- [x] 2.1 loader 版本校验：缺失/低于 version 2 抛 CynefinKeywordsError，信息含文件路径与同步指引
- [x] 2.2 实现排除跨度（exclude 复合词最长匹配）与门控评估（候选跨度 ±window 内命中 require_near）
- [x] 2.3 产出 signal_report：每条候选评估 `{rule, matched, verdict: fired|excluded|weak, reason, gate}`；direct 短语命中即 fired
- [x] 2.4 crisis 标志由任一 fired 决定；excluded/weak 不参与、不回流维度；warnings 文案（排除候选、弱信号、平票弃权、低覆盖）
- [x] 2.5 Derivation 结果对象暴露 signal_report 与 warnings；极性安全/最长匹配既有行为保持

## 3. 量表与裁定（analyzer + CLI）

- [x] 3.1 Rubric/RubricDimension 数据结构与 YAML 加载（缺失字段有兜底文案）
- [x] 3.2 ComplexityAssessment 增加 resolution（heuristic|adjudicated）、warnings、signal_report、mechanical_suggestion、rubric；to_dict 同步
- [x] 3.3 CLI：纯 `-d` 为 heuristic；任一显式维度选项 → adjudicated（source=user）
- [x] 3.4 新增 `--domain <域>` 终裁：绕过解析直接取域，deriver 卷宗/量表照常，mechanical_suggestion 记录机械建议；非法值 INVALID_ARG
- [x] 3.5 新增 `--rubric-only --json`：空白量表 + 档位说明，无需描述，exit 0
- [x] 3.6 JSON 契约输出 suggested_domain/domain/resolution/warnings/signal_report/rubric；文本模式标注草案/已裁定
- [x] 3.7 analysis-state 持久化完整 payload；`dm2 status` 区分 `~草案` 与 `✓已裁定`，旧记录无 resolution 不崩

## 4. Pipeline 与工作流模板

- [x] 4.1 IntentScopeResult 增加 cynefin_resolution、cynefin_warnings；step1 输出标注「启发式草案」并列 warnings，Disorder 不阻断
- [x] 4.2 propose.py：新增 Adjudicate Cynefin 步骤（读卷宗/warnings；接受建议→显式选项重跑；真危机误排除→--domain 并写理由；Disorder→先提问）
- [x] 4.3 ff.py：heuristic 必须标注未裁定；危机 weak 信号向用户确认后再承诺视图范围
- [x] 4.4 onboard.py：展示 rubric 锚点引导逐维确认
- [x] 4.5 重新生成 3 个 dm2-* skill 并核对 diff 仅含预期改动

## 5. 测试

- [x] 5.1 规则引擎：excluded（应急预案/演练/体系/能力/中断风险/防止失控）、weak（裸候选无门控）、fired（正在应急处置/全站中断/事态蔓延/濒于失控）、真危机与预案同句共存
- [x] 5.2 迁移现有 3 条规划类非危机回归为 excluded 语义断言；金标 5+3 语料全绿
- [x] 5.3 rubric：-d 输出含五维 question/anchors/prefill；--rubric-only 空白；锚点外部化可改
- [x] 5.4 裁定：默认 heuristic；显式选项升 adjudicated；--domain 绕过危机且保留 mechanical_suggestion；非法域报错
- [x] 5.5 v1 词库版本错误信息；analysis-state 新旧格式 status 测试
- [x] 5.6 CLI↔pipeline 一致性补 warnings/resolution 断言；全量 pytest + 新文件 ruff

## 6. 文档与工程同步

- [x] 6.1 docs/readme.md 命令参考更新（三层语义、--domain、--rubric-only、JSON 新字段）
- [x] 6.2 CHANGELOG：BREAKING（词库 v2、JSON 契约）、新增量表/裁定说明
- [x] 6.3 ~~覆盖同步 9 个 workNow 工程的 .dm2/reference/cynefin-keywords.yaml 为 v2~~
  （已取消 2026-09-16：workNow 工程数据不归本仓库管理，词库副本由各工程自行同步；v1 副本在 v2 loader 下会收到含同步指引的版本报错）
- [x] 6.4 ~~代表性工程冒烟（AI驱动安全/大模型服务群安全/SE-Agent）：规划语料非 Chaotic、真危机 Chaotic~~
  （已取消 2026-09-16：不访问用户工程目录；规划语料非危机与真危机语义已由 test_cynefin_deriver 金标语料 + test_cynefin_cli 契约测试覆盖）
- [x] 6.5 openspec validate cynefin-rubric-assessment --strict
