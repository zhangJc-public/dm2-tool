# Tasks

## 1. Index build pipeline

- [x] 1.1 Create `scripts/build_knowledge_indexes.py` (deterministic, no LLM): load `dm2-reference/dm2-data-dictionary.yaml` and `dm2-reference/dm2-metamodel-2.02.yaml`
- [x] 1.2 Implement submodel↔group reconciliation table in the script (rules→rules/guidance name split; activity/resource synthetic attribution per design §2)
- [x] 1.3 Emit `dm2-reference/core/terms.json`: 279 entries `{id, term, definition, aliases, groups, association, status, erd}`
- [x] 1.4 Emit `associations.json`: dedupe Tuple classes by label, extract 2 NavigableAssociation couples → `{label, endpoints:[{type, ideas_role, domain_role}], homes[]}`; print coverage report (expected ~67 binary, 63/106 dictionary associations resolved)
- [x] 1.5 Emit `taxonomy.json`: parents/children from `<<super-subtype>>` relations; `powertype_pairs` from `<<powertypeInstance>>`
- [x] 1.6 Emit `view-content-spec.json`: per view ID `{necessary_terms, optional_terms (capped 30), necessary_associations:[{label, endpoint_types, roles}]}` via monster-matrix n/o marks + catalog join; normalize view column names (`Standards View-1`→`StdV-1`)
- [x] 1.7 Add `test/test_knowledge_indexes.py`: snapshot/regeneration test asserting indexes are up-to-date with sources, and counts (279 terms, 52 views, ≥60 binary associations, 26 powertype pairs)

## 2. Term store switch

- [x] 2.1 Create `src/dm2/kernel/metamodel/__init__.py` with `MetamodelIndex` class loading associations/taxonomy/content-spec JSONs from the reference path (local `.dm2/reference/` first, package fallback)
- [x] 2.2 Extend `DM2KnowledgeIndexer` to load `terms.json` (CURIE id, aliases, groups, association flag) behind a loader flag
- [x] 2.3 Parity test: every `_dm2_v202_extract.json` term exists in `terms.json` with non-empty definition; term count ≥ 279
- [x] 2.4 Update `search_terms` to match aliases in addition to term names
- [x] 2.5 Remove `_dm2_v202_extract.json` and its loader after parity is green; update packaging (pyproject package-data) to ship the four new JSONs

## 3. Knowledge API

- [x] 3.1 `dm2 knowledge term <name>`: definition, aliases, groups, views marking it necessary/optional, association endpoint info if applicable
- [x] 3.2 `dm2 knowledge taxonomy <type>`: direct and transitive subtypes from taxonomy.json
- [x] 3.3 `dm2 knowledge associations [--type <type>] [--group <id>]`: catalog entries filtered by endpoint type or home group
- [x] 3.4 `dm2 knowledge views <view_id>`: view content spec (necessary terms/associations)
- [x] 3.5 All subcommands follow `{status:"success", data:{...}}` JSON envelope; CLI tests for each

## 4. Association manifest in generation instructions

- [x] 4.1 Extend the metadata-driven instruction builder (`src/dm2/core/agent/instructions.py`): when building view instructions, inject a "DM2 关联清单" section from `view-content-spec.necessary_associations` with endpoint types and domain roles
- [x] 4.2 Cap section size (skip label-only unresolved associations if >12 entries; list associations first, terms second)
- [x] 4.3 Test: instructions for OV-5b contain activityPerformedByPerformer/activityConsumesResource/activityProducesResource with endpoint types; CV-2 contains activityPartOfCapability
- [x] 4.4 Update skill/workflow templates (`src/dm2/core/templates/workflows/*.py`) only if they hardcode relationship lists — otherwise no change

## 5. Group template relationship reconciliation

- [x] 5.1 Add a `--check-templates` mode to the build script (or separate script) comparing each `groups/*/*Template.md` `relationships:` frontmatter against associations.json for that group's endpoint types
- [x] 5.2 Report: slots with no catalog basis (e.g. Performer `measuredByOrg`), misattributed slots (Performer `consumesResource` — Activity's association), missing associations (Performer `partiesToAnAgreement`)
- [x] 5.3 Regenerate `relationships:` frontmatter in the 17 templates from catalog projections (vernacular → catalog name mapping documented; e.g. `performs` → `activityPerformedByPerformer`)
- [x] 5.4 Test: every template relationship slot resolves to an associations.json label whose endpoints include a type of that template's group

## 6. Metamodel-grounded validation

- [x] 6.1 Create `src/dm2/reasoning/conformance.py` with `MetamodelConformanceChecker` loading MetamodelIndex
- [x] 6.2 Frontmatter extraction: read `dm2-type` and typed links (`relationships` slots / `related-dm2` entries with resolvable types) from vault instance notes; tolerate missing fields (skip → INFO)
- [x] 6.3 Rule unknown-relation: unknown label → WARNING with nearest catalog name suggestion (difflib)
- [x] 6.4 Rule endpoint-type: endpoint types subtype-compatible (taxonomy transitive closure) → ERROR on mismatch
- [x] 6.5 Rule required-association: generated view missing a necessary association present in project data scope → WARNING
- [x] 6.6 Rule type-layer: dm2-layer Type/Individual vs powertype_pairs consistency → INFO
- [x] 6.7 Rule unknown-term: dm2-type not in terms.json → WARNING
- [x] 6.8 Wire into `dm2 validate`: conformance rules first (structured data), legacy regex rules second (prose fallback); report labels the producing layer
- [x] 6.9 Tests: fixture notes for each rule — System linked via activityConsumesResource (legal, subtype), Organization linked via measure-only relation (mismatch), unknown slot typo, Individual without Type

## 7. Documentation & verification

- [x] 7.1 Document the sources→indexes pipeline and reconciliation table in `docs/` (how to regenerate, coverage expectations)
- [x] 7.2 Update `dm2 knowledge` command docs in `docs/readme.md`
- [x] 7.3 Full `pytest test/` green; `ruff check src/` clean
- [x] 7.4 End-to-end smoke: analyze a sample system description → recommendations unchanged in shape but now traceable to content spec; generate instructions show association manifest; validate reports conformance issues on seeded fixture
