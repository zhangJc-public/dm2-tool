# Proposal

## Why

`views.diagram_output` was removed in #7, but the "Format resolution order" requirement still lists it
as the third step. The corpus therefore documents a deployment step that cannot occur.

## What Changes

Restate the resolution order as: per-view override → project default → representation default. The
requirement's scenarios are unchanged.

## Non-goals

- No code change; the implementation already has three steps.
