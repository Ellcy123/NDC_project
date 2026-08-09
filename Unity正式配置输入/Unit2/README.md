# Unit2 Unity 正式配置输入

这个目录是 Unit2 正式 Unity 配表的独立输入副本。它允许为正式表修正 ID、动作标记、分支、证据引用和 state 结构，同时保证现有对白草稿、剧情设计、旧编辑器配置与预览内容不被修改。

## 内容优先级

1. `dialogue/Loop1-6_正式配置稿.md`：正式对白文字与流程的唯一可修改来源。
2. `state/loop1-6_state.yaml`：正式配置使用的结构化剧情状态。
3. `planning/`：复制的 Unit2 人物、场景、证据链、小玩法、美术和衔接资料。
4. `/Users/tisrashi/NDC_project/avg_editor_v2/data/table/`：只读旧配置蓝图。
5. `/Users/tisrashi/NDC_project/AVG/EPI02/`：只读旧生成结果，仅用于差异检查。

`preview_new2` 明确排除，不参与任何配置判断。

## 目录规则

- 只修改本目录中的副本，不回写原目录。
- `generated/numbered/` 只能由本目录 `scripts/assign_unit2_dialogue_ids.py` 生成。
- `generated/json/` 只能由本目录 `scripts/sync_to_json.py` 生成。
- Unity 正式配置只修改 `/Users/tisrashi/NDC/res/xls/*.xlsx`。
- `Assets/table/*.json` 和 `Assets/Resources/table/*.bytes.txt` 必须由 `Translate.exe` 从 Excel 生成。
- 禁止使用 `json_to_excel.py`。

## 固定角色 ID

- 201 Zack
- 202 Emma
- 203 Morrison
- 204 Frank
- 205 Mickey
- 206 O'Hara
- 207 Leonard
- 208 Moore
- 209 Tony
- 210 Vinnie
- 211 Danny
- 212 Lula
- 213 Margaret
- 214 Edith
- 215 Foster
- 216 Earl Hirsch
- 217 TideWater Liaison

## 来源完整性

`source_manifest.json` 记录创建副本时的源 Git 提交与 SHA-256。运行以下命令确认所有原文件仍未改变：

```bash
python3 Unity正式配置输入/Unit2/scripts/source_manifest.py --verify-originals
```

修正版配置稿允许与初始副本哈希不同；验收只要求原始文件哈希保持不变。

