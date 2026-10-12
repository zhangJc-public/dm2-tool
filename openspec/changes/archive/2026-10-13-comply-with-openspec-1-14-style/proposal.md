## Why

本地 `openspec` 已升级到 **1.14.1**（2026-10-12 23:41，本会话开始时为 1.13.1）。新版本把「requirement 文本 >500 字符」从 INFO 提升为 **WARNING**，而本仓库的关口是 `openspec validate --all --strict`（**strict 视警告为失败**），于是：

- **本地 strict 关口对 5 个既有 spec 变红**：`dm2-architecture-boundaries`(1)、`dm2-cynefin-auto-derive`(4)、`dm2-cynefin-model`(4)、`view-metadata-schema`(1)、`view-provenance`(1)，共 **11 条 requirement**（最长 1550 字符）
- **CI 仍然绿，但只因版本锁定**：`.github/workflows/test.yml` 安装 `@fission-ai/openspec@1.13.1`。于是本地与 CI 的关口口径不一致——同一份规范，本地判红、CI 判绿

这不是 dm2 的行为缺陷，而是**规范文本形态**跟不上新的风格规则。处理方式有两条（详见 design），本变更选「改写 11 条 requirement + 升级 CI」，因为那条路同时消除口径分歧并提升规范可读性：把表格、字段清单与示例从 requirement 正文移入场景，让每条 requirement 只陈述一条行为。

## What Changes

- **改写 11 条 requirement 的正文**（5 个 spec）：只做**结构调整**——枚举、表格、字段清单与举例移入场景，SHALL 语义一条不减
- **场景不丢**：所有既有场景**原样保留**（含标题与正文），OpenSpec 的 MODIFIED 校验会强制这一点；被移出的内容以**新增场景**承载
- **CI 升级**：`.github/workflows/test.yml` 的 openspec 版本从 `1.13.1` 提到 `1.14.1`，与本地一致
- **文档**：`docs/foundation.md` 的 D11 从「已记录」移入「已修复」，基线行恢复「38 通过 / 0 失败」；CHANGELOG 记录

## Capabilities

### Modified Capabilities

- `dm2-architecture-boundaries`、`dm2-cynefin-auto-derive`、`dm2-cynefin-model`、`view-metadata-schema`、`view-provenance`：**仅 requirement 正文的形态**变化（枚举与示例移入场景），行为契约不变。

## Impact

**Affected artifacts**:
- `openspec/specs/<上述 5 个>/spec.md`（经归档应用 delta）
- `.github/workflows/test.yml`（openspec 版本）
- `docs/foundation.md`、`CHANGELOG.md`

**Affected code**: 无。本变更**不改任何 Python 源码与测试**——这是纯规范文本重构。

**Compatibility**:
- 规范语义不变：每条 requirement 的 SHALL 陈述与场景断言逐条保留
- 归档后本地与 CI 的 strict 关口都回到全绿

**Invariant check**:
- 不违反任何横切不变量（零 LLM、架构边界、JSON 契约等均不涉及）
- 规范仍是行为权威来源，且**这次修改由 OpenSpec 自身的校验器守护**（MODIFIED 必须保留全部既有场景）
