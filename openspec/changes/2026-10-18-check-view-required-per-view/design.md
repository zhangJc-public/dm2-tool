# Design

## Why per-view, not global

The rule asks a per-view question — "does *this view* declare its necessary associations?" — and its
output names one view (`视图 X 缺少 N 个标准必要关联`). Aggregating the evidence across the whole
project answers a different question ("does the project mention these slots anywhere?"), and answers
it identically for every view. That is why the leak was invisible until frontmatter appeared
somewhere.

## Note lookup

```python
def _note_for_view(view_id, notes):
    if view_id in notes:
        return notes[view_id]
    for key, fm in notes.items():
        if key.startswith((f"{view_id} ", f"{view_id}-", f"{view_id}_")):
            return fm
    return {}
```

`dm2 validate` keys view notes by view id, so the exact match covers the normal path. Vault notes are
keyed by filename stem, which may carry the view name after the id — hence the prefix match. The
separators are what keep `OV-2` from matching `OV-20`; a bare `startswith(view_id)` would be wrong.

Returning `{}` for "no note" keeps the existing behaviour: every necessary association is reported
missing, which is what a project without frontmatter should see.

## Consequences

- The check is now falsifiable per view: adding frontmatter to one view fixes that view only.
- Projects without frontmatter are unaffected in count (verified on the 26-view reference project:
  still 17 warnings).
- Three existing tests were keyed by arbitrary note names (`"act"`), encoding the aggregate
  behaviour; they now use view ids, and a regression test pins the leak closed.
