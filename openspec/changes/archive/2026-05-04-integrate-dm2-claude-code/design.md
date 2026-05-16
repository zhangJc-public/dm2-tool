## Context

dm2-tool 是一个 DoDAF 系统工程辅助工具，已完成 AI Agent 接口层改造。目前 dm2 只能通过 shell CLI 调用（`python3 -m dm2.cli.main ...`），无法利用 Claude Code 的技能/命令体系。Claude Code 支持两种集成机制：

- **Skills**（`.claude/skills/`）：AI Agent 可以读取并按照指令执行的 Markdown 文件
- **Commands**（`.claude/commands/`）：用户手动输入的斜杠命令

当前 dm2 项目已存在 openspec 的 skills 和 commands（`.claude/skills/openspec-*`, `.claude/commands/opsx/`），可以作为参考模式。

## Goals / Non-Goals

**Goals:**
- 用户可以在 Claude Code 中通过 `/dm2:xxx` 斜杠命令手动调用 dm2 功能
- AI Agent 可以通过 Skill 工具读取 dm2 技能指令，自动调用 dm2 命令
- dm2 各命令的 skill/command 定义结构清晰、易于维护
- `dm2 init` 创建的项目自动包含 `.claude/` 配置（可选）

**Non-Goals:**
- 不修改 dm2 CLI 本身的命令签名或行为
- 不创建 MCP server（本期不做，后续迭代）
- 不创建全局安装的 skills（skills 是项目级的）

## Decisions

### Decision 1: 两层集成（Skills + Commands）

Commands 给用户手动触发（`/dm2:knowledge search OV-2`），Skills 给 AI Agent 自动调用。两者内容类似但角色不同：Command 是用户的快捷入口，Skill 是 AI 的操作手册。

**为什么不用 Hooks**：Hooks 适合触发自动化（如 pre-tool-hook 检查 dm2 项目状态），跟"调用 dm2 命令"的需求不匹配。Hooks 可以后续按需添加。

### Decision 2: 按命令组组织

dm2 有 15 个命令，按功能分为 5 组：

| 命令组 | 命令 | 用途 |
|--------|------|------|
| knowledge | search, concept, views, view, stats | DM2 知识库查询 |
| analyze | cynefin, analyze, generate | 架构分析 |
| pipeline | run, instructions | Agent 驱动 Pipeline |
| change | change new/status/list/archive | 变更管理 |
| project | init, status, list, archive, config, version | 项目管理 |

每组对应一个 skill 和一个 command。

### Decision 3: Skill 用 Bash 工具调用 dm2 CLI

Skill 指令指导 AI Agent 使用 `python3 -m dm2.cli.main <command> --json` 调用 dm2，而非通过 Python API。原因是：
- CLI 是稳定接口，已有完整的错误处理和 JSON 输出
- 不引入额外的 Python 依赖
- Agent 可以像人类一样通过 CLI 输出理解 dm2 行为

### Decision 4: 安装位置

Skills 和 commands 放在 dm2-tool 项目的 `.claude/` 目录下。`dm2 init` 时可以选择性地复制到新项目中。

对于已有项目（如 `md2_model/my-project`），提供脚本或命令来安装 `.claude/` 配置。

## Risks / Trade-offs

- [Risk] Skill 文件与实际 CLI 行为不一致 → 定期用 test suite 验证 CLI 输出与 skill 描述匹配
- [Risk] 用户安装了多个 dm2 项目，skill 重复 → 每个项目独立管理，不冲突
- [Trade-off] Skills 定义在 dm2-tool 仓库中，其他项目需要复制 → 保持简单，后续考虑发布为 plugin
