## Context

`openspec` 1.14.1 引入的严格风格规则要求 requirement 正文 ≤500 字符（超限即 WARNING，而本仓库 strict 视警告为失败）。11 条既有 requirement 是长文形态：它们把「维度定义表」「解析规则编号列表」「字段清单」直接写在正文里，例如 `view-provenance` 的 Pedigree 数据模型（1550 字符）就是一个字段清单表。

两种处理方式：

| 方案 | 做法 | 代价 |
|---|---|---|
| A（本变更） | 把表格/枚举/示例移入场景，正文只留 SHALL 陈述；CI 升到 1.14.1 | 需要改写 11 条正文，并保证语义不减 |
| B | 本地装回 `1.13.1`，与 CI 锁定版本一致 | 一行命令；但停在旧版，风格问题仍在，且未来升级会重复遇到 |

选 A：它同时消除「本地红 / CI 绿」的口径分歧，并把规范改成更符合 OpenSpec 意图的形态（一条 requirement 一条行为）。

## Goals / Non-Goals

**Goals**

- 5 个 spec / 11 条 requirement 的正文 ≤500 字符
- **语义一条不减**：正文里的每一条 SHALL 要么留在正文，要么以场景断言的形式保留
- 既有场景**零改动**（标题与正文原样保留），被移出的内容以新增场景承载
- 归档后本地与 CI 的 `openspec validate --all --strict` 都是 38/38

**Non-Goals**

- 不改任何 Python 源码、测试与运行时行为
- 不借机改写既有场景的措辞或断言（保持「只动正文」的可审性）
- 不重排 requirement 顺序、不改标题（避免 delta 变成大范围重写）
- 不引入 1.14 之外的其他新特性

## Decisions

### Decision 1: 用脚本搬运场景，只人工撰写正文

**选择**：delta 文件由脚本生成——从现行 spec 抽取每条 requirement 的**全部场景正文原样拼入** MODIFIED 块，人工只提供压缩后的正文与被移出内容的新场景。

**理由**：MODIFIED 块会**整块替换**现行 requirement，场景必须逐字保留否则归档会拒绝。手工转写 11 条 × 30 余个场景必然引入转写误差；脚本搬运把风险压到「我写的正文」这一处。

### Decision 2: 被移出的内容进**新增场景**，不进既有场景

**选择**：表格/字段清单移入新场景（如「The five levels are fixed」「The pedigree fields are fixed」），既有场景一字不动。

**理由**：改动既有场景会让「这次只动正文」这一可审性主张失效；新增场景既承载了被移出的规范内容，又保持 delta 的差异面最小。

### Decision 3: 正文压缩以「去掉枚举、保留 SHALL」为准，不做语义合并

**选择**：压缩时**只删除**可枚举的清单、示例与解释性从句；每条 SHALL 陈述保留原样或等价措辞。例如 `view-provenance` 的字段清单移入场景后，正文只留「SHALL define a `Pedigree` data model ... as a YAML-serializable dataclass」+「字段与类型固定如下」。

**理由**：规范语义是权威，压缩不能变成「顺手改需求」。逐条对照原文是验收动作（见任务 4）。

### Decision 4: CI 直接升到 1.14.1

**选择**：`.github/workflows/test.yml` 的 `npm install -g @fission-ai/openspec@1.14.1`。

**理由**：本地已是 1.14.1；继续锁 1.13.1 会让「本地红 / CI 绿」长期存在，而 CI 本来就该是权威关口。升版后 CI 与本地同口径。

## Risks / Trade-offs

- **[风险] 压缩过程中悄悄丢掉一条 SHALL** → 逐条对照原文核对（任务 4.1–4.5），并在归档后对每个 spec 复核「SHALL 计数不减少」。
- **[风险] 表格移入场景后语义弱化**（场景是「举例」语气）→ 新场景的 THEN 用 SHALL 措辞，并明确「as tabulated」的正文指向该场景。
- **[取舍] delta 体积大**（11 条 requirement 及其场景全文）→ 这是 MODIFIED 机制的必然代价；换来的是归档后规范自洽。
- **[风险] 未来 openspec 再加风格规则** → 本变更后 CI 与本地同版本，新规则会在下一轮升级时一次性暴露，而不是长期口径分歧。

## Migration Plan

1. 归档本变更 → 5 个 spec 应用新正文，新增场景就位。
2. 提升 CI 版本到 1.14.1 → CI 与本地同口径。
3. `docs/foundation.md` D11 关闭，基线行恢复全绿。

## Open Questions

- 是否要为「requirement 正文 ≤500 字符」加一条本地守护（例如 CI 里再跑一次 strict 就够）？**当前默认**：CI 的 strict 关口本身就是守护，不加额外脚本。
