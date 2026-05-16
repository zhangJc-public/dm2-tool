## 1. CLI 实现

- [x] 1.1 在 `cli/main.py` 中新增 `dm2 uninstall` 命令，三个 Option：`--self`、`--project`、`--user-config`
- [x] 1.2 实现 `--self` 模式：确认提示 → `subprocess.run([sys.executable, "-m", "pip", "uninstall", "dm2-tool", "-y"])`
- [x] 1.3 实现 `--project` 模式：检测 `.dm2/` 目录 → 确认提示 → `shutil.rmtree`
- [x] 1.4 实现 `--user-config` 模式：检测 `~/.config/dm2/config.yaml` → 确认提示 → `Path.unlink`
- [x] 1.5 无参数时显示帮助信息

## 2. 文档

- [x] 2.1 在 README.md 安装部分补充卸载说明

## 3. 验证

- [x] 3.1 测试 `dm2 uninstall`（无参数）显示帮助
- [x] 3.2 测试 `dm2 uninstall --project` 交互确认流程
- [x] 3.3 测试 `dm2 uninstall --user-config` 交互确认流程
