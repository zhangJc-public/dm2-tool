## 1. Delta specs (11 requirements / 5 specs)

- [x] 1.1 `dm2-architecture-boundaries`：`dm2 packages depend only downward`（503 → 333 字符），层表移入新场景
- [x] 1.2 `dm2-cynefin-auto-derive`：4 条（707/544/714/517 → 474/433/476/441），细节移入场景
- [x] 1.3 `dm2-cynefin-model`：4 条（936/1227/624/561 → 461/487/486/290），维度表/权重带/层级表移入新场景
- [x] 1.4 `view-metadata-schema`：`View definition includes pedigree metadata`（600 → 262），字段清单移入新场景
- [x] 1.5 `view-provenance`：`Pedigree data model`（1550 → 281），字段清单移入新场景

## 2. Scenario fidelity

- [x] 2.1 各 spec 的既有场景由脚本从现行 spec **原样搬运**（标题与正文不变）
- [x] 2.2 被移出的表格/清单以**新增场景**承载，THEN 用 SHALL 措辞
- [x] 2.3 `openspec validate <change> --strict` 通过（MODIFIED 必须保留全部既有场景，由校验器强制）

## 3. CI version alignment

- [x] 3.1 `.github/workflows/test.yml` 的 openspec 版本 `1.13.1` → `1.14.1`
- [x] 3.2 说明本地与 CI 同口径（注释或 CLAUDE.md）

## 4. Semantic review

- [x] 4.1 逐条对照：11 条 requirement 的 SHALL 陈述在压缩后仍可追溯（正文或场景）。机械核验：11 条关键规范词全部在位；SHALL 计数 9 条持平或增加，2 条下降——`Disorder fallback` 是三条 `SHALL NOT` 合并为一条并列（语义等价，接受），`Versioned context-rule lexicon` 是 `excluded` 丢掉 SHALL 动词（**已修正补回**）
- [x] 4.2 `dm2-cynefin-model`：五维定义、硬触发三规则、加权带边界、Disorder 两个分支、映射表逐项在位
- [x] 4.3 `dm2-cynefin-auto-derive`：证据包五要素、heuristic 标签、极性安全、共享 deriver、v2 上下文规则、rubric/adjudication 逐项在位
- [x] 4.4 `view-provenance` / `view-metadata-schema`：字段清单逐项在位（含必填/可选与枚举）
- [x] 4.5 `dm2-architecture-boundaries`：五级顺序表在位

## 5. Documentation

- [x] 5.1 `docs/foundation.md`：D11 移入「已修复」并写明处置（改写 11 条 + CI 升版）；基线行恢复「38 通过 / 0 失败」
- [x] 5.2 `CLAUDE.md`：关口说明补充「requirement 正文 ≤500 字符」与 openspec 版本口径
- [x] 5.3 `CHANGELOG.md`：记录本次规范文本重构与 CI 版本对齐

## 6. Quality gates & archive

- [x] 6.1 `openspec validate comply-with-openspec-1-14-style --strict` 通过
- [x] 6.2 `pytest test/` 与 `ruff check src/ test/ scripts/` 保持全绿（本变更不动代码，用于确认没有意外副作用）
- [x] 6.3 归档后 `openspec validate --all --strict` → **38 通过 / 0 失败**
- [ ] 6.4 `openspec archive comply-with-openspec-1-14-style` 并复核基线
