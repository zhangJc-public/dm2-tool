# Remove LLM packaging residuals

## Why

`dm2-tool`'s headline rule is zero LLM dependency, but that claim only holds for the code.
`pyproject.toml` still declares `anthropic>=0.39.0` as a **hard runtime dependency** and ships a
dead `[openai]` extra, while no file under `src/` imports either library. The historical
`remove-llm-from-dm2` change scoped its rule to `src/dm2/` imports only, and left
"`pyproject.toml` … 是否也删除？" as an unresolved Open Question in its design — so the hard
`anthropic` requirement was never even considered, and that change's `dm2-no-llm-dependency`
spec never reached `openspec/specs/`. Every `pip install dm2-tool` therefore pulls a 16 MB
network-capable LLM SDK plus its dependency tree into an environment that never calls it.

## What Changes

- **Remove the hard `anthropic>=0.39.0` dependency** from `[project.dependencies]`.
- **Remove the dead `[openai]` optional extra** (unused, and never installed).
- **Fix the README configuration section**: it documents `dm2 config -s llm.model=...` and the
  `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` environment variables, contradicting the shipped
  behaviour where `llm.*` settings are refused.
- **Fix two source-level examples** that teach the same removed key: the `--set` help text in
  `src/dm2/cli/main.py` and the `get()` docstring in `src/dm2/config/manager.py`.
- **Restore the zero-LLM rule as a live spec**: add a `dm2-no-llm-dependency` capability whose
  scope covers packaging and user-facing surfaces, not just `src/dm2/` imports.

## Capabilities

### New Capabilities

- `dm2-no-llm-dependency`: the dm2 distribution declares, imports, and documents no LLM
  dependency — covering packaging metadata and user-facing surfaces in addition to the
  `src/dm2/` import scan the original (never-merged) rule covered.

### Modified Capabilities

<!-- None: `dm2-generate-no-llm` governs the `dm2 generate` command's runtime behaviour, which
     this change does not touch. -->

## Impact

- **Packaging**: `pyproject.toml` — one dependency removed, one extra removed; the regenerated
  metadata lists only `pyyaml` and `typer` (plus the `dev` extra).
- **Docs**: `README.md` configuration section rewritten to state that no API key or LLM endpoint
  configuration is needed.
- **Source (help text and comments only)**: `src/dm2/cli/main.py` `--set` help example,
  `src/dm2/config/manager.py` `get()` docstring example. No behaviour changes.
- **Unchanged**: the `llm.*` rejection path in `dm2 config` stays — it is the behaviour the
  README previously contradicted.
- **Out of scope**: `docs/readme.md` already carried no LLM configuration instructions, and the
  `dm2 generate` / `analyze` no-LLM behaviour is untouched.
