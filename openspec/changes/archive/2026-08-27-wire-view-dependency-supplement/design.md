# Design: Wire view dependency supplement into analyze & skills

## Context

`ViewRecommender.verify_and_supplement_views()` already implements path-completeness
supplementation: `_check_path_completeness()` computes the transitive closure over
views.yaml `dependencies` and any missing ancestor is added back at score 0.6 with a
`路径完整性补充` reason. Retrospective analysis of why OV-1 keeps disappearing from
generated view sets found the mechanism was correct but **had zero callers**:

- `dm2 analyze` (src/dm2/cli/main.py) called only `recommend()`, whose output is
  intentionally unsorted ("CLI 不排序, AI Agent 做最终优先级排序").
- The propose workflow skill derived its view set as
  `concern core_views ∪ candidate_views` with no dependency scan.

Two secondary facts shaped the design:

1. `recommended_views` in the analyze JSON is `recs[:10]` of an unsorted list, so
   missing ancestors are not merely absent from the full set — they are invisible in
   the top-10 slice the agent consumes first.
2. Pictorial views (OV-1/CV-1/AV-1) are data-light in `view-content-spec.json`
   (OV-1: 1 necessary term / 0 necessary associations). Model-side reasoning
   ("little data → low value → drop") is therefore never contradicted unless the
   dependency data and a communication-baseline rule are made explicit at the
   instruction layer.

Constraints: zero LLM dependency, convention over configuration, CLI emits structured
JSON, skill text lives in Python templates and is regenerated into `.claude/`.

## Goals / Non-Goals

**Goals:**
- Every `dm2 analyze` `recommended_views` set is dependency-complete (transitive
  ancestors present), deduplicated, and deterministically ordered so ancestors land
  in the top-10 slice.
- The propose workflow skill enforces the same completeness on the concern-focused
  set, since the agent (not the CLI) builds that set from concerns.
- Pictorial views carry an explicit "communication baseline" status so data-lightness
  is never treated as grounds for exclusion.
- The explore workflow surfaces dependency chains during read-only discussion.

**Non-Goals:**
- Changing views.yaml dependencies, the monster-matrix content-spec, or group-to-view
  mappings — data-lightness of pictorial views is a standard fact, addressed at the
  instruction layer.
- Adding new backend recommenders or changing the concern-matching algorithm.
- Re-scoring supplemented views (0.6 is kept; ordering, not score, is the fix).

## Decisions

### D1: Call `verify_and_supplement_views()` in `dm2 analyze`, not inside `recommend()`

`recommend()` documents itself as unsorted output for agent-side prioritization, and
its callers (tests, `__main__` demo) rely on that shape. The supplement step is a
verification/presentation concern, so it is invoked from the CLI after `recommend()`
returns, mutating nothing about the recommendation algorithm itself.

Alternative considered: supplement inside `recommend()`. Rejected — it would couple
raw candidate generation to closure semantics and change the documented contract.

### D2: Sort at the supplement boundary

`verify_and_supplement_views()` already dedups via a `seen` set (first occurrence
wins, preserving the higher data-group-activated score on duplicate ids) and sorts by
`(priority, -relevance_score)`. Wiring it into analyze means the analyze JSON
`recommended_views`/`candidate_views` become sorted where they previously were not.
This is intentional and beneficial: priority-1 ancestors supplemented at 0.6 now
sort ahead of priority-2/3 activated views, guaranteeing OV-1/CV-1/AV-1 appear in the
top-10 slice. The propose skill explicitly does not rely on CLI priority ordering for
its own P1/P2/P3 assignment, which is concern-driven — no conflict.

### D3: Expose `reason` in analyze JSON view objects

The spec scenario "Reason present in JSON output" requires agents to distinguish
supplemented views. `ViewRecommendation.reason` existed but was omitted from the
`candidate_views`/`recommended_views` JSON dicts. Added `reason` to both; the
supplement marker `路径完整性补充 - {view}（被 {groups} 数据组需要）` is then visible
without extra CLI calls.

### D4: Completeness as a propose-skill step, not backend code

The propose focused set is built in the AI agent from concern `core_views`; the CLI
never sees it. The fix therefore belongs in the skill instruction text: a new step 7
"视图完整性确认" run after P1/P2/P3 assignment, scanning the analyze JSON
`view_dependencies` map for missing transitive ancestors, supplementing them into P3
marked `P3 supplement` with dependency rationale. The rule explicitly overrides
concern focus (data-security-and-compliance's core_views exclude OV-1, but
OV-2/OV-5a pull it back).

Alternative considered: compute the focused set in Python. Rejected — concern
matching and human selection deliberately run in the agent (per existing guardrails).

### D5: Pictorial baseline as an explicit named rule

OV-1/CV-1/AV-1 are named explicitly in both the step-7 instruction text and a
guardrail bullet, stating data-lightness in the monster matrix is never grounds for
exclusion because these views are the decision-maker communication baseline. Naming
the views (rather than a generic "keep pictorial views") is required so the rule
fires on the exact views the matrix scores at ~0 data.

### D6: Explore hint is advisory, bidirectional

The explore skill gets one bullet in "Explore architecture decisions": when
examining a view, note both `dependencies` (prerequisites) and `downstream`
(dependents) from `dm2 knowledge view <id> --json` — both fields already exist in the
knowledge JSON output. The OV-1 → OV-2/OV-5a example is included verbatim per spec.

### D7: Regenerate shipped skills from templates

`.claude/skills/dm2-*` are generated artifacts of `src/dm2/core/templates/workflows/*.py`
(via `generate_agent_config` / ClaudeCodeAdapter). After editing propose.py and
explore.py, regenerated so the shipped skills match; a generator test
(`test_workflow_templates.py::TestSkillRegeneration`) pins the round-trip.

## Risks / Trade-offs

- [Sorted analyze output changes an "unsorted" contract] → The unsorted guarantee was
  internal ("CLI 不排序"), not a spec requirement; consumers are the agent skills,
  which benefit from deterministic ordering. No test asserted unsorted order.
- [Supplemented views at fixed 0.6 may outrank genuinely weak activated views] →
  Sort is `(priority, -score)`; ancestors of recommended views are prerequisites by
  definition, so ranking them above the views that need them is correct.
- [Agent ignores the skill completeness step] → The CLI path (D1) guarantees
  completeness for `candidate_views` regardless; the skill step additionally covers
  concern-filtered sets the CLI never computes. Belt and suspenders.
- [design.md written after implementation] → Documented decisions match the shipped
  code; tests pin every behavioral claim.

## Migration Plan

1. Ship the one-line CLI wiring + JSON `reason` field (additive; no data migration).
2. Regenerate project-local skills on next `dm2 init`/regeneration; shipped repo
   skills already regenerated in this change.
3. Rollback: revert the single `verify_and_supplement_views()` call to restore prior
   behavior; skill text changes are inert without regeneration.

## Open Questions

None. All 14 tasks implemented and verified (118 tests green, ruff clean of new
errors, `openspec validate --strict` passes).
