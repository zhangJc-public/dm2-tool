## 1. 移动 config_manager

- [x] 1.1 新建 `src/dm2/config/` 包（含 `__init__.py`）
- [x] 1.2 移动 `src/dm2/llm/config_manager.py` → `src/dm2/config/manager.py`，移除 DEFAULT 中的 `llm:` 段
- [x] 1.3 更新 `src/dm2/cli/main.py` 中所有 `from dm2.llm.config_manager import ...` 为 `from dm2.config.manager import ...`

## 2. 移动 RAG 引擎

- [x] 2.1 移动 `src/dm2/llm/rag.py` → `src/dm2/kernel/rag.py`
- [x] 2.2 更新 `src/dm2/engine/view_generator.py` 中的 import 路径
- [x] 2.3 更新 `src/dm2/engine/pipeline/step3_data_requirements.py` 中的 import 路径

## 3. 删除 LLM provider/client/prompts

- [x] 3.1 删除 `src/dm2/llm/client.py`
- [x] 3.2 删除 `src/dm2/llm/provider.py`
- [x] 3.3 删除 `src/dm2/llm/prompts.py`
- [x] 3.4 删除 `src/dm2/llm/__init__.py`（如果为空）
- [x] 3.5 删除 `src/dm2/llm/` 目录（如果已空）

## 4. 删除 DoDAFViewGenerator

- [x] 4.1 从 `src/dm2/engine/view_generator.py` 中删除 `DoDAFViewGenerator` 类（约 370 行）
- [x] 4.2 从文件中删除 `DoDAFViewGenerator` 不再需要的 import（ClaudeClient, prompts 等）
- [x] 4.3 删除 `__main__` 测试块中对 `DoDAFViewGenerator` 的引用

## 5. 清理 CLI

- [x] 5.1 移除 `analyze` 命令的 `--llm` 标志
- [x] 5.2 移除 `analyze --llm` 对应的代码路径（create_provider + verify_and_supplement_views）
- [x] 5.3 `dm2 config -s llm.*` 操作时提示 LLM 配置已由 AI Agent 管理

## 6. 清理 view_recommender

- [x] 6.1 移除 `verify_and_supplement_views()` 中的 LLM 分支（保留路径完整性检查）
- [x] 6.2 删除 `_supplement_views_by_llm()` 方法
- [x] 6.3 删除 `_parse_llm_view_supplement()` 方法

## 7. 清理残留 import

- [x] 7.1 `step6_documentation.py` 移除 `DoDAFViewGenerator` 的 import（未实际使用）
- [x] 7.2 全项目搜索确认无残留 `from dm2.llm` import

## 8. 验证

- [x] 8.1 `dm2 version` 正常
- [x] 8.2 `dm2 generate AV-1 -d "test"` 正常
- [x] 8.3 `dm2 analyze -d "test"` 正常（无 --llm 标志）
- [x] 8.4 `dm2 knowledge stats` 正常
- [x] 8.5 `dm2 instructions view/OV-1 -d "test" --json` 正常
- [x] 8.6 `dm2 run --progress` 正常
- [x] 8.7 `dm2 config` 正常（无 llm 段）
- [x] 8.8 确认 `src/dm2/` 下无 `anthropic` 或 `openai` import
