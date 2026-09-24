# Report a missing knowledge base instead of answering empty

## Why

The runtime knowledge base is located by walking up from `src/dm2/` (`paths.py:24`). When neither the project-local copy nor the packaged copy exists — which is exactly the case for any non-editable install, since `dm2-reference/` is not packaged — `get_reference_path()` **returns a path that does not exist** instead of failing. The indexer then globs nothing and the CLI reports an empty but successful result.

Measured in an isolated venv with a plain `pip install .`:

```
dm2 version          → dm2-tool v0.1.0        exit 0
dm2 knowledge stats  → 术语 0 / 概念 0 / 视图 0   exit 0
dm2 concern list     → 未找到匹配的关切模板。      exit 0
```

`_get_concerns_path()` has the same shape: it returns `None` and `_load_concerns()` turns that into `[]`. A silent empty answer is worse than a loud failure: a user or an agent concludes the knowledge base *is* empty rather than that the tool cannot find it.

## What Changes

- **`get_reference_path()` fails loudly**: raise a dedicated `KnowledgeBaseNotFound` when no candidate exists, instead of returning a nonexistent path.
- **`concerns.yaml` resolution fails loudly** too — same defect, same asset class.
- **One central reporter**: the process entry points catch `KnowledgeBaseNotFound` and emit a `KB_NOT_FOUND` envelope in JSON mode, or a clear Chinese message in human mode, exiting non-zero. The catch is deliberately central rather than per-command: D3 was caused by per-command guard copies being forgotten, so this precondition gets exactly one implementation.
- **Guard tests**: resolution raises when nothing is found, and the CLI turns that into a `KB_NOT_FOUND` envelope (plus the human-mode message).

## Capabilities

### New Capabilities
<!-- 无：本变更补的是既有「运行时加载派生索引」要求的失败路径。 -->

### Modified Capabilities

- `dm2-metamodel-knowledge`: the "Runtime loads derived indexes" requirement gains a companion requirement that an unresolvable knowledge base is a reported failure, never an empty success.

## Impact

- **Code**: `src/dm2/utils/paths.py`（新异常 + 严格解析）、`src/dm2/cli/commands/concern.py`（严格解析）、`src/dm2/cli/main.py`（中央报错与两个入口点）。
- **行为变化**：知识库不可解析时，从「空结果 + exit 0」变为「`KB_NOT_FOUND` + exit 1」。**在 editable 安装（本仓库唯一支持的形态）下无任何变化**——两处候选都存在。
- **不改变**：editable / 源码检出下的正常路径；不引入打包布局变更（D10 的分发问题仍单列，不在本次范围）。
- **测试**：新增守护用例，套件 228 → 更多。
- **错误码**：`KB_NOT_FOUND` 遵守 `cli-json-contract` 的大写蛇形约定。
