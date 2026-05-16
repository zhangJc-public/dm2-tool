## Context

当前视图依赖数据存在两处独立维护：
1. `dm2-reference/core/views.yaml` — dependencies/downstream/priority 字段
2. `src/dm2/cognitive/view_recommender.py:_check_path_completeness()` — 31 个硬编码 `(target, required)` 元组

两处数据已有 5 处不一致（硬编码比 YAML 多了正确的传递依赖）。此外 views.yaml 本身也有 15 处缺失和 3 处错误（见 `VIEW-DEPENDENCY-RESEARCH-V2.md` §六）。任何依赖变更都需同时修改两处，且无自动化验证。

## Goals / Non-Goals

**Goals:**
- 确立 views.yaml 为视图依赖关系的唯一数据源
- `_check_path_completeness()` 改用 views.yaml 的传递闭包自动推导
- downstream 从 dependencies 反向自动推导
- `load_all()` 中添加 DAG 环检测
- views.yaml 补全所有缺失的依赖（基于 V2 研究）

**Non-Goals:**
- 不修改 `priority` 字段（属于独立决策）
- 不重构 `ArtifactGraph`（已按 dependencies 工作，无需变动）
- 不修改 `generate_with_derivatives()` 的级联逻辑
- 不删除 `DoDAFViewGenerator`（保留兼容）

## Decisions

### 决策 1：传递闭包替换硬编码

**方案**: `_check_path_completeness()` 使用 DFS 递归遍历 views.yaml 的 `dependencies` 字段，收集所有传递依赖，然后计算缺失集。

**替代方案**: 保留硬编码但添加同步脚本。但这是治标不治本——只要两个数据源存在，就会继续漂移。

**实现**:
```python
def _check_path_completeness(self, view_ids: set[str]) -> set[str]:
    deps = self._get_dependencies()  # 来自 views.yaml
    
    def transitive_deps(vid, visited=None):
        if visited is None:
            visited = set()
        if vid in visited:
            return set()
        visited.add(vid)
        result = set()
        for dep in deps.get(vid, []):
            result.add(dep)
            result.update(transitive_deps(dep, visited))
        return result
    
    all_needed = set()
    for vid in view_ids:
        all_needed.update(transitive_deps(vid))
    
    return all_needed - view_ids
```

**理由**: 
- 48 行 → 15 行
- 自动适应 views.yaml 的任何变更
- 自动发现新视图的依赖
- visited set 防止循环依赖导致的无限递归

### 决策 2：downstream 自动推导

**方案**: 在 `DM2KnowledgeIndexer._load_view_templates()` 中，加载 views.yaml 后，从 dependencies 反向构建 downstream：
```python
# 自动推导 downstream
for vid, template in self._view_templates.items():
    if not template.downstream:
        template.downstream = []
    for dep in template.dependencies:
        if dep in self._view_templates:
            if vid not in self._view_templates[dep].downstream:
                self._view_templates[dep].downstream.append(vid)
```

**理由**: 避免 views.yaml 中手动维护 downstream 字段的不一致性。YAML 中已有的 downstream 优先（允许显式覆盖），缺失的自动补全。

### 决策 3：DAG 环检测

**方案**: 在 `load_all()` 末尾，使用 Kahn 算法检测环：
```python
# 环检测
in_degree = {vid: len(t.dependencies) for vid, t in self._view_templates.items()}
# ... Kahn's algorithm ...
if len(order) != len(self._view_templates):
    missing = set(self._view_templates.keys()) - set(order)
    raise ValueError(f"Circular dependency detected involving: {missing}")
```

**理由**: 当前任何地方都不做环检测，Kahn 算法静默丢弃循环节点，DFS 无限递归。加载时检测是最早的防御点。

## Risks / Trade-offs

- [风险] 传递闭包可能引入"过度推荐" — 某个深层依赖不一定必须与推荐视图一起生成 → 当前硬编码也在做相同的事（甚至更激进），传递闭包是更保守的等价物
- [风险] downstream 自动推导可能与 YAML 中显式的 downstream 冲突 → YAML 中已有的 downstream 优先级更高（不覆盖）
- [风险] views.yaml 依赖修复后，ArtifactGraph 的拓扑排序输出顺序会变化 → 这是预期行为，修复后的排序更正确
