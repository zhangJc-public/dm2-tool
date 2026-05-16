## Context

当前 `dm2-reference/` 是一个扁平混合目录，所有内容放在一起：

```
dm2-reference/                    # 9.3 MB, 257 files
├── _dm2_v202_extract.json        # 核心：277 术语定义 (~100 KB)
├── views.yaml                    # 核心：52 视图定义 (~30 KB)
├── DM2-WG-Page*.png              # 2 张参考图
├── 00-基础模式/ ~ 16-InformationAndData/  # 17 数据组模板 (~400 KB)
├── 总览文档/                      # DM2 中文翻译、治理方案 (~70 KB)
├── 详细分析/                      # 8.3 MB！含 ~100 张 PNG (7 MB)
│   ├── DM2-*详细分析.md           # 20 篇分析报告
│   ├── 视图全集/                  # 52 个视图描述 + 方法论文档
│   └── 视图全集/images/          # 7 MB PDF 截图
├── 研究/                          # 5 篇研究文档 (~170 KB)
├── 01-Performer/Organization/...  # 具体项目实例（乙方/甲方/厂商）
└── 05-Guidance/Standard/...       # 具体法律条文（等保、网络安全法等）
```

当前代码中 `DM2KnowledgeIndexer` 从 `REFERENCE_PATH` 加载全部文件。打包时如果 include 整个目录，会打包 9.3 MB；如果 exclude 部分，需要改动加载逻辑。

## Goals / Non-Goals

**Goals:**
- 将 dm2-reference 重组为三层结构：`core/`（打包）、`reference/`（可选）、`examples/`（不打包）
- 剔除 7 MB PNG 截图（从 PDF 提取，AI 不使用）
- 删除 .DS_Store 和重复文件
- 移除项目示例数据（硬编码的防火墙型号、具体法律条文）
- 更新 Indexer 加载路径以匹配新结构
- 更新 pyproject.toml 的 package_data 配置

**Non-Goals:**
- 不修改 JSON/YAML 数据结构（术语格式、视图字段不变）
- 不删除任何 DM2 标准定义内容
- 不修改 17 数据组的模板内容
- 不修改 Knowledge API 的查询接口签名
- 不引入新的依赖

## Decisions

### Decision 1: 三层目录结构

```
dm2-reference/
├── core/                          ← pip 打包（~700 KB）
│   ├── _dm2_v202_extract.json
│   ├── views.yaml
│   └── groups/                    ← 17 数据组（重命名，去数字前缀）
│       ├── 00-foundation/
│       ├── 01-performer/
│       ├── 02-activity/
│       ├── 03-capability/
│       ├── 04-resource/
│       ├── 05-guidance/
│       ├── 06-measure/
│       ├── 07-location/
│       ├── 08-services/
│       ├── 09-project/
│       ├── 10-rules/
│       ├── 11-resource-flow/
│       ├── 12-pedigree/
│       ├── 13-information-pedigree/
│       ├── 14-org-structure/
│       ├── 15-reification/
│       └── 16-information-data/
├── reference/                     ← 可选下载（~1.5 MB）
│   ├── overview/                  ← 原 总览文档/
│   ├── analysis/                  ← 原 详细分析/（不含 images/）
│   └── research/                  ← 原 研究/
└── examples/                      ← 不打包
    ├── performer-instances/       ← 原 01-Performer 下的具体实例
    └── guidance-standards/        ← 原 05-Guidance 下的具体法律
```

**理由**: 三层分离让打包配置精确——`core/` 是必须的 DM2 标准数据（包体积从 9.3 MB → ~700 KB），`reference/` 是辅助阅读材料（可放在 GitHub Releases 或文档站），`examples/` 是项目特定的不应打包进通用工具。

### Decision 2: 删除截图而非保留

7 MB PNG 截图来自 DoDAF PDF 的视图示例（如 OV-1-p142.png）。这些图片对 AI Agent 无实际价值——AI 通过 `views.yaml` 中的结构化模板理解视图格式，不需要看 PDF 截图。

**替代方案被否决**: 压缩 PNG → 仍会占 2-3 MB，且维护负担大于价值。

### Decision 3: 项目示例数据移出 core/

具体防火墙型号（`天清汉马-USG-NF-12600GP.md`）、中国法律条文（`网络安全法.md`）等硬编码实例不应打包进通用工具。移至 `examples/` 供需要时参考。

### Decision 4: 保留 AGENT.md + *-Template.md

每个数据组的 `AGENT.md`（AI Agent 上下文说明）和 `*-Template.md`（Obsidian 模板）是 Knowledge API 的重要输入，保留在 core/ 中。它们是 DM2 数据组定义的组成部分。

### Decision 5: Indexer 路径向后兼容

在 `DM2KnowledgeIndexer` 中自动检测新旧目录结构：

```python
def _resolve_core_path(self) -> Path:
    new_path = REFERENCE_PATH / "core"
    if new_path.exists():
        return new_path
    return REFERENCE_PATH  # fallback to old flat structure
```

**理由**: 开发环境中新旧结构都能工作，避免在治理期间 blocking 其他开发。

## Risks / Trade-offs

- **[低] Indexer 加载失败**: 文件移动后路径硬编码可能遗漏。→ 逐文件 grep 所有 `dm2-reference/` 引用，统一更新。
- **[低] 示例数据丢失**: 用户可能依赖硬编码的防火墙实例做参考。→ 保留在 `examples/` 中，README 注明路径。
- **[低] AGENT.md 内容引用失效**: 部分 AGENT.md 可能引用旧路径。→ 治理时检查并修复交叉引用。

## Migration Plan

1. 创建新目录结构（core/reference/examples）
2. 移动/复制文件到新位置
3. 删除 .DS_Store、重复文件、images/
4. 更新 `src/dm2/kernel/indexer.py` 的路径常量
5. 更新 `pyproject.toml` 的 `package-data`
6. 运行 `dm2 status` 验证知识库加载正常
7. 删除旧目录结构
