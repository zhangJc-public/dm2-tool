## Context

dm2-tool 已完成 AI Agent 接口层改造（15 个命令支持 `--json`，InstructionBuilder 引擎）。用户希望在 Claude Code 中通 skills/commands 调用 dm2。对照 openspec 的集成模式进行研究后，发现 dm2 不需要 1:1 的 CLI 封装，而是需要 3 个复合工作流技能 + 状态记录补齐。

当前状态：
- `.claude/` 和 `openspec/` 由 openspec init/generate 管理
- dm2 有自己的项目结构（`.dm2/`, `dm2-changes/`, `output/`）
- dm2 缺少 View 生成状态追踪和 Claude Code 配置生成能力

## Goals / Non-Goals

**Goals:**
- 3 个工作流技能覆盖 dm2 的核心工程场景：探索、生成、Pipeline
- `dm2 init` 自动生成 `.claude/` 配置
- 补齐 View 生成状态追踪（ViewManager）
- 技能是"编排层"而非"知识层"——通过调用 dm2 CLI 获取指令

**Non-Goals:**
- 不封装所有 15 个 CLI 命令为独立 skill
- 不创建 MCP server
- 不修改现有 CLI 命令签名
- 不把 dm2 skills 发布为独立 plugin（后续迭代）

## Decisions

### Decision 1: 复合工作流而非 1:1 封装

dm2 有 15 个 CLI 命令，但大多数是原子操作。AI Agent 需要的是复合工作流：

```
dm2-explore:   knowledge search → cynefin → analyze → 输出推荐
dm2-generate:  instructions <view> → 生成内容 → reasoning 验证
dm2-pipeline:  run --agent → instructions → complete-step (循环4步)
```

每个技能内部调用多个 dm2 CLI 命令。AI 不需要知道每个原子命令——skill 文件告诉它怎么编排。

**Alternative**: 为每个 CLI 命令创建一个 skill → 拒绝，因为 15 个原子 skill 会让 AI 不知所措，且 openspec 也是按复合工作流组织的。

### Decision 2: "CLI is brain" 原则贯穿技能设计

Skill 文件不包含 DM2 领域知识（术语定义、视图规则、模板）。这些知识已经存在于 dm2 CLI 的 `InstructionBuilder` 中。Skill 文件只包含：
- 工作流步骤（调用哪些 CLI 命令，按什么顺序）
- 状态检查逻辑（如何判断当前进度）
- 错误处理指引

领域知识通过 `dm2 instructions <view> --json` 和 `dm2 knowledge * --json` 动态获取。

### Decision 3: ViewManager 状态模型

View 生成需要追踪状态，类似 ChangeManager 追踪 change 状态：

```python
class ViewStatus(Enum):
    PENDING = "pending"        # 推荐但未开始
    IN_PROGRESS = "in_progress" # Agent 正在生成
    GENERATED = "generated"     # 已生成内容
    VERIFIED = "verified"       # 通过一致性检查

# 状态文件: .dm2/view-state.yaml
views:
  OV-1:
    status: generated
    generated_at: "2026-05-04T..."
  OV-2:
    status: pending
```

这与 ChangeManager 的设计一致，数据持久化在 `.dm2/view-state.yaml`。

### Decision 4: `.claude/` 配置通过模板安装

`dm2 init` 时从 `templates/init/.claude/` 复制 skills 和 commands 到目标项目。已有项目通过 `dm2 setup-claude` 命令安装（本质是复制操作）。

**Alternative**: 在 dm2-tool 仓库内定义，用符号链接 → 拒绝，因为每个 dm2 项目应该独立拥有自己的 `.claude/` 配置。

## Risks / Trade-offs

- [Risk] Skill 描述的 CLI 调用与实际行为不一致 → 技能文件尽可能简单，把逻辑放在 CLI 中；CLI 的 `--json` 输出变更时会自然暴露
- [Risk] ViewManager 与 ChangeManager 状态不同步 → ViewManager 独立管理 view 状态，不与 change 耦合；视图是 change 的输出物，change archive 时不强制 view 完成
- [Trade-off] 模板复制 vs 动态生成 → 选择模板复制，简单可靠。缺点是 dm2-tool 升级后已创建的项目不会自动更新 `.claude/`，需要重新运行 `dm2 setup-claude`
