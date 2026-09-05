# 角色卡参考库

角色卡统一按人物维护，跨章节通过索引关联。同一人物不按章节复制图片。此处是长期参考资料；候选图、检查图、返工过程和待交付成品进入项目外工作区。

- 查询入口：[角色索引.json](角色索引.json)。路径均相对 `D:/NDC_project`。
- 表情图入口：[表情库说明](../角色表情/README.md) / [表情索引.json](../角色表情/表情索引.json)。按同一人物标识关联角色卡；绿幕与透明图按表情逐对登记。
- 图片位置：`人物/<characterId>/cards/`。
- `colored.png` 为彩色；`black_white_red.png` 为黑白红。多版本文件名带明确 variant。
- 提交、导入和归档都不代表美术定稿。本次 63 张图片全部登记为 `unconfirmed`；选择明确版本并取得用户确认后，才能用于要求已批准角色卡的新生产任务。
- 已有任务继续使用原 handoff 指定的卡和 hash，不因归档自动切换。
- 角色卡不在任务结束时删除，也不直接当作 Unity 运行时图片交付。

## 本次归档

2026-09-05：61 张新提交卡归入 42 位人物；另外保留 Margaret 旧深发版 2 张，共 63 张规范图片。102 个原始来源均有 SHA-256 和去向记录。

`image/角色卡666` 的 41 张旧图暂留原位：38 张与规范库字节完全相同、2 张 Margaret 不同造型、1 张身份未确认的男性。已有活跃任务引用这些地址，暂不删除；任务关闭后按索引逐项核验并清理兼容源，不按目录年龄自动删除。

- Margaret：`silver_hair` 与 `legacy_dark_hair`，两种发色分别保留彩色/黑白红。
- Pierce：`v1` 和 `v2` 分别保留；两版都没有被本次整理选为默认。
- Watts、Sarah：原文件长名仅作来源别名，不补写 canon 姓名。
- Vivian：Unit1 / Unit5 的姓氏口径不同，采用共同查询名，保留人物档案证据。
- 小/老 Charles 分人；NPC 312 的映射尚需内容确认，不自动绑定。
- 未识别旧图保留在 `image/角色卡666/ChatGPT Image 2026年8月3日 17_34_07.png`。

## 只读检查

```powershell
python -B scripts/art_pipeline/character_catalog.py --check
```

检查规范图片与兼容源的 hash、来源清单、重复内容、人物/变体唯一性、章节与 NPC 表关联；发现新加但未登记的卡会报错。检查不会写文件或清理图片。

## 人物入口

| 人物 | 目录 | 章节资料关联 | 卡数 |
|---|---|---|---|
| Anna O'Sullivan | [打开](人物/anna_osullivan/cards/) | Unit1 | 2 |
| Arthur Webb | [打开](人物/arthur_webb/cards/) | Unit1 | 2 |
| Bernard Wells | [打开](人物/bernard_wells/cards/) | Unit3 | 1 |
| Charles Miller Jr. | [打开](人物/charles_miller_jr/cards/) | Unit5 | 2 |
| Charles Miller Sr. | [打开](人物/charles_miller_sr/cards/) | Unit5 | 2 |
| 法院档案管理员 | [打开](人物/court_archivist/cards/) | Unit4 | 1 |
| Danny Kowalski | [打开](人物/danny_kowalski/cards/) | Unit2 | 2 |
| 辖区警员 | [打开](人物/district_police_officer/cards/) | Unit4 | 1 |
| Edith Ross | [打开](人物/edith_ross/cards/) | Unit2 | 1 |
| Eleanor Foster | [打开](人物/eleanor_foster/cards/) | Unit2, Unit3, Unit4 | 1 |
| Emily | [打开](人物/emily/cards/) | Unit3 | 1 |
| Emma O'Malley | [打开](人物/emma_omalley/cards/) | Unit1, Unit2, Unit3, Unit4, Unit5 | 2 |
| Father O'Connell | [打开](人物/father_oconnell/cards/) | Unit3 | 1 |
| Frank Kowalski | [打开](人物/frank_kowalski/cards/) | Unit2 | 2 |
| Harold Moore | [打开](人物/harold_moore/cards/) | Unit2 | 2 |
| Harold Morrison | [打开](人物/harold_morrison/cards/) | Unit1, Unit2, Unit3, Unit4 | 2 |
| Helen | [打开](人物/helen/cards/) | Unit3 | 1 |
| James O'Sullivan | [打开](人物/james_osullivan/cards/) | Unit1 | 2 |
| Judge Harrison | [打开](人物/judge_harrison/cards/) | Unit3, Unit4 | 1 |
| Lawson Vanderbilt | [打开](人物/lawson_vanderbilt/cards/) | Unit2, Unit5 | 1 |
| Leonard Ross | [打开](人物/leonard_ross/cards/) | Unit2, Unit3 | 2 |
| Lula Washington | [打开](人物/lula_washington/cards/) | Unit2 | 1 |
| Margaret Brennan | [打开](人物/margaret_brennan/cards/) | Unit2, Unit3, Unit4 | 4 |
| Mary Smith | [打开](人物/mary_smith/cards/) | Unit3 | 1 |
| Mickey Donnelly | [打开](人物/mickey_donnelly/cards/) | Unit2, Unit3, Unit4 | 2 |
| Mrs. O'Hara | [打开](人物/mrs_ohara/cards/) | Unit2, Unit4 | 1 |
| Patrick Brennan | [打开](人物/patrick_brennan/cards/) | Unit4 | 1 |
| Pierce | [打开](人物/pierce/cards/) | Unit4 | 2 |
| 退休法官 | [打开](人物/retired_judge/cards/) | Unit4 | 1 |
| Rosa Martinez | [打开](人物/rosa_martinez/cards/) | Unit1, Unit4 | 2 |
| Sarah | [打开](人物/sarah/cards/) | Unit4 | 1 |
| Seamus Byrne | [打开](人物/seamus_byrne/cards/) | Unit3 | 1 |
| 社会服务部调档员 | [打开](人物/social_service_records_clerk/cards/) | Unit4 | 1 |
| 夜班电话接线员 | [打开](人物/telephone_operator/cards/) | Unit4 | 1 |
| Thomas Smith | [打开](人物/thomas_smith/cards/) | Unit3 | 1 |
| Tommy Connelly | [打开](人物/tommy_connelly/cards/) | Unit1 | 2 |
| Tony | [打开](人物/tony/cards/) | Unit2 | 1 |
| Vinnie Moretti | [打开](人物/vinnie_moretti/cards/) | Unit2 | 2 |
| Vivian | [打开](人物/vivian/cards/) | Unit1, Unit5 | 2 |
| Watts | [打开](人物/watts/cards/) | Unit4 | 1 |
| Whitfield | [打开](人物/whitfield/cards/) | Unit4 | 1 |
| Zack Brennan | [打开](人物/zack_brennan/cards/) | Unit1, Unit2, Unit3, Unit4, Unit5 | 2 |
