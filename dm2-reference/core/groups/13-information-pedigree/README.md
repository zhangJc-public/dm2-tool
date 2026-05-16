# Information Pedigree（信息血缘）

> 📄 **完整分析** → [[../详细分析/DM2-InformationPedigree详细分析]]

InformationPedigree 是 Pedigree 在**信息领域的特化**，聚焦 Sign/Rep/Data 三层表示的血缘追溯。

## 与通用 Pedigree 的区别

| 维度 | Pedigree (通用) | InformationPedigree |
|------|-----------------|---------------------|
| 追溯对象 | 所有实体 | 仅信息和表示资源 |
| 特化节点 | 无 | Sign / Representation / Information / Guidance |
| 典型场景 | "这个系统哪来的" | "这份文档基于哪个版本的资料" |

## 三层表示体系的血缘

```
Sign（标记） ←representedBy← Representation（表示） ←representedBy← Data（数据内容）
   ↓ pedigree                    ↓ pedigree                      ↓ pedigree
  来源?符号编码方式?             来源?文件格式?                   来源?语义定义?
```

## 最实用的场景

**架构文档版本追溯矩阵**：
| 文档名 | 版本 | 基于 | 变更日期 | 置信度 |
|--------|------|------|---------|--------|
| SV-1 | v2.1 | CV-2 v1.0 + 现场调研 | 2026-04-15 | high |

---
*基于 DM2-InformationPedigree详细分析.md | 2026-04-18*
