## Context

D10 记录的分发问题有两半：`dm2-reference/` 不进包（打包布局），以及**知识库找不到时会静默给空答案**（运行时行为）。本次只修后半——因为它是**行为缺陷**，可在仓库内修好并用测试守住；前半是分发形态的产品决策，会显著改动打包布局。

实测（隔离 venv，`pip install .`）：`dm2 knowledge stats` → 全 0，`dm2 concern list` → 空，**两者 exit 0**。

两处静默解析：

| 位置 | 现状 | 后果 |
|---|---|---|
| `utils/paths.py:24-28` `get_reference_path()` | 两条候选都不存在时**仍返回 `base`** | 索引器 glob 空目录 → 空结果 |
| `cli/commands/concern.py` `_get_concerns_path()` / `_load_concerns()` | 返回 `None` → `[]` | 「未找到匹配的关切模板」 |

`get_reference_path()` 有 7 处调用点，横跨 `kernel`/`cognitive`/`reasoning`/`cli`。

## Goals / Non-Goals

**Goals:**

- 知识库（或 `concerns.yaml`）无法解析时，**以非零退出码明确报错**，而不是静默返回空。
- JSON 模式给出 `KB_NOT_FOUND` 信封；人类模式给出可操作的中文提示。
- 守护测试覆盖：解析抛错、信封形态、人类模式文案。

**Non-Goals:**

- 改变分发布局、把 `dm2-reference/` 真正打进包（D10 的另一半，属产品决策）。
- 让 editable 安装下的任何正常路径发生行为变化。
- 合并 `_require_project` 的多份拷贝（既有的独立问题）。

## Decisions

**1. 用中央报错，而不是逐命令加守卫。**
D3 的根因正是「按命令复制的守卫被漏加」（`view`/`run`/`validate` 都缺守卫，直到审计才发现）。同类的失败若再一次做成逐命令守卫，只会重演那个失效模式。因此本前置条件只在一个地方实现：进程入口。

**2. 异常定义在 `utils/paths.py`。**
`utils` 是 L0 叶子层，`kernel`/`cognitive`/`reasoning`/`cli` 都可向下引用它——不会违反刚立的 `dm2-architecture-boundaries`。异常与解析函数放在一起，避免调用方各自捕获 `FileNotFoundError` 这种过宽的异常。

**3. JSON 模式从 argv 判定。**
中央报错点拿不到各命令的 `json_flag`。已核实 `-j` 在整个 CLI 中**只**用于 JSON 标志（`grep '"-j"' src/` 全部命中 `json_flag`），因此扫描 `argv` 是安全的；这一点写进 spec 的实现注记，避免将来有命令挪用 `-j` 后此处静默失准。

**4. 两个入口都要走同一个包装。**
`dm2` 脚本调用 `main()`，而 `python -m dm2.cli.main` 走 `if __name__ == "__main__"`。测试正是用 `-m` 调用的，若只在 `main()` 里捕获，`-m` 路径会漏——所以两个入口都指向同一个 `_invoke_app()`。

**5. 顺带修 `concerns.yaml`：同一缺陷，且出现在同一份 D10 证据里。**
不修它，非 editable 安装仍会对 `dm2 concern list` 静默说「没有关切」。这不是扩大范围，而是把 D10 证据里的两个现象都收口。

**6. `DM2_DEBUG=1` 时重新抛出。**
中央捕获会让开发者看不到 traceback。沿用既有的 `DM2_DEBUG` 约定（索引器诊断同款），置位时重新抛出，便于定位。

## Risks / Trade-offs

- **一个返回 `Path` 的函数变成会抛异常的函数**：7 处调用点中若有靠「拿到一个不存在的路径也不报错」工作的代码，行为会变。已确认这些调用点都只是把结果用于读取/glob，不存在依赖该路径为空的分支。
- **中央捕获可能掩盖其他异常**：只捕获 `KnowledgeBaseNotFound`，不捕获其基类 `RuntimeError`，因此不会顺带吞掉无关的运行时错误。
- **argv 判定是启发式**：`-j` 目前的唯一性使其成立；spec 里写明该前提，并有测试固定 `KB_NOT_FOUND` 的信封行为。
- **行为变化的影响面**：仅在「知识库不可解析」这一原本就错误的状态下生效，editable 安装不受影响。
