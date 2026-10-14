# Design

## Context

See `proposal.md` — Why. Three constraints shape the approach:

- **The layer is orphaned.** `dm2.engine` is reached only by `dm2 run` without `--agent`. Nothing else imports it, so no fix here can break the agent path.
- **The guard exists but currently asserts the wrong thing.** Each defect is pinned by a `DEFECT-N` test written to pass *while the defect is present*, with a file-header note saying the test turning red is the signal to rewrite the expectation. Fixing a defect without touching its test turns the suite red — which is the intended mechanism, not an accident.
- **The existing specs are thin.** They describe outcomes ("warn the user", "report a circular-dependency violation") and say nothing about the internals that are broken. So most fixes need no implementation guidance from the spec — but the two places where the spec *does* name a behavior (circular-dependency detection, reverse questioning) are exactly where the code silently does nothing.

## Goals / Non-Goals

**Goals:**

- Every symptom the proposal lists stops being reproducible, and the test that pinned it now asserts the correct behaviour instead.
- Where a defect existed because two vocabularies drifted apart (group names, entity types), add a guard that fails if they drift again.

**Non-Goals:**

- Rewriting the heuristic quality of the analysis steps. Step 5's abductive reasoning stays pattern-based; we fix it to name what it found, not to reason better.
- Introducing a real graph model. The pipeline's inputs are prose, and the design keeps it that way.
- The four dead `to_json` static methods on the step classes. They are unreferenced and out of scope; removing them is a separate cleanup.

## Decisions

### D1 — Delete the file-template path rather than repair it

`ViewTemplateFiller.fill()` tries `_find_template_file` first. That method builds patterns by joining onto `reference_root`, which is absolute, and `Path.glob` rejects absolute patterns — so it raises for every registered view. It then looks in `dm2-reference/core/详细分析/`, a directory that does not exist and is not meant to (the analysis corpus lives under `docs/reference/`, declared out of runtime scope and out of the distribution).

**Decision:** remove `_find_template_file` and `_fill_from_file`; `fill()` goes straight to `_fill_from_scratch`, which already produces a heading, viewpoint, data groups and type-appropriate sections.

*Alternatives:* repointing the glob at `docs/reference/analysis/详细分析/` would put a directory the project declares "not read at runtime, not distributed" on the runtime path — it would also fail for any editable-only install. Creating a real template directory means authoring templates for 52 views before anything works.

*Consequence:* `GenerationResult` and `ArchitectureInput` are unreferenced and go with the code they were written for.

### D3 — A failed view is a failure, not placeholder text

Step 6 wraps the filler in a bare `except Exception` and substitutes `视图生成待 LLM 填充`.

**Decision:** remove the placeholder. With D1 fixed the filler no longer raises for a registered view, so the branch should not be reachable; keep an explicit failure path that records the view as not generated rather than writing a document that reads as if it were.

*Rationale beyond correctness:* that single string is the only place a *generated document* names an LLM, so it is the last thing standing between `dm2-no-llm-dependency` and being true end to end.

### D4 — One vocabulary for entity types

The four unpopulated buckets have no patterns. The tempting fix is to hand-write four more regex lists, which is how the current three came to exist and how they will drift again.

**Decision:** derive the four missing buckets' surface vocabulary from the entity types the project already curates in `DM2_GROUP_TO_ENTITY_TYPES` (`Resource` → resource/information/data/material, `Capability` → capability/function/ability, `Location` → location/site/facility/environment, `Measure` → measure/metric/KPI/indicator), and add Chinese surface forms alongside. Where that mapping is the single source, a test can assert that every group a 6W dimension can select has entity types — turning "someone forgot a bucket" into a failing test.

*Alternative:* a separate curated list per bucket. Rejected: two lists for one concept is the defect D7 already embodies.

### D5 — Aim each match at its anchor

The Chinese patterns are `[一-龥]*(?:系统|防火墙|…)[一-龥]*`. The leading class is what lets `防火墙系统` match as one entity; the trailing class is what makes the match run on to the end of the clause (`防火墙系统检测网络威胁`).

**Decision:** drop the trailing class everywhere, and shape verb-anchored buckets differently from noun-anchored ones. A noun bucket is *modifier + type noun*, so it keeps a leading class and now ends at the type suffix. An activity's anchor is a **verb**, so it takes no leading class at all — any unbounded prefix absorbs the subject (`安全团队负责监控` became one "activity").

*Alternatives:* a lazy class (`*?`) stops at the shortest anchor and truncates legitimate multi-word prefixes. Bounding a verb's object (`[一-龥]{0,6}`) still crosses into the next entity — the verb `分析` in `分析引擎检测威胁` swallows `引擎检测威胁`, and `引擎` belongs to a system name. Bounding a noun's modifier the same way yields fragments (`与地理位置`) rather than names, so it is not an improvement.

*Known limit:* a noun match's modifier prefix is still unbounded, so a long clause can put `需要评估能力与地理位置` in the `location` bucket. Keyword extraction cannot find Chinese entity boundaries reliably, and the Non-Goals rule out making the heuristic cleverer — so the spec states only what this guarantees (matches end at their anchor, buckets stay disjoint) rather than promising parsed entities.

### D6 — An edge needs two endpoints; skip the relation otherwise

`_check_temporal_consistency` captures the name *after* a `prerequisite:` / `successor:` marker and then assigns it an empty target list, so `_find_cycles` walks an empty adjacency map. `_find_cycles` itself is correct and needs no change.

**Decision:** parse both sides of the marker — the text before it on the same line is the subject, the captured group is the target — and record the edge. A line with no subject is skipped rather than defaulted.

*Rationale:* inventing an endpoint is the same mistake as D11's placeholders. Skipping is honest: an unparseable line simply contributes no edge.

*Note:* no spec fixes the declaration format, so this convention is the design's choice, not a reading of an existing contract. It is recorded here so a later change can revisit it deliberately.

### D7 — Key the estimate table by what callers pass

The table's keys (`"01-Performer"`) match neither the callers' bare names (`"Performer"`, from `SIX_W_TO_DM2_GROUPS`) nor the real directories (`01-performer`). It is doubly orphaned.

**Decision:** key it by the bare names the callers pass — they are the only consumers — and add a test asserting every group reachable from `SIX_W_TO_DM2_GROUPS` has a weight. That assertion is what makes the drift impossible to reintroduce silently; the same shape of guard the repo already uses for renamed relations.

*Alternative:* translate to directory names at the call site. Rejected: it couples runtime behaviour to a filesystem layout that has already drifted once (`00-基础模式` vs `00-foundation`).

### D8 — Primary dimension contributes both its questions

Each dimension has two reverse-questions; only `templates[0]` is ever read, and when `Why` is primary the "fewer than two" fallback re-appends the question already asked, yielding a duplicate.

**Decision:** take both questions from the primary dimension, then one from each secondary until the set reaches three, deduplicating. The spec asks for 2–3 distinct questions; the primary dimension is where the ambiguity is greatest, so it earns the extra slot.

*Alternative:* delete the unreachable second templates. Rejected — that removes authored content to match a bug.

### D9 / D10 — Remove the dead field and the dead parameter

`DataRequirement.required_concepts` is always `[]` and read by nobody; `_build_taxonomy(requirements, concepts)` never reads `concepts`. Neither is a spec-level behaviour (the step3 spec names the taxonomy and the gaps, not this field), so both are pure removals: drop the field, drop the parameter. No spec delta.

### D11 — An inference names what it is about

Two kinds of inference share one placeholder each. For a **missing** pattern there is no observed entity — which is why `"未知"` was written — but the relation still has endpoints: they are the DM2 types it would connect (`Activity` ↔ `Performer`). For a **matched** pattern the observed instance is right there in `matched_text`.

**Decision:** missing-pattern inferences name the DM2 types the relation connects; matched-pattern inferences name the matched text. `expected_patterns` grows from label-only to (label, endpoint types).

### D12 — Derive the out-degree from the same node set

`out_degree` is hardcoded `1`, and `format_output` prints it as `入度/出度` — so the step 5 document shows a fabricated number. The analysis has no edge model to read a real degree from.

**Decision:** derive it from the extracted flow nodes: the out-degree is the count of distinct *other* nodes the bottleneck co-occurs with in the analysed text. `in_degree` keeps its present meaning (reference count). Both then vary with the architecture, which is what the new scenario requires.

*Alternative:* parse explicit flow relations first and fall back to co-occurrence. Deferred — see Open Questions.

### D15 — Follow the spec, not the call site

Verifying the fixes end to end turned up a defect the twelve did not cover: the orchestrator passes a bare `output/` to `save_views`, while the `step6-documentation` spec (twice, inherited from the archived `complete-6step-pipeline` change), the step's module docstring and `DocumentationResult.output_dir` all say `.dm2/output/`.

**Decision:** correct the orchestrator. The spec has the weight of evidence — three sources inside the step against one call site — and `.dm2/output/` sits next to `.dm2/steps/`, which is where the pipeline already keeps its artifacts.

*Consequence, and the reason this is worth recording:* the fix exposed a latent bug in `save_views`, which built its `ViewManager` from `output_dir.parent`. That worked only because the output directory happened to sit exactly one level below the project root; nesting it one deeper silently registered the views under `.dm2/.dm2/`. It now resolves the project root by walking up for the project marker. The test fixture `tmp_project` had encoded the same wrong assumption and is corrected with it.

## Risks / Trade-offs

- **The DEFECT-N tests must be rewritten in the same commit as each fix.** A fix landed alone leaves a red suite; a test rewritten alone hides the defect. → Each task pairs one code change with its test rewrite, and the tasks file lists them together rather than as separate phases.
- **D4's value depends on `DM2_GROUP_TO_ENTITY_TYPES` staying current.** If a group's types are thin, its bucket is thin. → The reachability test fails on a missing group rather than silently producing an empty bucket.
- **D6 fixes reachability, not recall.** A relation the prose does not state is still not found; the spec's scenario only claims cycles are *reported*, not that every cycle is discoverable. → Accepted; the change makes a rule honest, it does not make it clever.
- **D12's co-occurrence degree is a proxy, not a graph degree.** It can overstate connectivity in prose that merely lists nodes together. → Accepted and recorded as the reason the explicit-flow alternative is documented.
- **Removing `required_concepts` and the filler's template path is an internal breaking change.** Both are unreferenced outside their own module, verified by search; the risk is a consumer outside this repository, which the editable-only distribution rule already rules out.

## Migration Plan

No data or state migration. `.dm2/steps/*.md` and `.dm2/output/*.md` are regenerated on the next `dm2 run`; existing files with placeholder content are simply overwritten. Rollback is a revert of the change — nothing persists a schema.

## Open Questions

- Should TOC bottlenecks read explicit resource-flow relations when an architecture declares them, falling back to co-occurrence only when it does not? Deferrable: the new scenario requires only that the degrees be derived, and the co-occurrence proxy satisfies it. Answering it would refine the heuristic, not change any spec or task.
