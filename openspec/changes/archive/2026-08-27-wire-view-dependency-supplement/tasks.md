# Tasks

## 1. Wire supplement into dm2 analyze

- [x] 1.1 In `src/dm2/cli/main.py` analyze command: after `recs = recommender.recommend(...)`, call `recs = recommender.verify_and_supplement_views(recs, result)` so dependency ancestors are included
- [x] 1.2 Verify the expanded set: dedup (`seen` set) and sort (priority, -relevance_score) behave correctly when ancestors are added at score 0.6
- [x] 1.3 Add `test/test_view_recommender.py` (or extend existing): `verify_and_supplement_views` unit test — set containing OV-2/OV-5a but not OV-1 gains OV-1 (+CV-1/AV-1 ancestors); dedup; priority sort order
- [x] 1.4 CLI smoke test: `dm2 analyze -d "作战节点连接、活动分解、资源流" --json` → `recommended_views` includes OV-1

## 2. Propose workflow skill

- [x] 2.1 In `src/dm2/core/templates/workflows/propose.py`, add a "视图完整性确认" step after phase assignment: scan `view_dependencies` reverse — any view in the focused set whose transitive ancestors are absent SHALL be supplemented and marked `P3 supplement` (or a dedicated note)
- [x] 2.2 Add pictorial communication-baseline rule to the instruction text: `pictorial` views (OV-1/CV-1/AV-1) SHALL NOT be dropped solely because the monster matrix marks them data-light; they are the communication baseline for decision-makers
- [x] 2.3 Test: `test/test_workflow_templates.py` (or extend existing) asserting the propose template instruction contains the completeness step and the pictorial baseline sentence
- [x] 2.4 Verify regeneration: template → `.claude/skills/`/`.claude/commands/` regeneration path still produces valid skill markdown (run the generator or its test)

## 3. Explore workflow skill

- [x] 3.1 In `src/dm2/core/templates/workflows/explore.py`, add a dependency-chain hint: when examining a view, note its `dependencies` and `downstream` (e.g. OV-1 is prerequisite of OV-2/OV-5a)
- [x] 3.2 Test: template instruction contains the dependency-chain hint

## 4. Verification

- [x] 4.1 Full `pytest test/` green (existing 107 + new)
- [x] 4.2 `ruff check src/ scripts/ test/` — no new errors
- [x] 4.3 End-to-end: `dm2 analyze -d "等保三级医院系统" --json` → recommended_views contains OV-1 and its ancestors; propose skill instructions contain the completeness step
- [x] 4.4 `openspec validate wire-view-dependency-supplement --strict` passes
