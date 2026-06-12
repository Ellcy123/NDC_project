# config-edit 踩坑清单（配置实战经验）

> 核心：多数事故**不是文案错，而是"剧情意图"和"配置事件链"没对齐**。
> 本 skill 只改 `avg_editor_v2/data/table`，不碰 Talk / Unity 打表。所以下面分两部分：
> ① 改我们表时**直接相关**（改前/校验时盯这些）；② **下游交接注意**——Talk/Unity 那条链本 skill 不改，但我们配的 events/资源名/证据会喂给它，落地时要提醒人。

## 一、改我们表时直接相关

### 1. comic 坐标要换算（配 `events.req` 时）
美术给的是 **2560×1600、左上角原点**坐标；comic 运行时用的是 **UI 中心锚点**坐标。req 里若直接抄美术坐标 → "图是对的，位置飞了"。
→ 写 events.req 的坐标时，标明"美术左上角原始坐标，落地 comic 需换算到中心锚点"，别当成最终值。

### 2. 全屏图 vs comic 叠图要分清
`l5_alley_headlights_01` 这种**全屏图 = 场景背景底图(scene_bg)**，不是 comic 叠图；`_02/_03/_04/_05` 才是叠加分镜。
→ 配 events：首格若是全屏铺底，应归底图；后续分格才是 comic 叠加。别把全屏图塞进叠图链。

### 3. 证据/证词/疑点的"获得时机"
搜证获得 / 指证后获得 / 仅展示道具，是三种不同来源。放错（指证后才得的塞进疑点 condition、展示道具当搜证物）→ 提前出现 / 无法提取 / 指证选项数量不对。
→ 疑点 condition 放“玩家在进入指证前必须已经拿到、且会触发当前怀疑的问题”的材料。普通 NPC `get` 默认不进疑点；但**指证要用的证词谎言 / 关键证词材料**必须进入对应 Loop 的疑点或碎片条件里。指证后才获得、或纯展示不入背包/证词池的内容，仍不作为前置疑点。

### 4. 地图解锁是独立状态链
获得地址 ≠ 地图自动有点。要 `MapConfig` 有该点 + 坐标 + `ChapterConfig.map2Scenes` + 解锁事件，缺一就不显示。
→ 新增地点别覆盖/挤掉初始酒吧等已有点位。改 map2Scenes 时连带核对 MapConfig。

### 5. 旧残留不能只看"文件在不在"
旧对白/旧 repeat/旧 NPC 行/旧资源路径可能还挂着但已失效。判断"有效" = 看是否被 **Scene/NPC/Loop/Map/Expose 入口真实引用**。
→ 改/删前先反查引用（validate.py 的外键检查覆盖一部分；删主键前必查"被引用"处）。

## 二、下游交接注意（本 skill 不改，但要提醒人）

### 6. 事件挂在哪一句 = 立刻触发
`comic / exhibit / get / new_npc_in / npc_out / change_scene / loop_end / finalexpose` 都是**当前对白一出现就触发**，不是这句播完才触发。例：`BANG!!` 挂在遗言那句 → 遗言刚冒出来枪就响。
→ 配 events 时在 req 里写清"该挂在哪句话触发"，别让接 Talk 的人挂错句。
→ `new_npc_in` 如果想表现“NPC 打断当前人说话后入场”，应挂在入场发生的那句；如果想等上一句完整播完再入场，就要挂到下一句，不要挂在上一句。


### 7. 人物入退场不是美术事件本身
`new_npc_in / npc_out` 是 Talk 脚本，不是 `ArtAssetConfig.events[]` 的运行时来源。只有入退场需要特殊分镜、镜头、拟声提示或整段表演时，才在底图 `events[]` 里写美术需求。
→ 普通入场：检查 NPCLoopData + Talk 参数即可；不要为了“有人进来”强行新建 event。
→ 需要表演：event.req 里必须写清 Talk 挂点、入场 NPC、提示文本、是否同步补 SceneConfig.NPCInfos。

### 8. change_scene 不能硬 next 到下一句
切场景后直接 `next` 接对白 → 旧面板/旧背景/黑底残留。稳妥：切到新 Scene → 用新 Scene 的 firstEnterTalk 接后续 AVG。

### 9. finalexpose / loop_end / end 别混
`finalexpose`=开指证结算/黑底面板；`loop_end`=循环结束结算；`end`=单纯对话结束。配错 → 突然黑 / 结算提前 / 场景断。

### 10. 对白左右显示是"场景语义"不是"整段人物语义"
同一批 ID 前半在大厅、后半在押走/后巷，不能一刀切全改左/右。

### 11. 源 JSON → xlsx → 生成表 三处一致
Unity 读的是打表后的 `Assets/table` + `bytes`；JSON 对了但 `Talk.xlsx` 残留旧 script 也白搭。
→ **本 skill 只在 avg_editor_v2，不碰这条链**。凡涉及"要进游戏"，提醒人走 xlsx + 打表(Translate.exe) + 三处核对。

## 检查顺序（配置正确性推荐链路）

```
剧情意图 → 入口场景 → 对话链 next → script 触发点 → 资源路径/坐标 → xlsx → 生成表 → Unity 表现
└──────── 本 skill 覆盖 ────────┘                                    └──── 下游，出"交接提醒" ────┘
```
本 skill 管前段（入口场景 / 资源路径坐标 / 设计期表）；中后段（对话链 / script / xlsx / 打表 / Unity）归下游。


