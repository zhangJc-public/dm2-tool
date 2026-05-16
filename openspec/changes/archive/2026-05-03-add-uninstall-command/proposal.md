## Why

当前 DM2 工具没有卸载命令。用户需要手动执行 `pip uninstall dm2-tool` 来卸载程序，手动删除 `.dm2/` 目录来清理项目。新增 `dm2 uninstall` 命令提供一键清理能力，降低使用门槛。

## What Changes

- 新增 `dm2 uninstall` 命令，支持三种卸载模式：
  - `--self`：卸载 DM2 工具本体（调用 `pip uninstall dm2-tool`）
  - `--project`：删除当前目录下的 `.dm2/` 项目（含 config.yaml、所有变更和输出）
  - `--user-config`：删除用户级配置 `~/.config/dm2/config.yaml`
- 卸载前均有确认提示（需用户输入 `y` 确认）
- 不指定选项时展示帮助信息

## Capabilities

### New Capabilities

- `uninstall-command`: `dm2 uninstall` 命令，提供工具卸载、项目清理、用户配置删除三种模式

### Modified Capabilities

<!-- 无 -->

## Impact

- `src/dm2/cli/main.py`：新增 `uninstall` 命令
- `README.md`：安装部分补充卸载说明
- 无其他模块影响
