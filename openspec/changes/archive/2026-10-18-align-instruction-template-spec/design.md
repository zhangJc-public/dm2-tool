# Design

## Why remove and re-add instead of modify

OpenSpec refuses a `MODIFIED` block that drops scenarios: it replaces the whole requirement, so
omitting one is treated as losing a contract. Here four scenarios *should* disappear — they describe
removed keys — and their names mention those keys (`Unknown diagram_output falls back to Mermaid`).
Retaining the names would leave the corpus pointing at a setting that no longer exists.

Removing and re-adding under a new name is the honest representation: the requirement's carrier
scenarios are genuinely gone, and the survivors are re-scoped.

## What the new requirement says

The template is assembled from the view's own `sections`, plus one carrier section chosen by the
resolved format. The carrier rules themselves are not restated here — `view-output-format` owns them,
so the two specs cannot drift into disagreeing about formats.
