## 1. Cynefin Auto-Derivation

- [x] 1.1 Add `_derive_cynefin_from_description()` function for keyword-based parameter derivation
- [x] 1.2 Add `--desc` / `-d` option to `cynefin` command in CLI
- [x] 1.3 Support parameter override: explicit CLI flags override auto-derived values

## 2. Generate Command LLM Removal

- [x] 2.1 Rewrite `generate` command to remove all LLM dependencies (create_provider, DoDAFViewGenerator, resolve_config)
- [x] 2.2 Use indexer for view template lookup instead of LLM
- [x] 2.3 Output structured JSON/YAML with view metadata, 6W analysis, data group activation, and AI Agent instructions
- [x] 2.4 Remove `--no-rag` parameter from generate command

## 3. Data Layer Updates

- [x] 3.1 Update `ViewRecommender.recommend()` to accept `raw_description` parameter for data group activation
- [x] 3.2 Add `recommend_from_description()` method for direct text-to-view mapping
- [x] 3.3 Add data_group_activation to JSON output and analysis-state.yaml persistence

## 4. AI Agent Integration

- [x] 4.1 Add 11 template frontmatter files with keywords and related_dm2_views
- [x] 4.2 Create group-to-views.yaml external mapping file
- [x] 4.3 Create dm2-propose-workflow SKILL.md and slash command
