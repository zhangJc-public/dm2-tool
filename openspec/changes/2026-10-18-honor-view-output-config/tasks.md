# Tasks

## 1 · Configuration plumbing

- [ ] 1.1 Add `views.diagram_output` (default `mermaid`) to `config.manager.DEFAULTS`
- [ ] 1.2 Add `_view_config` / `_mermaid_enabled` / `_diagram_output` helpers to `instructions.py` with a function-local config import
- [ ] 1.3 Scaffold `dm2 init`'s config from `DEFAULTS` instead of a hand-copied dict

## 2 · Diagram section channels

- [ ] 2.1 Gate the Mermaid section on `views.include_mermaid`
- [ ] 2.2 Emit the external-figure section when `views.diagram_output == "svg"`
- [ ] 2.3 Add the matching rule under the `svg` channel

## 3 · Representation conformance

- [ ] 3.1 Add `dm2/reasoning/representation.py` with `RepresentationChecker`
- [ ] 3.2 Wire it into `dm2 validate` beside `ConsistencyChecker`
- [ ] 3.3 Promote warnings to errors under `consistency.strict_mode`

## 4 · Tests

- [ ] 4.1 `test/test_instructions_config.py` — channel selection, fallbacks, precedence
- [ ] 4.2 `test/test_representation_check.py` — rules, severity, robustness
- [ ] 4.3 Prove both suites fail against the pre-change sources

## 5 · Documentation

- [ ] 5.1 `README.md` + `docs/readme.md` config tables
- [ ] 5.2 `CHANGELOG.md` entry under `[Unreleased]`
