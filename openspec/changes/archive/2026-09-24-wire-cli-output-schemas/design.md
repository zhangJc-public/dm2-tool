## Context

对 `schemas/` 的审计（全仓 grep、构建脚本输入、打包配置、真实输出比对）得到三个事实：

1. **零消费者**：`src/`、`scripts/`、`pyproject.toml`、`MANIFEST.in`、CI、`docs/` 均不引用它。因此漂移不会被任何机制发现。
2. **实际已漂移**，用真实输出逐一比对后：

| schema | 比对结果 |
|---|---|
| `common.json` | ✅ 准确（信封声明） |
| `status.json` | ✅ 准确 |
| `run.json` | ✅ 准确 |
| `analyze.json` | ❌ 要求 `priority`，实际 `recommended_views` 无此字段 |
| `cynefin.json` | ❌ 要求 `recommended_view_count`（已不存在）；`domain` 枚举用中文标签，实际输出枚举名；缺 `Disorder` |
| `generate.json` | ❌ 描述 `content`/`content_length`，即已移除的 LLM 内容生成 |

3. **`generate.json` 是第 5 处 LLM 残留**：此前 `remove-llm-packaging-residuals` 清理了源码、打包、文档与 CLI 帮助文本，但漏掉了它——因为它不含 "llm" 字样，且零引用使其不会出现在任何 import/引用扫描中。

## Goals / Non-Goals

**Goals:**

- `schemas/` 从孤儿变为**被执行的契约面**：每份 schema 都有测试把真实输出绑上去。
- 修正三处失真，删除描述已移除能力的那一份。
- 让「schema 与实现分叉」在 CI 中失败，而不是无人察觉。

**Non-Goals:**

- 引入 `jsonschema` 依赖（见决策 1）。
- 穷举式补全 `cynefin`/`run` 的扩展字段（那会把 schema 变成实现副本，维护成本高且容易再次漂移）。
- 改动任何 CLI 运行时行为或输出内容。

## Decisions

**1. 不引入 `jsonschema`，改用测试内子集校验器。**
本环境无 `jsonschema`（无 pip 缓存，py3.9 也没有），安装需网络与更宽权限；而项目刚清理掉无用的 `anthropic` 依赖，取向是最小依赖。因此在校验器内实现这批文件实际用到的 9 个断言关键字，并**对未实现的关键字直接抛错**。

这个「未知关键字即失败」的设计是关键：一个朴素的手写校验器最危险的失效模式是**静默跳过它看不懂的断言**，从而给出虚假的通过。显式失败把这种风险转成了可见的测试错误。

**2. 保留 `run.json` 不设全局 `required`。**
`run` 的三种模式（`--agent` 初始化 / `--status` / `--complete-step`）输出 `data` 的形状不同：只有 `pipeline` 恒定，`first_instructions` 与 `next_step` 各自只在特定模式出现。设全局 required 会把某一种模式的合法输出判为违规。已核对 `pipeline`、`first_instructions`、`next_step` 三个属性定义与实际输出一致。

**3. `cynefin.json` 声明核心而非穷举。**
该命令输出 16 个字段（含 `signal_report`、`dimensions`、`rubric` 等结构化扩展）。若逐一声明，schema 就变成实现的镜像，两者的漂移风险反而更高。因此只声明保证存在的核心字段（`domain`、`domain_label`、`confidence`、`reasoning`）与**取值空间**（域枚举），并在 description 里写明未声明字段默认允许。契约的价值在于钉住取值空间与必需项，不在于复制结构。

**4. 域取值空间以枚举名为准。**
`domain` 承载的是 `Domain` 枚举名（`Clear`/`Complicated`/`Complex`/`Chaotic`/`Disorder`），中文标签在 `domain_label`。旧 schema 把两者混为一谈，是它失效的主因之一。

**5. 删除而非改写 `generate.json`。**
改写等于为当前输出新写一份 schema——那属于「新增契约」而非「修残留」。当前 `generate` 的输出形状尚未被任何 spec 声明，若要声明应在独立的变更里连同契约一起做，避免把两件事混在一个清理变更中。

## Risks / Trade-offs

- **手写校验器覆盖不全**：只实现 9 个关键字。缓解——`test_every_schema_uses_only_implemented_keywords` 遍历全部 schema 断言无未实现关键字，且 `validate()` 自身对未知关键字抛错；校验器本身有正反用例测试。
- **`analyze.json` 要求全部 5 个字段**：以「实测每条推荐都含这 5 个字段」为据。若将来某条推荐路径省略 `reason`，测试会失败并要求显式更新 schema——这正是期望的契约变更信号，而非误报。
- **不校验 `schema` 自身合法性**：没有 `$schema` 元校验。可接受：文件小且由测试读入，语法错误会立即暴露。
- **`generate` 输出仍无 schema**：本次刻意不补（见决策 5），属已知空白。
