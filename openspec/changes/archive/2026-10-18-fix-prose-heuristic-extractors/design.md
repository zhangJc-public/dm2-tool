# Design

## Why the binding check is scoped to OV-5b

The old code compared OV-5a's activities against OV-5b's bindings. That comparison cannot be made
meaningful:

- OV-5a is a **decomposition tree** (50 nodes in the reference architecture, including leaves such
  as `A1.1`); OV-5b tracks the operational activities at a coarser granularity (9 rows).
- The comparison would flag every untracked leaf, which is a modelling choice, not a defect.

What is a defect: an activity OV-5b *claims to model* without naming who performs it. That is
decidable, and it is what the check now reports.

## How activity IDs are recognised

```
   _ACTIVITY_ID = (A\d+(?:\.\d+)?)\s+(?=[\w\u4e00-\u9fff])
```

The trailing lookahead is the whole point. Without it, a Mermaid node identifier
(`A53["A5.3 双人确认"]`) and edge syntax (`A1 --> A2`) both look like activities. With it, an ID is
only recognised when a label follows — which is how activity IDs are actually authored.

## Two authoring forms, one rule

| form | example | performer source |
|---|---|---|
| Mermaid node label | `A1["A1 侦测探测<br/>执行者：阵地<br/>输入：…"]` | text after `执行者：`, cut at `<br/>` or `|` |
| activity table | `| A1 侦测探测 | … | … | 阵地 | … |` | the `执行者` column, non-empty |

A performer marker with nothing after it (`执行者：<br/>`) is not a performer — the value is
extracted, not just the key.

## Consequences

- Existing projects with genuine unbound activities still see the ERROR; the rule did not soften,
  it stopped firing on syntax.
- Views that keep activities only in prose (no IDs, no table) yield no activities and therefore no
  finding — the heuristic stays quiet rather than guessing, which matches how it treats unknown
  metadata elsewhere.
