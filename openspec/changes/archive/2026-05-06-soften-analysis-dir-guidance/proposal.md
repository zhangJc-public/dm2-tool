## Why

`fix-dm2-output-path` 中 propose 模板强制要求 agent 将 CLI 的 cynefin/analyze 原始 JSON 输出写入 `analysis/`。但实测发现 CLI 输出基于简单关键词匹配，信息量极薄（对"省级安全边界平台"只命中一个关键词、一个数据组），审计价值为零。有价值的是 agent 自身深层分析生成的丰富版分析文档。模板应引导 agent 写自己的分析，而非 dump CLI 原始输出。

## What Changes

- **`propose.py` 模板**: 步骤 3/4 中的 "Save the Cynefin/analysis results to …" 改为软指引 "可选的审计文档"
- `analysis/` 目录保留（已有 change new 自动创建），用途从"强制写入"改为"agent 按需写入审计文档"

## Capabilities

### Modified Capabilities
<!-- None — template wording change only -->
