# 知识索引构建流水线

dm2-tool 的知识层由两级构成：**权威源**（人策划的 YAML）和**派生索引**（构建期生成的紧凑 JSON）。运行时只加载派生索引，从不解析源文件。

```
dm2-reference/                          dm2-reference/core/
（权威源，840KB）                        （派生索引，运行时加载）
├─ dm2-data-dictionary.yaml    ──┐
│   279 术语 + 怪物矩阵          │  python3 scripts/build_knowledge_indexes.py
│   （term × 52 视图 n/o 标记）   ├──────────────────────────────► terms.json
└─ dm2-metamodel-2.02.yaml     ──┘   （确定性、零 LLM）          associations.json
    19 子模型 / 621 类 / 435 关系                            taxonomy.json
    242 Tuple / 384 继承 / 47 powertype                     view-content-spec.json
```

## 索引内容

| 索引 | 内容 | 规模 |
|------|------|------|
| `terms.json` | 术语条目：CURIE id（`dodaf:<Term>`）、定义、别名、调和后数据组、是否关联术语 | 279 |
| `associations.json` | 二元关联目录：label、端点类型、IDEAS place 角色、领域语义角色（`<<place1Type>>\|consumer`）、多重度（仅 4/325 有值）、建模所在子模型 | 79 元组（67 二元） |
| `taxonomy.json` | super-subtype 父子映射 + powertype 配对（Type/Individual 桥接） | 193 子类 / 26 配对 |
| `view-content-spec.json` | 每视图必要术语、可选术语（截断至 30）、必要关联（怪物矩阵 n 标记 × 关联目录 join，带端点类型） | 52 视图 / 161 必要关联 |

## 子模型到 17 数据组的调和表

数据字典的 `submodels` x 标记与 17 数据组目录不一一对应，构建脚本内编码了显式调和规则（单一事实来源）：

| 数据字典 submodel | 17 组目录 |
|---|---|
| performer / capability / measure / location / services / project | 01 / 03 / 06 / 07 / 08 / 09 |
| rules | **按术语名拆分**：名含 Guidance/Standard/Agreement -> `05-guidance`，否则 -> `10-rules` |
| resource-flow / information-and-data / information-pedigree / organizational-structure | 11 / 16 / 13 / 14 |
| pedigree / reification-levels / dm2-foundation / ideas-foundation | 12 / 15 / 00（元组，不做视图推荐） |
| （无对应 submodel） | **按术语名合成**：`Activity`/`activity*` -> `02-activity`；`Resource`/`Materiel`/`resource*` -> `04-resource` |

跨组术语（如 Activity 属 11 组）在组级信号中以 1/N 权重投票。

## 组模板 relationships 投影

17 个数据组模板（`groups/*/*Template.md`）的 `relationships:` frontmatter 槽位不再是手写土话，而是关联目录的投影：

- **域子模型 home**：关联在哪个 LDM 子模型被建模 -> 归哪个组（`foundation_for_associations`/`domain_class_hierarchy` 等重复页不算 home）
- **rules home** 按端点类型做 05/10 拆分
- **基础模式元组**（wholePart/overlap/typeInstance…）归 `00-foundation`
- **02/04 组**（无子模型）按锚点类型归并

同步命令：

```bash
python3 scripts/build_knowledge_indexes.py --check-templates   # 校验（drift 时退出码 1）
python3 scripts/build_knowledge_indexes.py --fix-templates     # 从投影重写 relationships 块
```

重写只触及 `relationships:` 块，模板正文与其他 frontmatter 字段不动。

## 覆盖率与已知边界

- 数据字典 106 个关联术语中 63 个在元模型有 Tuple 定义；未解析的 43 个是 IDEAS 基础模式词汇（WholePartType、OverlapType…），在视图内容规范中降级为 label-only 条目。
- 96 个元模型类缺 `ideas_type`；多重度仅 4/325 couples 有值、导航性 0/325 -- **基数/导航性校验不可实现**，符合性校验只覆盖关系存在性 + 端点类型（分类学感知）。
- powertype 配对存在循环（Organization↔OrganizationType 双向 powertypeInstance）；type-layer 符合性规则只对单侧出现的名称判定，循环配对名称视为歧义跳过。

## 与测试的关系

`test/test_knowledge_indexes.py` 对四个索引做快照测试：源 YAML 变更而未再生成索引时测试失败。`test/test_template_relationships.py` 校验模板 `relationships` 块与目录投影一致。
