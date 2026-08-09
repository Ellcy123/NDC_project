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
- 218 City Hall Doorman

## 正式配置覆盖

- `planning/Unit2_正式配置覆盖说明.md` 记录了新旧文档冲突的最终裁定；它只补充派生快照，不回写原策划文档。
- 六个 `state/*.yaml` 底部的 `formal_config` 是正式配表覆盖层，共列出 44 个当前对白段。
- 当 state/planning 旧描述与正式对白冲突时，以 `dialogue/LoopN_正式配置稿.md` 和 `formal_config` 为准。
- `planning/Unit2_Unity正式配置完整方案与审查结论.md` 记录实际落表数量、六轮逐点流程、证据/疑点/指证映射和当前验收状态。

## 生成和验证

```bash
# 由已编号 MD 重建 44 个中间 JSON 段
python3 Unity正式配置输入/Unit2/scripts/sync_to_json.py --all --reconcile --purge --episode EPI02

# 由独立输入副本重建 U2 正式 Excel
python3 /Users/tisrashi/NDC/res/build_u2_formal_config.py --all

# 读取 Excel 和 runtime bytes 做跨表/六轮流程验证
python3 /Users/tisrashi/NDC/res/validate_u2_formal_config.py
```

当前中间输出为 44 个 JSON 文件、2038 个唯一 Talk ID。正式 Talk 另增加 24 条无副作用 repeat Talk，因此 U2 正式 Talk 总数是 2062。

Expose 中间 JSON 的 `correctNext` 是配表用的正确对白路径元数据；`ParameterInt0` 按当前 Unity 运行时语义保存成功后 Zack 连续台词数，不再保存 Talk ID。

## 来源完整性

`source_manifest.json` 记录创建副本时的源 Git 提交与 SHA-256。运行以下命令确认所有原文件仍未改变：

```bash
python3 Unity正式配置输入/Unit2/scripts/source_manifest.py --verify-originals
```

修正版配置稿允许与初始副本哈希不同；验收只要求原始文件哈希保持不变。
