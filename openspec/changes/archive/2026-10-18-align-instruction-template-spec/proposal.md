# Proposal

## Why

The `metadata-driven-instructions` spec still carries four scenarios describing `views.include_mermaid`
and `views.diagram_output`. Those switches were removed in #7, so the corpus now describes behaviour
that does not exist — and contradicts `view-output-format`, which is the authority for carriers.

The requirement's core claim (use the view's `sections` field, not hardcoded generic sections) is
still true; only its carrier scenarios are stale.

## What Changes

- Remove the requirement "InstructionBuilder generates template sections from metadata" and re-add it
  as "InstructionBuilder generates template and carrier sections", whose scenarios describe
  `views.formats` instead of the removed switches.

## Non-goals

- No code change: this realigns the corpus with behaviour already shipped in #4 and #7.
- The carrier contract itself stays in `view-output-format`; this requirement only states how the
  template is assembled.
