# NDC_project

1920 年代芝加哥背景的侦探推理游戏 **内容设计与预配置工作区**。玩家扮演侦探 Zack Brennan，通过对话、证据收集、时间循环机制解谜。

本仓库产出（对话、证据、配置表等）最终同步到独立的 Unity 工程。文中 `D:\NDC` 等旧机器地址仅是历史示例；美术工具按以下配置解析实际位置，不要求固定盘符或目录名。

## 美术生产与收尾（2026-09-05 用户确认）

美术生产前读取 `docs/美术生产工作区.md`。静态美术 Skill 主实现维护在本仓库 `.codex/skills/`；H3 视频生成、双音频调用、交付处理三个主实现维护在工程仓库 `.codex/skills/`，本仓库对应目录仅作兼容入口。角色卡唯一索引为 `美术资产交付/角色/角色索引.json`，表情配对索引为 `美术资产交付/角色表情/表情索引.json`。

从任一仓库根运行 `python -B scripts/art_pipeline/ndc_art.py configure --help` 配置本机三处路径；实际值保存在两库各自被 Git 忽略的 `ndc.local.json`，`paths` 查询，`skill NAME` 定位主实现。`production/art_pipeline/paths.json` 只维护团队预算和相对路径。Skill 必需的自有脚本、规则、模板和依赖清单必须随 Git 管理，不能只留在个人目录；第三方安装包、密钥、虚拟环境不进 Git。

新任务使用 `python -B scripts/art_pipeline/ndc_art.py workspace create`，图像/视频过程文件、候选和待确认成品全部放返回的项目外 `payload`。自检后展示具体成品，用户确认该版本后才交付工程。成功交付并校验副本，或用户明确取消后，关闭任务并清理临时大文件；等待确认、仍在返工、旧任务、角色卡和未安全保存的母版不可清理。兼容入口必须从 `skill NAME` 返回的唯一主目录解析支持文件。

道具 Skill 正由美术同学优化；本次整理不修改 `ndc-scene-evidence-placement` 及三个 `ndc-evidence-*` 子流程目录。道具打包经公共 `run` 入口检查受管输出，不能依赖旧脚本固定盘符的 Unity 禁写检查。旧子流程当前不兼容的命令不执行。公共路径、用户确认和三个本库校验器的映射以 `docs/美术生产工作区.md` 为准；艺术要求和原始审查门禁不因此放宽。并行兼容清单见 `production/art_pipeline/evidence_compatibility.json`。

---

## Canon 章节映射（重要）

章节身份、来源路径、完成度和历史版本的机器可读真源是仓库根目录的 `canon_manifest.json`。涉及 Unit / Episode / ID 段判断时，先读取该文件，不凭目录名猜测。

- 玩家第 1 章的唯一当前身份是 Unit1 / EPI01 / 1xxx；旧 Unit9 / EPI09 / 9xxx 已于 2026-08-10 完成迁移，仅存在于 Manifest 指向的历史归档。
- 玩家第 2 章的正式身份是 Unit2；Unit10 仅为策划标题来源别名，不计作额外章节。现行策划内容位于 `剧情设计/Unit1`、`剧情设计/Unit2`。
- Unit1 的策划 state、AVG、预览配置和 Unity 正式表统一使用 EPI01 与 1xxx，不再自动翻译或维护双 ID 空间。
- Unit2 当前保留 EPI02 与 2xxx；10xxx 只作为 Manifest 中的历史命名空间记录。
- 旧版内容只从 Manifest 的 `history[]` 所列归档路径读取，不能把归档内容当作当前既定事实。

---

## 目录结构

### 设计文档
| 目录 | 内容 |
|------|------|
| `第一章内容/` | EPI01 (Unit1) 剧情、场景、证据设计 |
| `第二章内容/` | EPI02 (Unit2) 剧情、场景、证据设计 |
| `第三章内容/` | EPI03 (Unit3) 剧情、场景、证据设计 |
| `剧情设计/` | 跨章节的剧情架构与循环设计 |
| `docs/` | 游戏系统设计文档（核心玩法、推理机制等） |
| `质量检查文档/` | 证据时序、谜题质量、逻辑自查清单 |
| `配置表规则/` | 各配置表的字段说明与填写规范 |

### 数据配置
| 目录 | 内容 |
|------|------|
| `AVG/` | 对话系统：按章节(EPI01/EPI02) → 类型(Talk/Expose) → 循环(loop1-6) 组织的 JSON 对话文件 |
| `AVG/对话配置工作及草稿/Unit1/` | EPI01 六个 Loop 的 AI 完整台本、索引、审查与迁移报告 |
| `AVG/Tools/` | Unit1 正式表重建、台本安全回写与对话验证工具 |

### 预览工具与配置表落地
| 目录 | 内容 |
|------|------|
| `avg_editor_v2/` | 当前预览网页 / 配置编辑器（流程图 + 证据表） |
| `avg_editor_v2/data/_table_drafts/Unit{N}/` | 按 Unit 组织的配置草稿中间层 |
| `avg_editor_v2/data/table/` | **当前预览配置表落地处**——全局合并 JSON；Unit1 使用 EPI01 / 1xxx |

### 脚本工具
| 目录 | 内容 |
|------|------|
| `AVG/Tools/` | 对话数据验证、Unity 正式表重建、Unit1 台本安全回写与引用审计 |

### 其他
| 目录 | 内容 |
|------|------|
| `Audio/` | 语音生成配置（ElevenLabs）、NPC 音色预设、音乐音效 |
| `image/` | 美术素材、角色立绘、背景图 |
| `美术对接文档/` | 美术资源命名规则、切图规范 |
| `旧文档/` | 已归档的旧文档（六章内容合集草稿、规划文档、AI生成等） |

### 工作流架构
| 目录 | 内容 |
|------|------|
| `.Codex/agents/` | 10 个专用 agent 定义（state-architect, dialogue-writer, expose-designer 等） |
| `.Codex/rules/` | 6 个路径作用域规则（编辑对应路径文件时自动加载） |
| `.Codex/skills/` | 4 个团队编排 skill（team-design, team-dialogue, team-expose, team-loop） + 工具类 skill |
| `.Codex/commands/` | slash command 定义（已迁移至 skills，目录保留备用） |
| `.Codex/hooks/` | 自动化校验脚本（对话格式、state 格式） |

---

## Game System Docs — Read On Demand (DO NOT use @ to auto-load)
These docs describe game mechanics in detail. Read the relevant one BEFORE working on related content:

| When you are... | Read this first |
|-----------------|-----------------|
| Writing/editing dialogue or testimony content | `docs/游戏系统/核心玩法/对话与证词系统.md` |
| Working with items, analysis, or combine logic | `docs/游戏系统/核心玩法/搜证与物品系统.md` |
| Modifying DoubtConfig or doubt unlock conditions | `docs/游戏系统/核心玩法/疑点系统.md` |
| Modifying ExposeData or writing Expose dialogue | `docs/游戏系统/核心玩法/指证系统.md` |
| Need full end-to-end reasoning chain overview | `docs/游戏推理机制完整规则.md` |

---

## 核心数据架构

### 层级关系

```
Chapter (章节: EPI01/EPI02/EPI03)
 └── Unit (单元: Unit1/Unit2/Unit3) — 与 Chapter 一一对应
      └── Loop (循环: loop1-loop6) — 每章 6 个循环，逐步揭示真相
           └── Scene (场景) — 每个循环包含多个调查场景
                └── Talk / Expose (对话 / 指证) — 场景内的交互内容
```

### ID 编码规则

**证据/道具 ID（ItemStaticData）：**
- EPI01: 1xxx 系列（loop1=11xx, loop2=12xx, ...）
- EPI02: 2xxx 系列（loop1=21xx, loop2=22xx, ...）
- 派生证据: 17xx (EPI01), 27xx (EPI02)

**对话 ID（Talk.id）：**
- 普通对话: 9 位 `{NPC:3位}{对话组:3位}{句序:3位}`
- 例: 105001001 = NPC 105 (Tommy) / 对话组 001 / 句序 001
- 指证对话: 6 位 `{轮次:2位}{序号:4位}`
- 例: 110001 = Loop1 指证 / 第 1 句

**证词 ID (TestimonyItem)：**
- 7 位 `{NPC:3位}{loop:1位}{seq:3位}`
- 例: 1031002 = NPC 103 (Rosa) / Loop1 / 第 002 条

### 数据格式分工

| 格式 | 用途 |
|------|------|
| **YAML** | state 文件 (`剧情设计/Unit{N}/state/loop{1-6}_state.yaml`) |
| **JSON** | AVG 对话文件 (Talk/Expose)、`avg_editor_v2/data/table/` 下的全局配置表 |
| **MD** | 设计文档、对话草稿（Phase 1 工作格式） |

---

## 主要工作流

### 1. AVG 对话（Talk / Expose）

**严格遵守两阶段流程：**

- **Phase 1**: Unit1 只修改 `AVG/对话配置工作及草稿/Unit1/Loop{1-6}_完整台本.md`，不碰 JSON
- **Phase 2**: 用户明确指示后才执行 `AVG/Tools/sync_unit1_script_to_json.py --write`；它只回写本地 EPI01 的 Words，不改 ID / 路由 / 脚本 / 参数，也不写 Unity
- 需要从 Unity 正式表重新覆盖时，使用 `AVG/Tools/rebuild_unit1_runtime_script.py`，先 `--check-only`，再写临时目录验证

详细的 MD 格式规范和审查清单见 `AVG/对话配置工作及草稿/AVG对话配置规则.md`。

**修改对话前必须先查阅对应章节的设计文档：**
| 章节 | 设计文档 |
|------|---------|
| EPI01 | `第一章内容/` |
| EPI02 | `第二章内容/` |
| EPI03 | `第三章内容/Unit3/` |

绝不凭记忆编写剧情细节。

### 2. 证据与谜题设计

设计文档 → state YAML（`剧情设计/Unit{N}/state/`）→ 配置草稿 / 配置编辑流程写入 `avg_editor_v2/data/table/*.json` → 预览验证 → 同步到 D:\NDC

关键约束：
- 每个场景/NPC 承载 1-3 个核心信息点，不超过 3 个
- 每轮循环只揭示一层真相，不在同一 Loop 解决多层疑问
- 疑点(Doubt)解锁推荐两种不同来源的信息交叉验证，以增强推理厚度；单件强证据/证词也允许直接触发疑点，由设计师基于谜题语境判断
- 指证硬约束：每一个指证步骤要出示的道具 / 证词，必须至少挂在某个疑点或疑点碎片的 `condition` 里；不存在"只在指证时出现、但没有进入疑点 / 碎片"的游离证据
- 时序硬约束：如果证据 X 在 Loop N 的指证中使用，那么 X 所属的疑点 / 碎片必须出现在 Loop N 或更早，不能把当前 Loop 指证要用的证据挂到后续 Loop 才点亮
- 查询或汇报疑点配置时，默认按"疑点 → 触发材料 → 是否指证用"说明，并标清哪些材料是"指证用"，哪些只是"触发疑点"

### 3. 配置表

- 落地处：`avg_editor_v2/data/table/*.json`（全局合并，16 张活跃表）
- 字段规范：[docs/配置表详解.md](docs/配置表详解.md)
- 数据流：
  - **非 Talk / Expose 的配置表**：state YAML → `/state-to-table` skill → JSON（增量按 ID 段合并）
  - **Unit1 Talk / Expose**：Unity 正式表 → `rebuild_unit1_runtime_script.py` → `AVG/EPI01` + AI 完整台本；台词文本回写使用 `sync_unit1_script_to_json.py`
  - **Expose 系列**：暂由专用流程或手动维护
- `_all_tables.xlsx` 是合并视图，仅供查看，由用户手动同步

### 3.1 avg_editor_v2 预览网页配置规则

`avg_editor_v2/data/table/*.json` 是预览网页 / 配置编辑器使用的设计期副本，不等同于 `D:\NDC\Assets\table\*.json` 的 Unity 运行时表。

预览副本可以保留少量 Unity 正式表没有的字段，用于网页定位、展示、校验和美术验收。同步到 Unity 前必须确认这些字段是否需要剥离，不能默认把预览字段当成 Unity 运行时字段。

#### 相对 Unity 表新增 / 强化的预览字段

下表中的“行定位”指 JSON 数组中的一条配置行；“列 / JSON 路径”指该行里的字段路径。

| 配置表 | 行定位 | 列 / JSON 路径 | Unity 正式表关系 | 预览网页用途 |
|------|------|------|------|------|
| SceneConfig | 每条 SceneConfig 行 | NPCInfos[].TalkInfo.id | Unity 可用入口字段 | 普通 NPC 对话第一句 Talk ID |
| SceneConfig | 每条 SceneConfig 行 | NPCInfos[].TalkInfo.videoScene | 预览增强字段 | AVG JSON 文件名，不带 .json，用于精准定位文件 |
| SceneConfig | 每条 SceneConfig 行 | NPCInfos[].TalkInfo.videoEpisode | 预览增强字段 | 标明章节，如 EPI01 / EPI02 |
| SceneConfig | 每条 SceneConfig 行 | NPCInfos[].TalkInfo.videoLoop | 预览增强字段 | 标明 loop，如 loop1 |
| SceneConfig | 每条 SceneConfig 行 | NPCInfos[].LoopTalkInfo.id | Unity 可用入口字段 | 重复点击 NPC 对话第一句 Talk ID |
| SceneConfig | 每条 SceneConfig 行 | NPCInfos[].LoopTalkInfo.videoScene | 预览增强字段 | 重复点击 AVG JSON 文件名，不带 .json |
| SceneConfig | 每条 SceneConfig 行 | NPCInfos[].LoopTalkInfo.videoEpisode | 预览增强字段 | 标明章节 |
| SceneConfig | 每条 SceneConfig 行 | NPCInfos[].LoopTalkInfo.videoLoop | 预览增强字段 | 标明 loop |
| SceneConfig | 每条 SceneConfig 行 | ArtRequirement | 预览增强字段 | 场景背景 / 环境音效美术需求 |
| NPCStaticData | 每条 NPC 行 | ArtRequirement | 预览增强字段 | 立绘 / 头像 / 表情图美术需求 |
| ItemStaticData | 每条道具行 | ArtRequirement | 预览增强字段 | 道具图标 / 模型 / 物件图美术需求 |
| MapConfig | 每条地图行 | ArtRequirement | 预览增强字段 | 地图小图标 / 地图表现需求 |
| ChapterConfig | 每条章节 / Loop 行 | ArtRequirement | 预览增强字段 | 章节封面 / 过场动画需求 |

#### NPC Talk 入口规则

`SceneConfig.NPCInfos[].TalkInfo` / `LoopTalkInfo` 在预览网页里必须优先显式挂载文件名和入口句：

```json
"TalkInfo": {
  "id": "103001001",
  "videoEpisode": "EPI01",
  "videoLoop": "loop1",
  "videoScene": "rosa_001"
}
```

解析优先级：

1. `videoScene + id` 精确定位，并校验 Talk ID 是否属于该 AVG 文件
2. 仅 `videoScene` 时，取该文件第一句作为入口
3. 仅 `id` 时，按旧配置兼容播放，但视为待补齐
4. NPC id / NPC 名字反查只作为历史兜底，不作为新配置规则

配置不一致时必须显式报错，不能静默改用 NPC 名字猜测。

---

## 游戏设计三大原则

以下三条原则是本项目一切内容设计（剧情、对话、证据、谜题、指证）的最高优先级准则，高于所有具体规则。

### 原则一：悬疑感优先——绝不提前破梗

- **这是游戏，不是电视剧。** 玩家必须自己思考、自己发现、自己推理。
- 角色对话中不能替玩家说出结论。Zack可以出示证据、指出矛盾，但不能像旁白一样解释"所以这说明……"。玩家要自己把逻辑链补完。
- **信息揭示严格按循环节奏**：每个Loop只揭示一层真相。后续Loop才揭晓的信息，在当前Loop中必须完全隐藏或伪装成无关细节。
- **藏梗 > 明示**：能藏的线索就藏（如脚印深浅暗示两人体重不同），让玩家回头看时恍然大悟。指证击破谎言后玩家"大概率会知道"，但在击破之前绝不能让答案显而易见。
- 对话中NPC的谎言、退守、狡辩都必须是NPC主动说出的自然反应，不是Zack喂话后的被动否认。

### 原则二：信息严密性——零矛盾、零漏洞

- 所有证据的物理属性（尺寸、时间、距离、品牌、价格）必须前后一致，跨循环引用时不能出现数值矛盾。
- 证词原文与提取摘要信息密度对等，不丢失关键限定词（时间、地点、人物、条件）。
- 每个NPC的陈述在其知识范围内必须自洽——即使在说谎，谎言本身也要有内在逻辑。
- 时序严格：证据获取时间不能早于其存在时间；角色不能引用尚未发生的事件。

### 原则三：逻辑闭环——每个谜题必须有严密指向 + 多方暗示

- **单一证据不定案（推荐但不强制）**：关键结论**推荐**用两种不同来源/类型的信息交叉验证（物证×证词、多方证词交叉、物证×物证等），以增强推理厚度。但单件强证据即可定案的情形也允许——由设计师基于谜题具体语境判断，不作为硬性拦截规则。
- **多方暗示、多种渠道**：同一个真相可以通过证据、环境细节、NPC反应、物品描述等不同渠道给出暗示，但每个暗示单独看都不足以确定结论——只有组合后才指向唯一答案。
- **谎言措辞精确匹配证据维度**：每轮指证的谎言必须精确到只有对应维度的证据能反驳。同一维度的证据不跨轮拆分，每轮用不同维度的证据打不同论点。

---

## 修改前先举例确认

**执行任何文件修改之前，必须先用文本举一个具体例子，让用户确认理解是否正确。用户确认"对"之后再执行真实修改。**

- 举例是纯文本展示（在对话中用代码块或引用贴出"改前 → 改后"的样例片段），**不要**直接调用 Edit/Write 工具改文件。
- 例子要具体到能看出意图：包含真实的旧内容片段和拟改写的新内容片段，而不是抽象描述"我会把 X 改成 Y"。
- 如果一次任务涉及多种不同类型的修改（例如同时改对话+改证据+改配置表），每种类型各举一个例子。
- 用户回复"对 / 可以 / 执行 / 开始"等确认后，才开始真正的修改。用户如果指出例子不对，按反馈调整后再举新例子，直到确认。
- 例外：单纯读取/查询/检索类操作（Read / Grep / Glob / 列表展示）不需要举例确认。

---

## 与用户讨论设计时的表述方式

聊设计问题时（疑点 / 证据 / 指证 / 对话的逻辑层面），先用大白话说清楚问题和改法，不要一上来就甩文件路径、行号、YAML diff、ID 变更等实现细节。

- **聊设计**：一两句话说清"问题是什么 + 为什么是问题 + 怎么改"。例如：「10502 这个疑点需要的证据全在 L5 指证之后才能拿到，L5 玩家根本看不到——应该当 L6 疑点处理」
- **不要聊落地**：除非用户主动问"具体动哪个文件"或"怎么改字段"，否则不要先讲文件路径、行号、YAML diff、ID 变更
- **场景判断**：
  - 找问题 / 讨论方向 → 大白话
  - 用户拍板要改 + 进入"修改前先举例确认"阶段 → 才上具体字段 / diff
- 用户说"看不懂"或"通俗说"时，立刻把刚才的回复砍成白话版本，去掉所有路径 / 行号 / 字段名

---

## Markdown 格式规则

- **表格单元格内不使用加粗(`**`)**——飞书无法正确识别，会显示为原始星号。需要强调的内容用文字本身表达（如加前缀 `→`、`!` 等）。

---

## 对话设计核心规则

17 条对话设计规则已外移至 `.Codex/rules/dialogue.md`（编辑 `AVG/` 或对话草稿文件时自动加载）。

完整版含示例见 `AVG/对话配置工作及草稿/AVG对话配置规则.md`。

---

### 4. 预览网站部署

本地预览使用 `avg_editor_v2/server.py` 或 `avg_editor_v2/start.bat`；当前仓库没有独立线上部署流程。

---

## 常用命令

```bash
# Unit1：从 Unity 正式表重建 / 校验 AI 台本与 EPI01
python AVG/Tools/rebuild_unit1_runtime_script.py --check-only
python AVG/Tools/rebuild_unit1_runtime_script.py --avg-output-dir .tmp/unit1_epi01_rebuild

# Unit1：完整台本文本回写本地 EPI01（写入前必须用户确认）
python AVG/Tools/sync_unit1_script_to_json.py             # 只读差异与结构检查
python AVG/Tools/sync_unit1_script_to_json.py --write     # 只写 Words，不写 Unity

# State → 配置表 JSON（非 Talk/Expose）：使用 /state-to-table skill，无独立 py 脚本

# 预览系统启动（从 D:\ 根目录启动，路径配置见 index.html 中 Config.paths）
python -m http.server 8080 --directory "D:\\"
# 访问 http://localhost:8080/NDC_project/avg_editor_v2/index.html

# 同步到 Unity 工程（手动 copy table JSON）
copy /Y "D:\NDC_project\avg_editor_v2\data\table\*.json" "D:\NDC\Assets\table\"
```

---

## Agent Team 编排

收到策划文档类任务时，使用 `.Codex/agents/` 下的专用 agent 和 `.Codex/skills/` 下的团队编排 skill。

| 任务类型 | 使用方式 |
|---------|---------|
| 单场景/单 NPC 设计 | `/team-design` |
| State 已定稿，整 Loop 补对话 | `/team-dialogue` |
| 完整指证设计 | `/team-expose` |
| 整个 Loop 规划（证据→指证→state→对话→审查） | `/team-loop` |
| Unit 大纲 → 6 个 state 文件 | `/unit-state-generator` |
| State YAML → 配置表 JSON（非 Talk/Expose） | `/state-to-table` |
| 全流程体验审计 | `/playthrough-audit Unit1`（~15 分钟，输出交互式 HTML 报告） |
| 简单改文案/小修 | 不开 team，直接做 |

Agent 定义见 `.Codex/agents/`（14 个角色），编排逻辑见对应 skill 的 `SKILL.md`。

---

## 与 D:\NDC 的关系

- **NDC_project** = 内容设计、预配置、预览验证
- **D:\NDC** = Unity 游戏工程，包含运行时代码和最终资源
- 数据流向：state YAML → `/state-to-table` 写入 `avg_editor_v2/data/table/*.json` → 人工校验后同步到 `D:\NDC\Assets\table\`；Unit1 对话当前以 Unity 正式表反向重建的 EPI01 和完整台本为准
- 美术资源位于 `D:\NDC\Assets\Resources/`
