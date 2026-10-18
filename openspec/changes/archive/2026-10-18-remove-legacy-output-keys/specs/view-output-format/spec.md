# Spec Delta

## REMOVED Requirements

### Requirement: Legacy output switches map onto the format axis
**Reason**: `views.formats` supersedes both switches. `views.diagram_output` was introduced while building the format axis and never released; `views.include_mermaid` only ever meant "not Mermaid", which the format axis expresses directly. Keeping a deprecated alias preserves two ways to express one decision, and the `include_mermaid: false` mapping to SVG is a surprising interpretation that exists only because the old key could not name a format. This is an internal tool with a single maintainer and no external consumers, so the shim carries cost without benefit. Migration is documented in the CHANGELOG: `include_mermaid: false` → `formats.default: svg`, `diagram_output: svg` → `formats.default: svg`, `diagram_output: mermaid` → delete.
