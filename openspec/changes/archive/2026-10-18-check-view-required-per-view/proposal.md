# Proposal

## Why

`MetamodelConformanceChecker.check_view_required` (rule R5) decides whether a view declares the
associations the metamodel requires of it. It gathered the "already declared" slots from **every**
note in the project, then compared that union against one view's requirements:

```python
present = set()
for fm in notes.values():        # ← every view, not the target view
    for slot in (fm.get("relationships") or {}):
        present.add(slot)
```

So a single view's frontmatter satisfied every other view's required associations. Demonstrated:
declaring all fifteen slots on one unrelated note drove SV-6 and CV-1 from 1 issue to 0.

The defect is latent for a project whose views have no frontmatter at all — which is why it had not
bitten yet. It would surface the moment one view gained frontmatter: R5 would go quiet for everything
and stop being a per-view check.

## What Changes

- `check_view_required` reads only the note belonging to the view under test.
- Note lookup tolerates the vault convention where a note is keyed by its filename stem with the view
  name appended (`OV-5b 作战活动分解`). Separator-delimited matching keeps `OV-2` from matching
  `OV-20`.
- Dead code removed: `ConsistencyChecker._extract_performers` was defined and never called.

## Non-goals

- No severity change: R5 stays a WARNING.
- `views.yaml` and the metamodel indexes are untouched.
- Projects with no frontmatter see the same number of issues (the rule's *meaning* changes, not its
  count).
