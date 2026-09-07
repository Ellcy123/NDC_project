# 角色表情参考库

[表情索引.json](表情索引.json) 是文件与配对查询入口；[角色卡库](../角色/README.md) 使用相同人物标识关联。

本批来自 `fa0b11c`（表情提交v1），共 15 位人物、99 对表情、1 张参考底图，199 张原图均保留。归档与配对不代表美术定稿，也不代表已完成视觉一致性审查或用户已同意交付工程。

## 目录规则

- 绿幕：`Unit2/绿幕/<人物目录>/<人物前缀>_<表情>.png`。
- 透明：`Unit2/透明/<同一人物目录>/<完全相同文件名>.png`。
- 参考底图：`Unit2/参考底图/emma/emma_base.png`；没有透明配对，不计入表情数量。
- `emma` 和 `zack` 两侧目录名已一致；文件只保留一个 `.png` 后缀。
- 其余两侧已经一致的人物目录保持原名；索引通过 `characterId` 关联角色卡，不按文件夹字面猜人物。
- 索引保留每张图的旧地址、新地址、SHA-256、源提交 Git blob 和图像尺寸。原始提交仍可追溯。
- 本批是同事提交的长期参考资源；后续新候选、返工和检查过程使用项目外受管工作区。

## 人物入口

| 人物 | 绿幕 | 透明 | 表情对数 | 角色卡关联 |
|---|---|---|---|---|
| Danny Kowalski | [打开](Unit2/绿幕/danny/) | [打开](Unit2/透明/danny/) | 7 | 已关联 |
| Earl Hirsch | [打开](Unit2/绿幕/earl/) | [打开](Unit2/透明/earl/) | 6 | 卡库尚未收录 |
| Edith Ross | [打开](Unit2/绿幕/Edith/) | [打开](Unit2/透明/Edith/) | 6 | 已关联 |
| Eleanor Foster | [打开](Unit2/绿幕/Dr.%20Foster/) | [打开](Unit2/透明/Dr.%20Foster/) | 4 | 已关联 |
| Emma O'Malley | [打开](Unit2/绿幕/emma/) | [打开](Unit2/透明/emma/) | 14 | 已关联 |
| Harold Moore | [打开](Unit2/绿幕/Harold%20Moore/) | [打开](Unit2/透明/Harold%20Moore/) | 5 | 已关联 |
| Lawson Vanderbilt | [打开](Unit2/绿幕/Lawson_%E5%8A%B3%E6%A3%AE%C2%B7%E8%8C%83%E5%BE%B7%E6%AF%94%E5%B0%94%E7%89%B9/) | [打开](Unit2/透明/Lawson_%E5%8A%B3%E6%A3%AE%C2%B7%E8%8C%83%E5%BE%B7%E6%AF%94%E5%B0%94%E7%89%B9/) | 4 | 已关联 |
| Leonard Ross | [打开](Unit2/绿幕/Leonard%20Ross/) | [打开](Unit2/透明/Leonard%20Ross/) | 8 | 已关联 |
| Lula Washington | [打开](Unit2/绿幕/lula/) | [打开](Unit2/透明/lula/) | 8 | 已关联 |
| Margaret Brennan | [打开](Unit2/绿幕/margaret/) | [打开](Unit2/透明/margaret/) | 4 | 已关联 |
| Mickey Donnelly | [打开](Unit2/绿幕/mickey/) | [打开](Unit2/透明/mickey/) | 5 | 已关联 |
| Mrs. O'Hara | [打开](Unit2/绿幕/Mrs.%20O%27Hara/) | [打开](Unit2/透明/Mrs.%20O%27Hara/) | 5 | 已关联 |
| Tony | [打开](Unit2/绿幕/tony/) | [打开](Unit2/透明/tony/) | 5 | 已关联 |
| Vinnie Moretti | [打开](Unit2/绿幕/Vinnie/) | [打开](Unit2/透明/Vinnie/) | 6 | 已关联 |
| Zack Brennan | [打开](Unit2/绿幕/zack/) | [打开](Unit2/透明/zack/) | 12 | 已关联 |

Earl Hirsch 有本批表情，但角色卡库尚未收录；索引引用人物档案，不用其他人的卡补位。

## 只读检查

```powershell
python -B scripts/art_pipeline/expression_catalog.py --check
```

检查原图哈希、提交来源、路径、重复后缀、人物关联和成对覆盖。透明版已检查存在实际透明通道；绿幕与透明版尺寸不同，归档不做缩放或补边。艺术质量与运行时适配需按具体生产任务验收。
