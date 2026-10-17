# Proposal

## Why

`views.include_mermaid` is documented as a working switch in `README.md` and `docs/readme.md`, and it
ships in `config.manager.DEFAULTS` — but no code path reads it. `InstructionBuilder` appends the
`## Mermaid 图表` section unconditionally, so setting the key to `false` changes nothing. That is a
dead switch users are told to trust.

The same layer has no way to emit a diagram as anything but inline Mermaid, so a project that draws
diagrams as standalone files cannot express that through configuration.

Separately, `views.yaml` declares a `representation` for every view and `dm2 validate` never checks
that a generated view honours it. A `table` view may ship a Mermaid graph; a `state-diagram` view
may ship no diagram at all. The declaration is advisory in name and in fact.

## What Changes

**A · make the existing switch real**

- `views.include_mermaid: false` stops the `## Mermaid 图表` section from being injected.
- `dm2 init` scaffolds its config from `DEFAULTS` instead of a hand-copied dict, so new projects
  stop pinning stale values (the copied dict was already missing `trace.enabled`).

**B · report representation drift**

- New `RepresentationChecker` (`dm2.reasoning.representation`) compares each view's declared
  `representation` with what the file actually contains: Mermaid presence and type, or an external
  figure reference.
- Wired into `dm2 validate` beside `ConsistencyChecker`. Warnings by default; errors under
  `consistency.strict_mode`.

**C · an external-figure output channel**

- New `views.diagram_output` config: `mermaid` (default) or `svg`. Under `svg`, diagram-bearing
  views get a `## 图示（独立 SVG 文件…）` section and a matching rule instead of inline Mermaid.

## Non-goals

- No SVG rendering: dm2 declares the output channel, it does not draw.
- No conformance rule R6 — that would change `pedigree.validation`'s `ran_R1..ran_R5` schema.
- No migration: under default configuration every existing project keeps its current behaviour.
