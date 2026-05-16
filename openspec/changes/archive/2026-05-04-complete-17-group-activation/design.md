## Context

The DM2 data group activation pipeline (`DataGroupActivator` + `group-to-views.yaml`) was implemented but only covers 10 of 17 groups. Groups 00, 11-16 lack template files, so `_scan_templates()` never discovers them and they're absent from the `data_group_activation` vector. The `dm2 analyze --json` output also lacks `group_to_views`, `views_completed`, and `view_dependencies` fields that the AI Agent contract specifies.

The 17-group model is a fundamental DM2 distinction — missing 7 groups means the activation vector is incomplete, and the AI Agent gets a partial signal for decision-making.

## Goals / Non-Goals

**Goals:**
- Create 7 missing group template files with proper DM2 frontmatter (keywords + related_dm2_views)
- Ensure `DataGroupActivator.activate()` returns all 17 groups
- Add `group_to_views`, `views_completed`, `view_dependencies` to `analyze --json` output
- Remove `priority` field from `recommended_views` in JSON output (AI Agent decides)

**Non-Goals:**
- No changes to keyword matching algorithm (substring match remains Phase 1)
- No changes to `dm2-propose-workflow` SKILL.md (it already consumes the JSON)
- No keyword weights system (defer to Phase 2 — needs ML/data-driven tuning)
- No changes to groups 01-10 template keywords beyond review/expansion

## Decisions

**Decision 1: 7 new templates follow existing `*-Template.md` structure**

Each new template has: DM2 type/relationships frontmatter + Markdown body. Keywords derived from group descriptions in `group-to-views.yaml` + DM2 domain knowledge. Views from `group-to-views.yaml`'s `group_views` array.

**Decision 2: Abstract groups (00, 12, 15) get domain-appropriate keywords**

Groups 00 (Foundation), 12 (Pedigree), 15 (Reification) map to "All" views. Their keywords target meta-architectural concepts (ontology, abstraction, provenance) rather than concrete system nouns. They activate when users describe architecture at a conceptual/philosophical level.

**Decision 3: DataGroupActivator loads ALL groups from group-to-views.yaml, not just templates**

`_scan_templates()` will also parse `group-to-views.yaml` to discover ALL 17 group IDs. Groups with templates get keyword-based scoring. Groups without templates get 0.0 activation (present in vector but inert). This ensures the activation vector is always 17-dimensional.

**Decision 4: `group_to_views` output merges template and YAML data**

The `analyze --json` `group_to_views` field provides: group_id, name, label, description (from YAML), keywords (from template), matched_keywords (from activation), mapped_views (from YAML). This gives the AI Agent all context for each group in a single field.

**Decision 5: Remove priority sorting, keep `dm2_groups` for context**

The `recommended_views` array becomes unsorted. Individual views keep `dm2_groups` and `relevance_score` for AI Agent context, but no `priority` field. The AI Agent uses `data_group_activation` scores + `group_to_views` mapping + conversation context to determine which views to generate first.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Keywords for new groups may have low activation rates (like existing groups) | Keywords stored in template frontmatter, iterable without code changes |
| 17-group vector may overwhelm simple use cases | AI Agent filters by non-zero activations; zero-score groups are noise-free |
| Removing `priority` from output breaks existing consumers | Check: `dm2-propose-workflow` SKILL.md reads raw activation data, not priority field |
| Abstract groups (00, 12, 15) keywords may be hard to trigger | Accept for Phase 1 — these are meta layers that should only activate for conceptual/system-of-systems discussions |
