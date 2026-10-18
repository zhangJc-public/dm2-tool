# Tasks

## 1 · Format taxonomy

- [x] 1.1 Add `dm2/kernel/formats.py` with the compatibility matrix and per-representation defaults
- [x] 1.2 Matrix coverage test against the representations used by `views.yaml`

## 2 · Resolution

- [x] 2.1 Add `views.formats.{default,overrides}` to `DEFAULTS`
- [x] 2.2 Implement `resolve_view_format` with override → project default → legacy → default order
- [x] 2.3 Restrict the project default to diagram views
- [x] 2.4 Report `representation` / `format` / `format_source` in the instruction template

## 3 · Carrier dispatch

- [x] 3.1 Section per carrier: mermaid / svg / png / html / external artefact / markdown
- [x] 3.2 Rule per carrier, stating when it differs from the default prose

## 4 · Legacy keys

- [x] 4.1 `include_mermaid: false` maps to a native non-Mermaid carrier
- [x] 4.2 `diagram_output: svg` maps to SVG for diagram views only
- [x] 4.3 `dm2 init` scaffolds `views.formats` from `DEFAULTS` (deep copy)

## 5 · Documentation

- [x] 5.1 CHANGELOG entry, including the `pictorial` behaviour change
