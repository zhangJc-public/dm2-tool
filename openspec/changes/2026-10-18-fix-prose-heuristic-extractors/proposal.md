# Proposal

## Why

Two of the prose heuristics in `ConsistencyChecker` report defects that are not there, and one of
them blocks the whole lifecycle: `unbound_activity` is an ERROR, and `dm2 validate` only attempts
the `verified` transition when the run has zero errors — so a single false positive keeps every view
in the project at `generated`.

On a 26-view architecture this fired as "123 unbound activities" whose suggestion list contained
Mermaid edge syntax and raw table rows, and `orphan_resource` suggested a resource literally named
`Flow Description）` — a fragment of the view's bilingual title.

## What Changes

**A · activity performer binding**

`_extract_activities` matched `A\d+[:\s]+` and captured whatever followed, including Mermaid syntax;
`_extract_bound_activities` split table rows on `|` and took `parts[0]`, which is the empty string
for a leading-pipe table. The two never intersected.

The check now reads the two forms OV-5b is actually authored in — Mermaid node labels
(`A1["A1 侦测探测<br/>执行者：…"]`) and the activity table — and compares **activity IDs** to
**stated performers**. Scope narrows to OV-5b: OV-5a decomposes further than OV-5b tracks, so
requiring every OV-5a leaf to appear in OV-5b reports gaps that are not gaps.

**B · resource extraction**

Level-1 headings are dropped before extraction. A title such as
`# OV-2 作战资源流描述（Operational Resource Flow Description）` is metadata, not a resource list.

## Non-goals

- No severity change: an activity the model declares without a performer remains an ERROR.
- No new rule; the two existing heuristics are corrected in place.
