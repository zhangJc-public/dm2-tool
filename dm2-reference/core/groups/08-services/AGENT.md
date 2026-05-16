# 08-Services

## 📌 一句话说明
**服务——提供的接口。** Performer 向外部暴露的功能访问点，是 SOA/SRV 视图的核心实体。

## 🎯 目录用途
- 存储服务类型和实例（API、接口、服务端口）
- 从 Performer 中拆出的独立数据组（DM2 v2 区分"执行者"与"接口"）
- 管理 ServicePort（服务端口）子类型

## 📂 结构一览
```
08-Services/
├── AGENT.md                  ← 本文件
├── Services-Template.md      ← 操作模板
└── ServicePort/              ← （待补充）服务端口类型
```

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 提供者 | `01-Performer` | providesService / hasPort |
| 访问者 | `01-Performer`, `04-Resource` | accessedVia |
| 资源 | `04-Resource` | 服务操作的资源对象 |
| 分析 | `../详细分析/DM2-Services详细分析.md` | 深度理论 |

## 🤖 Agent 协作规则
1. **vs Performer 的边界**：System 是"执行主体"，Service 是"访问接口"。一个 System 可以提供多个 Service
2. **ServicePort 是关键子概念**：每个 Service 由多个 Port 组成（输入/输出/异常处理）

## 📊 当前状态
- 实体数量: 1 个（仅模板，待创建）
- 最后更新: 2026-04-18（重构创建）
- 覆盖度: ⚠️ 新建目录（模板基于详细分析创建中）
