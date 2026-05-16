# dm2 工作流说明

dm2-tool 的工作流引擎基于 Python `WorkflowTemplate` 模板系统（`src/dm2/core/templates/workflows/`），通过 `ClaudeCodeAdapter` 自动生成 `.claude/skills/`（AI 实现指令）和 `.claude/commands/dm2/`（用户斜杠命令入口）。

---

## 工作流全景

```
CORE（核心路径）:

  /dm2:explore  ──→  /dm2:propose  ──→  /dm2:apply  ──→  /dm2:verify  ──→  /dm2:archive
    (只读探索)       (分析 + 规划)      (任务驱动实施)     (一致性检查)       (归档收尾)


EXPANDED（扩展命令）:

  /dm2:new          — 创建变更目录脚手架（不分析）
  /dm2:continue     — 逐步生成视图（分析驱动，可中断恢复）
  /dm2:ff           — 全自动批量生成（跳过规划）
  /dm2:bulk-archive — 批量归档多个变更
  /dm2:onboard      — 交互式教程
```

---

## 核心工作流详解

### `/dm2:explore` — 探索

**用途**: 只读思考模式。查询 DM2 知识库、对比 DoDAF 视图、讨论架构决策。

**触发**: `/dm2:explore [主题]`

**要点**:
- 不生成任何文件，不创建任何变更
- 使用 `dm2 knowledge * --json` 系列命令查询知识库
- 可以用 ASCII 图辅助讨论
- 讨论明确后，可自然过渡到 `/dm2:propose`

---

### `/dm2:propose` — 分析 + 规划产出

**用途**: 对系统描述执行全流程分析，产出规划文档（proposal.md、design.md、tasks.md）。

**触发**: `/dm2:propose <系统描述>`

**流程**:
1. 获取系统描述（如未提供则询问）
2. `dm2 change new <name>` — 创建变更目录
3. `dm2 cynefin --json -d "<描述>"` — Cynefin 复杂度评估
4. `dm2 analyze --json -d "<描述>"` — 17 数据组激活分析
5. `dm2 concern list --json` — 关注点匹配 + 人工选择
6. 聚焦视图集（P1/P2/P3 三阶段）
7. 生成规划产出：
   - `dm2-changes/<name>/proposal.md` — 为什么、范围
   - `dm2-changes/<name>/design.md` — 技术方案、决策
   - `dm2-changes/<name>/tasks.md` — 视图生成任务清单

**产出**:
```
dm2-changes/<name>/
├── proposal.md     ← 系统描述、复杂度评估、数据组激活、关注点选择、聚焦视图集
├── design.md       ← 数据组分析、视图选择逻辑、依赖链、阶段划分
├── tasks.md        ← 视图任务（P1/P2/P3 分阶段、依赖排序）
└── analysis/       ← AI Agent 可选分析产物（用于审计）
```

**下一步**: 推荐 `/dm2:apply`（备选：`/dm2:continue` 逐步生成、`/dm2:ff` 跳过规划）。

---

### `/dm2:apply` — 任务驱动视图生成

**用途**: 读取 tasks.md（propose 产出），按依赖顺序生成全部 DoDAF 视图，勾选 checkbox。

**触发**: `/dm2:apply [变更名称]`

**流程**:
1. 选择变更
2. 读取 `proposal.md` + `design.md` + `tasks.md`
3. 解析待执行任务：`- [ ] Generate <View-ID>: <description>`
4. `dm2 knowledge views --json` — 获取依赖拓扑，排序任务
5. 逐个生成视图：
   - `dm2 instructions <view_id> --change "<name>" --json`
   - 生成内容 → 写入 `dm2-changes/<name>/views/<View-ID>.<ext>`
   - `dm2 view register <view_id> --change "<name>" --path "..."`
   - tasks.md 中 `- [ ]` → `- [x]`
6. 显示摘要

**与 continue/ff 的区别**:

| 维度 | `/dm2:apply` | `/dm2:continue` | `/dm2:ff` |
|------|-------------|-----------------|-----------|
| 驱动源 | tasks.md | view-state.yaml | 重跑 cynefin + analyze |
| 节奏 | 批量 | 逐个 | 批量 |
| 可恢复 | 是 | 是 | 否 |
| 读规划文件 | 是 | 否 | 否 |
| 定位 | 标准路径 | 中断后继续 | 快速原型 |

---

### `/dm2:verify` — 视图一致性检查

**用途**: 验证已生成视图的完整性、正确性、跨视图一致性。

**触发**: `/dm2:verify [变更名称]`

**流程**:
1. 选择变更
2. `dm2 change status --json` — 检查变更状态
3. 读取 `dm2-changes/<name>/views/` — 遍历视图文件
4. `dm2 knowledge view <id> --json` — 获取期望的章节结构
5. 对比三方面：
   - **Completeness**: 推荐视图是否全部生成？视图是否缺章节？
   - **Correctness**: 是否符合 DM2 规则？术语是否准确？
   - **Coherence**: 跨视图是否一致？（Activity-Performer 绑定、Resource Flow 完整性等）
6. 生成检查报告 `dm2-changes/<name>/reports/verify.md`

**产出**: 三类问题级别：
- CRITICAL（必须修复才能归档）
- WARNING（建议修复）
- SUGGESTION（非必须改进）

---

### `/dm2:archive` — 单变更归档

**用途**: 归档单个已完成的架构变更，确认后移入 dm2-archive/。

**触发**: `/dm2:archive [变更名称]`

**流程**:
1. 选择变更
2. `dm2 change status --json` — 检查变更状态
3. 读取 tasks.md 汇总完成度
4. 可选验证：`dm2 validate --all --change "<name>" --json`
5. 展示归档摘要，确认
6. `dm2 archive "<name>" --json` — 执行归档
7. 显示归档位置

**注意**: 会警告未完成的任务，但不阻塞归档。

---

## 扩展命令

### `/dm2:new` — 创建变更目录

创建 `dm2-changes/<name>/` 脚手架（仅目录 + `.change.yaml`），不执行任何分析。由 `/dm2:propose` 内部复用，独立暴露用于手动管理场景。

### `/dm2:continue` — 逐步视图生成

每次生成一个视图（分析驱动，由 view-state.yaml 决定），适合中断后继续。区别 `/dm2:apply`（任务驱动批量）和 `/dm2:ff`（分析驱动批量）。

### `/dm2:ff` — Fast-Forward

全自动批量生成所有推荐视图。自己跑 cynefin + analyze 决定生成哪些视图，跳过规划阶段。

### `/dm2:bulk-archive` — 批量归档

多变更批量归档。检测跨变更的视图类型冲突（同类型视图在多个变更中出现），按时间顺序解决。适合并行开发后的清理。

### `/dm2:onboard` — 交互式教程

引导新用户走完完整 DoDAF 架构建模流程（~10-15 分钟），使用真实系统描述做 Cynefin 评估、6W 分析、视图生成和验证。

---

## 模板架构

每个工作流由 Python 模板定义：

```
src/dm2/core/templates/workflows/
├── apply.py            →  .claude/skills/dm2-apply-workflow/SKILL.md
│                           .claude/commands/dm2/apply.md
├── archive.py          →  .claude/skills/dm2-archive-workflow/SKILL.md
│                           .claude/commands/dm2/archive.md
├── bulk_archive.py     →  .claude/skills/dm2-bulk-archive-workflow/SKILL.md
│                           .claude/commands/dm2/bulk-archive.md
├── continue_workflow.py→  .claude/skills/dm2-continue-workflow/SKILL.md
│                           .claude/commands/dm2/continue.md
├── explore.py          →  .claude/skills/dm2-explore-workflow/SKILL.md
│                           .claude/commands/dm2/explore.md
├── ff.py               →  .claude/skills/dm2-ff-workflow/SKILL.md
│                           .claude/commands/dm2/ff.md
├── new_workflow.py     →  .claude/skills/dm2-new-workflow/SKILL.md
│                           .claude/commands/dm2/new.md
├── onboard.py          →  .claude/skills/dm2-onboard-workflow/SKILL.md
│                           .claude/commands/dm2/onboard.md
├── propose.py          →  .claude/skills/dm2-propose-workflow/SKILL.md
│                           .claude/commands/dm2/propose.md
├── verify.py           →  .claude/skills/dm2-verify-workflow/SKILL.md
│                           .claude/commands/dm2/verify.md
└── __init__.py         ← WORKFLOWS 注册表
```

模板使用 `WorkflowTemplate` dataclass（含 `SkillTemplate` + `CommandTemplate`），由 `generate_agent_config()` 统一生成到 `.claude/skills/` 和 `.claude/commands/dm2/`。Skills 设为 `user-invocable: false`，不出现在用户 "/" 菜单中；Commands 作为用户入口。

重新生成命令：

```bash
python3 -c "
from dm2.core.templates.generator import generate_agent_config
from dm2.core.adapters.claude import ClaudeCodeAdapter
from pathlib import Path
generate_agent_config(Path('.'), 'dev', ClaudeCodeAdapter())
"
```
