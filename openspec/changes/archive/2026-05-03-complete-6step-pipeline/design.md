## Context

DM2 当前实现了 DoDAF 6 步流程中的部分能力：Cynefin 判定（`dm2 cynefin`）、6W 分析（`dm2 analyze`）、单视图生成（`dm2 generate`）、一致性检查（reasoning/consistency.py）。但这些是独立命令，无法串联执行。

LLM 驱动的融合 6 步框架（DoDAF-6Step-LLM-Driven-Research.md）定义了新的流程结构：

```
Step 1+2：意图澄清 + 范围界定 → Cynefin + 上下文预算
Step 3+4：数据定义 + 知识沉淀 → 6W矩阵 + DM2笔记网络
Step 5：  分析执行（SE四算子）→ 溯因 + OODA + TOC
Step 6：  文档化 + 知识回流 → Composite View + wikilinks
                                   ↓
                            回 Step 1（迭代）
```

**约束**：本次只保证流程完整性（每个步骤都有实现且能串联），不追求优化（LLM 调优、性能优化等留给后续版本）。

## Goals / Non-Goals

**Goals:**
- 提供 `dm2 run` 命令，可从头到尾执行融合 6 步流程
- 每个步骤产生明确的中间产物（存入 `.dm2/steps/`）
- 支持断点续跑（`dm2 run --resume`）
- 支持单步执行（`dm2 run --step <N>`）
- 最大程度复用现有模块（cynefin_analyzer, six_w_analyzer, rag, consistency, view_generator）

**Non-Goals:**
- 不优化 LLM prompt 质量（后续版本）
- 不实现 GB/T → DM2 映射（后续研究）
- 不增加新的 LLM provider 或模型配置
- 不改动现有命令的行为
- 不实现 SE 四算子的深度算法（本版本用规则引擎模拟）

## Decisions

### Decision 1: Pipeline 作为独立模块

在 `src/dm2/engine/pipeline/` 下创建独立的 pipeline 包，包含 orchestrator 和各 step 模块。理由：

- 与现有 `view_generator.py` 解耦（现有命令保持不变）
- 各 step 可独立测试
- 后续优化时只需替换对应 step 模块

**替代方案**：直接在 CLI 层串联现有命令。❌ 拒绝——CLI 命令的输出格式不统一，难以在步骤间传递结构化数据。

### Decision 2: 状态管理用 YAML 文件

使用 `.dm2/state.yaml` 管理 pipeline 状态，而非内存或数据库。理由：

- 与项目现有的文件系统架构一致
- 人类可读，方便调试
- 断点续跑自然实现（读文件即可知道当前进度）

```yaml
# .dm2/state.yaml 结构
pipeline:
  status: in_progress | completed | failed
  current_step: 5
  started_at: "2026-05-03T10:00:00"
  steps:
    step1-intent-scope:
      status: completed
      output: .dm2/steps/step1-intent-scope.md
    step3-data-requirements:
      status: completed
      output: .dm2/steps/step3-data-requirements.md
    step5-analysis:
      status: in_progress
    step6-documentation:
      status: pending
  iteration: 1
  previous_outputs: []
```

### Decision 3: Step 5 用规则引擎实现，非 LLM

OODA/TOC/溯因推理在当前版本使用规则引擎模拟（基于 patterns.py 中的 8 种 DM2 模式），不依赖 LLM。理由：

- LLM 调用成本高、不稳定
- 规则引擎的结果可预测、可测试
- SE 四算子的 LLM 实现留给后续优化版本

### Decision 4: 融合步骤命名

使用文档中的融合编号（Step 1+2, Step 3+4, Step 5, Step 6），而非原始 6 步编号。理由：

- 与研究报告保持一致
- 减少步骤数量（4 个融合步骤 vs 6 个原始步骤）
- 每个融合步骤有明确的输入/输出边界

## Risks / Trade-offs

- **[中] Step 5 规则引擎覆盖不足**: 8 种 DM2 模式可能无法覆盖所有实际场景 → 在分析报告中明确标注"规则引擎推断"与"需人工确认"的边界
- **[低] 状态文件损坏**: `.dm2/state.yaml` 损坏会导致断点续跑失败 → 状态文件是 YAML 格式，每次写入前做基本校验；损坏时可删除重建
- **[低] Pipeline 执行耗时长**: 尤其 Step 5 在大型知识库上可能较慢 → 每步开始前打印预估耗时，Step 5 支持 `--quick` 模式跳过深度分析

## Open Questions

- Step 1 的"反向质问"是走 LLM 生成还是预定义模板？当前建议先用预定义模板（基于 6W 维度），后续版本再引入 LLM 动态生成
- Step 6 的 Composite View 具体组合方式？建议初始版本支持 OV-2+OV-5a（活动+流程组合）和 SV-4+DIV-1（系统+数据组合），后续扩展
