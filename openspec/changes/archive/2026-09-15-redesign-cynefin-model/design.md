# Design: Redesign Cynefin Complexity Model

## Context

`src/dm2/cognitive/cynefin_analyzer.py` implements the Cynefin assessment consumed by `dm2 cynefin`, `dm2 analyze` (via `Step1IntentScope`), and persisted to `.dm2/analysis-state.yaml`. Investigation (2026-09-15) established that the module is both theoretically wrong and partially dead:

- Dimension scores are 1/2/3 but domain thresholds start at 3.5/5.0 — the weighted average can never reach `Complex`; 5/5 complex votes still resolve to `Complicated`. `Complex` and `Chaotic` branches are unreachable.
- Two independent derivation implementations exist (`cli/main.py::_derive_cynefin_from_description`, `step1_intent_scope.py::_infer_cynefin_values`) and have drifted. The pipeline one contains a polarity inversion: 「不确定」 first matches `不确定` → complex, then the inner substring `确定` matches the positive lexeme and overwrites the vote to simple.
- Evidence computed during derivation is discarded; production callers never pass `evidence`, so confidence collapses to {0.5, 0.6, 0.7}, with all-default (all-medium) input earning the *highest* 0.7.
- `time_span` is a dead dimension always set to `medium`; `get_dynamic_thresholds()` has zero callers; the `reasoning` field is overwritten by a boilerplate string at return.
- The five legacy dimensions measure **scale** (system count, stakeholder count, time span, rule count) plus one uncertainty signal. Cynefin's actual axis is **knowability of cause and effect**: a rule-heavy 等保三级 engagement is Complicated (complete constraints, expert analysis suffices), not Complex; goal conflict between two stakeholders is Complex-er than ten aligned ones.
- The result is decorative: the domain never changes ViewRecommender output, and `propose.py` tells agents the CLI JSON is too thin to audit.

Constraints: zero LLM dependency (rule matching only); `--json` stream purity; convention-over-configuration; Chinese-first descriptions with English terms as secondary lexicon.

## Goals / Non-Goals

**Goals:**

1. Domain model aligned with Cynefin theory: five knowability dimensions, five domains (add `Disorder`), all four active domains reachable.
2. Every auto-derived vote carries evidence spans; abstention is honest and drives the Disorder fallback + clarification loop.
3. One deriver used by CLI and pipeline (identical input → identical output), lexicon externalized to YAML, polarity-safe.
4. Scale signals reported separately without influencing the domain.
5. Auditable structured output (per-dimension value + evidence, confidence decomposition, scale profile, depth tier).
6. Fix the spec violations already present: explicit-option override (currently impossible with Typer defaults) and JSON completeness.

**Non-Goals:**

- Making the domain drive ViewRecommender activation / view selection ("growing teeth") — separate follow-up change; the depth tier ID is the prepared seam.
- No ML/statistical NLP, no embedding, no LLM — lexicon + regex only.
- No rework of 6W analysis or other pipeline steps beyond consuming the new API.
- No migration tool for historical `.dm2/analysis-state.yaml` files (read compat only; files are disposable derived state).

## Decisions

### D1. Tendency values ARE domain votes

Dimension values are `clear | complicated | complex | abstain` (id `Tendency`), not a generic low/med/high scale. Each cast vote directly maps to a score of 1/2/3 and a domain tendency; `abstain` means the deriver found no evidence and the dimension is excluded from aggregation. This removes an indirection and makes the voting semantics the spec contract.

*Alternative rejected*: keep simple/medium/complex and map separately — preserves an illusion of ordinal "magnitude" that caused the scale-vs-knowability confusion in the first place.

### D2. Five semantic dimensions replace the legacy set

| ID | Legacy source |
|---|---|
| `requirement_knowability` | replaces `uncertainty`, but polarity-safe and anchored on requirement freeze/emergence |
| `practice_maturity` | new — the Clear↔Complicated↔Complex classic discriminator (best practice vs expert analysis vs no precedent) |
| `environmental_dynamics` | new — answer shelf-life (stable / predictable / rapid change) |
| `goal_alignment` | replaces stakeholder *count* with stakeholder *conflict* |
| `constraint_clarity` | replaces rule *count* with rule consistency/completeness |

Default weights: all `1.0` (the hard trigger and band edges already encode the discriminating logic; the old 1.2 uncertainty weight was compensating for a muddled signal). Weights remain named constants for future tuning.

### D3. Resolution order: crisis → Disorder gates → hard trigger → band

```
assess(votes, crisis, scale)
│
├─ crisis == True                     → Chaotic        (veto, depth tier full)
├─ n_voting == 0                      → Disorder
├─ n_voting < 3 and cross-domain split→ Disorder       (needs_clarification)
├─ count(complex votes) >= 3          → Complex        (hard trigger)
└─ else weighted band over voting dims:
        avg < 1.5                    → Clear
        1.5 ≤ avg < 2.5              → Complicated
        avg ≥ 2.5                    → Complex
```

- `n_voting` counts dimensions with evidence (derived matches or explicit user values); abstainers excluded from numerator, denominator, and agreement.
- "cross-domain split" = votes contain both `clear` and `complex`, or all three tendencies appear.
- Edge case: 2 complex + 3 complicated = avg 2.4 → Complicated (hard trigger not reached) — pinned by spec scenario.
- Crisis lexicon hits do not double-feed dimensions (e.g. 「应急」 must not inflate `constraint_clarity`).

*Alternative considered*: pure re-thresholded weighted average (edges 1.67/2.34/2.85). Rejected because a single extreme signal still gets averaged away and because "all complex = Chaotic?" was semantically broken; crisis veto + ≥3 trigger encodes Cynefin constraint theory (tightest constraint decides).

### D4. Confidence formula

```
coverage  = evidenced_dimensions / 5                     # explicit user values count
dispersion = (distinct_tendencies_among_voters - 1) / 2  # 1→0, 2→0.5, 3→1
agreement = 1 − dispersion                               # n_voting == 0 → agreement = 0
confidence = clamp(0.20 + 0.45·coverage + 0.30·agreement, 0.20, 0.95)
```

Anchor points: full evidence + uniform = 0.95; no information = 0.20; sparse conflicting ≈ 0.5–0.6. Both components are serialized as `confidence_breakdown`. The 0.20 floor (down from 0.50) lets the tool express real doubt; the 0.95 ceiling is retained.

### D5. Single `CynefinDeriver` + externalized YAML lexicon

New module `src/dm2/cognitive/cynefin_deriver.py`; lexicon at `dm2-reference/core/cynefin-keywords.yaml` — placed under `core/` (rather than the repo root used by `group-to-views.yaml`) so it is included by the existing `dm2-reference/core/**/*` wheel package-data; `dm2 init` copies it into `.dm2/reference/`, and the loader tries both `ref / <file>` and `ref.parent / <file>` to tolerate either layout (local-first/package-fallback via `get_reference_path()`). It is hand-authored config, NOT a derived index, so `build_knowledge_indexes.py` is untouched.

Schema sketch:

```yaml
version: 1
crisis: [应急, 应急响应, 应急处置, 中断, 全站中断, 失控, 战时, 蔓延, 紧急抢修, outage]
dimensions:
  requirement_knowability:
    clear:       [需求明确, 已冻结, 范围明确, 已知]
    complicated: [分阶段明确, 逐步收敛, 需调研, 需澄清部分需求]
    complex:     [涌现, 模糊, 探索性需求, 持续变化, TBD, 待定, 不明确, 不确定, 未知]
  practice_maturity:
    clear:       [成熟方案, 标准部署, 最佳实践, 常规交付]
    complicated: [定制集成, 专家分析, 多方案选型, 等保, 密评, 合规改造]
    complex:     [业内首次, 无先例, 前沿, 自研新范式, 探索]
  environmental_dynamics:
    clear:       [稳定, 固定不变, 长期不变]
    complicated: [可预测变化, 分期建设, 渐进演进]
    complex:     [快速变化, 动态, 自适应, 对抗演变, 答案会过期]
  goal_alignment:
    clear:       [统一目标, 各方一致]
    complicated: [多方协调, 跨部门协作, 利益相关方协调]
    complex:     [目标冲突, 立场对立, 诉求矛盾, 难以协调]
  constraint_clarity:
    clear:       [规则完备, 标准明确, 无合规要求]
    complicated: [有合规框架, 需解释, 行业规范]
    complex:     [规则缺失, 相互矛盾, 监管不明, 无章可循]
negation_prefixes: [不, 未, 没, 无, 毫, 并不, 尚未, 难以]
scale:
  system_terms: [子系统, 系统, 平台, 节点, 组件, 模块, 设备, 服务, 网关, 探针, ...]
  org_terms:    [组织, 部门, 机构, 团队, 公司, 厂商, 甲方, 乙方, 科室, ...]
  time:
    short: [一期, 单次, 短期, 三个月内]
    medium: [年度, 分阶段]
    long: [多年, 长期, 持续运营, 三到五年]
```

**Polarity strategy.** Two complementary mechanisms:

1. Negated forms are listed directly under the complex/abstain side where natural (「不确定」「未知」 in lexicon).
2. When scanning **positive** anchors, the regex is wrapped with a fixed-width negative lookbehind over the prefix list: `(?<!不)(?<!未)(?<!没)(?<!无)(?<!毫)确定` — Python `re` supports fixed-width classes/lookbehinds; multi-char prefixes (`并不`, `尚未`, `难以`) become additional alternated lookbehinds. Longest-first matching (`子系统` before `系统`) with non-overlapping `finditer` prevents double counting.

**Per-dimension decision:** tendency with the most matched spans wins; on an exact tie between tendencies, the dimension **abstains** but retains all matched spans as evidence (signal of conflict without overclaiming). Each cast vote carries up to N (3) deduplicated matched terms as evidence.

**Scale profile:** system count = distinct-match count banded (`≤1→1`, `≤5→3`, else `8` shape, as today); stakeholder level from org-term bands; time span from `time` groups, abstaining (null) when absent instead of forcing medium.

*Alternative considered*: polarity via tokenizer + prefix propagation. Rejected: Chinese has no token boundaries; lookbehind is simpler, testable, and sufficient for prefix negation.

### D6. Analyzer API (clean break, internal module)

```python
class Tendency(str, Enum): CLEAR / COMPLICATED / COMPLEX
class Domain(str, Enum): CLEAR / COMPLICATED / COMPLEX / CHAOTIC / DISORDER

@dataclass
class DimensionVote:
    dimension_id: str
    tendency: Tendency | None          # None = abstain
    evidence: list[str]
    source: str                         # "derived" | "user"

@dataclass
class ScaleProfile:
    systems: int | None
    time_span: str | None               # short | medium | long
    stakeholders: int | None

@dataclass
class ComplexityAssessment:
    domain: Domain
    domain_label: str                   # 明晰/繁杂/复杂/混沌/不明
    confidence: float
    confidence_breakdown: dict          # {coverage, agreement}
    votes: list[DimensionVote]
    scale_profile: ScaleProfile
    crisis: bool
    depth_tier: str                     # minimal|core|extended|full|none
    depth_guidance: str
    needs_clarification: bool
    reasoning_details: str

CynefinAnalyzer.assess(votes: list[DimensionVote], crisis: bool = False,
                       scale: ScaleProfile | None = None) -> ComplexityAssessment
```

Legacy `assess(dict[str,str])`, `ComplexityDimension`, `get_dynamic_thresholds`, and the boilerplate `reasoning` field are removed. All three call sites are rewritten in this change; the module is internal (no public stability promise, pre-1.0).

### D7. CLI surface and JSON contract

**BREAKING** option changes:

| Old | New |
|---|---|
| `--systems int` | `--systems int` (scale only; no longer flips a domain dimension) |
| `--stakeholders str` | `--alignment [clear\|complicated\|complex]` + `--stakeholder-count int` (scale) |
| `--uncertainty str` | `--knowability [clear\|complicated\|complex]` |
| `--rules str` | `--constraints [clear\|complicated\|complex]` |
| — | `--maturity`, `--dynamics`, `--time-span [short\|medium\|long]` |

All options default to `None` (Typer), so the command can distinguish "not passed" from a value: derivation fills the gaps, explicit options override individual dimensions (fixing the long-standing override bug) and are tagged `source: user`. Bare `dm2 cynefin` (no `-d`, no options) returns `Disorder` + `needs_clarification` as a successful result, exit 0.

`--json` `data` shape:

```json
{
  "domain": "Complicated",
  "domain_label": "繁杂（Complicated）",
  "confidence": 0.72,
  "confidence_breakdown": {"coverage": 0.8, "agreement": 0.5},
  "crisis": false,
  "needs_clarification": false,
  "depth_tier": "core",
  "depth_guidance": "12-17 个（P0 核心）",
  "dimensions": [
    {"id": "requirement_knowability", "tendency": "complicated",
     "evidence": ["分阶段明确"], "source": "derived"}
  ],
  "scale_profile": {"systems": 5, "time_span": null, "stakeholders": 3}
}
```

The same object is persisted under the `cynefin` key of `.dm2/analysis-state.yaml` (satisfies analysis-persistence's "same result" rule). Reading old-format state SHALL NOT crash: `dm2 status` prints fields defensively via `.get(...)`.

### D8. Pipeline / step1 integration

- Delete `_infer_cynefin_values`; `Step1IntentScope` gains a `CynefinDeriver` and calls `derive(description)` then `analyzer.assess(...)`.
- `IntentScopeResult` adds `needs_clarification: bool` and `scale_profile` (dict); `cynefin_domain` carries the five-valued label; `format_output` renders an extra 「⚠ 域判定不明，建议先回答澄清问题」 block in Disorder, reusing the already-generated 6W clarification questions.
- Disorder never blocks or fails the pipeline (advisory only); orchestrator print line accommodates the new label.

### D9. Golden corpus as acceptance anchors

Three real corpora (from the 2026-09-15 investigation) become parametrized test fixtures, plus one crisis corpus:

| Fixture (abridged) | Expected domain |
|---|---|
| 单一防火墙部署，需求明确，成熟方案，无合规要求 | `Clear` |
| 医院等保三级…多系统集成，监管/厂商/院方，法规完备，专家分析 | `Complicated` |
| AI 自适应安全编排，需求不确定/涌现，业内首次，环境快速变化，团队探索 | `Complex` |
| 核心业务全站中断，应急处置，事态蔓延 | `Chaotic` |
| `""` / 无关短句 | `Disorder` |

The fixtures must be tuned against the shipped lexicon during implementation; if a corpus starves (e.g. <3 votes) and lands in Disorder for lack of keywords rather than conflict, extend the YAML — do not loosen the algorithm. This keeps the lexicon the tuning surface.

### D10. Docs and workflow templates

- `propose.py` (and any other workflow template instructing agents to ignore CLI output) flips to: the Cynefin JSON is an auditable evidence pack; agents MAY accept it and SHOULD record their own reasoning only when overriding a vote.
- `docs/readme.md` command reference, `CLAUDE.md` module map (cognitive/ description), and CHANGELOG updated for the BREAKING CLI/JSON change.

## Risks / Trade-offs

- **[Disorder becomes noisy — sparse one-line descriptions now return Disorder instead of a fake domain]** → Disorder is advisory and non-blocking; coverage gate (3/5) and tie-abstention keep it rare on substantive input; golden corpus guards against regressions; agents/users can always pass explicit dimensions.
- **[Lexicon quality caps derivation quality]** → externalized YAML makes iteration cheap without code changes; honest abstention + evidence output makes misses visible instead of silently defaulting; lexicon ships bilingually (zh primary, en secondary).
- **[BREAKING CLI flags/JSON break existing scripts and skills]** → pre-1.0 tool; single CHANGELOG entry; all in-repo call sites updated in the same change; old analysis-state read-compatible.
- **[Negation forms beyond the prefix list ( rhetorical double negatives, 「并非不明确」)]** → accepted limitation; such forms still abstain rather than mis-vote because exact-tie and no-positive-match paths both abstain; prefix list is extensible in YAML.
- **[Band edges (1.5/2.5) are heuristic]** → named constants + golden fixtures pin intended behavior; weights/edges can be tuned without touching the algorithm or specs' anchor scenarios.
- **[Removing decorative fields could surprise readers of analysis-state]** → derived disposable state; no external consumer beyond `dm2 status`, which is updated.

## Migration Plan

1. Add `cynefin-keywords.yaml` + loader/package copy (`dm2 init`) and loader tests.
2. Implement new analyzer (`Tendency`, `Domain`, votes, resolution, confidence, depth tiers) behind new class names; unit tests for resolution order and confidence.
3. Implement `CynefinDeriver` (polarity, evidence, ties, scale, crisis); deriver tests including polarity and golden corpus.
4. Rewrite CLI command (options/JSON/persistence) and step1 wiring; add CLI↔pipeline parity test; delete the two legacy derivation functions and dead code.
5. Update workflow templates, docs, CHANGELOG; rewrite `test/test_cynefin.py` to the new contract.
6. Full `pytest` + `ruff check`.

Rollback: single self-contained feature commit; revert restores old behavior. Old `.dm2/analysis-state.yaml` files remain readable throughout (and after) since readers use defensive `.get`.

## Open Questions

1. Should `dm2 status` display the depth tier in addition to the domain label? (Resolved: yes.)
2. Do we want the persisted history to keep prior assessments (append) instead of overwrite? Out of scope — current overwrite semantics retained.
3. English lexicon coverage depth — ship the merged legacy English terms at minimum; expand reactively.
4. **Pre-existing wheel packaging gap (discovered during implementation, out of scope here):** `pip wheel` shows the built wheel contains NO `dm2-reference/` data at all — not even `views.yaml` or `groups/`. `[tool.setuptools.package-data] dm2 = ["dm2-reference/core/**/*"]` resolves relative to the package dir `src/dm2/`, while the data lives at the repo root. Editable installs (the development workflow) and `dm2 init` from a repo checkout work because the loader falls back to the repo root; non-editable wheel installs cannot see the KB. The new `cynefin-keywords.yaml` is no worse than the existing data files. A follow-up change should pick: (a) symlink `src/dm2/dm2-reference` → root (simple, Windows caveat), (b) `data-files` + runtime prefix resolution, or (c) a custom `build_py` step. The repo's CI release job currently publishes the data-less wheel.
