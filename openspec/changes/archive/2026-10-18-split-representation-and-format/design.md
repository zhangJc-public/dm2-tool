# Design

## Two axes, one compatibility matrix

```
   representation  →  what structure is conveyed     (fixed by the view)
   format          →  how it is carried              (a project decision)

   relation = COMPATIBLE_FORMATS[representation][format] ∈ {native, lossy, external}
```

`lossy` exists so the model can be honest about a carrier that drops structure — a
`pictorial` drawn as a Mermaid graph loses layout — without forbidding it. Projects that need the
old behaviour can still ask for it.

## Resolution order

```
   1. views.formats.overrides.<View-ID>     (if compatible)
   2. views.formats.default                 (diagram views only, if compatible)
   3. views.diagram_output == "svg"         (diagram views only, legacy)
   4. DEFAULT_FORMAT[representation]
```

The project default is deliberately restricted to diagram views. Without that guard,
`formats.default: svg` would drag every `table` view into a lossy SVG — a setting about diagrams
would silently change prose views.

Incompatible values are skipped rather than coerced, so a typo degrades to the default instead of
producing a view dm2 cannot render.

## Why `pictorial` defaults to SVG

A concept graphic conveys meaning through placement. A Mermaid node-link rendering preserves the
entities and edges but discards the composition — it is a *lossy* carrier for that representation.
Since exactly one view in the corpus is `pictorial` (OV-1), the blast radius of changing the default
is one view, and any project that prefers the old output can override it in one line.

## Consequences

- `views.yaml` is untouched: `representation` stays standard data, `format` stays a project decision.
- The instruction template gains `format` and `format_source`, so a user can see *why* a view got the
  carrier it did.
- External carriers are declarable but not produced by dm2; their rule text says so explicitly
  instead of implying generation.
- Stage 2 can now validate the `(representation, format)` pair rather than Mermaid alone.
