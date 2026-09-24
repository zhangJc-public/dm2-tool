# Tasks

## 1. 论证载体

- [x] 1.1 新增 `docs/foundation.md`：定位与边界、四层架构与实测依赖方向、不变量清单（每条指向 spec/test 锚点）、当前态基线（可复现命令与数值）、已知裂缝（D1–D9）、目标态与五条原则、显式非目标
- [x] 1.2 基线数值实测复核：33 spec / 119 requirement / 213 测试 / 18 顶层命令 / 30 命令的 JSON 契约分布
- [x] 1.3 记录缺陷族时按实测修正计数：D5 实为 4 个占位符 Purpose（非 6），并新增 D5b（标题层级不规范）

## 2. 规范层

- [x] 2.1 新增 delta spec `dm2-architecture-boundaries`：五级依赖序 + 「dm2 不生成视图内容」
- [x] 2.2 新增 delta spec `cli-json-contract`：信封形状、退出码、`--json` 普遍性、stdout 纯净性、错误码规范、豁免清单（`completion`/`__complete`/`uninstall`）
- [x] 2.3 新增 delta spec `view-register`（MODIFIED）：补项目前置条件与 `--json` 接受

## 3. 契约修复

- [x] 3.1 `src/dm2/cli/main.py` `_require_project(json_flag)`：JSON 模式输出 `NOT_IN_PROJECT` 信封，人类模式保留中文提示
- [x] 3.2 `src/dm2/cli/commands/change.py` 同名守卫做同样处理，4 处调用传入 `json_flag`
- [x] 3.3 `src/dm2/cli/main.py` 的 `list`/`status`/`archive`/`config` 调用点传入 `json_flag`
- [x] 3.4 `config -s` 的守卫**前置到写入之前**（原先先落盘再报错）
- [x] 3.5 `src/dm2/cli/commands/view.py` 新增守卫：`view list` 传 `json_flag`；`view register` 无人类模式故恒输出信封
- [x] 3.6 `view register` 接受 `--json`/`-j`（幂等，输出不变）
- [x] 3.7 `src/dm2/cli/main.py` 为 `validate` 补守卫
- [x] 3.8 `src/dm2/cli/main.py` 为 `run` 补守卫，且 `--agent`/`--status`/`--instructions`/`--complete-step` 子模式输出信封

## 4. 元数据卫生

- [x] 4.1 补全 4 个 spec 的占位 Purpose：`dm2-explore-workflow`、`dm2-metamodel-knowledge`、`no-new-capability`、`view-register`
- [x] 4.2 规范化 `dm2-data-group-activation` 的标题层级（`## 标题`/`### Purpose` → `# 标题`/`## Purpose`）
- [x] 4.3 删除死目录 `templates/` 并修正 `CLAUDE.md` 的两处描述（项目结构树、源码映射表）
- [x] 4.4 `CLAUDE.md` 的 JSON 契约条目改为指向 `cli-json-contract` 并列出豁免

## 5. 守护

- [x] 5.1 新增 `test/test_architecture_boundaries.py`：每个包必须有层级、无向上依赖、`utils` 为叶子
- [x] 5.2 新增 `test/test_cli_json_contract.py`：非豁免命令均接受 `--json`；豁免清单被钉住；11 条项目命令在项目外返回 `NOT_IN_PROJECT` 信封且不创建 `.dm2/`；人类模式保留中文提示
- [x] 5.3 修正测试的命令枚举：Typer 由函数名派生命令名时把下划线转连字符（`list_changes` → `list-changes`），枚举与用例路径须一致
- [x] 5.4 `.github/workflows/test.yml` 新增独立 `spec` job：`openspec validate --all --strict`（Node 20 + 固定版本 openspec）

## 6. 验收

- [x] 6.1 `pytest test/` 全绿（213 passed，194 + 19 新增）
- [x] 6.2 `ruff check` 对改动/新增文件零报错
- [x] 6.3 `openspec validate --all --strict` 通过（36 项，0 失败）
- [x] 6.4 手工逐条验收缺陷：各守卫命令在项目外返回 `NOT_IN_PROJECT` 信封且无 `.dm2/` 污染；`view register` 接受 `--json`；Agent 子模式输出信封；人类模式保持中文
- [x] 6.5 `openspec validate establish-dm2-foundation` 通过并归档
