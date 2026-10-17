# Tasks

## 1 · Configuration plumbing

- [x] 1.1 Add `views.diagram_output` (default `mermaid`) to `config.manager.DEFAULTS`
- [x] 1.2 Add `_view_config` / `_mermaid_enabled` / `_diagram_output` helpers to `instructions.py` with a function-local config import
- [x] 1.3 Scaffold `dm2 init`'s config from `DEFAULTS` instead of a hand-copied dict

## 2 · Diagram section channels

- [x] 2.1 Gate the Mermaid section on `views.include_mermaid`
- [x] 2.2 Emit the external-figure section when `views.diagram_output == "svg"`
- [x] 2.3 Add the matching rule under the `svg` channel

## 3 · Representation conformance

- [x] 3.1 Add `dm2/reasoning/representation.py` with `RepresentationChecker`
- [x] 3.2 Wire it into `dm2 validate` beside `ConsistencyChecker`
- [x] 3.3 Promote warnings to errors under `consistency.strict_mode`

## 4 · Tests

- [x] 4.1 `test/test_instructions_config.py` — channel selection, fallbacks, precedence
- [x] 4.2 `test/test_representation_check.py` — rules, severity, robustness
- [x] 4.3 Prove both suites fail against the pre-change sources

## 5 · Documentation

- [x] 5.1 `README.md` + `docs/readme.md` config tables
- [x] 5.2 `CHANGELOG.md` entry under `[Unreleased]`
