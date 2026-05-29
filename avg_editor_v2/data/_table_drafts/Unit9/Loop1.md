# Unit9 Loop1 - 配置表草稿

## ItemStaticData

### 9101 - Vivian的小手枪 / Vivian's Pocket Pistol
- itemType: 3
- canAnalyzed: true
- analysedEvidence: 9711
- canCombined: false
- Describe: |
    Vivian 手里那把——Colt Vest Pocket Model 1908，点 25 口径，女士随身款。
- ShortDescribe: Vivian 手里那把——Colt Vest Pocket Model 1908，点 25 口径，女士随身款。
- location: Webb 会客室 / WebbParlor
- Chapter: EPI09
- folderPath: EPI09\WebbParlor
- desSpritePath: SC9003_item_01_big
- mapSpritePath: SC9003_item_01
- Position: 待补充（美术）
- ArtRequirement: |
    小型半自动手枪特写，全长约 11-12 cm
    • 型号：Colt Vest Pocket Model 1908（.25 ACP 口径）
    • 枪身：蓝钢表面，光泽均匀，泛冷光
    • 握把：嵌一对乳白色象牙贴片，表面温润，有细微使用包浆
    • 握把下缘可见 Colt 小马立形徽标浮雕
    • 细节：保险推钮、扳机、击锤清晰可见
    • 整体气质：精致贵气，1920s 都市女性随身款
    • 角度：45 度侧视，枪口朝左下，陈列视图
    • 背景：深色天鹅绒 / 证据袋质感

### 9711 - 无硝烟的手枪（分析派生） / Pistol Without Gunpowder Residue
- itemType: 3
- canAnalyzed: false
- beforeAnalysedEvidence: 9101
- canCombined: false
- Describe: |
    枪管内无硝烟残留——这把枪近期没开过火。
- ShortDescribe: 枪管内无硝烟残留——这把枪近期没开过火。
- location: Webb 会客室 / WebbParlor
- Chapter: EPI09
- folderPath: EPI09\WebbParlor
- desSpritePath: SC9003_item_71_big
- mapSpritePath: SC9003_item_71
- Position: 待补充（美术）
- ArtRequirement: |
    同 9101 的放大特写镜头，聚焦枪管内部
    • 视角：从枪口向内窥视，或枪膛剖面图
    • 枪管内壁：清洁光亮，可见细微膛线螺纹，无任何黑色碳化残留
    • 关键视觉标注：右侧留白处以灰色手写小字注记 "No Residue — Z.B."
    • 对比示意（辅助用）：画面一角附一枚近期击发过的枪管特写做对照，枪膛内侧黑色烟痕厚重，浅灰小尺寸表达
    • 整体色调：冷灰金属色，强化"洁净"印象
    • 尺寸：与 9101 等比

### 9103 - Webb 委托协议书 / Webb's Commission Contract
- itemType: 3
- canAnalyzed: false
- canCombined: false
- Describe: |
    Webb 亲笔签的委托协议——指定 Zack Brennan 为遗嘱执行人，确保 Vivian 顺利继承 Webb 名下全部遗产。
    签约日期：三天前（1928 年 10 月 31 日）。
- ShortDescribe: Webb 三天前签的委托——指定 Zack 为遗嘱执行人，保 Vivian 顺利继承遗产。
- location: Webb 会客室 / WebbParlor
- Chapter: EPI09
- folderPath: EPI09\WebbParlor
- desSpritePath: SC9003_item_03_big
- mapSpritePath: SC9003_item_03
- Position: 待补充（美术）
- ArtRequirement: |
    **重点（信息表达必不可少）**：
    1. 标题可读：ESTATE EXECUTION AGREEMENT
    2. 主条款可读（编号 1）：Mr. Zack Brennan is appointed as executor to ensure Miss Vivian's full inheritance of Mr. Webb's estate.
    3. 日期栏可读：October 31, 1928（案发前三天）
    4. Webb 的钢笔签名（深蓝黑色墨水，笔锋刚劲）

    **美术参考（不影响推理）**：
    - 奶白色商业厚纸，纸纹细腻，整体微微泛黄
    - Underwood No. 5 打字机字体，油墨浓淡略有不均
    - "ESTATE EXECUTION AGREEMENT" 标题居中加粗的排版样式
    - 右上角 Webb 个人火漆印章（暗红色，字母 "W" 款）
    - 纸张曾对折过一次的中央折痕、右下角轻微卷边
    - 1920s 美国私人合同整体气质

## NPCStaticData

### 902 - Emma / Emma
- role: 4
- Chapter: EPI09

### 903 - Rosa / Rosa
- role: 3
- Chapter: EPI09
- IconSmall: rosa_small
- IconLarge: rosa_big

### 904 - Morrison / Morrison
- role: 2
- Chapter: EPI09
- IconSmall: morrison_small
- IconLarge: morrison_big

### 906 - Vivian / Vivian
- role: 3
- Chapter: EPI09
- IconSmall: vivian_small
- IconLarge: vivian_big

## SceneConfig

### 9001 - Rosa 储藏室 / Rosa's Storage
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9001_bg_RosaStorage
- backgroundMusic: 待补充
- ItemIDs: [9302, 9303]

### 9002 - Vivian 化妆室 / Vivian's Dressing Room
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9002_bg_DressingRoom
- backgroundMusic: 待补充
- ItemIDs: []

### 9003 - Webb 会客室 / Webb's Parlor
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9003_bg_WebbParlor
- backgroundMusic: 待补充
- ItemIDs: [9101, 9711, 9103]
- NPCInfos:
  - npc_ref: 906
    instance_id: 9061
    ResPath: Art\Scene\NPC\EPI09\SC9003_npc_Vivian1
    ClickResPath: Art\Scene\NPC\EPI09\SC9003_npc_Vivian2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）
  - npc_ref: 903
    instance_id: 9031
    ResPath: Art\Scene\NPC\EPI09\SC9003_npc_Rosa1
    ClickResPath: Art\Scene\NPC\EPI09\SC9003_npc_Rosa2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）
  - npc_ref: 904
    instance_id: 9041
    ResPath: Art\Scene\NPC\EPI09\SC9003_npc_Morrison1
    ClickResPath: Art\Scene\NPC\EPI09\SC9003_npc_Morrison2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）

### 9004 - 酒吧大堂 / Main Hall
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9004_bg_MainHall
- backgroundMusic: 待补充
- ItemIDs: []
- NPCInfos:
  - npc_ref: 902
    instance_id: 9021
    ResPath: Art\Scene\NPC\EPI09\SC9004_npc_Emma1
    ClickResPath: Art\Scene\NPC\EPI09\SC9004_npc_Emma2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）

### 9005 - 歌舞厅 / Dance Hall
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9005_bg_DanceHall
- backgroundMusic: 待补充
- ItemIDs: [9205, 9206]

### 9006 - 歌舞厅小包厢 / Dance Hall Small Box
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9006_bg_SmallBox
- backgroundMusic: 待补充
- ItemIDs: [9201, 9209]

### 9007 - 一楼走廊 / First Floor Corridor
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9007_bg_Corridor
- backgroundMusic: 待补充
- ItemIDs: [9402]

### 9008 - 一楼侧巷 / Side Alley
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9008_bg_SideAlley
- backgroundMusic: 待补充
- ItemIDs: [9301]

### 9009 - James 厨房 / James's Kitchen
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9009_bg_JamesKitchen
- backgroundMusic: 待补充
- ItemIDs: [9207, 9210]
- NPCInfos:
  - npc_ref: 907
    instance_id: 9072
    ResPath: Art\Scene\NPC\EPI09\SC9009_npc_James1
    ClickResPath: Art\Scene\NPC\EPI09\SC9009_npc_James2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）

### 9010 - Tommy 办公室 / Tommy's Office
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9010_bg_TommyOffice
- backgroundMusic: 待补充
- ItemIDs: [9204, 9208]
- NPCInfos:
  - npc_ref: 905
    instance_id: 9052
    ResPath: Art\Scene\NPC\EPI09\SC9010_npc_Tommy1
    ClickResPath: Art\Scene\NPC\EPI09\SC9010_npc_Tommy2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）

### 9011 - Webb 办公室 / Webb's Office
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9011_bg_WebbOffice
- backgroundMusic: 待补充
- ItemIDs: [9202, 9203]

### 9012 - James 家 / James's House
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9012_bg_JamesHouse
- backgroundMusic: 待补充
- ItemIDs: [9503, 9504, 9505]
- NPCInfos:
  - npc_ref: 908
    instance_id: 9085
    ResPath: Art\Scene\NPC\EPI09\SC9012_npc_Anna1
    ClickResPath: Art\Scene\NPC\EPI09\SC9012_npc_Anna2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）

### 9013 - Morrison 的家 / Morrison's House
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9013_bg_MorrisonHouse
- backgroundMusic: 待补充
- ItemIDs: [9603, 9604, 9605, 9606]

### 9014 - 警局 Morrison 办公室 / Police Station Morrison's Office
- sceneType: 3
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9014_bg_PoliceOffice
- backgroundMusic: 待补充
- ItemIDs: []
- NPCInfos:
  - npc_ref: 904
    instance_id: 9046
    ResPath: Art\Scene\NPC\EPI09\SC9014_npc_Morrison1
    ClickResPath: Art\Scene\NPC\EPI09\SC9014_npc_Morrison2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）

### 9103 - Webb 会客室 / Webb's Parlor
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9003_bg_WebbParlor
- backgroundMusic: 待补充
- ItemIDs: [9101, 9711, 9103]
- NPCInfos:
  - npc_ref: 906
    instance_id: 9061
    ResPath: Art\Scene\NPC\EPI09\SC9003_npc_Vivian1
    ClickResPath: Art\Scene\NPC\EPI09\SC9003_npc_Vivian2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）
  - npc_ref: 903
    instance_id: 9031
    ResPath: Art\Scene\NPC\EPI09\SC9003_npc_Rosa1
    ClickResPath: Art\Scene\NPC\EPI09\SC9003_npc_Rosa2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）
  - npc_ref: 904
    instance_id: 9041
    ResPath: Art\Scene\NPC\EPI09\SC9003_npc_Morrison1
    ClickResPath: Art\Scene\NPC\EPI09\SC9003_npc_Morrison2
    PosX: 待补充（美术）
    Posy: 待补充（美术）
    PosZ: 待补充（美术）

## TestimonyItem

### 9031001 - Rosa 谎言1：Vivian 刚刚开枪
- testimonyType: 2
- testimony: Vivian 此刻手里正拿着一把手枪，她一定是刚刚杀了 Webb。
- triggerType: 0
- triggerParam: "903"

### 9031002 - Rosa 谎言2：23:30 枪响 + 只有 Vivian 在场
- testimonyType: 2
- testimony: 23:30 枪响，当晚无其他枪响，当时只有 Vivian 在里面，所以只能是她杀的。
- triggerType: 0
- triggerParam: "903"

### 9031003 - Rosa 身份：清洁工
- testimonyType: 1
- testimony: 我是蓝月亮酒吧的清洁工。
- triggerType: 0
- triggerParam: "903"

### 9041004 - Morrison 身份：警察侦探
- testimonyType: 1
- testimony: 我是警察侦探。
- triggerType: 0
- triggerParam: "904"

### 9061001 - Vivian 身份：歌女
- testimonyType: 1
- testimony: 我是蓝月亮酒吧的歌女。
- triggerType: 0
- triggerParam: "906"

## Testimony

### 9031001 - Rosa 谎言1 完整证词
- npc_ref: 903
- chapter: 901
- words: |
    Vivian 此刻手里正拿着一把手枪，她一定是刚刚杀了 Webb。
- evidenceItem_refs: [9031001]

### 9031002 - Rosa 谎言2 完整证词
- npc_ref: 903
- chapter: 901
- words: |
    23:30 枪响，当晚并没有其他枪响，当时只有 Vivian 在里面，所以只能是她杀的。
- evidenceItem_refs: [9031002]

### 9031003 - Rosa 身份 完整证词
- npc_ref: 903
- chapter: 901
- words: |
    我是蓝月亮酒吧的清洁工。
- evidenceItem_refs: [9031003]

### 9041004 - Morrison 身份 完整证词
- npc_ref: 904
- chapter: 901
- words: |
    我是警察侦探。
- evidenceItem_refs: [9041004]

### 9061001 - Vivian 身份 完整证词
- npc_ref: 906
- chapter: 901
- words: |
    我是蓝月亮酒吧的歌女。
- evidenceItem_refs: [9061001]

## DoubtConfig

### 9101 - 23:30 的枪响真的是在 Webb 会客室发生的吗？
- text: 23:30 的枪响真的是在 Webb 会客室发生的吗？
- Chapter: EPI09
- condition:
  - {type: 1, param: 9711}
  - {type: 3, param: 9031001}

## ChapterConfig (部分写入)

### 901
- initScene: 9004
- doubts_ref: [9101]
- topBg: Art/Scene/Expose/epi09/top_rosa
- bottomBg: Art/Scene/Expose/epi09/rosa
- _skip_fields: [initTalk, exposeNpcId, exposes, suspectVideoPos, suspectTalkPos, zackTalkPos]
