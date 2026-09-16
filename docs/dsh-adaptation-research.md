# dm2-tool 适配 DeepSeek Harness 研究报告

> 调研日期：2025-09 · 调研对象：本仓库 `dm2-tool` v0.1.0（Python 3.9，Typer CLI）
> 对照平台：DeepSeek Harness（DSH，Cordis 组合式 Agent 运行时）
> 目标：弄清 dm2-tool 现有的 AI Agent 接口如何映射到 DSH 的 Skill / Tool / Command / Preset 机制，并给出分阶段适配路线。

---

## 1. 结论摘要（TL;DR）

dm2-tool 的设计哲学是 **「CLI 是大脑，AI 是手脚」**：它本身零 LLM 依赖，对 Agent 暴露三类接口：

1. **只读知识查询**：`dm2 knowledge ... --json`（279 术语 / 52 视图 / 关联目录 / 分类学）；
2. **Markdown 工作流指令**：`dm2 init` 经 `ToolAdapter` 抽象生成 `.claude/skills/`（10 个工作流 SKILL.md）+ `.claude/commands/dm2/`（10 个斜杠命令）；
3. **状态机协议**：变更生命周期（`dm2 change ...`）、视图生命周期（`dm2 view ...`）、`dm2 run --agent` 的 pipeline 步进协议，全部以统一 `{"status","data"|"error"}` JSON 信封输出。

DSH 对这三类接口有**精确对应物**，且 dm2-tool 已经预留了 `ToolAdapter` 扩展点：

| dm2-tool（Claude Code 现状） | DeepSeek Harness 对应机制 | 适配成本 |
|---|---|---|
| `.claude/skills/<id>/SKILL.md` | `<project>/.dsh/skills/<id>/SKILL.md`（同名约定，frontmatter 高度兼容，`user-invocable` 原生支持） | **低**：新增一个 Adapter 类 |
| `.claude/commands/dm2/*.md`（斜杠命令文件） | DSH **无项目级命令目录**；由宿主 `commands` 服务经插件注册（如 `/goal`），或直接用 user-invocable Skill 充当入口 | 中：二选一 |
| Agent 通过 Bash 调 `dm2 ... --json` | 等价：DSH 自带 `bash` 工具（开箱可用，零开发）；进阶：Cordis 宿主插件注册一组原生 `dm2_*` model Tool，内部经 `shell` 服务调用 CLI | 低 / 中 |
| `.claude/` 整体由 `dm2 init` 生成 | `dm2 init --tool dsh` 生成 `.dsh/skills/`；产品化形态 = 一个 dm2 agent preset（`agent.cordis.yml` 组合） | 中 |
| 技能正文里的 `AskUserQuestion` 工具、`/dm2:xxx` 命令语法 | DSH 对应工具名 `ask_user_question`；DSH 命令无冒号命名空间，需做文本改写层 | 低（模板令牌化） |

**推荐路线**：先做 **方案 A（DshAdapter + 模板令牌化，约 2–3 个文件）** 让 DSH 会话立即可用；再用 **方案 B（动态 Cordis 插件注册 dm2 原生工具）** 做原型验证工具体验；最终 **方案 C（dm2 agent preset 产品化分发）**。

---

## 2. dm2-tool 现状（适配视角）

### 2.1 四层架构与 Agent 接触面

```
Agent Interface Layer  ← CLI --json 统一信封 + Knowledge API
Core Engine Layer      ← Instructions Engine / Artifact Graph / Change Manager / Pipeline V2
Knowledge Base Layer   ← DM2KnowledgeIndexer + MetamodelIndex（启动时加载派生 JSON）
File System Layer      ← .dm2/ 项目 + dm2-changes/ + output/
```

关键事实：

- **统一 JSON 信封**（`src/dm2/cli/json_output.py`）：成功 `{"status":"success","data":...}`，失败 `{"status":"error","error":{"code","message"}}` + exit 1。几乎所有命令都有 `--json/-j`（main.py 中 40 处 `json_flag`、78 处信封调用）。这是任何 Tool 包装层的理想契约。
- **零 LLM 依赖**：analyze/cynefin 纯本地关键词+模板；`generate`/`instructions` 只产出结构化指令文本供 Agent 消费。
- **路径优先**：知识库优先读项目内 `.dm2/reference/`，回退包内置 `dm2-reference/core/`；非项目目录下 `knowledge` 类只读命令也可运行（已实测）。

### 2.2 ToolAdapter：已经存在的适配缝

`src/dm2/core/adapters/__init__.py` 定义抽象基类（4 个方法）：

```python
class ToolAdapter(ABC):
    tool_id: str                         # 'claude' / 未来 'dsh'
    get_skills_dir() -> str              # '.claude/skills'
    get_commands_dir() -> str            # '.claude/commands/dm2'
    format_skill_frontmatter(t, ver)     # SKILL.md YAML 头
    format_command_frontmatter(t)        # 命令 .md YAML 头
```

- 唯一实现：`src/dm2/core/adapters/claude.py`（`ClaudeCodeAdapter`）。
- 生成器：`src/dm2/core/templates/generator.py::generate_agent_config(target, version, adapter)` 遍历 `WORKFLOWS`（10 个），每个写 1 个 `SKILL.md` + 1 个命令 `.md`。
- **缺口**：`dm2 init`（`src/dm2/cli/main.py:80-83`）硬编码 `ClaudeCodeAdapter()`，没有 `--tool` 选择；命令文件在生成器中是必产物（DSH 没有对应目录概念，需要让 commands 变为可选）。
- 测试约束：`test/test_workflow_templates.py` 固定了「10 workflows × 2 文件」的生成契约，新增 Adapter 时需同步参数化。

### 2.3 工作流模板盘点（10 个，DSH 技能的直接来源）

`src/dm2/core/templates/workflows/`：

| workflow_id | 技能名 | 性质 |
|---|---|---|
| explore | dm2-explore-workflow | 只读思考姿态，无固定步骤 |
| onboard | dm2-onboard-workflow | 交互式入门教学 |
| new / propose / continue_workflow / ff | dm2-*-workflow | 变更创建→分析→计划→生成主流程 |
| apply / verify / archive / bulk_archive | dm2-*-workflow | 执行计划、校验、归档 |

模板正文经实测含两类 **Claude 专有耦合**（grep 已定位，约 30 处）：

1. **斜杠命令语法** `/dm2:propose`、`/dm2:ff`、`/dm2:knowledge ...`（onboard/propose/ff/continue/new/archive）——DSH 命令名不含冒号，且这些命令由插件注册而非文件；
2. **工具名** `AskUserQuestion tool`（ff/propose/new/continue/bulk_archive）——DSH 中对应 `ask_user_question`（本会话工具目录可证，语义一致：questions 数组 + id + options）。

另有一处 `python3 -m dm2.cli.main change list-changes --json` 的直接调用（continue_workflow.py:16），在 DSH 下照样可经 bash 执行，但原生 Tool 化后应换成工具调用。

### 2.4 CLI 表面（供 Tool 包装的清单）

实测 `dm2 --help` + 源码核对：

| 分类 | 命令 | JSON | 项目要求 | 适配备注 |
|---|---|---|---|---|
| 知识只读 | `knowledge search/concept/view/views/term/taxonomy/associations/content/stats` | ✅ 全部 | 否 | 优先 Tool 化；高频、低风险 |
| 变更生命周期 | `change new/status/list-changes/archive`、`list`、`archive` | ✅ | 是 | 写操作，需 DSH 审批/沙箱语义 |
| 视图生命周期 | `view list/register` | ✅ | 是 | pending→…→verified 状态机 |
| 分析 | `analyze`、`cynefin` | ✅ | 是 | 纯本地计算 |
| 校验/生成 | `validate`、`generate`、`instructions` | ✅ | 是 | generate/instructions 输出的是给 Agent 的 Markdown/规则载荷 |
| Agent pipeline | `run --agent / --status / --instructions / --complete-step` | ✅（隐式恒 JSON） | 是 | 显式的「CLI 出指令→Agent 执行→回执推进」步进协议 |
| 项目管理 | `init/config/status/completion/version/uninstall` | init ✅ | — | init 是适配入口 |
| 关切模板 | `concern list` | ✅ | 否 | 只读 |

### 2.5 实测发现的注意点

- **`knowledge search` 只匹配英文术语名/别名/英文定义**：`search "resource flow"`、`search "资源流"` 均返回 0 条；`search Performer` 正常（返回 10 条）。DSH 中文用户多，包装层的工具描述里应提示「输入英文 DM2 术语名」，或后续在 dm2-tool 侧补中文别名索引。
- **每次 CLI 调用都重建索引**：`KnowledgeAPI()` 构造即 `load_all()`（279 术语 + 52 视图 + 元模型 JSON）。独立进程冷启动可接受（实测亚秒级），但原生 Tool 插件若高频调用，可在插件内缓存。
- **残留依赖**：`pyproject.toml` 仍声明 `anthropic>=0.39.0`，但代码已无 LLM 调用（CLAUDE.md 明确「零 LLM」），适配前建议清理，避免 DSH 安装环境带入无关包。
- 知识库内容大量中文，JSON 用 `ensure_ascii=False`，DSH 侧无编码障碍。

---

## 3. DeepSeek Harness 对应机制（源码与实时探查证据）

### 3.1 Skill 发现与 SKILL.md 格式

DSH 的文件系统技能 Provider（`packages/skill/skill-filesystem/src/index.ts`）按 rank 发现以下根：

| 根 | source | 层级 |
|---|---|---|
| `<git-root>/.dsh/skills` | project-dsh | 项目（最高优先） |
| `<git-root>/.agents/skills` | project-agents | 项目 |
| `customSkillDirs`（preset 配置） | custom | preset 自带 |
| `$DSH_HOME/skills`（默认 `~/.dsh/skills`） | user-dsh | 用户 |
| `~/.agents/skills` | user-agents | 用户 |
| 部署内置 | bundled | 系统 |

要点：

- **不发现 `.claude/skills`**——这是必须新增输出目录的根本原因。
- 项目根通过向上查找 `.git` 确定；找不到时回退为 cwd（`findProjectRoot`）。
- 目录布局与 Claude 完全相同：`<root>/<skill-dir>/SKILL.md`，也支持根下扁平 `*.md`；同名技能按 rank 去重。dm2 的 `dm2-*` 命名天然防冲突。
- frontmatter 解析（`parseSkillFile`）规则：
  - **必需**：`name`（kebab-case 语法，`dm2-explore-workflow` 合法）、`description`；
  - **可选且 dm2 已在用**：`user-invocable: false`（DSH 原生支持，语义=模型可自动加载、用户不可直接 @ 触发）；
  - DSH 额外认 `whenToUse`、`disable-model-invocation`、`metadata`（对象）；
  - **其余字段直接忽略不报错**：dm2 现有的 `license / compatibility / metadata.author/version/generatedBy` 无需删除即可被 DSH 接受（`metadata` 会被原样保留）。
  - 注意 DSH 拒绝遗留键名 `userInvocable`（必须是 kebab 的 `user-invocable`），dm2 当前写法恰好正确。

### 3.2 斜杠命令：没有项目级文件，只有插件注册

DSH 的人类命令由宿主 `commands` 服务持有：`commands.register({ definitionId, name, description, input:{hint, attachments}, handler })`。参考实现 `packages/goal/command-goal/src/index.ts` 的 `/goal`：解析输入、调领域服务、返回 `{kind:'success'|'error', text}`，命令还可以 `agent.followup(...)` 注入消息从而驱动 Agent 回合。

**含义**：`.claude/commands/dm2/*.md` 这种「一段提示词文件」在 DSH 没有存放位置。两条映射路线：

- **轻量**：不生成命令文件，把 10 个工作流技能改为 `user-invocable: true`（DSH 中用户可经技能调用入口触发），正文中的 `/dm2:xxx` 改写为「加载技能 `dm2-xxx-workflow`」；
- **原生**：写一个命令插件注册 `/dm2-new`、`/dm2-propose` 等（handler 内 followup 一条等价于命令正文的用户消息），体验最接近现状，但属于方案 C 的开发量。

### 3.3 Model Tool：Cordis 宿主插件 + shell 服务

经实时 Inspect 探查，本会话宿主具备适配所需的全部服务：

- 内置 `harness.defineTool(def)` / `harness.registerTool(ctx, def)`：动态插件在**下一个模型步**注册工具，注册随 Fiber 自动撤销——适合做原型；
- 宿主 `tools.register(ToolDefinition)`：正式插件包的注册路径，Tool 即 `{name, description, parameters(JSON Schema), execute}`；
- `shell` 服务（`resolve/run/start`）与 `subprocess` 服务（`resolveExecutable/spawn`）：在插件内执行 `dm2 <args> --json`，解析信封后把 `data` 返回模型；写操作再配合 `approval` 服务或沿用 bash 工具的沙箱/审批语义；
- 对照：本会话的 `bash` 工具本身就是「执行 `bash -c`」的封装，因此**零开发方案**下 Agent 已能直接调用 dm2 CLI，原生工具只是更优的参数模式化与结果整形。
- 动态插件是**进程内临时物**（不跨重启）；要随产品分发须落成 TS 插件包（如 `@local/dsh-tool-dm2`）并在 preset 中以行（row）引用，参照 `@deepseek-ai/dsh-tool-bash`、`@deepseek-ai/dsh-command-goal` 的打包方式。

### 3.4 Agent Preset：最终组合形态

preset 是一个目录（用户自编位置 `~/.dsh/.agent-presets/<id>/`），含 `preset.yml`（name/description/order）+ `agent.cordis.yml`（插件行组合）。实测 `presets/cordis/agent.cordis.yml` 提供了直接可抄的模式：

- 行可以是工具插件、命令插件、persona（`@deepseek-ai/dsh-persona`，支持 `{{cwd}}/{{model}}`）、提示段（`@deepseek-ai/dsh-plan-mode` 式 section）；
- **技能随 preset 分发的标准做法**：`@deepseek-ai/dsh-skill-filesystem` 行 + `config.customSkillDirs` 用 `!!js` 解析为 preset 目录下的 `skills/`（见 cordis preset 第 256-260 行）；
- 可 `cordis:group` + `isolate` 给行划 realm；dm2 工具只注册工具、不发布服务，**不需要 realm**（与 tool-fs/tool-jobs 同型）；
- standard preset 含 31 个行，是 dm2 preset 的复制基线（在其之上加 dm2 行即可）。

---

## 4. 差距矩阵

| # | 差距 | 影响 | 处理 |
|---|---|---|---|
| 1 | 输出目录 `.claude/skills` vs `.dsh/skills` | DSH 完全发现不到现有技能 | `DshAdapter.get_skills_dir()` |
| 2 | 命令目录 `.claude/commands/dm2/` 无对应 | 生成器假设命令必出 | Adapter 声明「无命令目录」+ 生成器支持 commands 可选 |
| 3 | 正文 30 处 `/dm2:xxx` | DSH 中是无效语法 | 模板令牌化（如 `{{cmd:propose}}`），按 adapter 渲染；DSH 渲染为技能名/命令名 |
| 4 | `AskUserQuestion` 工具名 | 名称不匹配（语义一致） | 令牌 `{{tool.ask_user}}` 或 DSH 渲染层统一替换为 `ask_user_question` |
| 5 | skill frontmatter 的 `license/compatibility` | 无（被忽略） | 可保留；DSH 头可精简为 name/description/user-invocable/metadata |
| 6 | `dm2 init` 硬编码 Claude adapter | 无法选目标 | 新增 `--tool claude|dsh`（默认 claude 保持兼容），`claude_config` 返回字段相应改名 |
| 7 | CLI 仅经 bash 可用 | 能用但工具描述/参数无结构、模型要自己拼命令 | 方案 B：dm2 原生工具组 |
| 8 | 模板测试钉死 20 文件 | 新 adapter 测试失败 | 参数化「文件数/命令可选性」 |
| 9 | anthropic 残留依赖 | 无关重量 | 顺手删除并跑测试 |
| 10 | search 中文召回为 0 | 中文工作流体验 | 工具描述提示英文术语；中期补中文别名 |

---

## 5. 适配方案

### 方案 A：DshAdapter（最小可用，推荐先做）

改动：

1. **新增** `src/dm2/core/adapters/dsh.py`：
   - `tool_id = "dsh"`；`get_skills_dir() = ".dsh/skills"`；`get_commands_dir()` 返回 `None`（或 `.dsh/commands` 但 DSH 不识别——不生成）；
   - `format_skill_frontmatter` 输出：
     ```yaml
     ---
     name: dm2-explore-workflow
     description: ...
     user-invocable: false        # 工作流技能维持模型路由；入口型可置 true
     metadata:
       author: "dm2"
       version: "0.1.0"
       generatedBy: "dm2-tool/0.1.0"
     ---
     ```
2. **改** `generator.py`：commands 目录/文件变为 adapter 能力（基类加 `supports_commands -> bool` 或允许目录返回 None）；技能正文增加一次**适配器渲染**（替换命令/工具令牌）。
3. **改** 10 个 workflow 模板：把 `/dm2:xxx`、`AskUserQuestion` 抽成令牌（最小改法：渲染回调按 adapter 做字符串映射，模板正文不动也能实现——在 generator 中对 Claude 恒等、对 DSH 做 regex 替换表）。
4. **改** `cli/main.py init`：加 `--tool`/`-t` 选项，adapter 注册表 `{"claude": ClaudeCodeAdapter, "dsh": DshAdapter}`；JSON 返回里 `agent_config` 替换 `claude_config`。
5. **测**：`test/test_workflow_templates.py` 增加 DSH 用例（生成 10 个 SKILL.md、0 个命令文件、frontmatter 可被 YAML 解析、正文无 `/dm2:` 残留、含 `ask_user_question`）。

交付后：在任意 dm2 项目 `dm2 init -t dsh .`（或补一个 `dm2 init --tool dsh` 到已有项目的幂等路径），用 DSH 在该仓库开会话，10 个技能进入会话技能目录，模型经 `bash` 调 `dm2` CLI 即可跑完全部工作流。

### 方案 B：dm2 原生 Tool 动态插件（DSH 原生体验，原型）

用本会话的 Cordis 动态插件能力做**一次性原型**（也可直接作为正式 TS 包的蓝本）：

- 宿主 half：`harness.registerTool` 注册只读工具组（先无审批摩擦）：
  - `dm2_knowledge_search(query, limit?)`、`dm2_knowledge_view(view_id)`、`dm2_knowledge_views(viewpoint?)`、`dm2_knowledge_term(name)`、`dm2_knowledge_concept(name)`、`dm2_knowledge_taxonomy(type)`、`dm2_knowledge_associations(type?, group?)`、`dm2_knowledge_content(view_id)`、`dm2_knowledge_stats()`；
  - 项目/变更类（写）：`dm2_change_new/list/status/archive`、`dm2_view_list/register`、`dm2_analyze`、`dm2_cynefin`、`dm2_validate`、`dm2_generate`、`dm2_instructions`；
  - pipeline 协议：`dm2_run_start(desc)` / `dm2_run_status` / `dm2_run_step_instructions(step)` / `dm2_run_complete(step)`。
- 执行：经 `shell` 服务 `resolve+run`（cwd=会话工作区）调 `dm2 <args> --json`；stdout 解析信封，`data` 直返；`error` 以工具错误抛出；stderr 透传诊断。可执行文件用 `subprocess.resolveExecutable('dm2')` 解析，找不到时返回「pip install -e .」指引（onboard 技能已有同款话术）。
- 生命周期：注册返回 disposer，天然随插件 stop/update 清理；无 Client UI 需求，**不需要 client half**。
- 技能侧：工作流正文把 `dm2 knowledge ...` 的 shell 调用改写为工具调用表（adapter 渲染层的 DSH 分支）。

价值：模型拿到结构化参数 schema 而非自由拼命令；写操作天然进入 DSH 工具管道（可挂 guard/审批）；省掉每轮 bash 文本。风险：动态插件不跨重启，仅适合验证；正式分发走方案 C。

### 方案 C：dm2 agent preset（产品化）

新 preset 目录 `dm2/`：

- `preset.yml`：name「DoDAF 架构工程（DM2）」、description、order；
- `agent.cordis.yml`：复制 standard 全部行（baseline 能力），追加：
  - `@local/dsh-tool-dm2`（方案 B 的正式 TS 插件包：dm2 工具组，可选 `commands` 插件提供 `/dm2-new` 等人类命令）；
  - `@deepseek-ai/dsh-skill-filesystem` + `customSkillDirs: <preset>/skills`，技能内容即方案 A 生成物（脱离 `dm2 init` 也自带工作流知识；项目侧仍靠 `.dm2/` 状态）；
  - persona/prompt 短段：声明「CLI 是大脑」模式、`.dm2/` 约定、只读/写命令边界（也可继续由项目 `.dsh/skills` 提供，避免双份）；
  - 不 isolate realm（工具行无自有服务）。
- 分发选项：① 内部部署直接放进 `~/.dsh/.agent-presets/dm2/`；② 随 dm2-tool 仓库带一个 `assets/dsh-preset/` 模板 + `dm2 init --tool dsh` 复制到 presets 目录；③ 长期做成 DSH 插件包发布。

### 路线建议

1. **第 1 步（小时级）**：方案 A 的 adapter + 令牌渲染 + `--tool` + 测试。立即获得「DSH 会话 + bash + .dsh/skills」完整可用性。
2. **第 2 步（会话级原型）**：用 Cordis 动态插件实现方案 B 只读工具组，在真实 DM2 建模会话中观察模型调用质量，再决定写工具组的审批粒度。
3. **第 3 步（产品化）**：把验证过的插件落成 TS 包 + dm2 preset；同时清理 anthropic 依赖、补 search 中文别名。

---

## 6. 文件级改动清单（方案 A）

| 文件 | 改动 |
|---|---|
| `src/dm2/core/adapters/dsh.py` | 新增：`DshAdapter`（skills 目录、frontmatter、无命令支持） |
| `src/dm2/core/adapters/__init__.py` | `get_commands_dir()` 允许返回 None；加 `supports_commands`/正文渲染钩子 |
| `src/dm2/core/templates/generator.py` | commands 可选；正文经 adapter 渲染（命令语法/工具名替换） |
| `src/dm2/core/adapters/claude.py` | 渲染恒等（保持现状） |
| `src/dm2/cli/main.py` | `init --tool claude\|dsh`，adapter 注册表；`agent_config` 字段通用化 |
| `test/test_workflow_templates.py` | 参数化生成器测试 + DSH 断言（无 `/dm2:`、无命令文件、frontmatter 合法） |
| `pyproject.toml` | 删除残留 `anthropic` 依赖 |
| `docs/` | 本文档 + `dm2 init --tool dsh` 使用说明 |

## 7. 风险与约束

- **动态 Cordis 插件不持久**：进程重启即失效，不能当作交付物；交付走项目 `.dsh/skills`（文件）或正式 preset/插件包。
- **审批边界**：`change new/archive`、`view register`、`generate` 是写操作。bash 路径下受 DSH 文件沙箱约束（实测当前策略 workspace-write）；原生工具路径应显式区分只读/写工具并接入 `approval`。
- **技能触发模型**：dm2 工作流技能现为 `user-invocable: false`（模型路由）。若希望用户像 `/dm2:explore` 一样显式入口，DSH 下需置 `user-invocable: true` 或注册命令插件——这是产品决策点。
- **项目根发现依赖 `.git`**：非 git 的 dm2 项目会回退 cwd；`dm2 init` 可提示 `git init` 或确保在项目根启动会话。
- **Python 环境**：`dm2` 装在 `~/Library/Python/3.9/bin`，插件 shell 需保证 PATH；插件应支持配置可执行路径（含 `python3 -m dm2.cli.main` 回退）。
- **模板契约测试**：多个断言钉死中文/英文指令短语，渲染替换必须避开被钉死的字符串（如 explore 的 dependency-chain 句），令牌化时以新增、不改写既有英文句为原则。
