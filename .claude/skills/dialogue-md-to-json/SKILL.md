---
name: dialogue-md-to-json
description: "把 Unit9 的对话 MD 草稿（Talk + Expose）落地到 AVG/EPI09/ 下的 JSON 配置。三段式：LLM 跨表预检 → py 脚本 dry-run → 用户确认后写入。预检会校验 NPC 名、get/Lie 引用的 testimony/item ID 是否在配置表中真实存在。"
argument-hint: "[Loop 编号 1-6，可选；不给跑全部 6 个 Loop]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
---

把 Unit9 对话 MD 草稿同步到 JSON。**目标：`AVG/EPI09/Talk/loop{N}/*.json` + `AVG/EPI09/Expose/*.json`**。

> **范围**：当前只支持 Unit9（→ EPI09）。其他 Unit 不要走这个 skill——EPI01/EPI02 直接命令行用 `sync_to_json.py --episode EPIxx`，EPI08 已废弃。
>
> 后续若要支持新 Unit/Episode，需扩展 `sync_to_json.py` 的 NPC 映射表（不在本 skill 范围）。

## 设计原则：LLM 不直接写 JSON

底层 py 脚本已经成熟（[AVG/对话配置工作及草稿/sync_to_json.py](../../../AVG/对话配置工作及草稿/sync_to_json.py)，1050 行）。本 skill 的价值是**包装 + 跨表预检**：

| 阶段 | 谁干 | 输入 | 输出 |
|---|---|---|---|
| Phase 1 | **LLM**（按本 SKILL 预检清单） | MD 草稿 + 4 张配置表 | 预检报告（不一致列表） |
| Phase 2 | **py 脚本** `--dry-run` | MD 草稿 | 新建/同步条数预览 |
| Phase 3 | **py 脚本** 实际写入 | MD 草稿 | JSON 文件 + 写入报告 |

**LLM 完全不写 JSON**。py 脚本不做跨表校验（那是 LLM 的活）。

## 输入约定

| 参数 | 必需 | 说明 |
|------|------|------|
| Loop 编号 | 否 | `1`-`6`；不给则跑 Unit9 全部 6 个 Loop |

调用示例：
- `/dialogue-md-to-json` → 跑 Loop1-6
- `/dialogue-md-to-json 3` → 只跑 Loop3

**默认参数**（写死，本 skill 范围内不可改）：
- `--episode EPI09`
- MD 路径前缀 = `AVG/对话配置工作及草稿/Unit9/Loop{N}_生成草稿.md`

## 处理范围

| 文件类型 | 输出位置 |
|---|---|
| `## Talk: xxx.json` 段 | `AVG/EPI09/Talk/loop{N}/xxx.json` |
| `## Expose: LoopN_xxx.json` 段 | `AVG/EPI09/Expose/LoopN_xxx.json` |

`sync_to_json.py` 通过文件名前缀（`loop` / `Loop`，大小写不敏感）判断是 Talk 还是 Expose。

## Phase 1: LLM 跨表预检

### 加载的依赖表

按 Loop 处理时，**全量加载**以下 4 张表（用于跨 Loop 引用校验）：

| 表 | 路径 | 用途 |
|---|---|---|
| NPCStaticData.json | `preview_new2/data/table/NPCStaticData.json` | NPC 中文名 → ID 映射，校验 speaker |
| TestimonyItem.json | `preview_new2/data/table/TestimonyItem.json` | 校验 `get → {ID}` 引用的 testimony 存在 |
| ItemStaticData.json | `preview_new2/data/table/ItemStaticData.json` | 校验 `Lie` 行可用证据 ID 存在 |
| SceneConfig.json | `preview_new2/data/table/SceneConfig.json` | （可选）校验场景 ID |

> **跨 Loop 引用合法**：Loop3 的 `get → 9011002`（引用 Loop1 的证词）合规。预检要把 Loop1-N 的 testimony 全部加载，不限制只校验本 Loop。

### 预检清单（按优先级）

#### A. 结构性错误（必须拦截）

- [ ] MD 文件存在：`AVG/对话配置工作及草稿/Unit9/Loop{N}_生成草稿.md`
- [ ] 每个 `### {id}` 标题是 9 位数字（格式 `{loop}{scene}{seq}`）
- [ ] 每个对话条目都有 `**说话人**`（旁白除外）
- [ ] 每段 `## Talk: xxx.json` / `## Expose: xxx.json` 文件名格式合法（含 `.json` 后缀）

#### B. 跨表引用错误（默认拦截，可强行写入）

- [ ] `` `get` → {testimonyId} `` 中的 testimonyId **存在于 TestimonyItem.json**（不限本 Loop，跨 Loop 合法）
- [ ] `Lie` 行的 `🎯 可用证据: {ids}` 每个 ID **存在于 ItemStaticData.json**
- [ ] 分支 `→ {id}` 跳转目标 **存在于本 MD 文件内**
- [ ] `→ 汇合至 {id}` 目标存在于本 MD 文件内

#### C. NPC 警告（不拦截，列出由用户决定）

- [ ] 每个 `**说话人**` 中文名在 `NPC_SPEAKER_MAP_EPI09`（即 EPI08 映射表）中
  - 找不到 → 标记为"警告"（py 脚本会留空 IdSpeaker，后续可手补）
  - 一次性临时角色（如"酒保"、"路人"）允许，但要列在报告里让用户确认

#### D. 软提示（不拦截）

- [ ] 提到具体物品时，物品名是否与 `ItemStaticData[id].Describe` 一致（仅做粗扫，由 LLM 判断）
- [ ] `## Expose:` 段的 `Lie` 步骤数量 ≥ 1

### 预检报告格式

```
## Phase 1 预检报告 — Unit9 Loop{N}

### A. 结构性 ✅/❌
- emma_001.json: 37 条对话，全部合法
- 异常: 第 901001234 行缺少 speaker

### B. 跨表引用
- ✅ get 引用: 12 处全部命中 TestimonyItem
- ❌ Lie 可用证据: Loop1_rosa.json 第 R2 引用 ID 9999（不在 ItemStaticData）

### C. NPC 警告
- ⚠️ 901001005: '酒保' 不在 NPC 映射表（IdSpeaker 将留空）

### D. 文件清单
- 将新建/同步:
  - AVG/EPI09/Talk/loop1/emma_001.json [新建 37 条]
  - AVG/EPI09/Talk/loop1/vivian_001.json [新建 30 条]
  - AVG/EPI09/Expose/Loop1_rosa.json [新建 34 条]
- 总计: 5 个文件，160 条对话
```

### Phase 1 决策点

如有 **B 类错误**，AskUserQuestion：
- "我先去改 MD 修引用错误"（推荐，停下）
- "强行写入（escape hatch，错误 ID 会进 JSON）"
- "取消本次同步"

如只有 C 类警告 / D 类软提示，AskUserQuestion：
- "OK，跑 dry-run"
- "我先看看报告"
- "取消"

## Phase 2: py 脚本 dry-run

```bash
cd "AVG/对话配置工作及草稿"
python sync_to_json.py Unit9/Loop{N}_生成草稿.md --episode EPI09 --dry-run
```

把脚本输出原样呈现：
- 每个文件：`[NEW] 将生成 N 条` / `[SYNC] N 处变更` / `[OK] 无变更`
- 警告（如未知 speaker）

AskUserQuestion：
- "确认写入"
- "我再调 MD"
- "取消"

## Phase 3: 实际写入

```bash
python sync_to_json.py Unit9/Loop{N}_生成草稿.md --episode EPI09
```

检查退出码 + stderr：
- 成功：输出最终报告（写入条数 + 路径）
- 失败：把错误原样呈现，停下，**不要重试**

### 多 Loop 模式

不带 Loop 编号调用时，**逐 Loop 处理**（不一次性 `--all`，因为 py 的 `--all` 只看根目录，不会进 `Unit9/`）：

```python
for loop_n in range(1, 7):
    # Phase 1 预检 Loop{loop_n}
    # Phase 2 dry-run
    # Phase 3 写入
```

每个 Loop 走完整三段式。如某 Loop Phase 1 拦截，AskUserQuestion 选"跳过本 Loop 继续下一个"或"全部停下"。

## 不要做的事

- **不要直接编辑 `AVG/EPI09/**/*.json`**：所有写入走 sync_to_json.py
- **不要碰 EPI01 / EPI02 / EPI08 的文件**：本 skill 锁定 EPI09
- **不要碰 MD 草稿** 除非用户明确要求修一行：MD 是源头，由 narrative 设计师维护
- **不要扩展 sync_to_json.py 的 NPC 映射表**：那是阶段 B 的事
- **不要写英文翻译**：MD 只写中文，英文留空，由后续批量翻译流程补
- **不要在 Phase 1 / 2 失败后跳到 Phase 3**：每个阶段都必须用户明确确认
- **不要假设 Loop 编号**：参数没给就跑全部 6 个，不要默认某一个 Loop

## 与现有工具的关系

- `sync_to_json.py`：本 skill 调用的底层工具，已加 `EPI09` 分支（沿用 8XX NPC 编码）
- `extract_to_md.py`：反向 JSON → MD，本 skill 不调用，但用户可手动跑做往返一致性验证
- `state-to-table` skill：处理非 Talk/Expose 的配置表（DoubtConfig / ItemStaticData / SceneConfig 等）
- `team-dialogue` skill：写 MD 草稿（本 skill 的上游）
- `team-expose` skill：写 Expose MD 草稿（本 skill 的上游）

## 后续步骤（不在本 skill 范围）

1. JSON 写入完成 → 用户在 preview 页面验证对话流
2. JSON 同步到 Unity 工程 → 独立流程
3. 英文翻译批量补 → 独立流程

## 工作流总览

```
用户调用 /dialogue-md-to-json [LoopN?]
   ↓
Phase 1: LLM 读 MD + 4 张表 → 预检报告 → 用户确认
   ↓
Phase 2: py --dry-run → 新建/同步预览 → 用户确认
   ↓
Phase 3: py 实际写入 → 写入报告
   ↓
完成
```
