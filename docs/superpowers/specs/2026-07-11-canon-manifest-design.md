# Canon Manifest 设计规范

日期：2026-07-11
状态：方向已获用户确认，待书面规范复核

## 1. 目标

为 NDC_project 新增一份机器可读的项目级 Canon Manifest，统一回答以下问题：

- 玩家看到的是第几章、章节标题是什么；
- 策划内容实际位于哪个 Unit 目录；
- Unit9、Unit10 等名称与正式 Unit 的关系；
- Unity 使用哪个 Episode；
- 现行设计期与运行时分别使用哪些 ID 命名空间；
- 大纲、state、AVG、配置表的现行来源在哪里；
- 每个章节当前落地到什么阶段；
- 哪些版本已归档或废弃，日期是否有可靠证据。

Manifest 只负责“章节身份、位置、成熟度和历史状态”，不保存剧情事实，不替代大纲、state、AVG 或配置表本身。

## 2. 已确认的核心决策

1. 正式章节身份为 Unit1、Unit2、Unit3、Unit4、Unit5。
2. Unit9 是 Unit1 的现行创作侧别名，不是额外章节。
3. Unit10 是 Unit2 大纲仍在使用的标题别名，不是额外章节。
4. 不迁移、不重编任何现有 ID。
5. 不执行单条 ID 的自动翻译；Manifest 只登记命名空间之间的章节级对应关系。
6. Unit1 同时保留两套现行命名空间：
   - 策划 state 与 AVG/EPI09 使用 9xxx；
   - Unity／正式表使用 EPI01 与 1xxx。
7. Unit2 当前现行内容统一使用 EPI02 与 2xxx；10xxx 只记录为 2026-05-19 之前的历史命名空间。
8. Unit4、Unit5 的 EPI04／EPI05 与 4xxx／5xxx 只能标记为预留，不能标记为已经落地。
9. 没有明确日期证据时，废弃日期使用 `null`，不得根据目录名或推测伪造日期。

## 3. 实施范围

本次实施包括：

1. 新增仓库根目录 `canon_manifest.json`。
2. 新增无第三方依赖的 `scripts/validate_canon_manifest.py`。
3. 修改 `avg_editor_v2/build_unit_flow.py`，从 Manifest 读取正式 Unit、Episode 与流程别名，不再把 U9 映射写死在代码中。
4. 修改 `AGENTS.md`，删除“Unit9／Unit10 是独立章节、不要查看 Unit1／Unit2”的过时说明，改为引用 Manifest。
5. 在 `README.md` 增加 Canon Manifest 入口和一句映射说明。

本次明确不包括：

- 修改或批量重编号任何 Item、Scene、Doubt、Testimony、Talk、Expose ID；
- 移动或重命名 `剧情设计/Unit1`、`剧情设计/Unit2`、`AVG/EPI09` 等现有目录；
- 把 EPI09 文件复制或转换为 EPI01；
- 生成、覆盖或清理任何 table JSON；
- 判定剧情内容是否最终定稿；
- 整理 EPI08、旧 Unit2 备份等历史文件。

## 4. Manifest 文件结构

顶层结构：

```json
{
  "schemaVersion": 1,
  "updatedAt": "2026-07-11",
  "policy": {
    "idMigration": "none",
    "automaticIdTranslation": false,
    "canonicalUnits": ["Unit1", "Unit2", "Unit3", "Unit4", "Unit5"]
  },
  "chapters": [],
  "flowAliases": []
}
```

每个 `chapters[]` 条目包含：

- `canonicalUnit`：唯一正式 Unit 名；
- `playerChapter`：玩家章节顺序，整数；
- `playerTitle`：玩家可读章节标题；
- `aliases[]`：仍出现在现行来源中的其他名称及其用途；
- `planningDirectory`：策划目录；
- `unityEpisode`：Unity／正式配置使用的 Episode；
- `idSpaces[]`：命名空间、范围、Episode、用途与保留策略；
- `sources`：现行大纲、state、AVG、table／draft 路径；
- `maturity`：各生产阶段的结构化完成状态和核验日期；
- `history[]`：已归档、已废弃或被替代的来源与可证日期。

`flowAliases[]` 单独控制构建产物的兼容别名。它与章节身份别名分开，避免只因为大纲标题出现 Unit10，就在编辑器里额外生成一个 Unit10 章节。

当前只保留既有兼容行为：

```json
{
  "name": "Unit9",
  "target": "Unit1",
  "enabled": true,
  "reason": "Preserve current avg_editor flow lookup without changing IDs"
}
```

Unit10 不新增流程别名，因为当前构建脚本没有生成 Unit10 顶层节点。

## 5. 首版章节登记内容

| 正式章节 | 现行别名 | Unity Episode | ID 状态 | 内容成熟度 |
|---|---|---|---|---|
| Unit1《黑哨之夜》 | Unit9（现行创作侧） | EPI01 | 策划／EPI09 保留 9xxx；运行表保留 1xxx | 大纲、6/6 state、EPI09 六轮 AVG 已有；Unit9 table 为 draft；最终性未声明 |
| Unit2《黄昏悲歌》 | Unit10（大纲标题） | EPI02 | 当前统一保留 2xxx；10xxx 只进历史记录 | 大纲仍有挂起风险；6/6 state、EPI02 六轮 AVG、正式表已存在；最终性未声明 |
| Unit3《漫长的坠落》 | 无 | EPI03 | 保留 3xxx | 大纲、6/6 state、设计期表已有；AVG/EPI03 不存在；活跃迭代中 |
| Unit4《四十二层之前》 | 无 | EPI04（预留） | 4xxx（预留） | 0710 v2 大纲；无 state、AVG、正式表 |
| Unit5《系统没有主人》 | 无 | EPI05（预留） | 5xxx（预留） | v0.7 大纲；无 state、AVG、正式表 |

### 5.1 Unit1 主要来源

- 大纲：`剧情设计/Unit1/Unit1_大纲.md`
- state：`剧情设计/Unit1/state/loop{1-6}_state.yaml`
- Phase 1 草稿：`AVG/对话配置工作及草稿/Unit9/`
- 当前创作输出：`AVG/EPI09/`
- table 草稿：`avg_editor_v2/data/_table_drafts/Unit9/`
- 运行表：`avg_editor_v2/data/table/`

Unit1 的两个 ID 空间只做并列登记，不建立逐 ID 映射。

### 5.2 Unit2 主要来源

- 大纲：`剧情设计/Unit2/Unit2_大纲.md`
- state：`剧情设计/Unit2/state/loop{1-6}_state.yaml`
- 当前 AVG：`AVG/EPI02/`
- 运行表：`avg_editor_v2/data/table/`
- 重构前归档：`旧文档/Unit2_重构前备份_20260519/`

历史条目记录 2026-05-19 的 Unit10／EPI10／10xxx 合并事件；现行来源不再声明 10xxx。

### 5.3 历史版本规则

- `AVG/EPI08` 登记为 `deprecated_retained`。
- EPI08 文档没有显式废弃日期，因此 `deprecatedDate` 为 `null`。
- 可同时记录声明提交 `1abe679` 与提交日期 `2026-04-23`，但提交日期不能冒充内容的正式废弃日期。
- 归档目录名中的日期可登记为 `archivedSnapshotDate`，除非另有明确声明，否则不自动等同于 `deprecatedDate`。

## 6. 数据读取与生成流程

```text
canon_manifest.json
  ├─ validate_canon_manifest.py：校验结构、唯一性、路径和状态
  ├─ AGENTS.md / README.md：告诉人当前章节身份和入口
  └─ build_unit_flow.py：读取正式 Unit、Episode 和兼容流程别名
          └─ unit_flow 输出保持现有业务 ID，不进行任何翻译
```

构建脚本加载失败时必须直接报错并停止，不得静默回退到旧的硬编码映射。否则 Manifest 与代码仍可能再次分叉。

## 7. 校验规则

校验器使用 Python 标准库实现，不新增依赖。至少检查：

1. JSON 可解析且 `schemaVersion` 为支持的版本。
2. `canonicalUnit`、`playerChapter`、`unityEpisode` 在非预留章节中唯一。
3. `policy.idMigration` 必须为 `none`，`automaticIdTranslation` 必须为 `false`。
4. Unit9、Unit10 不得作为独立的 `canonicalUnit`。
5. `flowAliases[].target` 必须指向现存正式 Unit，且不能形成循环。
6. 标记为 `present`、`active`、`current` 的文件／目录必须存在。
7. 标记为 `reserved`、`absent` 的来源允许路径为 `null` 或不存在。
8. `presentLoops` 不得超出 `expectedLoops`，且不能重复。
9. 历史条目没有可靠日期时必须使用 `null`，不能写占位字符串。
10. Manifest 中不能出现单条 ID 对照表或 ID 重写规则。

校验错误返回非零退出码，并给出章节名、字段路径和具体原因。

## 8. 构建兼容策略

`build_unit_flow.py` 的首版改造只替换身份元数据与别名来源，不改变流程推导算法：

- Unit1、Unit2 的正式输出结构保持原样；
- 继续根据 Manifest 的 `flowAliases` 生成 Unit9 → Unit1 兼容视图；
- 不新增 Unit10 顶层兼容视图；
- 不读取或改写 `idSpaces` 中的具体 ID；
- 不在实施过程中覆盖当前已有未提交修改的 `avg_editor_v2/data/formal/unit_flow.json`。

验证构建行为时使用临时输出文件，比较改造前后的 Unit1、Unit2 ID 集合完全一致。

## 9. 文档改写口径

`AGENTS.md` 的新口径为：

> 玩家第1章的正式身份为 Unit1，现行策划别名为 Unit9；玩家第2章的正式身份为 Unit2，现行策划标题别名为 Unit10。Unit9、Unit10 不计作额外章节。现行策划内容直接位于 `剧情设计/Unit1`、`剧情设计/Unit2`；旧版内容只从 Canon Manifest 标出的归档目录读取。现有 ID 不迁移、不自动转换。

`README.md` 只增加入口与摘要，不复制完整映射，避免再次产生两份需要同步维护的表。

## 10. 验收标准

实施完成后必须满足：

1. `canon_manifest.json` 包含 Unit1 至 Unit5，且能被标准 JSON 解析器读取。
2. 校验器无第三方依赖，成功校验当前 Manifest。
3. 故意制造重复正式 Unit、无效别名目标或错误现行路径时，校验器会失败。
4. 构建脚本不再硬编码 Unit9 → Unit1 映射。
5. 临时构建结果中的业务 ID 与改造前完全一致。
6. 未修改任何 state、AVG、table JSON 或现有业务 ID。
7. Unit4、Unit5 明确显示为预留／未落地，不被误判为完成。
8. `AGENTS.md` 与 `README.md` 均指向 Manifest，不再把 Unit9、Unit10 解释成额外章节。

## 11. 实施安全边界

当前工作区已有用户未提交修改，尤其涉及 `ChapterConfig.json`、`unit_flow.json` 和 Unit3 内容。本任务只编辑批准范围内的独立文件和映射代码；测试使用临时文件，不清理、不还原、不覆盖任何用户修改。
