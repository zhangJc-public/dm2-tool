# 05-Guidance

## 📌 一句话说明
**治理——遵守什么规则。** 法规（Rule）和标准（Standard）的统一容器。

## 🎯 目录用途
- 存储安全相关的法律法规和国家/行业标准
- Rule: 法律、法规、政策、指令、通知
- Standard: 国际/国家/行业/企业/项目标准
- 已清理 slides/ 污染 ✅

## 📂 结构一览
```
05-Guidance/
├── AGENT.md                        ← 本文件
├── Guidance-Template.md            ← 主模板（已修复 YAML ✅）
├── Rule/
│   ├── Rule-Template.md            ← 法规专用模板
│   ├── 中华人民共和国网络安全法.md
│   ├── 中华人民共和国数据安全法.md
│   ├── 中华人民共和国密码法.md
│   └── 中华人民共和国个人信息保护法.md
└── Standard/
    ├── Standard-Template.md        ← 标准专用模板
    ├── 公共安全行业标准-Template.md
    ├── GB-T-22239-2018-...md       ← 等保基本要求（最大文件 90KB）
    ├── GB-T-22239-2008-...md       ← 旧版等保
    ├── GB-T-25069-2022-...md       ← 术语标准
    ├── 安全管理与控制...md
    └── 管理与控制...md
    ~~slides/~~                     ← ❌ 已删除（Node.js 工程污染）
```

## 🔗 关联目录
| 关联 | 目录 | 关系 |
|------|------|------|
| 约束对象 | 所有数据组 | constrains |
| 合规度量 | `06-Measure` | measuredBy |
| 规则逻辑 | `10-Rules` | Rules 是 Guidance 的形式化特化 |
| 分析 | `../详细分析/DM2-Rules详细分析.md` | 深度理论 |

## 🤖 Agent 协作规则
1. **Rule vs Standard 边界**：Rule = "你必须"（法律强制力）；Standard = "你应该"（合规推荐级）
2. **classification/compliance 字段**：Rule 和 Standard 模板保留了扩展业务字段，创建法规/标准实例时尽量填写完整
3. **大文件警告**：GB-T-22239-2018 有 90KB，编辑时注意性能

## 📊 当前状态
- 实体数量: ~15 个（1 主模板 + 2 子模板 + 4 法规 + 6 标准）
- 最后更新: 2026-04-18（重构修复YAML+删除slides+AGENT）
- 覆盖度: ✅ 较完善（仅次于 Performer）
