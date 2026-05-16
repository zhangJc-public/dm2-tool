## Why

views.yaml 中的视图依赖数据不完整（15处缺失、3处错误、downstream未补全），且 `view_recommender.py` 中的 `_check_path_completeness()` 以 31 个硬编码元组重复维护了一份独立依赖规则，两处数据已有 5 处不一致。需将 views.yaml 确立为唯一数据源，消除硬编码。

## What Changes

- views.yaml: 补全 15 处缺失的 dependencies（CV-3→+CV-1+PV-2, CV-5→+CV-2+OV-4+PV-2+SV-1+SvcV-1, CV-6→OV-5a→OV-5b, 等）
- views.yaml: 修正 3 处错误的 dependencies（SV-2: SV-4→SV-1+StdV-1, CV-6: OV-5a→OV-5b, DIV-1: 0→OV-2+OV-5b+OV-6a）
- views.yaml: 为出度≥2 的视图补全 downstream 字段（从 dependencies 反向推导）
- `view_recommender.py`: 删除 `_check_path_completeness()` 中的 31 个硬编码元组，替换为基于 views.yaml dependencies 的传递闭包递归推导
- `indexer.py`: `load_all()` 中添加 DAG 环检测，防止循环依赖导致排序死循环

## Capabilities

### New Capabilities

- `dm2-view-dependency-graph`: 视图依赖关系以 views.yaml 为单一数据源，所有依赖查询（拓扑排序、路径完整性、就绪检查）均从此推导，下游字段自动生成

### Modified Capabilities

- `dm2-data-group-activation`: ViewRecommender 的路径完整性检查从硬编码改为 YAML 驱动，影响 `recommend()` 和 `verify_and_supplement_views()` 的输出

## Impact

- `dm2-reference/core/views.yaml`: 52 个视图的 dependencies/downstream 字段全部更新
- `src/dm2/cognitive/view_recommender.py`: `_check_path_completeness()` 重写（48行→15行）
- `src/dm2/kernel/indexer.py`: `load_all()` 新增环检测逻辑
- `src/dm2/core/artifacts/graph.py`: 受 views.yaml 依赖变更影响，拓扑排序输出顺序变化（无代码变更）
- `src/dm2/core/agent/instructions.py`: AI Agent 指令中的依赖 artifact 列表自动更新（无代码变更）
