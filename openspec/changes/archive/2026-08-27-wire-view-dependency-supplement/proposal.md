# Wire view dependency supplement into analyze & skills

## Why

A retrospective on why the OV-1 view (High-Level Operational Concept Graphic) keeps getting
dropped from generated view sets found the root cause is **not** missing tooling but a
**disconnected mechanism**:

- `ViewRecommender.verify_and_supplement_views()` (src/dm2/cognitive/view_recommender.py:566)
  already implements the desired "coverage check": `_check_path_completeness()` computes the
  transitive closure over views.yaml `dependencies` and supplements ancestors (if OV-2/OV-5a
  are in the set, OV-1 + CV-1 + AV-1 are added back).
- **It has zero callers.** `dm2 analyze` calls only `recommend()` (src/dm2/cli/main.py:596),
  and the propose workflow builds its view set as `concern core_views ∪ candidate_views`
  (src/dm2/core/templates/workflows/propose.py:96-100). Neither path runs the supplement.
- The model-side bias ("pictorial OV-1 carries little data → low value → drop it") is
  therefore never caught by the tool: OV-1 has only 1 necessary term / 0 associations in
  `view-content-spec.json` (monster-matrix fact for pictorial views), so the drop looks
  data-justified, and the dependency data that contradicts it is present but unused.

Fix: wire the existing mechanism into `dm2 analyze`, add a dependency-completeness step to
the propose workflow skill, and add a communication-baseline rule for pictorial views.

## What Changes

- **Wire supplement into `dm2 analyze`**: after `recommend()`, call
  `verify_and_supplement_views()` so `recommended_views` includes dependency ancestors.
  Verify its dedup/sort behavior on the expanded set (priority, -relevance_score).
- **Propose workflow skill**: after P1/P2/P3 phase assignment, require a reverse
  dependency-completeness scan against the `view_dependencies` field of the analyze output;
  any missing ancestor (e.g. OV-1 when OV-2/OV-5a present) is added and marked as
  supplement. Pictorial communication views (OV-1/CV-1/AV-1) SHALL NOT be excluded solely
  because the monster matrix marks them data-light.
- **Explore workflow skill**: add a light dependency-chain check hint (view lookups mention
  checking dependents/dependencies).
- **Tests**: analyze CLI smoke (desc activating OV-2/OV-5a paths yields OV-1 among
  recommended_views); unit test for `verify_and_supplement_views` dedup/sort on an expanded
  set; skill template test asserting the propose instruction contains the completeness step
  and the pictorial baseline rule.

## Capabilities

### Modified Capabilities

- `dm2-view-dependency-graph`: supplement invocation contract (analyze output includes
  dependency-complete recommendations).
- `dm2-propose-workflow`: view-set completeness step + pictorial communication-baseline rule.
- `dm2-explore-workflow`: dependency-chain check hint.

## Impact

- Code: one call in `src/dm2/cli/main.py` (analyze command) + tests.
- Skill templates: `src/dm2/core/templates/workflows/propose.py` and `explore.py` instruction
  text additions (regenerated into `.claude/skills/` on `dm2 init`).
- Data: none (views.yaml / content-spec unchanged — data-lightness of pictorial views is a
  standard fact, addressed at instruction level, not data level).
- Behavior: `recommended_views` grows by dependency ancestors; verify dedup/sort handles it
  (existing logic), tests pin the shape.
