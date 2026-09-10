# NDC_project

1920 年代芝加哥背景的侦探推理游戏 **内容设计与预配置工作区**。玩家扮演侦探 Zack Brennan，通过对话、证据收集、时间循环机制解谜。

本仓库产出（对话、证据、配置表等）最终同步到独立的 Unity 工程。文中 `D:\NDC` 等旧机器地址仅是历史示例；美术工具按以下配置解析实际位置，不要求固定盘符或目录名。

## 美术生产与收尾（2026-09-05 用户确认）

美术生产前读取 `docs/美术生产工作区.md`。静态美术 Skill 主实现维护在本仓库 `.codex/skills/`；H3 视频生成、双音频调用、交付处理三个主实现维护在工程仓库 `.codex/skills/`，本仓库对应目录仅作兼容入口。角色卡唯一索引为 `美术资产交付/角色/角色索引.json`，表情配对索引为 `美术资产交付/角色表情/表情索引.json`。

任何实际 Photoshop MCP 操作还必须先完整读取 `production/art_pipeline/PS_MCP_操作参考手册.md`，并在当前作业记录手册版本、SHA-256 和当前会话能力快照。该文件与维护工作区根目录的 `PS_MCP_操作参考手册.md` 必须字节一致；不允许使用旧缓存替代。手册约束通用效率、抠图、Alpha、路径、单引擎、超时回退和视觉/技术验收，具体 Skill 的授权、内容和专用门禁仍优先，实时目录只执行 `supported` 能力。

Photoshop MCP 已实际导出可打开的非生成 RGBA 后，即使提取不完整或低置信度，也要保留提取前原图与 SHA-256、尝试 RGBA、恢复 PSD／蒙版／路径／动作证据、多底预览和缺陷记录，标记 `PROVISIONAL_EXTRACTION_PENDING_USER_REVIEW`，继续清晰标记的 provisional 合成、规格派生、Map／XY、重建及整包检查。原图和全部继承状态的派生件进入项目外 `工作过程文件` 的独立待用户审核交付包；不得进入正式美术目录、冒充 PASS 或覆盖历史。用户审核／修正后建立新修订并重跑受影响门禁；完全没有合规 RGBA 输出以及语义、身份、结构、文字、承托等非提取问题仍按原规则阻断。

Photoshop MCP 的单个命令、动作、按钮或输出失败不能代表 Photoshop 整体能力耗尽。提取任务必须按当前手册建立独立路线耗尽日志，对所有材质适用、授权范围内且端到端命令为 `supported` 的非生成路线逐条实测并保留回执、输入／输出哈希、视觉结论和失败点；同一原样命令最多重试一次，但要继续下一条独立路线。正式 RGBA 通过后可停止，否则只有所有适用路线均有执行或不适用／不受支持证据时才能登记整体失败。选区无法落实 Alpha 只阻断该路线；已导出但仍含场景矩形的 Remove Background 结果属于 provisional／质量失败输出，必须保留并继续其它路线及 provisional 下游。未另行明确授权时不得用 Computer Use／界面自动化补位。

角色入场景的同一场景默认优先完成、回收、提取前审核并冻结全部必需角色／状态的正式生成或合法复用源，再统一安排抠图、去背景、Alpha、注册与合成；这是优先调度，不是硬门禁。网页生成、回收或浏览器传输真实等待／受阻，或有其它可记录的具体调度理由时，可先处理已经就绪角色的合规 Photoshop 提取和独立下游工作，避免空转。例外须记录原因、完整 scope、已就绪与未就绪项及恢复顺序，不得漏项、把局部结果当整场完成，或绕过候选、提取与最终验收门禁。旧任务已有提取结果正常续用。

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

## 修改确认范围

**只有大范围改动，以及改变剧情或策划含义的修改，才需要先展示具体方案或"改前 → 改后"示例并等待确认。小修、常规脚本修改和不改变设计含义的修正，可在用户已授权的任务范围内直接执行。**

- 需要确认的剧情 / 策划修改：改变人物事实、关系、动机、台词含义、信息揭示节奏、证据链、谜题逻辑、疑点条件、指证结构或玩法规则；即使只改一行也按此执行。
- 需要确认的大范围改动：跨模块架构重构、批量改变正式数据结构或 ID / 引用体系、大范围内容重写等。按实际影响判断，不单凭文件数量或修改行数判断。
- 可直接执行的小修：错别字、标点、排版、链接修正，以及不改变剧情 / 策划含义的局部代码修复、常规脚本修改和实现细节调整。脚本若会改动上述剧情 / 策划内容或产生大范围影响，仍需先确认。
- 对需要确认且尚未获授权的修改，先用纯文本展示真实旧内容与拟改内容；新增内容展示具体草案。涉及多种不同类型的实质改动时，每种类型各举一个例子。确认前可继续读取、检索、分析和准备方案，不提前写入待确认的修改。
- 用户明确给定具体改法，或已回复"对 / 可以 / 执行 / 开始"等确认方案后，在该范围内直接完成，不重复询问。只有新增或超出已确认范围的实质改动才重新确认。
- 单纯读取 / 查询 / 检索 / 列表展示不需要确认。
- 本条收窄通用修改确认范围；Unit1 台本回写 JSON、美术成品交付工程等专门流程的明确授权要求，仍按各自条款执行，已有授权不重复索取。

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

收到策划文档类任务时，按下表使用对应 skill。对白文字创作默认使用 `.codex/skills/ndc-dialogue/SKILL.md`；其他设计任务保留专用团队编排。

| 任务类型 | 使用方式 |
|---------|---------|
| 单场景/单 NPC 设计 | `/team-design` |
| 写对白、优化对白、单场景或整 Loop / Unit 补对话 | `/ndc-dialogue`；`/team-dialogue` 默认也转到此流程 |
| 完整指证设计 | `/team-expose` |
| 整个 Loop 规划（证据→指证→state→对话→审查） | `/team-loop` |
| Unit 大纲 → 6 个 state 文件 | `/unit-state-generator` |
| State YAML → 配置表 JSON（非 Talk/Expose） | `/state-to-table` |
| 全流程体验审计 | `/playthrough-audit Unit1`（~15 分钟，输出交互式 HTML 报告） |
| 简单改非对白文案/小修 | 不开 team，直接做；对白润色默认 `/ndc-dialogue` |

Agent 定义见 `.Codex/agents/`（14 个角色），编排逻辑见对应 skill 的 `SKILL.md`。

### 默认对白流程（2026-09-07 用户确认）

- 当前窗口模型负责读取剧情来源、控制人物知识与信息揭示、写完整初稿，并亲自编写每轮润色提示词；经 NovAI 显式调用 `[次]gemini-3.8-flash`，附初稿、信息边界和 skill 内保存的 Nyra 提示词全文做重写级润色；主模型最后核对事实和结构，保留润色后的语言风格。
- 用户指定的磕点、搞笑、压抑等情感效果属于每轮提示词的核心要求，不作为末尾的可选修饰；未要求时不默认加磕点或搞笑。用户的新反馈覆盖冲突的旧要求，其余目标与喜欢的内容持续保留。
- 多轮都按“主模型理解反馈、控信息并写提示词 → 同一 Gemini 3.8 润色 → 主模型核对信息”推进。默认每次请求一轮，用户授权多轮时按约定推进；不默认开审查团队或以主模型个人审美追加试验。用户当次指定的流程和模型优先。
- 上述流程也适用于其他设计 skill 中的对白文字产出阶段；谜题、State、指证步骤、证据、Repeat 路由和正式配置仍由原专用流程负责。`team-dialogue` 的旧多代理全流程仅在用户明确要求团队审查时启用。
- 详见 `.codex/skills/ndc-dialogue/SKILL.md`。中间稿不自动同步 JSON、预览配置或 Unity；项目文件的修改与同步仍遵守已有授权和两阶段规范。

### 轻量模型执行白名单

未列入下表的任务与步骤继承当前对话模型，不固定绑定 Astra 或其他高阶模型。用户为当前任务指定的模型优先。

下表绑定的是执行子代理的模型，不是 Midjourney、image_gen、H3、Seedance 或抠图工具实际使用的生成 / 处理模型，也不会切换主对话模型。需要分派独立子任务，且主代理同时有可推进的工作时，按表使用子代理；一次工具调用即可完成的小步骤由当前代理直接执行，避免为换模型额外开代理。

| Skill / 子流程 | 可绑定的执行范围 | 子代理模型 | 思考强度 |
|---|---|---|---|
| `runninghub-h3-ref2va-audio` | 提示词、参考素材、节点和预算已确定后的上传、dry-run、提交、查询、下载与任务记录 | `gpt-5.6-sol` | `medium` |
| `dreamina-cli` | 提示词、素材和参数已确定后的命令核对、提交、查询、下载；不负责创作提示词或选择生成模型 | `gpt-5.6-sol` | `medium` |
| `novai-gemini` 对白写作 / 返修操作员 | 按已确定的材料、提示词和模型参数调用 Gemini，取回并原样交接结果；不代写对白或承担内容审核 | `gpt-5.6-sol` | `medium` |
| `ndc-midjourney-operator` | 已通过交接检查的单轮网页操作：按指定提示词和参考角色提交、读取任务状态、执行已授权下载 | `gpt-5.6-sol` | `medium` |
| `ndc-h3-avatar-delivery` | 候选、增益、裁切边界和目标均已确定且获授权后的处理脚本、技术校验、staging 与记录更新 | `gpt-5.6-sol` | `medium` |
| `ndc-generate-expressions` | 输入及缩放 / 位移参数已确定后的 E5 非最终交接打包、E7 双规格合成、校验图制作和文件 / 收据校验 | `gpt-5.6-luna` | `medium` |
| `ndc-coordinate-image-edit` | 原图、区域、遮罩和参数已确定后的 prepare / compose / scan 脚本执行、像素差异与尺寸报告 | `gpt-5.6-luna` | `medium` |
| `dialogue-md-to-json` | 运行现有结构检查、报告差异数量、执行已明确授权的 Words 回写并复查；不修复或改写剧情与路由 | `gpt-5.6-luna` | `medium` |
| `feishu-docs` | 批量读取原文 / 元数据、保留顺序和来源；不承担剧情或策划结论判断 | `gpt-5.6-luna` | `low` |
| `pm-dashboard scan` | 本地扫描与原样汇报统计；不包括 analyze、init、上传或任务进度修改 | `gpt-5.6-luna` | `low` |

- 分派时提供精确输入路径、已确定的提示词 / 参数、允许的输出目录、已有授权与预算，以及应返回的任务 ID、文件路径和校验结果。写文件的子代理必须有明确的文件责任范围，并知晓其他代理可能同时工作，不得撤销他人修改。
- 白名单只覆盖表内步骤，不把整个美术 Skill 交给轻量模型。剧情理解、提示词创作、镜头 / 站位设计、选图、视觉与听觉验收、返工诊断和最终放行仍由当前模型负责；每个阶段原有的审核要求继续执行，技术校验通过不能代替视觉 PASS。
- 输入不完整、需要改变设计或出现无法按既定流程处理的失败时，执行代理返回材料和问题，由主代理接回判断；不自行改动已确定的提示词、参考素材、裁切边界或追加付费尝试。模型或所需工具不可用时，由主代理接回并说明实际执行方式，不宣称已经使用指定模型。
- 美术 Skill 从公共 `skill NAME` 入口解析唯一主实现。此白名单不放宽用户确认、受管工作区、正式工程写入和受保护道具流程的边界；也不授权自动抠图，表情 Skill 的用户手工去背景流程保持有效。

#### Gemini 对白操作员固定分派

- Gemini 对白写作流程需要独立操作员时，创建子代理必须显式指定 `model="gpt-5.6-sol"`、`reasoning_effort="medium"`、`fork_turns="none"`，不能省略模型参数而继承主对话模型。用户为当前任务明确指定其他模型时，以用户指示为准。
- 操作员只执行当前窗口模型写定的提示词和参数，提交、查询并原样返回结果；不代写初稿、改提示词或承担内容判断。调用操作员与实际生成模型分开设置，不因操作员变轻量而改变 `[次]gemini-3.8-flash`。
- 只传本阶段必要的材料、路径、提示词、参数和授权，不继承主对话完整历史，不重复加载无关项目文档。每轮 Gemini 请求使用新上下文和独立 run ID，输入由主模型准备的本轮工作稿与反馈。
- 默认流程是“主模型控信息并写初稿/逐轮提示词 → Gemini 3.8 润色 → 主模型核对信息”。仅当用户明确选择旧 A/B 方案时，初稿操作员 A 和返修操作员 B 才必须新建为两个独立 worker，B 不继承 A 的生成过程。
- 指定模型不可用时，返回具体问题并说明实际执行方式，不得静默改用 Astra，也不得宣称已使用 Sol。一次固定脚本调用即可完成的小步骤仍按白名单总则由当前代理直接执行，避免为换模型额外开代理。

---

## 与 D:\NDC 的关系

- **NDC_project** = 内容设计、预配置、预览验证
- **D:\NDC** = Unity 游戏工程，包含运行时代码和最终资源
- 数据流向：state YAML → `/state-to-table` 写入 `avg_editor_v2/data/table/*.json` → 人工校验后同步到 `D:\NDC\Assets\table\`；Unit1 对话当前以 Unity 正式表反向重建的 EPI01 和完整台本为准
- 美术资源位于 `D:\NDC\Assets\Resources/`
