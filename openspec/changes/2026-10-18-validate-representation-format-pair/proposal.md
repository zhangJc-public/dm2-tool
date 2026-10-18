# Proposal

## Why

Stage 1 made `format` a first-class axis, but validation still checked only Mermaid evidence against
the declared `representation`. That leaves the new axis unenforced: a view declared as `svg` may
contain inline Mermaid, a view declared `xlsx` may reference nothing at all, and both pass.

Worse, the old check could not see the carrier the project actually chose, so it validated a
different question than the one the configuration answers.

## What Changes

**A · the checker resolves the format first**

`RepresentationChecker` now resolves each view's format through the same
`kernel.formats.resolve_view_format` the instruction builder uses, so validation and generation agree
on what a view is supposed to be.

**B · evidence is checked per carrier**

| format | accepted evidence |
|---|---|
| `markdown` | no Mermaid block (an illustration reference is fine) |
| `mermaid` | a Mermaid block whose type matches the representation |
| `svg` / `png` / `html` / `xlsx` / `csv` / `mp4` | a reference to an artefact with that extension |

Declaring `mermaid` while shipping only a figure is a mismatch, and so is the reverse — the declared
carrier and the delivered carrier must be the same thing.

**C · one resolver, two callers**

`resolve_view_format`, `MERMAID_TYPE_BY_REPRESENTATION` and `ARTEFACT_EXTENSIONS` move into
`dm2.kernel.formats`; `instructions.py` reuses them instead of holding its own copy.

## Non-goals

- No severity change: still WARNING by default, ERROR under `consistency.strict_mode`.
- No change to `views.yaml` or to the format taxonomy itself.
- Dropping the legacy config keys remains stage 3.
