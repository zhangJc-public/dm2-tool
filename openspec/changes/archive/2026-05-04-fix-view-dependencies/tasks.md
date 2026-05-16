## 1. views.yaml dependency fixes

- [x] 1.1 Add 15 missing dependencies per VIEW-DEPENDENCY-RESEARCH-V2.md §6.1:
  - CV-3: +CV-1, +PV-2
  - CV-5: +CV-2, +OV-4, +PV-2, +SV-1, +SvcV-1
  - CV-7: +SvcV-4
  - OV-2: +OV-5b
  - OV-3: +OV-5b, +DIV-2
  - SV-6: +SV-4
  - SV-7: +SV-1, +StdV-1
  - SV-8: +SV-1, +SV-9
  - SV-10c: +SV-5a, +SV-10a
  - PV-2: +CV-3, +SV-8, +SvcV-8
  - StdV-2: +SV-8, +SvcV-8, +SvcV-9
- [x] 1.2 Fix 3 wrong dependencies:
  - SV-2: SV-4→SV-1, StdV-1
  - CV-6: OV-5a→OV-5b
  - DIV-1: (none)→OV-2, OV-5b, OV-6a
- [x] 1.3 Update downstream field for the 5 views that already have it (OV-1, OV-5b, SV-4, SvcV-4, StdV-1) to reflect new dependency edges from fixes above

## 2. Eliminate hardcoded dependency rules

- [x] 2.1 Add `_get_dependencies()` method to `ViewRecommender` that reads dependencies dict from `DM2KnowledgeIndexer` (from `self._indexer.view_templates`)
- [x] 2.2 Replace `_check_path_completeness()` body with recursive transitive closure using `_get_dependencies()`:
  - Implement `transitive_deps(vid, visited)` inner function with cycle guard
  - Compute `all_needed - view_ids` as return value
  - Remove all 31 hardcoded `path_rules` tuples (~48 lines → ~15 lines)
- [x] 2.3 Verify `_get_view_sequence()` (DFS topological sort in same class) is consistent with updated views.yaml deps

## 3. Indexer: downstream auto-derivation and cycle detection

- [x] 3.1 Add downstream auto-derivation in `_load_view_templates()`:
  - After loading all templates, for each template.dependencies, add reverse edge to dep's downstream
  - Preserve YAML-declared downstream values (explicit wins)
- [x] 3.2 Add DAG cycle detection using Kahn's algorithm in `load_all()` after `_load_view_templates()`:
  - Compute in_degree from dependencies
  - Run Kahn's topological sort
  - If result size < total views, raise ValueError with view IDs in cycle
- [x] 3.3 Remove any manually-maintained downstream fields from views.yaml that are now auto-derived (keep only the 5 explicit ones as baseline)

## 4. Validation

- [x] 4.1 Run `python3 -m dm2 knowledge views` and verify all 52 views load without cycle-detection errors
- [x] 4.2 Run `python3 -m dm2 generate AV-1 -d "test"` and verify path completeness check runs without errors
- [x] 4.3 Run `python3 -m dm2 analyze -d "网络安全防护体系" --json` and verify `missing_dependencies` field in output is populated from views.yaml
- [x] 4.4 Check that `dm2 instructions generate -d "test" --view AV-1` output includes correct dependency artifact lists from views.yaml
