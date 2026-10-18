# Design

## Migration

| old setting | replacement |
|---|---|
| `include_mermaid: false` | `formats.default: svg` for diagram views; `formats.overrides` for individual views |
| `diagram_output: svg` | `formats.default: svg` |
| `diagram_output: mermaid` | delete it — that is already the default |

## Why no deprecation shim

The previous change (#4) kept both keys working and documented them as deprecated. That was the
conservative choice while the new axis was unproven. It is now proven — the project adopted it, and
validation enforces it — so the shim only preserves two ways to express one decision.

There is also a correctness argument: the `include_mermaid: false` mapping turns "no Mermaid" into
"SVG" for diagram views. That is a reasonable interpretation, but a surprising one, and it only
exists because the old key could not name a format. Removing the key removes the surprise.

## Consequences

- `resolve_view_format` loses two branches; the resolution order becomes override → project default →
  representation default.
- Reading `views.include_mermaid` in a project config has no effect. Since this tool has no external
  users, that is acceptable; the CHANGELOG lists the mapping for anyone revisiting an old project.
- `formats.overrides` remains the per-view escape hatch — including for restoring Mermaid output on a
  `pictorial` view (`OV-1: mermaid`).
