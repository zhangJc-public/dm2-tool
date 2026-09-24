# Declare and enforce CLI output schemas

## Why

`schemas/` 有 6 个 JSON Schema 文件，但**没有任何消费者**——代码、脚本、打包配置、文档全都不引用它们，因此无人能察觉漂移。而它确实漂移了：`generate.json` 仍要求 `content`/`content_length`（已被 `remove-llm-from-dm2` 移除的 LLM 内容生成输出）；`analyze.json` 仍要求推荐器早已不再输出的 `priority`；`cynefin.json` 用中文域标签去描述一个实际承载枚举名的字段，且缺 `Disorder`。与此同时，准确的 `common.json` 正是 `cli-json-contract` 已规范、却无人强制执行的信封声明。要么接线，要么删除——让它们继续无消费者地腐烂是最差选项。

## What Changes

- **`schemas/analyze.json`**：把已移除的 `priority` 换成推荐器实际输出且始终存在的字段（`reason`、`dm2_groups`）。
- **`schemas/cynefin.json`**：修正 `domain`/`suggested_domain` 的取值空间为枚举名（含 `Disorder`），补 `domain_label`、`resolution`、`crisis`、`needs_clarification`，移除已不存在的 `recommended_view_count`；description 说明它声明的是**保证存在的核心字段**、不穷举扩展字段。
- **删除 `schemas/generate.json`**：它描述的是已被移除的 LLM 内容生成能力（第 5 处 LLM 残留）。
- **新增 `test/test_cli_output_schemas.py`**：一个 JSON Schema 子集校验器 + 把每份 schema 绑到真实 CLI 输出的测试。校验器对**未实现的关键字显式失败**，防止 schema 被静默漏校。
- **`cli-json-contract`**：新增「输出形状必须以 schema 声明并被执行」的要求。

## Capabilities

### New Capabilities
<!-- 无：schema 是既有 JSON 契约的声明形式，不构成新能力。 -->

### Modified Capabilities

- `cli-json-contract`：新增一条要求——各命令的 JSON 输出形状须在 `schemas/` 中以 JSON Schema 声明，并由测试对照真实输出执行。

## Impact

- **`schemas/`**：从孤儿目录变为被执行的契约面；`status.json`、`run.json`、`common.json` 经核对准确，保持不变。
- **测试**：新增 10 个用例，套件 213 → 223。
- **LLM 残留**：清除第 5 处（`schemas/generate.json`）。此前两轮清理未发现它，因为它既不含 "llm" 字样、又零引用，常规 grep 扫不到。
- **未改动**：CLI 运行时行为、命令输出内容、`src/` 下任何代码。
- **依赖**：不新增（`jsonschema` 在本环境不可得，且项目取向是最小依赖，故校验器为测试内实现）。
