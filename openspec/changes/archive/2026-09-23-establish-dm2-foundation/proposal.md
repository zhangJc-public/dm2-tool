# 打好 dm2 地基

## Why

dm2 的架构原则在代码里**确实被遵守**（分层无反向依赖、`utils` 是纯叶子），但横切契约从未被规范化：JSON 信封被 28/30 个命令实践，却**既无 spec 也无测试守护**。结果是同类不一致反复出现——项目守卫覆盖不全，导致 stdout 被纯文本污染、`view register`/`run` 在项目外静默写状态、`validate` 返回误导性成功；而 `view register` 拒绝 `--json`，恰恰与 5 个技能模板「总是传 `--json`」的要求自相矛盾。更根本的是 CI 只跑 pytest 与 ruff，**不校验 spec**，这正是此前 17 个 spec 能长期烂掉的原因。地基不牢，后续每个功能都会叠在漂移之上。

## What Changes

- **新增地基文档** `docs/foundation.md`：论证当前 dm2（附可复现证据与实测基线）与改进后的 dm2（原则、边界、目标态）。（D1）
- **新增 spec `cli-json-contract`**：信封形状、退出码、`--json` 普遍性、stdout 纯净性、错误码规范、**显式豁免清单**。（D2）
- **新增 spec `dm2-architecture-boundaries`**：五级依赖序（`utils` < `config`/`kernel` < `cognitive`/`reasoning`/`core` < `engine` < `cli`）与「dm2 不生成视图内容」。（D2）
- **修复项目守卫缺陷族**：守卫感知 JSON 输出 `NOT_IN_PROJECT` 信封；为 `view list`/`view register`/`validate`/`run` 补缺失守卫；`config -s` 守卫前置到写入之前。（D3a–D3e）
- **`view register` 接受 `--json`**，使模板约定普遍适用。（D4）
- **补全 4 个 spec 的占位 Purpose**，并规范化 1 个 spec 的标题层级。（D5/D5b）
- **删除死目录 `templates/`** 并修正 `CLAUDE.md` 对它的错误描述。（D6）
- **CI 增加 spec 关口**：`openspec validate --all --strict` 独立 job。（D7）
- **新增两个守护测试**：架构依赖方向、CLI JSON 契约。

## Capabilities

### New Capabilities

- `dm2-architecture-boundaries`：分层依赖方向与「CLI 是大脑」分工，使架构原则从散文变为可测试的不变量。
- `cli-json-contract`：Agent 机器可读接口的完整契约（信封、退出码、`--json` 普遍性、stdout 纯净性、豁免清单）。

### Modified Capabilities

- `view-register`：该命令新增项目前置条件（项目外返回 `NOT_IN_PROJECT`）并接受 `--json`，其原有「总是输出 JSON」的要求需要与契约 spec 对齐。

## Impact

- **代码**：`src/dm2/cli/main.py`（共享守卫感知 JSON、`validate`/`run` 补守卫、`config -s` 守卫前置）、`src/dm2/cli/commands/change.py`（同守卫）、`src/dm2/cli/commands/view.py`（新增守卫 + `view register --json`）。
- **行为变化**：`list`/`status`/`archive`/`config`/`change *`/`view *`/`validate`/`run` 在**项目外**由「纯文本错误」或「静默成功」变为 `NOT_IN_PROJECT` 信封（exit 1）。项目内行为不变。
- **测试**：新增 `test/test_architecture_boundaries.py`、`test/test_cli_json_contract.py`；套件 194 → 213。
- **CI**：`.github/workflows/test.yml` 新增 `spec` job（Node 20 + `@fission-ai/openspec@1.13.1` 固定版本）。
- **文档**：新增 `docs/foundation.md`；`CLAUDE.md` 修正 `templates/` 与 JSON 契约条目。
- **规范**：4 个 spec 的 Purpose 由归档占位符改为真实内容；1 个 spec 结构规范化。
- **删除**：`templates/`（死目录，已被 git 跟踪）。
- **未改动**：视图/变更生命周期、知识库索引生成、适配器与技能模板正文、Claude 生成物。
