# Unit9 场景美术需求分类

> 本文件为 SceneConfig.backgroundImage 字段的信息分类研究文档。
> 判断依据：loop1-loop6_state.yaml（scenes 段）+ SceneConfig.json 现有 EPI01 资源清单 + `剧情设计/Unit9/场景/` 场景文档。
> 规则：Unit9 绝大多数场景复用 EPI01（Unit1）背景资源；新增场景才写完整 ArtRequirement。
> "重点"=推理/叙事必需的视觉元素；"美术参考"=氛围/构图自由发挥。

---

## 9001 - Rosa 储藏室

**美术资源**：复用 EPI01（已有）
- sceneName: Rosa 储藏室 / Rosa's Storage
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC001_bg_RosaStorageRoom`

---

## 9002 - Vivian 化妆室

**美术资源**：复用 EPI01（已有）
- sceneName: Vivian 化妆室 / Vivian's Dressing Room
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC007_bg_VivianDressingRoom`

---

## 9003 - Webb 会客室

**美术资源**：复用 EPI01（已有）
- sceneName: Webb 会客室 / Webb's Parlor
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC004_bg_WebbReceptionRoom`

---

## 9004 - 酒吧大堂

**美术资源**：复用 EPI01（已有）
- sceneName: 酒吧大堂 / Main Hall
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC010_bg_BarLobby`

---

## 9005 - 歌舞厅

**美术资源**：复用 EPI01（已有）
- sceneName: 歌舞厅 / Dance Hall
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC009_bg_BarCabaret`

---

## 9006 - 歌舞厅小包厢（🆕 新增）

**当前 ArtRequirement**：
蓝月亮酒吧歌舞厅（9005）内部的小包厢，约 3×4 m 的半封闭式私人包厢。
• 位置：位于歌舞厅大厅一侧，由歌舞厅内部进入（非独立楼层/独立房间），属于歌舞厅包间区
• 布局：红丝绒软包卡座环绕矮桌，桌上有酒杯、烟灰缸、半空的香槟桶
• 墙面：暗金色壁纸 + 装饰艺术风格（Art Deco）几何线条镶边
• 光源：顶部一盏低悬的罩灯（暖黄色）+ 墙壁烛台若隐若现——整体低亮度暧昧氛围
• 帘幕：包厢入口有一道半垂的丝绒帘（深酒红色），拉开/闭合状态可视
• 装饰：墙上挂一幅小尺寸 1920s 风景画 + 一面复古圆镜
• 时代气质：1920s 芝加哥 speakeasy 私密包厢——低调奢华，适合不被打扰的"交易"
• 视角：略微俯视（玩家视角进入包厢），能看到卡座 + 矮桌 + 帘幕入口

**重点（信息表达必不可少）**：
1. 半封闭式私密空间——视觉上能看出"外人无法轻易窥视"（帘幕/矮屏风）
2. 桌上有酒杯/烟灰缸（前一场谈话遗留痕迹，烘托"勒索交易"氛围）
3. 低亮度暧昧光线（符合仙人跳照片拍摄的光环境——与 9201 勒索照片背景呼应）

**美术参考（不影响推理）**：
- 红丝绒软包卡座 + 暗金色 Art Deco 壁纸具体配色
- 顶灯 + 烛台的具体款式
- 墙面装饰画、圆镜的具体构图
- 帘幕的具体色调与垂坠感

---

## 9007 - 酒吧一楼走廊

**美术资源**：复用 EPI01（已有）
- sceneName: 酒吧一楼走廊 / BarFirstFloorCorridor
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC002_bg_CabaretFirstFloorCorridor`

---

## 9008 - 一楼侧巷（🆕 新增）

**用途说明**：纯指证硬切场景——L5 指证 James 时作为 CG 背景硬切出现（暗处尾款交易、Whale 手下出现），不作为可探索场景存在；玩家无法从任何场景步行/过渡进入，因此无需考虑与周边场景（9004 酒吧大堂 / 9007 酒吧一楼走廊）之间的衔接视角或入口对位。**注**：L3 玻璃碎片拾取已迁移到独立场景 9020（侧巷 L3 破窗向外搜证视角），9008 仅服务 L5 指证。

**当前 ArtRequirement**：
蓝月亮酒吧一楼侧门外的狭窄后巷，约 2 m 宽、延伸 6-8 m 深。
• 地面：1920s 芝加哥典型后巷石板/砖石地面，缝隙有积水/泥渍
• 墙面：两侧是红砖墙，其中一侧可见酒吧侧门（深色木门，门上方小窗）
• 关键视觉元素：
  - 墙面上有一扇被子弹打穿过的窗户（玻璃碎裂，缺口边缘参差）
  - 地面堆放两只黑色垃圾袋（鼓鼓的，蒙着灰尘）
  - 垃圾袋底部周围散落玻璃碎片（9301 取证点）
• 其他道具：锈蚀铁桶、堆放的木板/酒箱、一盏低悬的煤气灯（昏黄）
• 光线：低光、阴湿，夜色或清晨，阴影浓重
• 时代气质：1920s 芝加哥 speakeasy 后巷——低调、半合法、藏污纳垢

**重点（信息表达必不可少）**：
1. 被击穿的窗户（玻璃碎裂、缺口形状显示枪击角度）
2. 两只黑色垃圾袋（压在碎片上方）——与 9301 证据"碎片压在袋下"物理关系一致
3. 地面有玻璃碎片散布（9301 取证位置明确可辨）

**美术参考（不影响推理）**：
- 后巷整体氛围（砖墙/石板地/阴湿）
- 煤气灯、铁桶、酒箱等氛围道具具体款式
- 光线的具体冷暖调
- 侧门的门锁、门把手细节

---

## 9009 - James 厨房

**美术资源**：复用 EPI01（已有）
- sceneName: James 厨房 / James's Kitchen
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC011_bg_JamesKitchen`

---

## 9010 - Tommy 办公室

**美术资源**：复用 EPI01（已有）
- sceneName: Tommy 办公室 / Tommy's Office
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC003_bg_TommyOffice`

---

## 9011 - Webb 办公室

**美术资源**：复用 EPI01（已有）
- sceneName: Webb 办公室 / Webb's Office
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC008_bg_WebbOffice`

---

## 9012 - James 家卧室（原 Jimmy 家卧室）

**美术资源**：复用 EPI01（已有）
- sceneName: James 家卧室 / James's Bedroom
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC012_bg_JamesHomeBedroom`

---

## 9013 - Morrison 家客厅（原 Morrison 家客厅）

**美术资源**：复用 EPI01（已有）
- sceneName: Morrison 家客厅 / Morrison's Living Room
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC005_bg_MorrisonHomeLivingRoom`

---

## 9014 - 警局 Morrison 办公室

**美术资源**：复用 EPI01（已有）
- sceneName: 警局 Morrison 办公室 / Police Station Morrison's Office
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC018_bg_MorrisonOffice`

---

## 9015 - James 家客厅（原 Jimmy 家客厅）

**美术资源**：复用 EPI01（已有）
- sceneName: James 家客厅 / James's Living Room
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC013_bg_JamesHomeLivingRoom`

---

## 9016 - Morrison 家书房（原 Morrison 家书房）

**美术资源**：复用 EPI01（已有）
- sceneName: Morrison 家书房 / Morrison's Study
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC006_bg_MorrisonHomeStudy`

---

## 9017 - 酒吧二楼走廊（🆕 地图连接节点）

**美术资源**：复用 EPI01（已有）
- sceneName: 酒吧二楼走廊 / BarSecondFloorCorridor
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC014_bg_CabaretSecondFloorCorridor`

**用途**：2F 布局上本就存在的走廊，作为玩家从 1F 进入 2F 各房间的过渡空间。无证据、无 NPC、不进入任何 Loop 的 state scenes 段——仅 SceneConfig + 美术资源挂载。

---

## 9018 - 厨房走廊（🆕 地图连接节点）

**美术资源**：复用 EPI01（已有）
- sceneName: 厨房走廊 / KitchenCorridor
- backgroundImage: `Art\Scene\Backgrounds\EPI01\SC016_bg_kitchenCorridor`

**用途**：通往 James 厨房（9009）的独立走廊/楼梯——厨房是酒吧内的单独空间；此楼梯与 9007 酒吧一楼走廊的楼梯是**两条不同的楼梯**。无证据、无 NPC、不进入任何 Loop 的 state scenes 段——仅 SceneConfig + 美术资源挂载。

---

## 9019 - Webb 会客室（L3 勘验后态，🆕 新增）

**用途**：L3 会客室深度搜证——🔓 free_exploration（Morrison 勘验完毕、尸体已运走）。物理上同 9003 会客室，但勘验后状态。L1 复用 9003（EPI01\SC004 复用），L3 单独新画此版本以承载粉笔轮廓 + 4 件证据视觉锚点 + 破窗引导。

**当前 ArtRequirement**：
• 复用 9003 视角构图，但：
  - 尸体已无（地板/沙发上仅余警察粉笔轮廓 + 暗色血迹痕）
  - 沙发归位、案发感消退
  - 窗户依旧破碎、无玻璃（核心搜证锚点，引导玩家点击进入 9020）
• 整体光线：白天/明亮自然光，与 9003 夜晚暧昧光形成对比

**L3 证据视觉锚点（4 件 pickup item + 1 件 envir）**：
1. 9304 保险箱字条——墙上保险箱旁，一张小纸条
2. 9305 Webb 和 Vivian 合影——9304 字条旁簇拥（同位置），相框立着
3. 9307 Rita 的照片（envir 不可拾取）——Webb 桌上显眼位置摆放（与勒索日记区分开）
4. 9308 Webb 勒索记录日记（封面右下烫金 'W.'）——Webb 桌边抽屉位置，抽屉口能识别有书状物
5. 破窗——窗户依旧无玻璃，玩家点击触发进入 9020

**重点（信息表达必不可少）**：
1. 同房间案发感消退（粉笔轮廓 + 已清理）
2. 窗户依旧破碎且无玻璃（点击锚点）
3. 4 件证据各有独立视觉位置，不要全堆在桌面

---

## 9020 - 侧巷（L3 破窗向外搜证视角，🆕 新增）

**用途**：L3 玩家在 9019 会客室点击破窗后进入的侧巷搜证视角——伸手拾取 9301 玻璃碎片。**与 9008 区别**：9008 是 L5 指证 James 硬切 CG（外部俯视、暗处尾款交易，不可探索）；9020 是 L3 玩家可探索/拾取证据的搜证视角（屋内向外、强调碎片+袋视觉锚点）。

**当前 ArtRequirement**：
• 视角：屋内向外，破碎窗框为前景（玻璃缺口参差形成画面边缘）
• 中景：侧巷地面，两个黑色垃圾袋清晰可见
• 关键证据视觉锚点：
  - 几片明显的玻璃碎片露出垃圾袋外足够多——玩家一眼能识别"这里有玻璃可拾取"
  - 碎片压在垃圾袋下方的物理关系清楚（袋边缘骑在碎片上）
  - 碎片有亮度/反光，与周围地面区分
• 光线：白天侧巷阴影 + 屋内回光，前景暗、远景明（自然透窗光对比）
• 侧巷氛围：1920s 芝加哥典型侧巷——红砖墙、石板地、低调阴湿

**重点（信息表达必不可少）**：
1. 玻璃碎片在窗外不在窗内（弹道由内→外）
2. 碎片压在垃圾袋下方（关键时序：袋 23:20 放下→碎片更早→枪击早于 23:30）
3. 碎片反光足够，玩家直觉能拾取

---

# 综合报告

## 场景数统计
共 **20 个场景**（原 18 个 + L3 会客室拆分新增 9019/9020 两个 sceneId）：
- **16 个复用 EPI01 背景**（无需新增美术）
- **4 个新增场景**（需美术新画）：
  - 9006 歌舞厅小包厢（`EPI09\SC9006_bg_SmallBox`）
  - 9008 一楼侧巷（`EPI09\SC9008_bg_SideAlley`）— L5 指证 James 硬切 CG
  - 9019 Webb 会客室 L3 勘验后（`EPI09\SC9019_bg_WebbReception`）— L3 深度搜证
  - 9020 侧巷 L3 破窗向外搜证视角（`EPI09\SC9020_bg_BrokenWindowOut`）— L3 玻璃碎片拾取

## James 家 / Morrison 家的拆分方案

| 场景组 | sceneId | 对应 EPI01 资源 | 主要承载 |
|---|---|---|---|
| James 家 | 9012 卧室 | SC012_bg_JamesHomeBedroom | 9505 Anna 移民通知（卧室梳妆抽屉） |
| James 家 | 9015 客厅 | SC013_bg_JamesHomeLivingRoom | 9503 James 回信 / 9504 Berlitz 英语练习书 / Anna 迎客 |
| Morrison 家 | 9013 客厅 | SC005_bg_MorrisonHomeLivingRoom | Whale 调查电话事件 / 9606 马票存根 |
| Morrison 家 | 9016 书房 | SC006_bg_MorrisonHomeStudy | 9603 赌债欠条 / 9604 借 Whale 钱记录 / 9401 找回（书桌抽屉深处） |

## 对 SceneConfig.json 的影响
- 原 9012/9013 两条目需改写（名称、backgroundImage、ItemIDs 重新分配）
- 新增 9015/9016 两条目
- 新增 9017/9018 两条地图连接节点（无 NPC、无证据，不进入 state scenes 段）
- 其余 12 个复用场景的 backgroundImage 从占位的 `EPI09\SC9XXX_bg_XXX` 改回 EPI01 实际资源路径
- 4 个新增场景占位路径：`EPI09\SC9006_bg_SmallBox` / `EPI09\SC9008_bg_SideAlley` / `EPI09\SC9019_bg_WebbReception` / `EPI09\SC9020_bg_BrokenWindowOut`，待美术交付后替换
