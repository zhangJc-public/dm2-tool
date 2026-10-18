# Proposal

## Why

dm2 models a view with one axis — `representation` — and derives the carrier from it through
`REPRESENTATION_TO_MERMAID`, a one-to-one mapping. That conflates two independent properties:

- **representation**: what information structure the view conveys
- **format**: how that structure is carried

The conflation is not cosmetic. It forced `pictorial` (a concept graphic, whose semantics *are* the
layout) into a Mermaid node-link diagram; it left `table` and `text` with no carrier concept at all;
and it made "can a view be a video?" unanswerable, because video is a carrier and the model had no
carrier axis.

A project that wants a concept graphic drawn as SVG had no way to say so — it could only hand-edit
the view, with nothing recording the decision.

## What Changes

**A · a compatibility matrix replaces the mapping**

New `dm2.kernel.formats` holds `COMPATIBLE_FORMATS` (representation → {format: native | lossy |
external}), `DEFAULT_FORMAT` (per representation) and the resolver helpers. One representation may
be carried by several formats; one format may carry several representations; incompatible pairs are
rejected rather than silently coerced.

**B · format resolution is layered**

Per-view override → project default (diagram views only) → legacy `diagram_output` → representation
default. `dm2 instructions` reports the result as `template.format` with a `format_source` trail.

**C · carriers are first class in the instruction template**

Sections and rules dispatch on the carrier: inline Mermaid, standalone SVG/PNG, HTML output, or an
external artefact (`xlsx` / `csv` / `mp4`) that the view references.

**D · legacy keys map onto the new axis**

`views.include_mermaid` and `views.diagram_output` keep working; both are documented as deprecated
and mapped onto format resolution.

## Non-goals

- No rendering: dm2 declares and checks the carrier, it does not draw.
- No schema change to `views.yaml`: format is a project decision, not a DoDAF view property.
- Stage 2 (validation of the pair) and stage 3 (removing the legacy keys) are separate changes.
