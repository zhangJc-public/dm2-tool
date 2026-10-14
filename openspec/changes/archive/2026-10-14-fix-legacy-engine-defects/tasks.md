# Tasks

Each task pairs a fix with the rewrite of the test that pinned it. Run the pinned
test first to watch it turn red — that is the signal the defect is gone and the
expectation now has to assert the correct behaviour. A task is not done while its
file still carries a `DEFECT-N` marker for the behaviour it fixed.

## 1. A · Wrong output (D1–D5)

- [x] 1.1 **D1/D2** — delete the file-template path from `ViewTemplateFiller`: remove `_find_template_file` and `_fill_from_file`, point `fill()` at `_fill_from_scratch`, and drop the now-unreferenced `GenerationResult` / `ArchitectureInput` dataclasses. Verify `test/test_view_generator.py` passes with `TestTemplateFileLookup` and `TestFillPropagatesTheDefect` replaced by assertions that `fill()` returns a populated document for OV-1 / OV-2 / OV-5a / CV-1, and that no `DEFECT-1`/`DEFECT-2` marker remains in the file.
- [x] 1.2 **D3** — remove the `except Exception` placeholder in `Step6Documentation.execute`; a view the filler cannot produce is recorded as not generated rather than written as a document. Verify `test/test_step6_documentation.py`'s `TestPerViewDocumentsArePlaceholders` is replaced by assertions that each view body carries its heading and generated sections, that `[[wikilinks]]` are present, and that no generated string contains `LLM`.
- [x] 1.3 **D4** — populate the four declared-but-empty entity buckets in `six_w_analyzer._extract_entities`, sourcing the type vocabulary from `DM2_GROUP_TO_ENTITY_TYPES` so the buckets and the step-3 mapping cannot drift apart. Verify `test/test_six_w_analyzer.py`'s `TestEntityBuckets` asserts each of the seven buckets can be filled, plus a new test asserting every group reachable from `SIX_W_TO_DM2_GROUPS` has entity types.
- [x] 1.4 **D5** — drop the trailing `[一-龥]*` from the Chinese entity patterns so a match ends at its type suffix. Verify `test_six_w_analyzer.py`'s `TestGreedyChinesePatterns` is rewritten to assert the extracted entity is the name alone and that one clause no longer appears in several unrelated buckets.

## 2. B · Silently inert (D6–D8)

- [x] 2.1 **D6** — make `ConsistencyChecker._check_temporal_consistency` record the edge it parses: the text before a `prerequisite:` / `successor:` marker is the subject and the captured group is the target; a line without a subject contributes no edge. `_find_cycles` is already correct and stays as it is. Verify `test/test_consistency.py`'s `TestTemporalRuleIsUnreachable` is replaced by a test asserting a declared cycle produces a `circular_dependency` issue at ERROR severity, and one asserting an acyclic declaration produces none.
- [x] 2.2 **D7** — re-key `DM2_GROUP_TOKEN_ESTIMATES` to the bare group names callers pass, so per-group weights reach `_estimate_context_budget`. Verify `test/test_step1_intent_scope.py`'s `TestContextBudget` shows two groups of different known size yielding different estimates, and that a new test asserts every group reachable from `SIX_W_TO_DM2_GROUPS` has a weight.
- [x] 2.3 **D8** — make reverse questioning ask distinct questions: the primary dimension contributes both of its questions, secondaries contribute one each up to three, duplicates are removed. Verify `test_step1_intent_scope.py` asserts a `Why` primary no longer repeats a question, that every dimension's second template is reachable, and that the result is 2–3 distinct questions.

## 3. C · Empty placeholders (D9–D12)

- [x] 3.1 **D9/D10** — remove `DataRequirement.required_concepts` and the unused `concepts` parameter of `_build_taxonomy`, updating its call site. Verify `test/test_step3_data_requirements.py` passes with the tests referencing `required_concepts` deleted and a test asserting `_build_taxonomy` takes only the requirements.
- [x] 3.2 **D11** — make abductive inferences name what they are about: grow `expected_patterns` from a label to a label plus the DM2 endpoint types the missing relation would connect, and name the matched text for pattern-matched inferences. Verify `test/test_step5_analysis.py`'s `TestAbductiveReasoning` asserts no endpoint is an unnamed placeholder, that a missing-pattern inference names two DM2 types, and that a matched-pattern inference names its matched text.
- [x] 3.3 **D12** — derive `TOCBottleneck.out_degree` from the analysed node set instead of hardcoding `1`. Verify `test_step5_analysis.py` asserts the out-degree varies with the input, and that `.dm2/steps/step5-analysis.md` printed after a `dm2 run` shows a derived `入度/出度` rather than `/1` for every architecture.

## 4. Integration

- [x] 4.1 Run the full gate matrix and confirm no pinned expectation survived its fix: all of `test/` passes on 3.9.25 / 3.11.16 / 3.13.12 with and without `GITHUB_ACTIONS=true`, `ruff check src/ test/` is clean, and `openspec validate --all --strict` reports 38/38 (`grep -rn 'DEFECT-' test/` returns only markers for defects this change deliberately left, if any).
- [x] 4.2 Run `dm2 run -d "<description>"` in a throwaway project and verify the artifacts are real: `.dm2/output/OV-1.md`, `OV-2.md`, `OV-5a.md` and `composite-view.md` carry content rather than placeholders, step 5's document shows a derived degree pair, and no generated file contains `LLM`.
- [x] 4.3 Update `docs/foundation.md`: mark the D14 row's twelve defects as fixed, record the guard files that cover them, and refresh the §4 baseline test count. Verify `openspec validate --all --strict` still passes and the baseline figure matches `pytest test/` output.

## Workflow follow-up

- Archive the change after review, using the project's standard OpenSpec archive flow.
- After archiving, confirm the delta specs merged into `openspec/specs/` and that the `six-w-analysis` capability appears in `openspec list --specs`.
