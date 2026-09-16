# Design

## 1. Data flow: sources → derived indexes → runtime

```
dm2-reference/                                (committed sources)
├── dm2-data-dictionary.yaml      543 KB   279 terms + monster matrix
└── dm2-metamodel-2.02.yaml       303 KB   19 submodels, taxonomy, tuples
                 │
                 ▼  scripts/build_knowledge_indexes.py   (manual, deterministic, zero-LLM)
                 │
dm2-reference/core/                           (shipped artifacts)
├── terms.json                 279×{id,term,definition,aliases,groups,association,erd}
├── view-content-spec.json     52×{necessary_terms, optional_terms, necessary_associations}
├── associations.json          ~67×{label, endpoints:[{type, ideas_role, domain_role}], homes}
├── taxonomy.json              {parents, children, powertype_pairs:[{individual, type}]}
└── (legacy _dm2_v202_extract.json retired after parity check)
                 │
                 ▼  runtime (zero-LLM, loads small JSONs only)
┌────────────────────────────────────────────────────────────┐
│ DM2KnowledgeIndexer ── terms.json                          │
│ MetamodelIndex      ── associations / taxonomy / content   │
│        │                  │                │               │
│   KnowledgeAPI      Instructions      ConsistencyChecker   │
│   (term/taxonomy/   (association       (conformance rules) │
│    associations)     manifest)                             │
└────────────────────────────────────────────────────────────┘
```

Build script is invoked manually (`python3 scripts/build_knowledge_indexes.py`)
and is tested by a snapshot/parity test in CI. Runtime never parses the 840 KB
sources — consistent with the project convention "templates generated, not
runtime-configured".

## 2. Submodel ↔ 17-group reconciliation

The dictionary's 15 `submodels` x-marks don't partition cleanly into the 17
data-group directories. The build script encodes an explicit reconciliation
table (single source of truth, documented in code):

| Dictionary submodel | 17-group dir(s) |
|---|---|
| performer | `01-performer` |
| capability | `03-capability` |
| measure | `06-measure` |
| location | `07-location` |
| services | `08-services` |
| project | `09-project` |
| rules | `10-rules` **or** `05-guidance` — split by term name: names containing Guidance/Standard/Agreement → `05-guidance`; otherwise → `10-rules` |
| resource-flow | `11-resource-flow` |
| information-and-data | `16-information-data` |
| information-pedigree | `13-information-pedigree` |
| organizational-structure | `14-org-structure` |
| pedigree | `12-pedigree` (meta) |
| reification-levels | `15-reification` (meta) |
| dm2-foundation / ideas-foundation | `00-foundation` (meta) |
| (no submodel) | synthetic attribution by term name: `Activity`/`activity*` → `02-activity`; `Resource`/`Materiel`/`resource*`/`materiel*` → `04-resource` |

A term joining N groups contributes weight 1/N when deriving view/group
signals (monster-matrix analysis uses this vote). The 3 meta groups
(00/12/15) never produce view recommendations.

## 3. Association catalog derivation

- Iterate all submodel `classes` with `ideas_type: Tuple`; dedupe by `label`
  (a tuple appears in up to 11 submodels — first NavigableAssociation couple
  pair wins, homes recorded).
- Keep tuples with exactly 2 NavigableAssociation couples → binary
  association. Each endpoint records: participant CURIE (→ short type name),
  IDEAS place role (`<<place1Type>>`, `<<part>>`, `<<before>>`…), and domain
  role after `|` when present (`consumer`, `constrainer`,
  `desirerFutureResourceState`…).
- Generalization/Dependency couples (super-subtype, powertypeInstance) are
  excluded — those feed `taxonomy.json`, not the association catalog.
- Expected yield: ~67 binary associations; 63/106 dictionary association
  terms resolve; the unresolved 43 are IDEAS foundation pattern vocabulary
  (WholePartType, OverlapType…) — accepted, documented in a coverage report.

## 4. View content spec derivation

For each of the 52 views (column-name → view-ID normalization:
`Standards View-1` → `StdV-1`):

- `necessary_terms`: terms with monster-matrix `n` (entity terms only)
- `optional_terms`: terms with `o` (top-k capped, e.g. 30, for instruction
  size control)
- `necessary_associations`: terms with `n` AND `association: true`, joined to
  the association catalog → `{label, endpoint_types, roles}`. Example for
  CV-2: `activityPartOfCapability(Activity→Capability)`,
  `activityMapsToCapabilityType(Activity→CapabilityType)`, …

Associations not resolvable in the catalog (foundation pattern types) are
listed by label only.

## 5. Taxonomy & powertype

- `taxonomy.json` parents/children from all `<<super-subtype>>` relations
  (384; source=subtype, target=supertype per naming convention
  `ruleSubtypeOfGuidance`).
- `powertype_pairs` from `<<powertypeInstance>>` relations (47):
  `{individual: Organization, powertype: OrganizationType}` etc. Feeds
  Type/Individual layer guidance and the layer-consistency check.
- Endpoint-type conformance is **subtype-aware**: an endpoint requiring
  Performer accepts System, Service, Organization, Port (transitive closure
  of children).

## 6. Validation rule set (structured-frontmatter level)

Inputs: instance notes' frontmatter (`dm2-type`, optional
`relationships`/`related-dm2` typed links) and generated view notes. New
issues from `MetamodelConformanceChecker`:

| Rule | Severity | Basis |
|---|---|---|
| unknown-relation: relationship label not in associations.json | WARNING + nearest-name suggestion | catalog |
| endpoint-type: endpoint `dm2-type` not subtype-compatible with catalog endpoint | ERROR | catalog + taxonomy |
| required-association: view missing a `necessary_associations` entry | WARNING | view-content-spec |
| type-layer: `dm2-layer: Individual` without corresponding Type powertype, or vice versa | INFO | powertype_pairs |
| unknown-term: `dm2-type` not matching any dictionary term | WARNING | terms.json |

Legacy `ConsistencyChecker` regex rules (activity-performer binding, resource
flow integrity, capability mapping, temporal cycles) remain for prose content
and run second; reports label which layer produced each issue.

Multiplicity/navigability rules are explicitly out of scope (source data
absent: 4/325 and 0/325).

## 7. Instruction manifest

`metadata-driven-instructions` path gains a section per generated view:

```
## DM2 关联清单（标准必要关联）
- activityConsumesResource: Activity (consumer) ──▶ Resource
- activityPerformedByPerformer: Performer ──▶ Activity
- activityProducesResource: Activity (before) ──▶ Resource
```

Sourced from `view-content-spec.necessary_associations`. This replaces
template-authored relationship prose as the authoritative relation list for
the view; group template `relationships:` frontmatter becomes a *catalog
projection* per group (regenerated from associations whose endpoints touch
the group's types), not hand-maintained.

## 8. Migration & compatibility

1. Derived indexes land first; indexer loads `terms.json` with
   `_dm2_v202_extract.json` fallback retained one release.
2. Parity test: every legacy JSON term exists in terms.json with matching
   definition; after green, legacy file deleted.
3. Group template frontmatter regeneration is a reviewable diff
   (17 files); bodies untouched.
4. `dm2 knowledge` commands are additive; JSON schema follows the standard
   `{status, data}` envelope.

## Risks

- **Submodel reconciliation errors** (rules/guidance split, synthetic
  activity/resource attribution) — mitigated by coverage report reviewed
  against the monster-matrix analysis numbers in this proposal.
- **96 classes lack `ideas_type`** and ~40 associations unresolved — checks
  degrade to WARNING/label-only, never hard-fail.
- **Frontmatter quality varies** in vault instances; conformance checker
  must tolerate missing fields (skip → INFO, not error).
