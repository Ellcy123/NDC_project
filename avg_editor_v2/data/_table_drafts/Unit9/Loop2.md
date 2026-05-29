# Unit9 Loop2 - 配置表草稿

## ItemStaticData

### 9201 - 勒索用的照片 / Blackmail Photos
- itemType: 1
- canAnalyzed: true
- analysedEvidence: "9706"
- canCombined: false
- Describe: |
    Vivian 和中产男士的暧昧合影。背面有几处淡黄褐色污渍——肉眼看不出意义。
- ShortDescribe: Vivian 和中产男士的暧昧合影；背面有几处淡黄褐色污渍，肉眼看不出意义。
- location: 歌舞厅小包厢 / SmallBox
- Chapter: EPI09
- folderPath: EPI09\SmallBox
- desSpritePath: SC9006_item_01_big
- mapSpritePath: SC9006_item_01
- Position: 待补充（美术）
- ArtRequirement: |
    一组黑白照片，3-4 张成套，每张约 10×15 cm
    • 照片正面：Vivian 与中年男性在私密包厢内的亲密合影（坐姿 / 举杯），男性面部清晰可识别
    • 照片背面（显影前）：泛黄纸面，几处不规则淡黄褐色水渍，无可读文字（待玩家通过煤油灯烘烤显影）
    • 纸质：1920s 亚光相纸，边缘微泛黄，有指纹和折痕
    • 拍摄光线：暖色低光，典型 speakeasy 包厢氛围
    • 备注：正反面要能独立出图，供烘烤显影玩法交互用

### 9706 - 带金额显影的勒索照片 / Revealed Blackmail Photo
- itemType: 1
- canAnalyzed: false
- beforeAnalysedEvidence: "9201"
- canCombined: false
- Describe: |
    Vivian 与中产男士的暧昧合影；背面经煤油灯加热显影，柠檬汁字迹浮现："花瓶 — $4,000 / 油画 — $7,000"。Webb 的惯用勒索手法。
- ShortDescribe: 勒索照片背面金额显影：花瓶 $4,000 / 油画 $7,000——这是账本，不是花边。
- location: 歌舞厅小包厢 / SmallBox
- Chapter: EPI09
- folderPath: EPI09\SmallBox
- desSpritePath: SC9006_item_71_big
- mapSpritePath: SC9006_item_71
- Position: 待补充（美术）
- ArtRequirement: |
    重点（信息表达必不可少）：
    1. 照片背面字迹清晰可读两行："Vase — $4,000" / "Painting — $7,000"（褐色显影字）
    2. 照片边缘轻微焦褐色，提示曾经加热

    美术参考（不影响推理）：
    • 同 9201 等比尺寸（约 10×15 cm）
    • 字迹笔迹潦草偏行书，深褐色
    • 纸面整体仍泛黄，有不规则浅褐色背景渍痕（显影残留）

### 9202 - Webb 办公室 VIP 合影 / VIP Group Photo
- itemType: 1
- canAnalyzed: false
- canCombined: false
- Describe: |
    Webb 和 Thompson、Coleman 在酒吧里的合影。
    他们就是勒索照片背面那两个化名对应的人。
- ShortDescribe: Webb 和 Thompson、Coleman 的合影——正是"花瓶""油画"对应的人。
- location: Webb 办公室 / WebbOffice
- Chapter: EPI09
- folderPath: EPI09\WebbOffice
- desSpritePath: SC9011_item_02_big
- mapSpritePath: SC9011_item_02
- Position: 待补充（美术）
- ArtRequirement: |
    黑白 / 棕褐调社交场合合影，尺寸约 15×20 cm
    • 画面：Webb 居中，左右两侧各一位中年男性（Thompson 和 Coleman，西装+领带），三人举杯微笑
    • 背景：蓝月亮酒吧的 VIP 包厢或歌舞厅装饰
    • 相框装饰或桌面摆台样式
    • 纸张：标准室内合影纸张，半哑光
    • 可选背面：手写日期标注"1928 秋"

### 9203 - Webb 收入记录 / Webb's Income Ledger
- itemType: 3
- canAnalyzed: false
- canCombined: false
- Describe: |
    Webb 的个人收入记录。月净入 $15,000，来源一栏模糊不清。
- ShortDescribe: Webb 的个人收入记录——月净 $15,000，来源不清。
- location: Webb 办公室 / WebbOffice
- Chapter: EPI09
- folderPath: EPI09\WebbOffice
- desSpritePath: SC9011_item_03_big
- mapSpritePath: SC9011_item_03
- Position: 待补充（美术）
- ArtRequirement: |
    手写 / 打字账目单，letter size 纸张（约 22×28 cm）
    • 栏目：日期 / 项目 / 收入 / 来源
    • 月度汇总行显著："Monthly Net: $15,000"
    • "Source" 来源栏：大量项目空白 / "—" / "Misc."（故意模糊）
    • 少数可辨认项：酒吧营业额、入场费、私酒销售（合计远低于 $15,000）
    • 纸张：商业账本纸，淡黄色，有浅蓝格线
    • 装订：活页或账本页

### 9204 - Tommy 酒吧账本 / Tommy's Bar Ledger
- itemType: 3
- canAnalyzed: false
- canCombined: false
- Describe: |
    蓝月亮酒吧的正式账本。月净收益 $4,000，主要来自私酒和舞会入场费。
    还有两笔"古董买卖"——花瓶卖给 Thompson，油画卖给 Coleman。
- ShortDescribe: 酒吧账本——月净 $4,000；古董买卖：花瓶给 Thompson、油画给 Coleman。
- location: Tommy 办公室 / TommyOffice
- Chapter: EPI09
- folderPath: EPI09\TommyOffice
- desSpritePath: SC9010_item_04_big
- mapSpritePath: SC9010_item_04
- Position: 待补充（美术）
- ArtRequirement: |
    正式营业账本，硬皮精装，尺寸约 25×35 cm，翻开状态
    • 双页显示：左页为日期 + 项目明细，右页为合计
    • 栏目：Date / Item / Amount / Buyer
    • 可辨识条目：
      - "Vase — $4,000 — Thompson"
      - "Oil painting — $7,000 — Coleman"
      - 多项 "Private liquor sales — $XX" 小额条目
    • 底部合计："Monthly Net: $4,000"
    • 字迹：Tommy 的手写账目，工整但有擦改痕迹
    • 纸张：淡黄色账本纸，浅蓝横格

### 9205 - 假油画 / Forged Painting
- itemType: 3
- canAnalyzed: false
- canCombined: false
- Describe: |
    装裱精良的油画，挂在歌舞厅墙上。
    Tommy 的账本写"已卖给 Coleman"——但这画明明还在。
    仔细看，画风粗糙，是仿品。
- ShortDescribe: 账本写"卖给 Coleman"的油画还挂在墙上——仿品。
- location: 歌舞厅 / DanceHall
- Chapter: EPI09
- folderPath: EPI09\DanceHall
- desSpritePath: SC9005_item_05_big
- mapSpritePath: SC9005_item_05
- Position: 待补充（美术）
- ArtRequirement: |
    镀金画框油画，尺寸约 60×80 cm，墙挂状态
    • 画面内容：1920s 欧式古典风景 / 人物肖像（假装是"名画"）
    • 近看笔触粗糙、颜色过于鲜艳、光影处理不协调——一眼仿品
    • 画框：镀金巴洛克风格，装饰过度
    • 背景：歌舞厅墙面
    • 可选：画面一角有微小的仿冒签名（非大师手笔）

### 9206 - 花瓶现场照 / Vase in Scene Photo
- itemType: 1
- canAnalyzed: false
- canCombined: false
- Describe: |
    案发当晚拍的歌舞厅现场照。
    账本上写着"已卖给 Thompson"的花瓶，还摆在原位。
- ShortDescribe: 案发当晚的现场照——"卖给 Thompson"的花瓶还在原位。
- location: 歌舞厅 / DanceHall
- Chapter: EPI09
- folderPath: EPI09\DanceHall
- desSpritePath: SC9005_item_06_big
- mapSpritePath: SC9005_item_06
- Position: 待补充（美术）
- ArtRequirement: |
    黑白 / 棕褐调室内环境照片，尺寸约 15×20 cm
    • 画面：歌舞厅一角，中景或全景
    • 画面中：一只装饰性花瓶立于基座或桌面
    • 构图自然，非刻意拍花瓶（像案发后排查用的普通照）
    • 照片背面：铅笔手写备注"1928-11-3 案发现场"
    • 纸张：半哑光相纸，边缘有白边

### 9207 - James 工资单 / James's Payslip
- itemType: 3
- canAnalyzed: false
- canCombined: false
- Describe: |
    James 的月薪条——主厨，$80 一个月。
- ShortDescribe: James 的月薪条——主厨，$80 一个月。
- location: James 厨房 / JamesKitchen
- Chapter: EPI09
- folderPath: EPI09\JamesKitchen
- desSpritePath: SC9009_item_07_big
- mapSpritePath: SC9009_item_07
- Position: 待补充（美术）
- ArtRequirement: |
    小型工资单，尺寸约 10×15 cm
    • 格式：1920s 标准工资单（印刷表格 + 手填数字）
    • 姓名栏：James O'Sullivan（或 James）
    • 职位栏：Chef
    • 月薪栏：$80.00
    • 日期栏：1928 年某月
    • 雇主栏：Blue Moon Saloon
    • 纸张：薄型商业凭证纸，淡黄色
    • 底部：盖章或签字

### 9208 - Vivian 排班表 / Vivian's Work Schedule
- itemType: 2
- canAnalyzed: false
- canCombined: false
- Describe: |
    酒吧演出人员排班表——Vivian 那栏写着：每晚最后一项，23:30 送酒至会客室。
- ShortDescribe: 演出排班表——Vivian 每晚最后一项：23:30 送酒至会客室。
- location: Tommy 办公室 / TommyOffice
- Chapter: EPI09
- folderPath: EPI09\TommyOffice
- desSpritePath: SC9010_item_08_big
- mapSpritePath: SC9010_item_08
- Position: 待补充（美术）
- ArtRequirement: |
    大型排班表 / 周程表，尺寸约 40×60 cm，墙挂状态
    • 栏目：演出人员 / 每日时间段 / 任务内容
    • Vivian 行：每晚任务列表，最后一行 "23:30 — Deliver liquor to parlor"
    • 其他行：Tommy、James 等员工的排班
    • 载体：打印在硬纸板 / 写字板上，墙挂
    • 字体：1920s 办公打字 + 手填内容

### 9209 - 便携相机 / Portable Camera
- itemType: 3
- canAnalyzed: false
- canCombined: false
- Describe: |
    1920s 便携相机，落了灰。
    卷片轴上还有半卷未冲洗的底片，成像风格和勒索照片一样。
- ShortDescribe: 1920s 便携相机——卷片轴上半卷底片，成像风格与勒索照片一致。
- location: 歌舞厅小包厢 / SmallBox
- Chapter: EPI09
- folderPath: EPI09\SmallBox
- desSpritePath: SC9006_item_09_big
- mapSpritePath: SC9006_item_09
- Position: 待补充（美术）
- ArtRequirement: |
    1920s 折叠皮腔便携相机（Kodak Vest Pocket 或类似型号），尺寸约 15×10×5 cm（折叠状态）
    • 外壳：黑色皮革 + 金属包边，1920s 复古风
    • 状态：半开皮腔或侧视
    • 表面落灰，但金属件仍有光泽
    • 细节：背面卷片转钮、镜头上的型号标
    • 背景：木质抽屉一角或证据袋

### 9210 - 厨房工作表 / Kitchen Work Schedule
- itemType: 2
- canAnalyzed: false
- canCombined: false
- Describe: |
    2F 厨房当晚的值班表。
    James 一栏：22:00–00:00 厨房值守，其中 23:00–23:10 下楼送餐。
- ShortDescribe: 2F 厨房当晚值班表——James 22:00-00:00 厨房，23:00-23:10 下楼送餐。
- location: James 厨房 / JamesKitchen
- Chapter: EPI09
- folderPath: EPI09\JamesKitchen
- desSpritePath: SC9009_item_10_big
- mapSpritePath: SC9009_item_10
- Position: 待补充（美术）
- ArtRequirement: |
    手写 + 打字结合的值班表，letter size 纸张
    • 栏目：员工 / 时段 / 岗位
    • James 行：22:00-00:00 主线条目 + 23:00-23:10 "Deliver to downstairs" 小字注
    • 其他员工行：副厨 / 服务生的排班
    • 纸张：厨房油渍轻微污染，纸角略卷
    • 顶部打印酒吧 Logo

## NPCStaticData

### 905 - Tommy / Tommy
- role: 3
- Chapter: EPI09
- IconSmall: tommy_small
- IconLarge: tommy_big

### 907 - James / James
- role: 2
- Chapter: EPI09
- IconSmall: james_small
- IconLarge: james_big

## SceneConfig

### 9204 - 酒吧大堂 / Main Hall
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9004_bg_MainHall
- backgroundMusic: 待补充
- ItemIDs: []

### 9205 - 歌舞厅 / Dance Hall
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9005_bg_DanceHall
- backgroundMusic: 待补充
- ItemIDs: [9205, 9206]

### 9206 - 歌舞厅小包厢 / Dance Hall Small Box
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9006_bg_SmallBox
- backgroundMusic: 待补充
- ItemIDs: [9201, 9209, 9211, 9212]

### 9207 - 一楼走廊 / First Floor Corridor
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9007_bg_Corridor
- backgroundMusic: 待补充
- ItemIDs: []

### 9209 - James 厨房 / James's Kitchen
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

### 9210 - Tommy 办公室 / Tommy's Office
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

### 9211 - Webb 办公室 / Webb's Office
- sceneType: 1
- Chapter: EPI09
- backgroundImage: Art\Scene\Backgrounds\EPI09\SC9011_bg_WebbOffice
- backgroundMusic: 待补充
- ItemIDs: [9202, 9203]

## TestimonyItem

### 9052001 - Tommy 谎言：酒吧只有正当生意
- testimonyType: 1
- testimony: 酒吧里都是正当生意，除了私酒没有别的交易。
- triggerType: 0
- triggerParam: "905"

### 9052003 - Tommy 身份：酒吧经理
- testimonyType: 1
- testimony: 我是蓝月亮酒吧的经理。
- triggerType: 0
- triggerParam: "905"

### 9072001 - James 随口：很缺钱
- testimonyType: 1
- testimony: 我很缺钱，最近家里不容易。
- triggerType: 0
- triggerParam: "907"

### 9072002 - James：同病相怜
- testimonyType: 2
- testimony: Vivian 杀 Webb 情有可原——我们都挺惨的。
- triggerType: 0
- triggerParam: "907"

### 9072003 - James 身份：主厨
- testimonyType: 1
- testimony: 我是蓝月亮酒吧的主厨。
- triggerType: 0
- triggerParam: "907"

## Testimony

### 9052001 - Tommy 谎言 完整证词
- npc_ref: 905
- chapter: 902
- words: |
    酒吧里都是正当生意，除了私酒之外没有别的交易。
- evidenceItem_refs: [9052001]

### 9052003 - Tommy 身份 完整证词
- npc_ref: 905
- chapter: 902
- words: |
    我是蓝月亮酒吧的经理。
- evidenceItem_refs: [9052003]

### 9072001 - James 缺钱 完整证词
- npc_ref: 907
- chapter: 902
- words: |
    唉，最近真是很缺钱，家里不容易。
- evidenceItem_refs: [9072001]

### 9072002 - James 同病相怜 完整证词
- npc_ref: 907
- chapter: 902
- words: |
    Vivian 杀 Webb 的事，情有可原——我们这种人过得都挺惨的。
- evidenceItem_refs: [9072002]

### 9072003 - James 身份 完整证词
- npc_ref: 907
- chapter: 902
- words: |
    我是蓝月亮酒吧的主厨。
- evidenceItem_refs: [9072003]

## DoubtConfig

### 9201 - 这些照片上的人，似乎在哪里见过一样？
- text: 这些照片上的人，似乎在哪里见过一样？
- Chapter: EPI09
- condition:
  - {type: 1, param: 9201}
  - {type: 1, param: 9202}

### 9202 - 两本账为何对不上？
- text: 两本账为何对不上？
- Chapter: EPI09
- condition:
  - {type: 1, param: 9203}
  - {type: 1, param: 9204}

### 9203 - 这些东西摆在这里是做什么呢？
- text: 这些东西摆在这里是做什么呢？
- Chapter: EPI09
- condition:
  - {type: 1, param: 9205}
  - {type: 1, param: 9206}

### 9204 - James 很缺钱（碎片）
- text: James 很缺钱…（碎片）
- Chapter: EPI09
- isFragment: true
- condition:
  - {type: 3, param: 9072001}

## ChapterConfig (部分写入)

### 902
- initScene: 9005
- doubts_ref: [9201, 9202, 9203, 9204]
- topBg: Art/Scene/Expose/epi09/top_tommy
- bottomBg: Art/Scene/Expose/epi09/tommy
- _skip_fields: [initTalk, exposeNpcId, exposes, suspectVideoPos, suspectTalkPos, zackTalkPos]
