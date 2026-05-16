## Context

`dm2 instructions` 命令入口处有一个无条件 `--desc` 空值检查（`main.py:957-960`），在任何类型解析之前执行。这导致 view 类型指令（如 `StdV-1`）即使不需要系统描述，也被迫要求 `--desc`。下游 `InstructionBuilder.build_view_instructions()` 已兼容空 `description` 参数。

## Goals / Non-Goals

**Goals:**
- view 指令的 `--desc` 变为可选，不提供时注入引导提示
- step 指令保持 `--desc` 必填，但检查移到类型解析之后
- 下游代码不变

**Non-Goals:**
- 不新增独立字段（复用 `project_description` 注入提示）
- 不改变带 `--desc` 时的现有行为
- 不改造 `InstructionBuilder`

## Decisions

**1. 检查后移到 `is_step` 确定之后**

空值检查从 line 957 移到 line 991 之后。只有在 `is_step=True` 且 `description=""` 时才报错。原因：类型解析必须先行，才能区分 view/step 的不同需求。

**2. View 路径注入引导提示到 `project_description`**

当 `!is_step` 且 `description=""` 时，将默认值从 `""` 替换为引导提示文案。提示内容：

```
⚠️ 未提供 --desc 参数。建议使用 AskUserQuestion 工具与用户互动，提供几个讨论方向或预设选项，共同明确视图生成目标。
```

选择 `project_description` 作为载体而非新增字段，因为：
- 不改变输出 JSON schema，Agent 无需适配新字段
- `project_description` 是 Agent 必须读取的 context 字段
- 对下游 `InstructionBuilder` 完全透明

**3. Step 路径保持硬阻断**

Step 指令（`step1-intent-scope` 等）的模板围绕系统描述构建（意图澄清、Cynefin、6W），空描述产生的指令空洞无意义。保持 `MISSING_ARG` 错误，但错误信息精准到 step 类型。

## Risks / Trade-offs

- 引导提示是中文硬编码 → 后续可考虑模板化或根据 `$LANG` 自适应，但当前不支持多语言
- 如果 Agent 忽略了引导提示直接生成视图 → 风险低，因为 DM2 context 和 rules 仍在返回中，Agent 至少有 DoDAF 规范指导
