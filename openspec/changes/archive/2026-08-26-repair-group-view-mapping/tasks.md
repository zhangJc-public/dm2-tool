# Tasks

## 1. Mapping data repairs

- [x] 1.1 In `dm2-reference/group-to-views.yaml`, replace dead entry `SvcV-3` under `08-services` with `SvcV-3a` (Systems-Services Matrix) and `SvcV-3b` (Services-Services Matrix), `basis: matrix`
- [x] 1.2 Add to `05-guidance`: `StdV-2` (Standards Forecast — TechnicalStandard necessary term), `basis: matrix`
- [x] 1.3 Move `OV-6a` from `05-guidance` to `10-rules` (9 optional Rules terms vs 2 optional Guidance terms; joins sibling rules models SV-10a/SvcV-10a), `basis: matrix`
- [x] 1.4 Add to `06-measure`: `OV-3`, `SV-6`, `SvcV-6` (3–4 necessary measure terms each: PerformanceMeasure, NeedsSatisfactionMeasure, TemporalMeasure), `basis: matrix`
- [x] 1.5 Add to `01-performer` (System is the performer-family host of the SV family, mirroring 08-services↔SvcV): `SV-1, SV-3, SV-5a, SV-5b, SV-8, SV-9, SV-10b, SV-10c`, `basis: matrix`
- [x] 1.6 Add to `11-resource-flow` (flow associations activityConsumes/ProducesResource + Data are necessary content): `OV-2, OV-3, SV-1, SvcV-1, SV-6, SvcV-6`, `basis: matrix`
- [x] 1.7 Add to `02-activity` (activityPartOfCapability / activityMapsToCapabilityType necessary; behavioral views): `CV-2, CV-6, OV-6b, OV-6c`, `basis: matrix`
- [x] 1.8 Annotate entries: `basis: practice` only for `07-location → OV-1, OV-2` (zero monster-matrix location terms); all other entries (including `01-performer → OV-4` and `14-org-structure → OV-4`, which carry optional Organization/PersonRole terms) marked `basis: matrix`
- [x] 1.9 Add a YAML comment block documenting deliberate non-claims: `AV-1`, `AV-2` are meta views delivered through the view dependency graph (AV-2 becomes semi-auto-generated under `ground-kb-in-dm2-metamodel`)

## 2. Regression tests

- [x] 2.1 Create `test/test_group_view_mapping.py`
- [x] 2.2 Test: every `group_views[].id` (except `All`) exists as a view ID in `dm2-reference/core/views.yaml` (fails on dead IDs like `SvcV-3`)
- [x] 2.3 Test: every view in `views.yaml` except the documented meta set {`AV-1`, `AV-2`} is claimed by ≥1 group
- [x] 2.4 Test: every `group_views` entry has a `basis` field with value `matrix` or `practice`
- [x] 2.5 Test: `basis: practice` entries are exactly the documented allow-list {location→OV-1, location→OV-2}

## 3. Verification

- [x] 3.1 Run `pytest test/ -k group_view` — all pass
- [x] 3.2 Smoke-test recommendation: `dm2 analyze -d "系统接口、系统间通信、数据交换矩阵" --json` shows SV-1/SV-6/SvcV-6 candidates (previously absent)
- [x] 3.3 Smoke-test: a description activating guidance (标准、规范、StdV) recommends StdV-2
- [x] 3.4 `ruff check src/` clean (no source changes expected; test file only)
