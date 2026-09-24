# Tasks

## 1. 设计前置研究

- [x] 1.1 定位 `get_reference_path()` 的全部 7 处调用点（跨 kernel/cognitive/reasoning/cli），确认调用方都只把结果用于读取/glob，无分支依赖「路径为空」
- [x] 1.2 确认 CLI **没有**中央异常处理：抛出会变成 traceback，反而违反 `cli-json-contract`
- [x] 1.3 核实 `-j` 在整个 CLI 中只用于 JSON 标志（`grep '"-j"' src/` 全部命中 `json_flag`），使 argv 判定 JSON 模式成立
- [x] 1.4 发现第二处同类静默解析：`_load_concerns()` 在 `_get_concerns_path()` 返回 `None` 时给出 `[]`——正是 D10 证据里 `concern list` 输出空的原因

## 2. 严格解析

- [x] 2.1 `src/dm2/utils/paths.py`：新增 `KnowledgeBaseNotFound(RuntimeError)`，说明「知识库缺失」与「知识库为空」是两件事
- [x] 2.2 `get_reference_path()`：两条候选都不存在时**抛异常**，不再 `return base`；错误信息列出两处已检查路径与修复方式
- [x] 2.3 `src/dm2/cli/commands/concern.py`：`_get_concerns_path()` 改为返回 `Path` 并在缺失时抛同一异常；`_load_concerns()` 相应简化

## 3. 中央报错

- [x] 3.1 `_json_mode_requested()`：从 `sys.argv` 判定 JSON 模式，注释写明该前提（`-j` 的唯一性）及失准时的处理
- [x] 3.2 `_invoke_app()`：只捕获 `KnowledgeBaseNotFound`（不捕获基类），JSON 模式输出 `KB_NOT_FOUND` 信封，人类模式输出中文提示，均以非零码退出
- [x] 3.3 `DM2_DEBUG` 置位时重新抛出，保留开发者所需的 traceback
- [x] 3.4 **两个入口点** `main()`（console script）与 `if __name__ == "__main__"`（`-m` 调用）都指向 `_invoke_app()`——测试正走 `-m` 路径，只在 `main()` 里捕获会漏

## 4. 守护测试

- [x] 4.1 新增 `test/test_missing_knowledge_base.py`：通过 monkeypatch `__file__` + chdir 制造「两条候选都不存在」，不触碰真实仓库
- [x] 4.2 解析层：抛异常、错误信息含两处候选与修复方式、`concerns.yaml` 同样抛异常
- [x] 4.3 **过严保护**：正常检出路径仍能解析到 `views.yaml`（防止把函数改得过度严格）
- [x] 4.4 CLI 层：`--json` 与 `-j` 两种写法都得到 `KB_NOT_FOUND` 信封且 exit 1；人类模式输出「错误: …」且无 `Traceback`
- [x] 4.5 `DM2_DEBUG=1` 时异常向上传播而非被转成消息
- [x] 4.6 守护有效性验证：临时把 `get_reference_path()` 还原为旧的 `return base`，6/8 用例**如预期失败**；恢复后全过

## 5. 验收

- [x] 5.1 `pytest test/` 全绿（228 → 236）
- [x] 5.2 `ruff check src/ test/` 零报错
- [x] 5.3 `openspec validate --all --strict` 通过
- [x] 5.4 editable 安装（本仓库唯一支持形态）下行为无变化：`knowledge stats` 仍为 279 术语 / 52 视图
- [x] 5.5 归档本变更，并把 `docs/foundation.md` 的 D10 拆分标注为「运行时半边已修，分发半边仍待决策」
