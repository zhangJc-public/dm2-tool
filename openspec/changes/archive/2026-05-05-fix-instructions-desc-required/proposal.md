## Why

`dm2 instructions` 对 `--desc` 参数做了无条件拦截：无论指令类型是 view 还是 step，只要 `--desc` 为空就直接报 `MISSING_ARG` 错误。这导致 AI Agent 在 `/dm2:ff` 等自动化工作流中、对已有项目描述的场景（如 StdV-1 标准轮廓这类零依赖视图），被迫重复提供描述文本才能获取 DM2 上下文和模板。Agent 被阻断在获取指令这一步，无法继续执行。

## What Changes

- `--desc` 参数对 view 类型指令变为可选：不提供时注入引导提示，驱动 Agent 与用户互动明确方向
- `--desc` 参数对 step 类型指令保持必填，但检查从入口处移到类型解析之后
- 下游 `InstructionBuilder` 无需修改（已有空值兼容）

## Capabilities

### New Capabilities

- `instructions-desc-optional`: `dm2 instructions` 命令的 `--desc` 参数按指令类型差异化处理——view 可选（注入引导提示），step 必填（类型解析后检查）

### Modified Capabilities

<!-- No existing specs to modify — instructions command has no dedicated spec -->

## Impact

- `src/dm2/cli/main.py` lines 957-960（删除无条件检查）+ 991 附近（新增条件检查 + view 路径引导提示）
- 不影响下游 `InstructionBuilder`、`KnowledgeAPI`、`ArtifactGraph`
- 不影响现有调用方式（带 `--desc` 时行为完全不变）
