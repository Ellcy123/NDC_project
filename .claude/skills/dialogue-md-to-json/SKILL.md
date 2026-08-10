---
name: dialogue-md-to-json
description: "把 Unit1 EPI01 完整台本中的中英文 Words 安全回写到本地 AVG/EPI01，并验证 1690 个正式 ID、场景与跳转完全一致。"
argument-hint: "[可选 --check-only；默认先检查，写入前必须再次确认]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

# Unit1 正式台本 → 本地 AVG/EPI01

当前 Unit1 已统一为 Unit1 / EPI01 / 1xxx。旧 Unit9 / EPI09 / 9xxx 只在
`canon_manifest.json` 指向的历史归档中存在，绝不能作为当前输出目标。

## 真源与边界

- AI 可读台本：`AVG/对话配置工作及草稿/Unit1/Loop{1-6}_完整台本.md`
- 本地正式 AVG 镜像：`AVG/EPI01/`
- Unity 运行时真源：`D:\NDC\Assets\table\Talk.json`
- 重建工具：`AVG/Tools/rebuild_unit1_runtime_script.py`
- 文本回写工具：`AVG/Tools/sync_unit1_script_to_json.py`

`sync_unit1_script_to_json.py` 只允许更新本地 JSON 的 `Words` 中英文文本；ID、说话人、
`next`、分支、script、参数、场景归属和演出字段只校验、不生成、不改写。该工具永远不写
`D:\NDC`。

如需改分支选项、入口、脚本参数、说话人或演出字段，本 skill 必须停止并报告：这超出
文本同步范围，需要先扩展专用迁移器，不能用旧 `sync_to_json.py` 冒险写入。

## 三阶段流程

### Phase 1：正式结构检查

```powershell
python AVG/Tools/rebuild_unit1_runtime_script.py --check-only
python AVG/Tools/sync_unit1_script_to_json.py
```

必须同时满足：

- Markdown 与 AVG 都是 1690 个唯一 ID；
- missing、scene mismatch、loop mismatch、routing mismatch 全部为 0；
- SceneConfig、ExposeData、get/指证材料引用校验通过。

任何结构错误都拦截，不允许写入。

### Phase 2：差异报告

把 `sync_unit1_script_to_json.py` 的 `Text changes` 数量与涉及文件数原样报告给用户。
同时说明写入只影响项目内 `AVG/EPI01`，不会同步 Unity。没有文本变化时直接结束。

### Phase 3：用户确认后写入

只有用户明确确认后运行：

```powershell
python AVG/Tools/sync_unit1_script_to_json.py --write
python AVG/Tools/sync_unit1_script_to_json.py
python AVG/Tools/rebuild_unit1_runtime_script.py --check-only
```

写入后第二次检查必须回到 `Text changes: 0`，且全部结构校验仍为 0。

## 禁止事项

- 不直接调用旧 `AVG/对话配置工作及草稿/sync_to_json.py`；它只保留解析库能力，CLI 已禁用，Unit2 由 `sync_unit2_to_json.py` 包装调用。
- 不写 `AVG/EPI09`、`AVG/EPI08` 或任何 Unit9/Unit8 目录。
- 不把归档 EPI09 的动作、说话人或旧台词覆盖到正式 EPI01。
- 不直接改 Unity 表；Unity 同步是独立发布步骤，需要用户另行授权。
- 不在 Phase 1 失败或未获确认时运行 `--write`。

## 从 Unity 重新建立台本

当用户明确要求以 Unity 当前表覆盖项目镜像时，先执行只读检查，再把输出写到临时目录验收：

```powershell
python AVG/Tools/rebuild_unit1_runtime_script.py --check-only
python AVG/Tools/rebuild_unit1_runtime_script.py --avg-output-dir .tmp/unit1_epi01_rebuild
```

只有验证 60 个文件、1690 行、1690 个唯一 ID 后，才可在用户确认下替换 `AVG/EPI01`。
