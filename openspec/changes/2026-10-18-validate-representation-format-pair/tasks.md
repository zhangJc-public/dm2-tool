# Tasks

## 1 · Shared resolver

- [x] 1.1 Move `resolve_view_format` into `dm2.kernel.formats`
- [x] 1.2 Move `MERMAID_TYPE_BY_REPRESENTATION` and add `ARTEFACT_EXTENSIONS`
- [x] 1.3 Make `instructions.py` reuse them instead of holding a copy

## 2 · Pair-aware checker

- [x] 2.1 Resolve the format before checking evidence
- [x] 2.2 Check evidence per carrier (markdown / mermaid / figure / external artefact)
- [x] 2.3 Add `representation_missing_artifact`
- [x] 2.4 Keep the injectable `format_resolver` seam for tests

## 3 · Tests and verification

- [x] 3.1 Cover every carrier and both mismatch directions
- [x] 3.2 Prove the suite fails against the stage-1 source
- [x] 3.3 Integration check against a real 26-view project, including an injected mismatch

## 4 · Documentation

- [x] 4.1 CHANGELOG entry
