## Why

dm2-tool 已经完成了 AI Agent 接口层的改造（15 个命令全部支持 `--json`），但在 Claude Code 中只能通过 `python3 -m dm2.cli.main ...` 手动调用。用户无法使用 Claude Code 的技能（skill）、钩子（hook）、斜杠命令（slash command）来调用 dm2，终端体验差，无法发挥 "CLI is brain, AI is hands" 的架构意图。

## What Changes

- 创建 `.claude/skills/dm2/` 技能目录，让 dm2 命令可作为 Claude Code 技能被 AI 直接调用
- 创建 `.claude/commands/dm2/` 斜杠命令目录，让用户可通过 `/dm2:xxx` 手动触发
- 在 dm2 项目初始化时自动生成 `.claude/` 配置（或提供 `dm2 setup-claude` 命令）
- 更新 CLAUDE.md 的项目说明，让 Claude Code 了解 dm2 的技能体系

## Capabilities

### New Capabilities
- `dm2-claude-skills`: 创建 Claude Code 技能文件，封装 dm2 的 CLI 命令，让 AI Agent 可以通过 Skill 工具直接调用 dm2
- `dm2-claude-commands`: 创建 Claude Code 斜杠命令，让用户可以手动输入 `/dm2:knowledge` 等命令

### Modified Capabilities
<!-- None: this is a new integration layer, existing dm2 CLI behavior is unchanged -->

## Impact

- `.claude/skills/dm2/` 目录（新增，约 10-15 个技能文件）
- `.claude/commands/dm2/` 目录（新增，约 10-15 个命令文件）
- `CLAUDE.md`（更新，添加技能/命令索引）
- dm2 项目模板 `templates/init/`（可选更新，让 `dm2 init` 自动生成 `.claude/` 配置）
