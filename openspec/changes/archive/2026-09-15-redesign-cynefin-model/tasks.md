# Tasks: redesign-cynefin-model

## 1. 词库配置与加载

- [x] 1.1 新建 `dm2-reference/core/cynefin-keywords.yaml`（version、crisis、5 维度三档词表、negation_prefixes、scale 词表），按 design D5 的 schema 落中英双语词表
- [x] 1.2 在 `src/dm2/cognitive/` 实现配置加载器（参照 `_load_group_to_views`：`get_reference_path()` 本地优先 + 包内回退，候选 `ref / cynefin-keywords.yaml` 与 `ref.parent / cynefin-keywords.yaml`），缺失时抛出明确异常而非静默
- [x] 1.3 在 `src/dm2/cli/main.py` 的 init 参考库复制逻辑中增加 `cynefin-keywords.yaml`（core 段，复制进 `.dm2/reference/`）
- [x] 1.4 验证 wheel 打包：实测发现**先于本变更的缺陷**——wheel 不含任何 dm2-reference 数据（package-data glob 相对 src/dm2 包目录解析，数据在仓库根）；词库与 views.yaml/groups 处境相同，editable/仓库安装不受影响。修复需独立变更（symlink 或 data-files 方案选型），已记入 design.md Open Questions

## 2. 分析器内核重写（cynefin_analyzer.py）

- [x] 2.1 定义 `Tendency`（clear/complicated/complex）与扩展后的 `Domain`（新增 `DISORDER`，中文标签「不明」）
- [x] 2.2 定义 `DimensionVote`、`ScaleProfile`、重写后的 `ComplexityAssessment`（含 confidence_breakdown、votes、scale_profile、crisis、depth_tier、needs_clarification）
- [x] 2.3 实现解析顺序：crisis 否决 → 零投票 Disorder → 低证据+跨域矛盾 Disorder → ≥3 complex 硬触发 → 加权带（1.5/2.5 边界，弃权维度不进分母），阈值/权重用具名常量
- [x] 2.4 实现置信度公式 `clamp(0.20 + 0.45·coverage + 0.30·agreement, 0.20, 0.95)`，输出 coverage/agreement 分解
- [x] 2.5 实现域 → depth_tier/depth_guidance 映射（minimal/core/extended/full/none）与 reasoning_details 生成
- [x] 2.6 删除旧 API：`assess(dict)` 签名、`ComplexityDimension`、`get_dynamic_thresholds`、return 处套话覆盖的 reasoning 字段

## 3. 统一推导器（cynefin_deriver.py，新文件）

- [x] 3.1 实现 `CynefinDeriver`：加载 YAML，对描述文本做 crisis 命中（不回流维度词表）
- [x] 3.2 实现极性安全扫描：正面锚点正则加否定前缀后顾断言（`不|未|没|无|毫|并不|尚未|难以`），「不确定」不得被「确定」二次命中；长度优先、非重叠匹配防「子系统/系统」双计
- [x] 3.3 逐维度决策：命中最多的倾向胜出，平票则该维度弃权但保留双向证据；每个投票携带去重后的命中词（≤3 条）
- [x] 3.4 产出规模剖面（systems 计数分档、stakeholders、time_span，缺失为 null 而非强制 medium）
- [x] 3.5 提供 `derive(text) -> Derivation(votes, crisis, crisis_evidence, scale_profile)` 接口供 CLI 与 pipeline 共用

## 4. CLI 命令重写（cli/main.py cynefin）

- [x] 4.1 选项改造：`--knowability/--maturity/--dynamics/--alignment/--constraints`（Choice clear|complicated|complex，默认 None），规模选项 `--systems/--stakeholder-count/--time-span`；移除 `--stakeholders/--uncertainty/--rules` 旧语义选项（BREAKING）
- [x] 4.2 无 `-d` 且无任何显式维度时输出 Disorder（exit 0，success JSON）
- [x] 4.3 有 `-d` 时走统一 deriver；显式选项逐维覆盖（修复 override 缺陷），被覆盖维度 `source=user` 且证据注明用户指定
- [x] 4.4 按 design D7 输出新 JSON 契约（domain/confidence/confidence_breakdown/dimensions+evidence/scale_profile/depth_tier/needs_clarification 等），保持 `--json` 2>&1 纯净
- [x] 4.5 删除 `_derive_cynefin_from_description`；文本输出适配 Disorder 澄清指引
- [x] 4.6 analysis-state.yaml 持久化写入同一完整对象；`dm2 status` 用 `.get()` 防御性读取新旧两种格式，展示域 + depth tier

## 5. Pipeline 接入（step1_intent_scope.py）

- [x] 5.1 删除 `_infer_cynefin_values`，改用 `CynefinDeriver` + 新分析器
- [x] 5.2 `IntentScopeResult` 新增 `needs_clarification` 与 `scale_profile` 字段；Disorder 时 format_output 追加「先回答澄清问题」警示块（复用已有 6W clarification_questions）
- [x] 5.3 保证 Disorder 不阻断 pipeline（其余 step1 产出正常返回）；更新 orchestrator 展示行适配新标签

## 6. 测试

- [x] 6.1 重写 `test/test_cynefin.py`：解析顺序五类判定、硬触发、带边界、Disorder 两路径、置信度锚点（0.95/≤0.40）、规模不变性
- [x] 6.2 新增 `test/test_cynefin_deriver.py`：极性安全（「不确定」「不明确」）、平票弃权、证据携带、最长匹配防双计、crisis 命中、规模分档
- [x] 6.3 Golden 语料参数化测试：单一防火墙→Clear、等保三级医院→Complicated、AI 涌现系统→Complex、全站中断应急→Chaotic、空/无关短句→Disorder；语料不足时扩词库而非放松算法
- [x] 6.4 CLI↔pipeline 一致性测试：同一描述两条路径产出相同维度/crisis/scale/domain
- [x] 6.5 CLI 行为测试：显式选项覆盖单维、裸跑 Disorder、`--json` 契约字段完整、旧格式 analysis-state 读取不崩
- [x] 6.6 外部 YAML 加载测试（临时配置注入与缺失处理）

## 7. 模板、文档与清理

- [x] 7.1 更新 `src/dm2/core/templates/workflows/propose.py`（及其他让 Agent 无视 cynefin CLI 输出的模板）：改为「JSON 是可审计证据包，覆盖投票时才需记录自己的推理」；ff/onboard 模板顺手修正失效的位置参数调用与五域说明，并重新生成 3 个 dm2-* skill
- [x] 7.2 更新 `docs/readme.md` cynefin 命令参考（含场景示例）、`CLAUDE.md` cognitive 模块说明
- [x] 7.3 CHANGELOG 记录 BREAKING：选项变更、JSON 契约变更、新增 Disorder 域
- [x] 7.4 全局复查无残留引用（旧维度 ID、旧选项名、被删函数），更新受影响的 skill 模板正文（由 Python 模板重新生成）

## 8. 收尾验证

- [x] 8.1 `pytest test/` 全绿（180 passed）；`ruff check` 新文件零告警（存量 E402 未增加）
- [x] 8.2 手工冒烟：`dm2 cynefin`（裸跑）、四条 golden 描述的 `-d` 与 `-d --json`、显式覆盖组合各一次
- [x] 8.3 `dm2 init` 到临时目录确认 `cynefin-keywords.yaml` 被复制且新项目内命令可用；`dm2 run --step step1-intent-scope` 验证 Chaotic/Disorder 两路径
- [x] 8.4 `openspec validate redesign-cynefin-model --strict` 通过
