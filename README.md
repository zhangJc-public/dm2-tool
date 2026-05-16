# dm2-tool

**DoDAF Meta Model 2.02 系统工程辅助工具**

基于 DoDAF 元模型 2.02 的架构分析工具，帮助系统工程团队进行 6W 分析、DoDAF 视图生成和知识管理。

[![Tests](https://github.com/zhangJc-public/dm2-tool/actions/workflows/test.yml/badge.svg)](https://github.com/zhangJc-public/dm2-tool/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 安装

```bash
pip install -e .                # 基础安装
pip install -e ".[dev]"         # 含测试和 lint
```

## 快速开始

```bash
dm2 init my-project             # 创建项目
dm2 analyze -d "系统描述..."     # 6W 分析 + 视图推荐
dm2 cynefin                      # 复杂度评估
dm2 generate OV-1 -d "..."      # 生成 DoDAF 视图
dm2 validate --all              # 一致性校验
```

## 核心功能

| 功能 | 说明 |
|------|------|
| **6W 分析** | What/How/Where/Who/When/Why 架构分析 |
| **Cynefin 评估** | 复杂度域判断，指导方法论选择 |
| **视图生成** | 支持 52 个 DoDAF 视图（OV/SV/SvcV/CV/DIV/PV/AV/StdV） |
| **一致性校验** | 跨视图引用和逻辑一致性检查 |
| **AI Agent 接口** | JSON 输出，兼容 Claude Code 等 Agent 工具 |

## AI Agent 工作流

```
/dm2:explore  →  /dm2:propose  →  /dm2:apply  →  /dm2:verify  →  /dm2:archive
  (只读探索)      (分析规划)        (任务实施)       (一致性检查)      (归档)
```

`dm2 init` 自动生成 10 个 Claude Code 斜杠命令，从 Python 模板动态生成 `.claude/skills/` 和 `.claude/commands/`。

## 可用视图

| 视点 | 数量 | 视图 |
|------|------|------|
| 作战 (OV) | 9 | OV-1 ~ OV-6c |
| 系统 (SV) | 14 | SV-1 ~ SV-10c |
| 服务 (SvcV) | 13 | SvcV-1 ~ SvcV-10c |
| 能力 (CV) | 7 | CV-1 ~ CV-7 |
| 数据 (DIV) | 3 | DIV-1 ~ DIV-3 |
| 项目 (PV) | 3 | PV-1 ~ PV-3 |
| 全视点 (AV) | 2 | AV-1, AV-2 |
| 标准 (StdV) | 2 | StdV-1, StdV-2 |

共 52 个视图。

## 配置

```bash
dm2 config                          # 查看配置
dm2 config -s llm.model=claude-opus-4-7  # 设置 LLM
```

环境变量：`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`

## 命令参考

```bash
dm2 --help                          # 所有命令
dm2 version                         # 版本信息
dm2 knowledge search <q>            # 搜索 DM2 术语
dm2 knowledge views                  # 列出所有视图
dm2 change new <name>               # 创建架构变更
dm2 run -d "..."                    # 6 步融合流程
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE)