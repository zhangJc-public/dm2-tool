# Design

## Why the checker must resolve, not assume

After stage 1 a view's carrier is a project decision, so a checker that assumes Mermaid validates the
wrong thing. Resolving through the same function the instruction builder uses means a view is judged
against the carrier it was told to produce.

## Evidence per carrier

| format | evidence | absence |
|---|---|---|
| `markdown` | no Mermaid block | a Mermaid block → `representation_unexpected_diagram` |
| `mermaid` | Mermaid block of an allowed type | `representation_missing_diagram` / `representation_mismatch` |
| figure + external | a reference matching the format's extensions | `representation_missing_artifact` |

Two deliberate details:

- **A supporting illustration in a markdown view is allowed.** Only Mermaid is a *carrier* for those
  views; an illustration attached to a table is not a carrier conflict.
- **Artefact detection accepts a plain mention, not just a Markdown image link.** A view that says
  "详见 OV-1.svg" has referenced its artefact; requiring `![](...)` syntax would flag correct work.

## The migration signal

A project that hand-drew an SVG for a node-link view never declared that choice, so the default
(Mermaid) now disagrees with its content and it receives a warning. That warning is the point: it
names the configuration key that records the decision. Default severity stays WARNING so nothing
breaks, and `strict_mode` is available for projects that want it enforced.

## Consequences

- `instructions` and `validate` share one resolver — they cannot drift apart.
- New issue type `representation_missing_artifact`; existing types keep their names.
- The checker is injectable (`format_resolver`), so its tests do not depend on config state.
