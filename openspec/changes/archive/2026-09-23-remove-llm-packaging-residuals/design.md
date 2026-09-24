## Context

The project asserts zero LLM dependency as a headline rule (`CLAUDE.md`), and the archived
change `2026-05-04-remove-llm-from-dm2` deleted every LLM code path. Its spec
`dm2-no-llm-dependency` — which never reached `openspec/specs/` — stated the rule as:

> The dm2 codebase **under `src/dm2/`** SHALL contain zero imports of LLM client libraries
> (anthropic, openai) and zero code paths that invoke external LLM APIs.

That wording measures imports, not packaging, and its `design.md` closed with an unanswered
Open Question about the `openai` extra. Two independent consolidations (`remove-llm-from-dm2`,
`remove-llm-residuals`) therefore both passed while `anthropic>=0.39.0` stayed a hard
dependency in `[project.dependencies]`.

Measured state before this change:

| Surface | Before |
|---|---|
| `src/` imports of `anthropic` / `openai` | none |
| `[project.dependencies]` | `pyyaml`, `typer`, `anthropic>=0.39.0` |
| Optional extras | `dev`, `openai` (dead) |
| Installed footprint | `anthropic` 1.6.0 present, 16 MB, 16 declared transitive deps |
| `README.md` | documented `dm2 config -s llm.model=…`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` |
| `dm2 config --help` | `--set` example was `llm.model=claude-opus-4-7` |
| `dm2 config -s llm.model=…` | prints "LLM 配置由 AI Agent 层管理" and exits 0 |

The last row is the contradiction: the code already refuses `llm.*`, while two user-facing
surfaces still advertised it.

## Goals / Non-Goals

**Goals:**

- No LLM library is declared as a dm2 dependency, in any form.
- No user-facing surface instructs configuring an LLM or an API key.
- A live spec enforces this at the distribution level, so the rule cannot silently drift again.

**Non-Goals:**

- Re-auditing non-LLM dependencies, or pruning `pyyaml`/`typer`.
- Changing `dm2 generate` / `dm2 analyze` behaviour (already covered by `dm2-generate-no-llm`).
- Removing the `llm.*` rejection path in `dm2 config` — it is the guard, not a residual.
- Rewriting the historical archived change or its Open Question.

## Decisions

**Scope the rule to the distribution, not the source tree.** The narrow `src/dm2/` wording is
the direct cause of this residual: it let a hard dependency pass two cleanups. The new spec
names packaging metadata and user-facing surfaces explicitly, so a future cleanup audit has a
checkable surface beyond `grep src/`.

**Delete the `[openai]` extra rather than keep it for future use.** Nothing imports the library,
the extra was never installed, and keeping a dormant LLM extra would preserve exactly the
ambiguity this change exists to remove. A future need can re-add it in the change that
introduces the code.

**Fix documented examples instead of adding deprecation notes.** A deprecation note would keep
teaching the removed key. The replacement examples use real, settable keys
(`views.include_mermaid=true`) so the documentation demonstrates something that works.

**Keep `dm2 config`'s `llm.*` rejection.** It produces an explicit informational message and is
the runtime half of the zero-LLM guarantee. The README was the side that was wrong.

**Restore the lost capability as a new spec rather than amending `dm2-generate-no-llm`.**
That spec governs one command's runtime contract; the zero-LLM rule is a distribution-wide
invariant. Reusing the original capability name keeps continuity with the archived change and
puts the rule back where it belongs.

## Risks / Trade-offs

- **A consumer installing `dm2-tool[openai]` breaks.** Accepted: the extra installed a library
  the tool never imports, the project is pre-1.0, and no in-repo consumer references it.
- **Local environment metadata is stale until reinstalled.** `src/dm2_tool.egg-info/` is
  gitignored build output, so it is not a deliverable; `pyproject.toml` is the source of truth
  and the editable reinstall in verification refreshed both it and the installed `dist-info`.
- **The first reinstall attempt was denied by the file sandbox** because the console script and
  `dist-info` live outside the workspace. It was retried with wider access; the retry succeeded
  and no partial uninstall was left behind.
- **Grep-based enforcement can miss indirect references.** The spec therefore also asserts the
  observable consequence — the declared dependency list — rather than only a text scan.
