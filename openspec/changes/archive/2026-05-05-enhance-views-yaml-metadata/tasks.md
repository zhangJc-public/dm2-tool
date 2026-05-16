## 1. Data layer — views.yaml enhancement

- [x] 1.1 Write enhanced AV views (AV-1, AV-2) with all 6 new fields
- [x] 1.2 Write enhanced CV views (CV-1 through CV-7) with all 6 new fields
- [x] 1.3 Write enhanced DIV views (DIV-1 through DIV-3) with all 6 new fields
- [x] 1.4 Write enhanced OV views (OV-1 through OV-6c) with all 6 new fields
- [x] 1.5 Write enhanced PV views (PV-1 through PV-3) with all 6 new fields
- [x] 1.6 Write enhanced SV views (SV-1 through SV-10c) with all 6 new fields
- [x] 1.7 Write enhanced SvcV views (SvcV-1 through SvcV-10c) with all 6 new fields
- [x] 1.8 Write enhanced StdV views (StdV-1, StdV-2) with all 6 new fields
- [x] 1.9 Full views.yaml: 52 views with both old and new fields, valid YAML

## 2. Data layer — indexer + API changes

- [x] 2.1 Add new fields to `ViewTemplate` dataclass in `indexer.py`
- [x] 2.2 Add YAML parsing for new fields in indexer `_load_views()`
- [x] 2.3 Add `_validate_view()` function with enum checks and logic rules
- [x] 2.4 Add new fields to `ViewResult` dataclass in `api.py`
- [x] 2.5 Update `_view_to_result()` to map new fields to ViewResult

## 3. Logic layer — InstructionBuilder metadata-driven

- [x] 3.1 Define `REPRESENTATION_TO_MERMAID` mapping dict in `instructions.py`
- [x] 3.2 Implement `_build_rules_from_metadata(view_result)` generating rules from representation, model_category, required_fields
- [x] 3.3 Implement `_build_template_from_metadata(view_result)` generating sections + optional Mermaid block
- [x] 3.4 Refactor `build_view_instructions()` to prefer metadata path with hardcoded VIEW_RULES as fallback
- [x] 3.5 Remove generic `"## Mermaid 图表"` from universal template fallback

## 4. CLI + verification

- [x] 4.1 Verify `dm2 knowledge view OV-2 --json` outputs all new fields
- [x] 4.2 Verify `dm2 knowledge view StdV-1 --json` shows representation=table, no Mermaid
- [x] 4.3 Verify `dm2 instructions OV-6b --json` generates stateDiagram rules
- [x] 4.4 Verify `dm2 instructions OV-3 --json` generates table rules (no Mermaid)
- [x] 4.5 Verify `dm2 instructions PV-2 --json` generates gantt rules
- [x] 4.6 Verify fallback: mock a view without new fields → hardcoded rules used
- [x] 4.7 Verify all 52 views load without validation errors
