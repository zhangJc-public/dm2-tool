# Proposal

## Why

`views.formats` replaced the two older output switches:

- `views.diagram_output` was introduced while building the format axis and was never released — it
  is superseded by `formats.default`.
- `views.include_mermaid` predates the format axis and only ever meant "not Mermaid", which the
  format axis now expresses directly.

Keeping them as deprecated aliases means two ways to say the same thing, and the legacy path has a
mapping subtlety (`include_mermaid: false` silently becomes SVG for diagram views) that is easy to
misread. This is an internal tool with a single maintainer and no external consumers, so carrying a
compatibility shim has cost and no benefit.

## What Changes

- Remove `views.include_mermaid` and `views.diagram_output` from `DEFAULTS` and from
  `resolve_view_format`; a project that still sets them is no longer affected by them.
- Remove `preferred_non_mermaid()`, which existed only to serve the `include_mermaid` mapping.
- Update the two documentation examples that used `views.include_mermaid` as the config example.

## Non-goals

- `views.formats` is unchanged: same resolution order minus the legacy step, same compatibility
  matrix, same validation.
- No migration shim: this is a breaking change released as 0.3.0 (0.x minor).
