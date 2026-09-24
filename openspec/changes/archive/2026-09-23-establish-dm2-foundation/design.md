## Context

一次针对「地基」的只读审计（证据全部可复现，见 `docs/foundation.md`）得到两个结论：

**架构原则是真被遵守的。** 对 `src/dm2/**` 做 import 静态扫描，层间依赖严格自上而下，无反向边，`utils` 是不依赖任何内部层的纯叶子。

**横切契约从未被规范化。** JSON 信封被 28/30 个命令实践，但既无 spec 也无测试；项目守卫只覆盖部分命令，且失败时输出纯文本；CI 不校验 spec。

审计发现的缺陷族（编号对应 `docs/foundation.md` §5）：

| 缺陷 | 现象 |
|---|---|
| D3a | 守卫失败时 `stdout` 为纯文本，Agent 无法解析 |
| D3b | `view list`/`view register` 无守卫 → 在任意 CWD 静默创建 `.dm2/` |
| D3c | `run` 无守卫 → 项目外静默创建 `.dm2/state.yaml` 并返回 `success` |
| D3d | `validate` 无守卫 → 项目外返回**误导性成功**（`issues: []`） |
| D3e | `config -s` 守卫在写入之后 → 先落盘再报错 |
| D4 | `view register` 拒绝 `--json`，而 5 个技能模板要求「总是传 `--json`」 |
| D7 | CI 不校验 spec → 此前 17 个 spec 长期烂掉 |

## Goals / Non-Goals

**Goals:**

- 把已经做对的事（分层、信封）变成**不会被悄悄做错**的事：spec 化 + 测试守护 + CI 关口。
- 让地基文档成为可引用的权威：每条不变量都指向守护它的 spec 或 test。
- 收口审计暴露的全部矛盾，或显式判定为豁免。

**Non-Goals:**

- 环境适配（DSH 原生工具、agent preset、多工具分发）——按用户决定延后。
- 中文检索召回（`knowledge search` 对中文返回 0）——属知识库内容层，独立变更。
- 非交互式 `uninstall`——判定为豁免。
- 合并 `_require_project` 的多份拷贝——属重构；且**不得**下沉到 `utils`（那会形成向上依赖，违反本次刚立的不变量）。
- 全面审计既有 spec 体系——仅补 Purpose 与新增两条契约。

## Decisions

**分层用「五级依赖序」而不是四个概念层名。** `CLAUDE.md` 的四层是概念划分（Agent Interface / Core Engine / Knowledge Base / File System），与 `src/` 包不是一一对应。为了让测试可判定，spec 采用包级可执行的五级序（`utils` L0 < `config`/`kernel` L1 < `cognitive`/`reasoning`/`core` L2 < `engine` L3 < `cli` L4），并在文档中说明它是概念四层的可执行形式。这样规则既忠于原意又能被机械检查。

**守卫必须输出信封，判定依据是「该命令有没有人类输出模式」**，而不是「调用方有没有传 `--json`」：

| 命令形态 | 守卫行为 |
|---|---|
| 有人类模式（`list`/`status`/`validate`…） | 传 `--json` 才输出信封，否则保留中文提示 |
| 无人类模式（`view register`） | 恒输出信封 |
| Agent 子模式（`run --agent/--status/--instructions/--complete-step`） | 恒输出信封（这些模式本就无条件输出 JSON） |

只按 `json_flag` 判定会漏掉后两类——实测中 `run --agent` 与不带 `--json` 的 `view register` 都会退化成纯文本。

**`view register` 接受 `--json` 而非改为人类输出。** 该命令没有人类输出需求，加人类模式是为对称而造需求。正确做法是它接受该 flag（幂等），使模板里「总是传 `--json`」的约定**普遍适用**——这正是 D4 矛盾的根源。

**守卫放在 CLI 层，而不是让 `ViewManager` 等核心类快速失败。** 信封是 CLI 契约，CLI 层是它的归属。改核心库行为会扩大影响面，且核心类以 `Path.cwd()` 回退是有意为之（允许显式指定 project_root）。

**`uninstall` 判定为豁免而不是补 JSON。** 它是带交互确认的人工维护命令；给 Agent 提供无人值守卸载能力与「CLI 是大脑」的定位相悖。豁免写进 spec 的清单，避免成为「未判定的不一致」。

**豁免清单由测试钉住。** 新增豁免必须同时改 spec 与测试，否则测试失败——防止豁免被悄悄扩大。

**CI 用 `--strict` 且独立成 job。** strict 会把警告也视为失败（占位 Purpose 正是被它抓到的类别）；独立 job 避免在 4 个 Python 版本上重复跑同一个校验。

## Risks / Trade-offs

- **行为变化可能影响既有调用方**：项目外调用 `validate`/`run`/`view *` 从「静默成功」变为报错。这正是修复目标，但属**可观察的行为变更**；已在 proposal 的 Impact 中列出。项目内行为不变。
- **三份 `_require_project` 拷贝**：本次补齐并统一语义，但保持独立。风险是未来新增第四份时漏加 JSON 感知——由契约测试的 `--json` 覆盖面 + 守卫用例缓解。
- **架构测试对新增包敏感**：新包未登记进 `LEVELS` 会直接失败（`test_every_package_has_a_level`），这是有意的——强制显式归层，而不是默默放行。
- **CI 新增 npm 依赖**：openspec 版本固定为 `1.13.1`（与本地一致），避免校验器行为漂移导致假失败；若 npm 源不可达，该 job 会明确失败而不是静默跳过。
- **`templates/` 删除**：已三重确认无引用（无代码引用、未参与打包、`init` 内联生成），故无功能影响。
- **用正则解析 import 判定分层**：只匹配 `from dm2.X` / `import dm2.X` 形式，动态导入不在覆盖内。当前代码无动态导入；若将来引入，测试需同步增强。
