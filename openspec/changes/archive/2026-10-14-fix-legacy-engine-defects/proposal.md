# Proposal

## Why

`dm2 run` without `--agent` executes a four-step pipeline under `src/dm2/engine/` — the *only* caller of that whole package (`src/dm2/cli/main.py:1391`, marked `# Legacy mode`). Until 2026-10-14 that layer had **zero test coverage**, so its defects have shipped since the initial commit with CI green.

Adding coverage (`test: cover the legacy engine layer and pin its twelve defects`, `c40dda2`; 197 cases, 481 → 678) exposed **12 defects** and pinned each one with a `DEFECT-N` test. Now is the moment to fix them because the safety net finally exists: every fix has a test that fails the moment behaviour changes, which is exactly what this layer never had.

Two of the defects are not merely wrong but contract-breaking: Step 6 writes the literal string `视图生成待 LLM 填充` into every per-view document, contradicting `dm2-no-llm-dependency`, and Step 5's circular-dependency detection — named explicitly in its spec — has been unreachable since it was written.

## What Changes

**A · wrong output**

- **BREAKING (internal)**: `ViewTemplateFiller` drops its file-template path entirely — `_find_template_file` (which can never succeed: it hands an absolute pattern to `Path.glob`) and `_fill_from_file` are removed, and `fill()` goes straight to `_fill_from_scratch`, which already produces a usable skeleton. The two unused dataclasses `GenerationResult` / `ArchitectureInput` go with them.
- Step 6 no longer swallows a filler failure into placeholder text. Per-view documents carry real content and the `[[wikilinks]]` its spec requires.
- `six_w_analyzer` implements the four entity buckets it declares but never fills (`resource`, `capability`, `location`, `measure`), and its Chinese patterns stop swallowing whole clauses into a single "entity".

**B · silently inert**

- `ConsistencyChecker`'s temporal rule becomes reachable: the prerequisite/successor targets are parsed into the graph instead of being assigned empty lists, so `circular_dependency` can actually fire.
- `Step1IntentScope`'s token-estimate table is re-keyed to the names its callers pass (and to the real group directory names), so per-group weights take effect instead of every group costing the 2500 default.
- Reverse questioning asks distinct questions: the second template per dimension becomes reachable, and a `Why` primary no longer duplicates the same question.

**C · empty placeholders**

- **BREAKING (internal)**: `DataRequirement.required_concepts`, always empty and read by nobody, is removed; `_build_taxonomy` loses the `concepts` parameter it never reads.
- Step 5's abductive inferences identify the entities they are about instead of `"未知"` / `"(从描述提取)"`.
- **User-visible**: `TOCBottleneck.out_degree` is derived rather than hardcoded to `1` — it is printed in `.dm2/steps/step5-analysis.md` as `入度/出度`.

**D · view output path** (found while verifying the above, folded in with the user's approval)

- **D15**: the orchestrator writes generated views to `<project>/output/` while the `step6-documentation` spec, the step's own module docstring and its `DocumentationResult.output_dir` field all say `.dm2/output/`. The orchestrator is the outlier (a `CLAUDE.md` sentence repeats its mistake) and is corrected. Fixing it exposed a latent bug: `save_views` used `output_dir.parent` as the project root to construct its `ViewManager`, which lands the registration in `.dm2/.dm2/` as soon as the output directory gains a level — it now resolves the root by walking up for the project marker.

Not in scope: the four `to_json` static methods on the step classes are dead (nothing calls them) but are left alone.

## Capabilities

### New Capabilities
- `six-w-analysis`: 6W interrogative analysis of an architecture description — dimension scoring (which drives scope and view recommendation) and entity extraction across the seven entity buckets. Currently unspecified; `dm2 analyze --json` exposes `extracted_entities`, and `dm2 generate` requires a `six_w_analysis` field.

### Modified Capabilities
- `step6-documentation`: the requirement that Step 6 produce generated views must state that a view document carries real content and its wikilinks — a placeholder is a violation, and the placeholder text must not name an LLM.
- `step5-analysis`: `Consistency validation` must make circular-dependency detection an actual check (today the rule is unreachable), and `Abductive reasoning` must require inferences to name the entities involved.
- `step1-intent-scope`: `Context budget estimation` must require the per-group weights to inform the estimate, and `Intent convergence with reverse questioning` must require the questions to be distinct.

## Impact

- **Code**: `src/dm2/engine/view_generator.py`, `src/dm2/engine/pipeline/step6_documentation.py`, `src/dm2/cognitive/six_w_analyzer.py`, `src/dm2/reasoning/consistency.py`, `src/dm2/engine/pipeline/step1_intent_scope.py`, `src/dm2/engine/pipeline/step3_data_requirements.py`, `src/dm2/engine/pipeline/step5_analysis.py`.
- **Tests**: the 12 pinned `DEFECT-N` expectations flip to asserting correct behaviour — the guards stay, their assertions change. New expectations are needed for the four entity buckets and for a `Why`-primary question set.
- **Consumers**: `dm2 analyze --json` (`extracted_entities` gains buckets), `.dm2/steps/step5-analysis.md` (`入度/出度` becomes real), `.dm2/output/*.md` (real view documents instead of placeholders). No public CLI signature changes.
- **Contract**: `openspec/specs/dm2-no-llm-dependency` is currently satisfied on the source side; the placeholder string is the one remaining place where a *generated document* names an LLM. Removing it keeps that spec true end to end.
- **Risk**: low blast radius — the layer is reached only by the non-`--agent` path, and `dm2 run --agent` (the workflow the shipped skills use) does not touch it.
