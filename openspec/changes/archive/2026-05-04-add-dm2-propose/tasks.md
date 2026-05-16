## 1. /dm2:new 简化

- [x] 1.1 修改 `.claude/skills/dm2-new-workflow/SKILL.md`：将 Step 3-7（cynefin/analyze/视图生成）替换为"创建 change + 提示运行 /dm2:propose"
- [x] 1.2 修改 `.claude/commands/dm2/new.md`：更新命令描述，反映 scaffold-only 行为

## 2. dm2-propose-workflow 技能 + 命令

- [x] 2.1 创建 `.claude/skills/dm2-propose-workflow/SKILL.md`，包含 YAML frontmatter 和 Steps（输入处理 → dm2 change new → cynefin → analyze → 产物生成）
- [x] 2.2 创建 `.claude/commands/dm2/propose.md`，引用 dm2-propose-workflow 技能

## 3. DM2 数据组模板扩充

- [x] 3.1 在 17 个 dm2-reference/core/groups/*/*-Template.md 的 frontmatter 中增加 `keywords` 字段（每组的激活检测关键词）
- [x] 3.2 在 17 个模板的 frontmatter 中增加 `related_dm2_views` 字段（各组对应的 DoDAF 视图）

## 4. 外部映射文件

- [x] 4.1 创建 `dm2-reference/group-to-views.yaml`，汇总 17 个数据组→视图映射关系

## 5. ViewRecommender 升级

- [x] 5.1 修改 `src/dm2/cognitive/view_recommender.py`：新增 DataGroupActivator 类，从模板 frontmatter 加载 keywords，计算激活度
- [x] 5.2 修改 `recommend()` 方法：用数据组激活检测替代当前 6W 单维度推荐
- [x] 5.3 加载 `group-to-views.yaml`：数据组→视图映射
- [x] 5.4 实现修正因子：依赖就绪度检查（ArtifactGraph）+ 已完成视图过滤（ViewManager）
- [x] 5.5 增强 `--json` 输出：包含数据组激活向量、关键词命中记录、候选视图的原始结构化数据
