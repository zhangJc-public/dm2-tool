## Why

The DM2 data group activation pipeline was partially implemented (10 of 17 groups have templates with keywords). Groups 00, 11-16 lack templates entirely, meaning they can never be activated. Additionally, the `dm2 analyze --json` output doesn't fully comply with the `dm2-data-group-activation` spec: it's missing `group_to_views` mapping, `views_completed`, and `view_dependencies` context fields that the AI Agent needs for decision-making.

## What Changes

- **Create 7 missing group templates** (00-foundation, 11-resource-flow, 12-pedigree, 13-information-pedigree, 14-org-structure, 15-reification, 16-information-data) with proper DM2 frontmatter including `keywords` and `related_dm2_views`
- **Review and expand keywords** for existing 10 templates to improve activation detection coverage
- **Add `group_to_views` to `analyze --json`** output — mapping from activated groups to candidate view IDs, so AI Agent can trace which groups drove which views
- **Add `views_completed` and `view_dependencies` to output** — context for AI Agent to filter already-generated views and assess dependency readiness
- **Ensure DataGroupActivator returns all 17 groups** in activation vector, including groups without templates (score 0.0)

## Capabilities

### Modified Capabilities
- `dm2-data-group-activation`: Complete the 17-group template coverage, add `group_to_views`/`views_completed`/`view_dependencies` fields to JSON output contract

### New Capabilities
<!-- None — this is completing an existing capability -->

## Impact

- `dm2-reference/core/groups/` — 7 new template files (00, 11-16)
- `dm2-reference/core/groups/01-10/` — keyword updates (optional)
- `src/dm2/cognitive/view_recommender.py` — Ensure 17-group output; expose group→view mapping in JSON
- `src/dm2/cli/main.py` — Add `views_completed` + `view_dependencies` to analyze --json output
