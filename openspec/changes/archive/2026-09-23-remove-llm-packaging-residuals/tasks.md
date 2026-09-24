# Tasks

## 1. Packaging

- [x] 1.1 Remove `"anthropic>=0.39.0"` from `[project.dependencies]` in `pyproject.toml`
- [x] 1.2 Remove the dead `[project.optional-dependencies] openai` extra
- [x] 1.3 Confirm no file under `src/`, `test/`, `scripts/`, or `templates/` imports `anthropic` or `openai`

## 2. User-facing surfaces

- [x] 2.1 Rewrite the `## 配置` section of `README.md` to drop the `dm2 config -s llm.model=...` example and the `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` environment variables, and state that no API key or LLM endpoint configuration is needed
- [x] 2.2 Change the `--set` help example in `src/dm2/cli/main.py` from `llm.model=claude-opus-4-7` to a settable key (`views.include_mermaid=true`)
- [x] 2.3 Change the `get()` docstring example in `src/dm2/config/manager.py` from `'llm.model'` to `'views.include_mermaid'`
- [x] 2.4 Verify `docs/readme.md` carries no LLM configuration instructions (it already did not — no edit needed)

## 3. Verification

- [x] 3.1 Reinstall editable (`python3 -m pip install -e .`) and confirm the regenerated `src/dm2_tool.egg-info/requires.txt` lists only `pyyaml`, `typer`, and the `dev` extra
- [x] 3.2 Confirm the installed `dist-info/METADATA` `Requires-Dist` entries contain no LLM library
- [x] 3.3 Confirm `dm2 version` and `python3 -m dm2.cli.main version` still work after the reinstall
- [x] 3.4 `pytest test/` green (194 passed, including concurrent cynefin work outside this change's scope)
- [x] 3.5 `ruff check` clean on every touched file
- [x] 3.6 Confirm `dm2 config -s llm.model=…` still prints the informational rejection and exits 0, so the guard behaviour is preserved

## 4. Spec

- [x] 4.1 Add the `dm2-no-llm-dependency` capability with requirements covering imports, declared dependencies, user-facing guidance, and configuration defaults
- [x] 4.2 Note that this restores a capability whose spec was declared by `2026-05-04-remove-llm-from-dm2` but never merged into `openspec/specs/`
- [x] 4.3 `openspec validate remove-llm-packaging-residuals` passes, then archive the change
