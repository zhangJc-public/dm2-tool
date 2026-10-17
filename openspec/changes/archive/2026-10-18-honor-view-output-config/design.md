# Design

## Precedence between the two switches

```
   diagram_output == "svg"       → emit the external-figure section; include_mermaid is not consulted
   diagram_output == "mermaid"   → emit an inline Mermaid section only when include_mermaid is true
   diagram_output invalid/absent → fall back to "mermaid"
```

`diagram_output` wins because it names the *carrier*; `include_mermaid` only decides whether the
Mermaid carrier is used. This ordering is what makes `test_svg_wins_over_include_mermaid` meaningful.

## Representation check rules

| declared `representation` | accepted evidence |
|---|---|
| maps to a Mermaid type | a `mermaid` block whose type is in the allowed set, **or** a figure reference (`svg`/`png`/`jpg`) |
| `table` / `text` | no `mermaid` block |
| unknown / absent | skipped — the checker stays silent rather than guessing |

`graph` and `flowchart` are treated as one family: both are directed graphs and the Mermaid
distinction between them is cosmetic.

## Severity policy

Warnings by default. A checker that suddenly fails `verified` for every project written before this
change would be a breaking change disguised as a bug-fix, so promotion is opt-in through the
existing `consistency.strict_mode` key rather than a new knob.

## Why not rule R6

`pedigree.validation` stores explicit `ran_R1..ran_R5` booleans. A sixth conformance rule would need
a model field, a migration for existing records, and a change to `last_ran_rules` reporting. The
representation check is a property of one view's content, not of the metamodel, so it fits beside
`ConsistencyChecker` — which also keeps its issues in the same `ConsistencyIssue` shape the report
and JSON output already understand.

## Consequences

- Views that reference an external figure satisfy the diagram requirement without dm2 learning about
  images — this is what keeps the checker usable for projects that draw in SVG.
- `dm2 validate` output can gain warnings for views written before this change. Documented in the
  CHANGELOG; no `verified` state is withdrawn retroactively.
