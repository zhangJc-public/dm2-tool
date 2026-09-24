# Tasks

## 1. Schema 修正

- [x] 1.1 逐一核对 6 份 schema 与真实 CLI 输出（`status`/`analyze`/`cynefin`/`run` 实际运行取数）
- [x] 1.2 `schemas/analyze.json`：移除 `priority`，改为 `reason` + `dm2_groups`，required 取实测恒存的 5 个字段
- [x] 1.3 `schemas/cynefin.json`：`domain`/`suggested_domain` 改为枚举名（含 `Disorder`）；补 `domain_label`、`resolution`、`crisis`、`needs_clarification`；删 `recommended_view_count`；description 说明「声明核心、不穷举」
- [x] 1.4 删除 `schemas/generate.json`（描述已移除的 LLM 内容生成能力，第 5 处 LLM 残留）
- [x] 1.5 确认 `common.json`、`status.json`、`run.json` 与真实输出一致，保持不变

## 2. 接线（让 schema 有消费者）

- [x] 2.1 新增 `test/test_cli_output_schemas.py`：实现 JSON Schema 子集校验器（`type`/`required`/`enum`/`minimum`/`maximum`/`properties`/`items`/`additionalProperties`/`oneOf`）
- [x] 2.2 校验器对**未实现的关键字显式抛错**，杜绝静默漏校
- [x] 2.3 校验器自身正反用例：缺 required、类型不符、越界、`bool` 不算 `integer`、未知关键字失败
- [x] 2.4 全部 schema 断言仅使用已实现关键字
- [x] 2.5 信封契约：成功信封（`knowledge stats --json`）与错误信封（项目外 `list --json`）均满足 `common.json`
- [x] 2.6 参数化用例把 `status.json`/`analyze.json`/`cynefin.json`/`run.json` 绑到真实命令输出
- [x] 2.7 断言 `generate.json` 已不存在

## 3. 规范

- [x] 3.1 `cli-json-contract` delta：新增「输出形状须以 JSON Schema 声明并由测试执行」的要求（含信封声明、真实输出比对、未知关键字失败、失效 schema 须同步删改四个场景）

## 4. 验收

- [x] 4.1 守护有效性验证：把 `priority` 临时加回 `analyze.json` 的 required，`test_command_data_satisfies_declared_schema[analyze.json]` **如预期失败**；恢复后通过
- [x] 4.2 `pytest test/` 全绿（213 → 223）
- [x] 4.3 `ruff check` 对新增文件零报错
- [x] 4.4 `openspec validate --all --strict` 通过
- [x] 4.5 归档本变更
