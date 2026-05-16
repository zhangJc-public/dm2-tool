## 1. Core implementation

- [x] 1.1 Update `get_reference_path()` in `paths.py` to check project-local `.dm2/reference/` first, fall back to package path
- [x] 1.2 Update `dm2 init` in `main.py` to copy `dm2-reference/core/` (views.yaml, _dm2_v202_extract.json, groups/) and `group-to-views.yaml` into `.dm2/reference/`
- [x] 1.3 Fix hardcoded path in `instructions` command to use `get_reference_path()` instead of `Path(__file__).parent.parent.parent.parent / "dm2-reference"`
- [x] 1.4 Add `.dm2/reference/` to the init output message

## 2. Documentation

- [x] 2.1 Update `README.md` project structure diagram to include `.dm2/reference/` and description
- [x] 2.2 Update `README.md` "内置知识库" section to reflect project-local availability
- [x] 2.3 Update `CLAUDE.md` project mode section to document `.dm2/reference/` as part of project initialization
