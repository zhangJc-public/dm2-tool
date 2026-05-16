## 1. Pipeline 基础设施

- [x] 1.1 创建 `src/dm2/engine/pipeline/` 包目录结构和 `__init__.py`
- [x] 1.2 实现 `state_manager.py`：读写 `.dm2/state.yaml`，支持 step 状态 CRUD
- [x] 1.3 实现 `.dm2/steps/` 目录初始化逻辑（项目 init 时创建或 run 时按需创建）

## 2. Step 1+2：意图澄清 + 范围界定

- [x] 2.1 实现 `step1_intent_scope.py`：接收用户描述，生成反向质问（预定义模板，基于 6W 维度）
- [x] 2.2 复用 `cynefin_analyzer.py`：对澄清后的意图执行 Cynefin 复杂度判定
- [x] 2.3 实现上下文预算估算函数：基于选定的 DM2 数据组数量估算 token 消耗
- [x] 2.4 输出 `step1-intent-scope.md`：含意图描述、Cynefin 结果、数据组选择、范围边界

## 3. Step 3+4：数据定义 + 知识沉淀

- [x] 3.1 实现 `step3_data_requirements.py`：接收 scope 定义，执行 6W 矩阵分析
- [x] 3.2 实现 DM2 数据组到实体类型的映射逻辑（基于 views.yaml 中的 Required Data 字段）
- [x] 3.3 复用 `rag.py`：按数据需求检索 DM2 知识库中的相关概念和关联
- [x] 3.4 实现数据缺口检测：对比需求清单 vs 知识库已有内容，标记缺失项
- [x] 3.5 输出 `step3-data-requirements.md`：含 6W 映射、概念列表、数据组织、缺口清单

## 4. Step 5：分析执行

- [x] 4.1 实现 `step5_analysis.py`：协调溯因推理、OODA、TOC、一致性检查四个子模块
- [x] 4.2 实现溯因推理子模块：基于 DM2 8 种模式（patterns.py）推断缺失关系
- [x] 4.3 实现 OODA 子模块：检测架构中的决策断点（缺少 Observe→Orient→Decide→Act 链路中的节点）
- [x] 4.4 实现 TOC 子模块：在资源流链路上识别瓶颈节点（最大入度/出度比异常）
- [x] 4.5 复用 `consistency.py`：执行一致性检查，格式化结果
- [x] 4.6 输出 `step5-analysis.md`：含溯因推断、OODA 断点、TOC 瓶颈、一致性违规

## 5. Step 6：文档化 + 知识回流

- [x] 5.1 实现 `step6_documentation.py`：基于 Step 5 分析结果生成 Composite Views
- [x] 5.2 实现 Composite View 组合逻辑：OV-2+OV-5a、SV-4+DIV-1 两种初始组合
- [x] 5.3 复用 `view_generator.py`：填充视图模板（已有 DoDAFViewGenerator）
- [x] 5.4 实现 wikilinks 生成：在视图输出中插入 DM2 概念的 `[[]]` 链接
- [x] 5.5 实现知识回流摘要：汇总新增实体/关系，提供迭代建议
- [x] 5.6 输出视图文件到 `.dm2/output/`，输出摘要到 `step6-documentation.md`

## 6. CLI 集成

- [x] 6.1 实现 `pipeline_orchestrator.py`：步骤调度、状态检查、迭代循环控制
- [x] 6.2 在 `cli/main.py` 中注册 `dm2 run` 命令：参数 `-d`、`--resume`、`--step <N>`
- [x] 6.3 实现进度输出：每步开始/结束时打印状态和产物路径

## 7. 端到端验证

- [x] 7.1 用示例描述 `"某云原生微服务系统的安全架构"` 走通完整 6 步流程
- [x] 7.2 验证 `--resume` 断点续跑：中断后从 Step 5 恢复
- [x] 7.3 验证 `--step <N>` 单步执行：各步骤可独立运行
- [x] 7.4 验证迭代循环：Step 6 完成后可选择回到 Step 1
