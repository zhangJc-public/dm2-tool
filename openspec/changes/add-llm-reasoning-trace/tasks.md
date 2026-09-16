## 1. Setup & Scaffolding

- [ ] 1.1 Create `src/dm2/core/pedigree/` module directory with `__init__.py`
- [ ] 1.2 Create `src/dm2/core/pedigree/schema.yaml` documenting the Pedigree structure
- [ ] 1.3 Update `templates/` to include `.dm2/pedigree/` creation in `dm2 init`
- [ ] 1.4 Add `trace.enabled: true` to default `.dm2/config.yaml` template
- [ ] 1.5 Add `pedigree` directory to `.gitignore` template (or document as committed)

## 2. Data Model

- [ ] 2.1 Create `src/dm2/core/pedigree/model.py` with `Pedigree` dataclass and nested types (`Author`, `Source`, `Reasoning`, `DecisionFactor`, `Alternative`, `ModificationRecord`, `ValidationRecord`, `ValidationIssue`)
- [ ] 2.2 Add field validation in Pedigree constructor (required vs optional, type checks, enum constraints for `reliability`, `author.type`)
- [ ] 2.3 Implement `to_yaml()` and `from_yaml()` class methods using `yaml.safe_dump` / `yaml.safe_load`
- [ ] 2.4 Write unit tests in `test/test_pedigree_model.py` covering round-trip, validation, missing fields

## 3. Storage Layer

- [ ] 3.1 Create `src/dm2/core/pedigree/store.py` with `PedigreeStore` class
- [ ] 3.2 Implement `load(view_id)` and `save(pedigree)` with atomic write (temp file + rename)
- [ ] 3.3 Implement `list_all()` returning all view_ids with pedigrees
- [ ] 3.4 Implement `exists(view_id)` and `delete(view_id)` (delete only via admin command, not CLI default)
- [ ] 3.5 Write integration tests in `test/test_pedigree_store.py` with temporary project directory

## 4. Auto-Capture (Fact Layer)

- [ ] 4.1 Create `src/dm2/core/pedigree/recorder.py` with `PedigreeRecorder` class
- [ ] 4.2 Implement event subscription mechanism for `ViewManager` state changes (use simple observer pattern)
- [ ] 4.3 Add event hooks to `dm2/core/views/manager.py` at: view registration, state transitions (pending→in_progress→generated→verified)
- [ ] 4.4 Implement `record_modification(view_id, actor, change_description)` method on PedigreeRecorder
- [ ] 4.5 Modify `dm2/reasoning/consistency.py` to call PedigreeRecorder after validation completes
- [ ] 4.6 Write unit tests verifying state changes produce ModificationRecord entries

## 5. CLI Commands — trace record

- [ ] 5.1 Create `src/dm2/cli/commands/trace.py` with `trace_app` Typer subcommand
- [ ] 5.2 Implement `dm2 trace record <view_id>` with `--summary` and `--reasoning-file` flags
- [ ] 5.3 Implement `--stdin` flag for piping YAML directly
- [ ] 5.4 Implement `dm2 trace show <view_id>` (read-only display of full pedigree)
- [ ] 5.5 Implement `dm2 trace lineage --term <term>` and `--capability <name>` for cross-change queries
- [ ] 5.6 Register `trace_app` in `src/dm2/cli/main.py` as new subcommand
- [ ] 5.7 Write CLI tests in `test/test_cli_trace.py` covering happy path, malformed input, missing pedigree

## 6. CLI Commands — audit

- [ ] 6.1 Create `src/dm2/cli/commands/audit.py` with `audit_app` Typer subcommand
- [ ] 6.2 Implement `dm2 audit <view_id>` with Markdown default output
- [ ] 6.3 Implement `--json` and `--output` flags
- [ ] 6.4 Implement `dm2 audit-report` with project-level aggregation
- [ ] 6.5 Implement `--min-confidence` filter on audit-report
- [ ] 6.6 Implement audit report's "trace gaps" section (views with absent/incomplete pedigrees)
- [ ] 6.7 Register `audit_app` in `src/dm2/cli/main.py`
- [ ] 6.8 Write CLI tests in `test/test_cli_audit.py`

## 7. View Lifecycle Integration

- [ ] 7.1 Extend `.dm2/view-state.yaml` schema to include `pedigree_status` and `pedigree_missing` per view
- [ ] 7.2 Modify `ViewManager` to refuse `verified` transition when pedigree core fields are missing
- [ ] 7.3 Add `--force-pedigree` flag to `dm2 validate` for explicit override
- [ ] 7.4 Update `dm2 view list` to show `pedigree_status` column and `--pedigree-status` filter
- [ ] 7.5 Update `dm2 view list --json` to include `pedigree_status` and `pedigree_missing` fields
- [ ] 7.6 Write tests verifying verified gating and override behavior

## 8. View Frontmatter Pedigree

- [ ] 8.1 Extend `dm2/utils/frontmatter.py` parser to handle `pedigree` block (nested mapping)
- [ ] 8.2 Create helper to write pedigree block to view frontmatter (preserve existing fields)
- [ ] 8.3 Create helper to extract pedigree_id from frontmatter and link to external YAML
- [ ] 8.4 Update InstructionBuilder to include pedigree context when generating view instructions
- [ ] 8.5 Write tests for frontmatter round-trip with pedigree block

## 9. SKILL.md Template Updates

- [ ] 9.1 Update `src/dm2/core/templates/workflows/propose.py` to include Trace Plan section instructions and `dm2 trace record` calls in generated SKILL.md
- [ ] 9.2 Update `src/dm2/core/templates/workflows/apply.py` to require `dm2 trace record` after each view generation
- [ ] 9.3 Add `dm2 audit <view_id>` reference in the SKILL.md output
- [ ] 9.4 Update `src/dm2/core/templates/generator.py` to include pedigree section guidance in the template
- [ ] 9.5 Manually verify generated SKILL.md files contain the new trace requirements (snapshot test)

## 10. Knowledge API Integration

- [ ] 10.1 Extend `dm2/core/knowledge/api.py` `KnowledgeAPI` with `get_pedigree(view_id)`, `list_pedigrees()`, `list_pedigrees(author_type=...)` methods
- [ ] 10.2 Ensure `dm2 knowledge view <view_id> --json` output includes pedigree_summary
- [ ] 10.3 Write tests for new KnowledgeAPI methods

## 11. Migration Support

- [ ] 11.1 Create `src/dm2/core/pedigree/migration.py` with one-time migration helper for existing projects
- [ ] 11.2 Migration: scan existing view files, mark as `pedigree_status: absent` in view-state.yaml
- [ ] 11.3 Add `dm2 trace migrate` command to run the migration
- [ ] 11.4 Add `config.yaml` option `trace.enabled: false` to disable all pedigree writes (escape hatch for legacy projects)
- [ ] 11.5 Write tests for migration correctness

## 12. Testing & Documentation

- [ ] 12.1 Add end-to-end test in `test/test_e2e_pedigree.py` covering: propose → apply → validate → audit full flow
- [ ] 12.2 Add fixture in `test/fixtures/sample-system-with-trace/` (or extend existing) showing a complete trace example
- [ ] 12.3 Update `docs/readme.md` with new `dm2 audit` and `dm2 trace` command documentation
- [ ] 12.4 Update `CLAUDE.md` project structure section to mention `src/dm2/core/pedigree/`
- [ ] 12.5 Add example pedigree YAML in `docs/examples/pedigree-example.yaml`

## 13. Quality Gates

- [ ] 13.1 Run `pytest test/` — all tests pass, including new pedigree tests
- [ ] 13.2 Run `ruff check src/` — no new lint errors
- [ ] 13.3 Verify CLI commands work end-to-end: `dm2 init`, `dm2 change new test`, `dm2 trace record ...`, `dm2 audit ...`, `dm2 audit-report`
- [ ] 13.4 Verify `--force-pedigree` override path works and is logged
- [ ] 13.5 Verify LLM-driven flow works: regenerated SKILL.md contains trace instructions, and a Claude session can successfully complete a propose→apply→audit cycle
