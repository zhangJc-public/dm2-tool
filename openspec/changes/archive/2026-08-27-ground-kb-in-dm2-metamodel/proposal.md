# Ground knowledge base in DM2 data dictionary & metamodel

## Why

dm2-tool's knowledge layer currently runs on hand-maintained approximations:

| Surface | Today | Problem |
|---|---|---|
| Term store | `core/_dm2_v202_extract.json` — flat 280-entry extract (term/definition/alias/groups) | Subset of the official data dictionary; no CURIE ids, no structured submodel membership, no aliases for most terms |
| View content requirements | `views.yaml` hand-written Chinese `required_fields` / `required_data` | Not derived from any standard; no term-level or association-level requirements |
| Group template relationships | Hand-written vernacular slots in each `*-Template.md` frontmatter (e.g. Performer: `performs`, `consumesResource`, `measuredByOrg`…) | `consumesResource` is an Activity association misattributed to Performer; `measuredByOrg` has no DM2 basis; `partiesToAnAgreement`, `serviceEnablesAccessToResource` are missing |
| View validation | 4 regex heuristics in `reasoning/consistency.py` scanning Markdown prose (`r'活动[^\n]*'`) | High false positive/negative rates; no standard conformance basis |
| Pattern detection | `reasoning/patterns.py` guesses 8 patterns via Chinese/English keyword regexes | No connection to the authoritative IDEAS pattern definitions |

Two authoritative machine-readable sources now exist in `dm2-reference/`
(verified, CURIE-linked via `dodaf:<Term>`):

- **`dm2-data-dictionary.yaml`** — 279 DM2 terms (254 In Model + 25 ERD-derived),
  each with definition, source definitions, aliases, submodel membership, and
  the **monster matrix** (per-term n/o marks across all 52 DoDAF view products).
- **`dm2-metamodel-2.02.yaml`** — 19 verified LDM submodels: 621 classes,
  435 relations, 242 tuples. Provides the **type taxonomy** (384
  super-subtype relations: Performer→System/Service/Organization/…,
  Guidance→Rule→Standard→…), the **association catalog** (67 unique binary
  tuples with endpoint types + IDEAS place roles + domain semantic roles,
  covering 63/106 dictionary associations), **powertype pairs** (47
  powertypeInstance relations formalizing the Type/Individual vault
  convention), and the foundation pattern vocabulary (wholePart/overlap/
  beforeAfter).

Differential analysis (see `repair-group-view-mapping` for the mapping surface)
confirmed the joins are sound: 192/279 dictionary terms join metamodel classes;
the monster matrix's 52 view columns match `views.yaml` IDs 1:1.

## What Changes

- **Build-time index derivation** — a deterministic, zero-LLM build script
  reads the two source YAMLs and emits compact derived indexes
  (`terms.json`, `view-content-spec.json`, `associations.json`,
  `taxonomy.json`) shipped under `dm2-reference/core/`. Runtime keeps loading
  small JSONs, not the 840 KB sources. A submodel↔17-group reconciliation
  table (rules→10-rules/05-guidance name split; synthetic activity/resource
  group attribution by term name) lives in the build script.
- **Term store switch** — `DM2KnowledgeIndexer` loads `terms.json` (CURIE id,
  definition, aliases, groups, association flag). Legacy
  `_dm2_v202_extract.json` is retired after behavior parity is confirmed.
- **View content spec** — `view-content-spec.json` gives each view its
  necessary terms, optional terms, and **necessary associations with endpoint
  types** (monster matrix n-marks joined to the association catalog). Consumed
  by both instructions and validation.
- **Association catalog & template reconciliation** — `associations.json`
  (label → endpoint types, IDEAS/domain roles, home groups). The 17 group
  templates' `relationships:` frontmatter is regenerated/validated against the
  catalog; unknown slots (e.g. `measuredByOrg`) are removed or corrected.
- **Metamodel-grounded validation** — new checks operating on structured
  frontmatter (`dm2-type`, `relationships`/`related-dm2`), not prose:
  unknown-relationship (not in catalog → WARNING with suggestion),
  endpoint-type conformance (taxonomy-aware: System is-a Performer is legal →
  ERROR on mismatch), required-association completeness per view (→ WARNING),
  Type/Individual layer consistency (powertype pairs → INFO). Existing regex
  checks remain as prose fallback.
- **Association manifest in generation instructions** — `dm2 generate`
  instructions for a view include the authoritative "DM2 关联清单": each
  necessary association with endpoint types and semantic roles
  (e.g. `activityConsumesResource: Activity(consumer) ─▶ Resource`).
- **Knowledge API extension** — `dm2 knowledge term <name>` (definition,
  aliases, groups, views marking it n/o), `dm2 knowledge taxonomy <type>`
  (subtypes), `dm2 knowledge associations [--type <T>]` (catalog lookup).

## Non-goals

- **Multiplicity / cardinality validation** — the metamodel carries
  multiplicity on only 4/325 couples and navigability on 0/325; cardinality
  rules cannot be derived.
- **LLM-based extraction from prose views** — conformance checks run on
  structured frontmatter; free-text Markdown stays on the legacy regex path.
- **Full automation of group-to-views mapping** — the monster matrix cannot
  express practice-based mappings (location→OV-1) or n=0 rules views;
  `group-to-views.yaml` stays hand-maintained with `basis` annotations
  (see `repair-group-view-mapping`).
- **Using `core_process_requirements`** — only 24 terms, marked "conceptual
  draft"; deferred.
- **Regenerating group template prose** — only the `relationships:` frontmatter
  slots are reconciled; template body text is untouched.
- **AV-2 auto-generation** — enabled but kept semi-automatic (assist, don't
  overwrite).

## Capabilities

### New Capabilities

- `dm2-metamodel-knowledge`: build-time derivation of terms/content-spec/
  associations/taxonomy indexes from the two source YAMLs; indexer loading;
  knowledge API queries (term, taxonomy, associations).

### Modified Capabilities

- `view-validation`: metamodel-grounded conformance checks (unknown relation,
  endpoint type, required association completeness, Type/Individual layering)
  on structured frontmatter, with the legacy regex checks retained as fallback.
- `metadata-driven-instructions`: view generation instructions include the
  per-view necessary-association manifest with endpoint types and roles.
- `view-metadata-schema`: group template `relationships:` slots are validated
  against the association catalog (catalog names replace vernacular slots).

## Impact

- New module: `src/dm2/kernel/metamodel/` (build script + loaders + query API).
- New derived data files under `dm2-reference/core/`; source YAMLs stay in
  `dm2-reference/` as inputs.
- Modified: `src/dm2/kernel/indexer.py` (term source switch),
  `src/dm2/reasoning/consistency.py` (new checks), instruction builder in
  `src/dm2/core/agent/instructions.py` / metadata-driven path,
  `src/dm2/cli/commands/knowledge.py` (new subcommands).
- Data: 17 group template frontmatters reconciled; legacy
  `_dm2_v202_extract.json` removed after parity.
- Tests: index derivation snapshot tests, taxonomy/catalog query tests,
  conformance validation tests, instruction-manifest tests.
- Dependency: PyYAML already a dependency; no new packages.
- Zero-LLM principle preserved — all derivation is deterministic YAML
  processing.
