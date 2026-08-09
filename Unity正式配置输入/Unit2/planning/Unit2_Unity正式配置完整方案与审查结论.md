# Unit2 Unity 正式配置完整方案与审查结论

> 日期：2026-08-10  
> Unity 分支：`u2-unity-formal-config`  
> 正式配置输入：`/Users/tisrashi/NDC_project/Unity正式配置输入/Unit2/`  
> 旧配置蓝图：`/Users/tisrashi/NDC_project/avg_editor_v2/data/table/`  
> `preview_new2` 明确不作为内容依据。

## 一、当前结论

U2 在“不包含音频、视频和尚未交付的专用美术”的范围内，已经具备完整正式配表数据：六个 Loop 的章节、场景、NPC、道具、对白、分支、证言、疑点、指证和结算链均已落到 Unity 正式 Excel，并已生成 JSON 和 runtime bytes。

当前的表级验收结果是通过：

- 6 个 ChapterConfig，24 个 ChapterStep。
- 10 个 MapConfig，46 个 LocationConfig，46 个 SceneConfig。
- 18 个 NPCStaticData，24 个 NPCLoopData。
- 82 个 ItemStaticData，包含 8 组 Type6/Type7 容器对、21 个门/楼梯导航项和 2 组合成。
- 2038 条正式草稿对白 + 24 条无副作用重复对白 = 2062 条 U2 Talk。
- 36 条 Testimony，35 个归一化 TestimonyItem，19 个 Doubt，18 轮 ExposeData。
- 6 条 `finalexpose` 和 6 条 `loop_end`，六轮指证后流程均能到达各自结束点。
- 原始对白、state 和策划文档 81/81 份 SHA-256 未变。

尚未完成的是 Unity Editor 内的最终导入/GM 跳转实机验收。当前 `/Users/tisrashi/NDC` 已被一个正在运行的 Unity 2022.3.62f2c1 实例打开，Unity 拒绝第二实例的 batchmode。这不是配表错误，但在现有 Editor 刷新/重启并完成 GM Loop 201–206 跳转前，不应把“实机可玩”标记为最终完成。

## 二、内容依据与冲突裁定

配置时的优先级如下：

1. `dialogue/Loop1-6_正式配置稿.md`：上周改过的对白文字和当前对白流程。
2. `state/loop1-6_state.yaml` 中的 `formal_config`：当前 44 个对白段、入口、后续段和覆盖规则。
3. 本目录 `planning/` 中复制的人物、场景、证据链、美术和衔接资料。
4. `avg_editor_v2/data/table/`：只提供旧场景、道具概念、资源路径和坐标蓝图，不覆盖新对白。
5. `AVG/EPI02/`：只用于差异检查。

已排除 `preview_new2`。旧蓝图与新对白冲突时，不会为了迁就预览页而退回旧剧情。

## 三、MD、state、NPC ID、分支和 evidence 解析修复

### 3.1 独立输入副本

六份对白 MD、六份 state YAML、全部 U2 策划目录、编号器和 JSON 同步脚本都复制到了新目录。修复只发生在这份副本内，不回写旧 MD、旧 state、旧策划文档或旧编辑器配置。

### 3.2 NPC ID

正式 U2 NPC 固定为：

| ID | 角色 | 处理 |
|---:|---|---|
| 201 | Zack | 全部 Zack 台词统一 |
| 202 | Emma | 全部 Emma 台词统一 |
| 203 | Morrison | L1/L6 |
| 204 | Frank | 关系网/证言对象 |
| 205 | Mickey | L2 医院和 L3 城政厅衔接 |
| 206 | O'Hara | L2/L4 |
| 207 | Leonard | L2/L3/L6 |
| 208 | Moore | L3 |
| 209 | Tony | L2/L5/L6 |
| 210 | Vinnie | L2/L5 |
| 211 | Danny | L3/L4 |
| 212 | Lula | L4 |
| 213 | Margaret | L6 |
| 214 | Edith | L6 |
| 215 | Foster | L1/L5/L6 证言 |
| 216 | Earl Hirsch | 新增正式 NPC，接管旧表中错挂 Tony 的 2162001–2162003 |
| 217 | TideWater Liaison | L6 赌场交接人 |
| 218 | City Hall Doorman | L3 城政厅门卫 |

中间 JSON 中已没有 U2 说话人错用 EPI01 ID 的情况。

### 3.3 分支

- `@branch/@opt/@path/@goto/@label` 按编号后的真实 Talk ID 生成。
- 正式 Talk 支持 5 组分支参数；U2 当前最大 4 选项，不再被旧脚本的 3 选项上限截断。
- `branches.next` 为空，走 `ParameterInt0-4` 目标。
- 已检查 2038 条正式草稿 Talk：无重复 ID、无缺失 next、无缺失分支目标、无未收束标签。

### 3.4 get/del 与终止节点

- 当 `@get/@del` 紧贴 `@branch` 时，现在会先生成独立无台词动作节点，再进入分支，避免动作被 `branches` 覆盖。
- 章节最后一条如果是 `get/del`，会自动追加无台词 `end`，确保获取动作可执行且对话能关闭。
- 当前正式草稿共 47 个 `get/del` 动作，动作多集与 MD 标注完全一致。
- L2 新增派生动作 `@get 2112001`，以满足 L2/L4 对 Danny—Leonard 交谈的引用。

### 3.5 Lie / Expose 参数语义

已修正一个会影响运行时的解析错位：

- Unity 当前把 `Talk.script=expose` 的 `ParameterInt0` 解释为“成功后 Zack 连续台词数”，不是正确路径 Talk ID。
- 中间 JSON 现在把正确路径单独保存为 `correctNext`，`ParameterInt0` 写入 1–3 的合理台词数。
- 正式配表器用 `correctNext` 连接下一轮 ExposeData，不再把几十万的 Talk ID 误当点击计数。
- `ParameterStr0` 保留本轮所有正确证据，支持单件和多件组合。
- 最后一轮指证成功后，当前 Lie 的 `next` 会穿过正确结果台词到达 `finalexpose`。

### 3.6 证言 ID 归一化

MD 中的 `2105002a` 和 `2105002b` 是同一份 Vinnie 认罪中的两个维度，但 Unity TestimonyItem 主键必须是整数。正式表中将两者归一为 `2105002`，保留两段文字来源，L6 第 4 轮用 `2105002 + 2601`。

## 四、全局正式表方案

| 表 | U2 行数 | 主要作用 |
|---|---:|---|
| GameFlowConfig | 1 | Chapter 2，6 Loop |
| ChapterConfig | 6 | 201–206 入口、疑点、指证、地图映射 |
| ChapterStepConfig | 24 | 每轮 4 个调查条目 |
| DayTimeConfig | 1 | 1106，18:00–26:00，支持 U2 时间线 |
| MapConfig | 10 | U2 地图点 |
| NPCStaticData | 18 | NPC201–218 |
| NPCLoopData | 24 | 场景 NPC 实例、主对话、重复对话和场景立绘 |
| LocationConfig | 46 | 场景名和背景资源 |
| SceneConfig | 46 | NPC/Item 的唯一场景绑定容器 |
| ItemStaticData | 82 | 证据、环境物、容器、门和合成物 |
| Talk | 2062 | 2038 条剧情 + 24 条 safe repeat |
| Testimony | 36 | 证言获取时的对白归属 |
| TestimonyItem | 35 | 证言卡、时间线和关系网触发 |
| DoubtConfig | 19 | 六轮调查疑点 |
| ExposeData | 18 | L1–L6 的 3/3/3/3/2/4 轮指证 |

### 4.1 SceneConfig 绑定原则

NPC 和 Item 只通过 `SceneConfig.NPCInfos[]` 与 `SceneConfig.ItemIDs[]` 出现在玩法场景中。对白 `get`、容器 Type7 子物品、分析产物和合成结果不重复直绑场景。

### 4.2 重复对话

24 个 NPCLoop 都有可解析的重复 Talk。重复 Talk 只显示“目前没有更多可补充的信息”并 `end`，不重复发放道具或证言。

### 4.3 门、容器和合成

- 8 组 Type6/Type7：O'Hara 邮箱、鞋坊工作台、Danny 纸箱/抽屉/枕头、Leonard 办公室上下抽屉、Margaret 卧室抽屉。
- 2403 = 2409 枯萎玫瑰 + 2410 水杯。
- 2605 = 2611 柜面嵌入碎片 + 2603 医用镊子。
- 2108 保留为 L1 地下室锁门，`ActionParam=2410|1541`。当前 `IODoor` 明确规定：第二段存在锁定提示文本时不转场。L4 真正进入地下室使用独立门 2940。
- 2605 是合成结果，不直绑 Scene，因此不需要场景 XY。

## 五、六个 Loop 逐点配置

### Loop1：死者身份逆转

- ChapterConfig：201；初始 Talk `201001001`；初始 Scene `2191`。
- 可玩主链：案发开场 → Scene2101 鞋坊搜证 → 2901 到 Scene2102 卧室 → 2902 到 Scene2103 警局大厅/Morrison → Scene2119 Emma 电话 → Scene2104 指证 → Morrison post-expose → Scene2105 办公室电报 → `201101022 loop_end`。
- 核心道具：2101 尸体手指照片、2102 Margaret 相册、2103 空首饰盒、2104 现场地面照片、2105–2107 环境证据、L1 锁定门 2108。
- 疑点：2101 = 2101+2102；2102 = 2103+2104；2103 = Foster 证言 2151001。
- 指证：
  1. Expose18：攻击 2031001，出示 2101+2102+2103，Talk210001。
  2. Expose19：出示 2104，本轮正确结果根 Talk210010，进入 Lie210024。
  3. Expose20：出示 2151001，正确结果根 Talk210028，进入 Lie210035。
- 终结：`210044 finalexpose` → `203101001` → Scene2105 firstEnter `201101001` → `201101022 loop_end`。

### Loop2：Leonard—Vinnie 催债链

- ChapterConfig：202；初始 Talk `201002001`；初始 Scene `2206`。
- 可玩主链：医院开场 → Mickey → Scene2207 O'Hara 街角/邮箱 → Scene2211 银行大厅 Leonard → Scene2212 VIP 室 → Scene2215 Silver Moon（先触发 Vinnie `210002001`，再可与 Tony/Earl 交互）→ Earl 收束到 Scene2292 指证 → `207102039 loop_end`。
- 场景互动：2801/2802 邮箱容器产出 2201、2203、2204；2910/2911 连接银行大厅和 VIP 室。
- 核心证据：2102001 Vinnie 说出 Russo；2208 Leonard 奖杯；2202 O'Hara 贿赂钞票；2206 Tony 找零钞票；2162002 Earl 对“赚了”的确认；2205 Vinnie 记账本。
- 疑点：2201 = Relation2102001+2208；2202 = 2202+2206；2203 = 2162002+2205；2204 = 2112001。
- 指证：
  1. Expose21：攻击 2072001，2102001+2208，Lie220008。
  2. Expose22：2202+2206，结果根 220010，Lie220020。
  3. Expose23：2162002+2205，结果根 220024，Lie220038。
- 终结：`220053 finalexpose` → `207102001` → `207102039 loop_end`。

### Loop3：掠夺性贷款与伪造签名

- ChapterConfig：203；初始 Talk `201003001`；初始 Scene `2316`。
- 可玩主链：城政厅开场/Doorman → Scene2318 Frank 主屋 → Scene2309 Danny 卧室 → Scene2311 银行大厅 → Scene2314 Leonard 办公室 → Scene2313 档案室 / Scene2312 Moore VIP 室 → Scene2392 指证 → `208103052 loop_end`。
- 门：2930/2931 连接主屋与 Danny 房间；2920–2925 构成银行大厅—办公室—档案室—VIP 室往返。
- 容器：2811/2812 下层抽屉产出 2302、2306；2813/2814 保留上层抽屉互动位。
- 核心证据：2301 牛奶签收单、2302 客户贷款档案、2303 贷款协议、2701 贷款计算分析报告、2306 对账单。2308 在 post-expose 发放；2307 不发放。2321 仅作柜中可见环境物。
- 疑点：2301 = 2301+2302；2302 = 2701；2303 = 2306。
- 指证：
  1. Expose24：攻击 2083001，2301+2302，Lie230008。
  2. Expose25：2701，结果根 230009，Lie230024。
  3. Expose26：2306，结果根 230027，Lie230046。
- 终结：`230092 finalexpose` → `208103001` → `208103052 loop_end`。

### Loop4：Danny 嫌疑与 Frank—Lula 关系翻案

- ChapterConfig：204；初始 Talk `201004001`；初始 Scene `2491`。
- 可玩主链：医院开场 → Scene2401 鞋坊废墟/Lula → 2940 到 Scene2410 地下室 → Scene2407 O'Hara 街角 → 2942 到 Scene2409 Danny 房间 → 2944 到 Scene2420 厕所 → Scene2492 指证 → Danny post-expose → `211204029 loop_end`。
- 容器：2805/2806 纸箱产出 2404；2807/2808 抽屉产出 2405、2407；2809/2810 枕头保留可互动位。
- 合成：2409 枯萎玫瑰 + 2410 水杯 → 2403 求婚戒指。
- 疑点：2401 = 2112001+2083004+2404；2402 = Timeline2064001+2405；2403 = 2403+Relation2064002。
- 指证：
  1. Expose27：攻击 2114001，2064001+2405，Lie240012。
  2. Expose28：2083004+2404，结果根 240013，Lie240026。
  3. Expose29：2064002+2403，结果根 240030，Lie240049。
- 终结：`240095 finalexpose` → `211204001` → `211204029 loop_end`。

### Loop5：Vinnie 纵火认罪与死因反转

- ChapterConfig：205；初始 Talk `201005001`；初始 Scene `2518`。
- 可玩主链：Frank 主屋开场 → Scene2501 鞋坊废墟拾取 2501 打火机 → Scene2515 Silver Moon（Tony firstEnter `209005001`）→ Vinnie 对话 → Scene2592 指证 → Vinnie 抢话认罪 → Scene2519 电话亭 firstEnter `215005001` → `215005015 loop_end`。
- 已修复的断点：旧方案中 post-expose 只切到 Scene2519，但场景未挂电话对白，会停在空场景。现在 `Scene2519.firstEnterTalk=215005001`。
- 疑点：2501 = 2501+2095001+Timeline2114004；跨轮的 2502 = 2105002+2601，放在 L6 ChapterConfig。
- 指证：
  1. Expose30：攻击 2105001，2501+2095001，Lie250008。
  2. Expose31：2114004，结果根 250009，Lie250021。
- 终结：`250030 finalexpose` → `210105001` → Scene2519/`215005001` → `215005015 loop_end`。

### Loop6：Leonard 终极指证

- ChapterConfig：206；初始 Talk `201006001`；初始 Scene `2691`。
- 可玩主链：医院开场 → Scene2606 Margaret/Foster → Scene2604 Morrison 签搜查令 → Scene2615 TideWater 交接 → Scene2611 Leonard 银行大厅 → Scene2617 Leonard 住所/Edith → Scene2692 指证 → Leonard post-expose → Scene2693 墓地结尾 → `201106053 loop_end`。
- 新增场景：2615 Silver Moon 赌场·TideWater 交接；NPC217 暂用 Tony 已有资源。
- 工作台：Scene2601 的 2803/2804 产出 2611；2611+2603 医用镊子 → 2605 眼镜碎片。
- 医院取证区：2960/2961 连接 Scene2606 与 Scene2621，Scene2621 提供 2603。
- 核心证据：2605 眼镜碎片、2610 维修单、2136001 20:16 目击、2606 凹陷货箱、2105002 Vinnie 认罪细节、2601 法医报告。
- 疑点：2502 = 2105002+2601；2601 = 2605+Timeline2136001；2602 = 2610；2603 = 2606+2602；2604 = 2105002+2606。
- 指证：
  1. Expose32：攻击 2076001，2605+2136001，Lie260008。
  2. Expose33：2610，结果根 260009，Lie260021。
  3. Expose34：2136001+2606，结果根 260027，Lie260037。
  4. Expose35：2105002+2601，结果根 260040，Lie260162。
- 终结：`260202 finalexpose` → `207106001` → Scene2693 firstEnter `201106001` → `201106053 loop_end`。

## 六、证言、时间线与关系网配置原则

- 普通口供用 `TriggerType=None`，不伪装成时间线。
- 只有精确到时间的口供用 `Timeline`，当前 DayTime1106 覆盖 18:00–26:00。
- 只有明确的人物关系用 `RelationNetwork`。
- 已排除旧蓝图中无新 MD `@get` 来源的 5 个过期证言：2062001、2082001、2092001、2092002、2092003。
- 已纳入新对白中真正出现的 2072002、2083002、2113002、2162001–2162003 和归一化 2105002。

## 七、音视频与美术缺口

本阶段明确不生成音频和视频：

- U2 Talk 音频路径全部为空。
- 对白保留 `videoEpisode/videoLoop/videoScene/videoId` 元数据，但不把视频文件当成可玩前置。
- 每个有可见说话人的 Talk 都有存在于 Resources 的静态图兜底。
- Earl/NPC216 和 TideWater/NPC217 尚无专用立绘，暂用 Tony 的有效场景资源。
- 多数 EPI02 NPCStaticData 的 UI 小头像/大头像暂用 Morrison 占位图。

上述三项美术问题已被验证器作为 warning 明示记录，不会以缺失路径的方式静默失败。

## 八、验收结果与最后运行步骤

已完成：

1. 原始文件哈希：81/81 未变。
2. 派生对白：2038 个唯一 ID，47 个 get/del，0 个缺失 next/分支目标。
3. 非 U2 Excel 行：GameFlow、Chapter、Map、NPC、Scene、Item、Talk、Testimony、Doubt、Expose 全部与分支基线逐单元格值一致。
4. Excel → JSON/bytes：`Translate.exe` 退出码 0，所有目标表 runtime bytes 已重建。
5. 跨表：Chapter/Scene/NPC/Item/Talk/Testimony/Doubt/Expose 引用均存在。
6. 资源：背景、场景 NPC、Talk 静态兜底、道具 sprite 均可解析。
7. 指证流程：
   - L1：210001 → 210024 → 210035 → final210044 → loop_end201101022。
   - L2：220008 → 220020 → 220038 → final220053 → loop_end207102039。
   - L3：230008 → 230024 → 230046 → final230092 → loop_end208103052。
   - L4：240012 → 240026 → 240049 → final240095 → loop_end211204029。
   - L5：250008 → 250021 → final250030 → loop_end215005015。
   - L6：260008 → 260021 → 260037 → 260162 → final260202 → loop_end201106053。

Translator 在 JSON/bytes 生成完成后，其附带的 C# 独立集成步骤会报 `netstandard.dll not found`。这是当前 macOS/Mono 下的已知工具链警告，不影响本次 JSON/bytes 输出，且表 C# schema 文件未产生 Git 差异。

待现有 Unity Editor 可用时，最后验收应按以下顺序：

1. 让 Editor 刷新 `Assets/Resources/table/*.bytes.txt`，确认 Console 无新的表加载错误。
2. 用 GM Loop Jumper 分别进入 ChapterConfig 201–206，确认初始 Talk/Scene。
3. 每轮至少走一次场景门、NPC 主对话、重复对话、容器和道具获取。
4. 逐轮确认 Doubt 解锁、Expose 正确证据数量、错误证据返回、正确证据推进和 finalexpose。
5. 确认 L5 Scene2519 电话段、L6 Scene2693 墓地段以及六轮 `loop_end`。
6. 记录只能在实机中复现的阻断，再做范围最小的定向修复。
