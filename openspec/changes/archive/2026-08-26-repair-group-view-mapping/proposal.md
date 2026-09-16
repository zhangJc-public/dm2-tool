# Repair group-to-views mapping against DM2 monster matrix

## Why

`dm2-reference/group-to-views.yaml` is the runtime-loaded data file that drives
data-group-activation-based view recommendation (see `dm2-data-group-activation`
capability). A read-only differential analysis against the authoritative DoDAF
2.02 DM2 Data Dictionary monster matrix (term × view n/o marks, 279 terms × 52
views, in `dm2-reference/dm2-data-dictionary.yaml`) found concrete defects:

1. **Dead mapping ID** — `08-services` claims view `SvcV-3`, which does not exist
   in `views.yaml` (only `SvcV-3a` / `SvcV-3b`). The entry silently never fires,
   and both real views fall into the blind spot below.
2. **15 of 52 views are claimed by no data group** — activation can never
   recommend them (only 6W fallback at score 0.1). These include the whole SV
   systems family (`SV-1, SV-3, SV-5a, SV-5b, SV-8, SV-9, SV-10b, SV-10c`),
   behavioral views (`OV-6b, OV-6c`), `SvcV-3a/3b`, and `StdV-2`. Root cause:
   the hand mapping covers the SvcV (services) family completely under
   `08-services`, but System lives in `01-performer`, which only claimed
   `OV-4, PV-1`.
3. **Mis-attribution** — `OV-6a` (Operational Rules Model) is mapped to
   `05-guidance`, but in the monster matrix it carries 9 optional Rules terms
   vs 2 optional Guidance terms; it belongs with its sibling rules models
   `SV-10a` / `SvcV-10a` under `10-rules`.
4. **Evidence gaps** — `07-location → OV-1/OV-2` and `14-org-structure → OV-4`
   have zero monster-matrix support (no n/o terms); they are practice-based
   judgments and are currently indistinguishable from matrix-supported entries.

This is a data-only change (one YAML file + one regression test). The larger
knowledge-base upgrade (loading the data dictionary and metamodel into the
indexer) is tracked separately in `ground-kb-in-dm2-metamodel`.

## What Changes

- **Fix dead ID**: replace `SvcV-3` with `SvcV-3a` + `SvcV-3b` under `08-services`.
- **Fill blind spots** (matrix-supported additions):
  - `01-performer` (System host): `SV-1, SV-3, SV-5a, SV-5b, SV-8, SV-9, SV-10b, SV-10c`
  - `11-resource-flow`: `OV-2, OV-3, SV-1, SvcV-1, SV-6, SvcV-6`
  - `02-activity`: `CV-2, CV-6, OV-6b, OV-6c`
  - `06-measure`: `OV-3, SV-6, SvcV-6`
  - `05-guidance`: `StdV-2` (TechnicalStandard is necessary, same as StdV-1)
  - `10-rules`: `OV-6a` (moved from `05-guidance`)
- **Annotate evidence basis**: each `group_views` entry gains an optional
  `basis: matrix | practice` field. `matrix` = monster-matrix necessary/optional
  terms support it; `practice` = practitioner judgment outside the matrix
  (location→OV-1/OV-2, org-structure→OV-4). Deliberate non-claims (`AV-1`,
  `AV-2` meta views, delivered via the dependency graph) get documented in a
  YAML comment instead of being silently absent.
- **Regression test**: a test asserts (a) every mapping view ID exists in
  `views.yaml`, (b) every view except the documented meta set is claimed by at
  least one group.

## Capabilities

### Modified Capabilities

- `dm2-data-group-activation`: group-to-views mapping validity and coverage
  requirements; evidence-basis annotation.

## Impact

- Data file: `dm2-reference/group-to-views.yaml` (runtime-loaded; no code change
  to `ViewRecommender` — it already iterates `group_views[].id`).
- New test: `test/test_group_view_mapping.py`.
- Recommendation output changes for descriptions that activate performer /
  resource-flow / activity / measure groups: SV-family and behavioral views now
  appear as candidates. No change to JSON output schema.
- No breaking changes; `basis` is an optional additive field.
