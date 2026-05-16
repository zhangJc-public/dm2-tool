## Context

当前 DM2 没有卸载命令。用户需手动执行 `pip uninstall dm2-tool` 卸载程序，手动 `rm -rf .dm2/` 清理项目。新增 `dm2 uninstall` CLI 命令提供统一入口。

## Goals / Non-Goals

**Goals:**
- 提供 `dm2 uninstall --self` 卸载包本身
- 提供 `dm2 uninstall --project` 清理项目目录
- 提供 `dm2 uninstall --user-config` 清理用户配置
- 所有操作前均需确认

**Non-Goals:**
- 不卸载 pip 依赖（由 pip 自身处理）
- 不清理非当前目录的 `.dm2/` 项目
- 不删除 obsidian vault 或 dm2-reference 中的文件

## Decisions

### Decision 1: 直接调用 pip

`--self` 模式通过 `subprocess` 调用 `pip uninstall`。不用 Python API（`pip` 模块不提供稳定的编程接口）。

```python
import subprocess
subprocess.run([sys.executable, "-m", "pip", "uninstall", "dm2-tool", "-y"])
```

### Decision 2: 三个独立 flag，非子命令

使用 `--self`、`--project`、`--user-config` 三个 Option，而非子命令。理由：Typer 子命令需要额外类定义，三个 flag 更简单直接。

## Risks / Trade-offs

- **[低] 卸载后 dm2 命令不可用**: `--self` 执行后 pip 删除二进制，当前 shell 中的 `dm2` 命令消失。→ 这是预期行为，执行前有确认提示。
