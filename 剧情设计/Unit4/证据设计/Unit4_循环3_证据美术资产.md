# Unit4 循环3 - 证据美术资产清单

> 叙事主题：Morrison 之死  
> 正式证据总数：14 条（均为原始物件、现场或环境证据）  
> ID 范围：4311-4324  
> 数据源：`剧情设计/Unit4/state/loop3_state.yaml`、`avg_editor_v2/data/table/ItemStaticData.json`、`剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`  
> 全局规范与跨循环复用要求：见 [Unit4 证据美术资产总览](./Unit4_证据美术资产_总览.md)

---

## 证据总表

| ID | 中文名 | 类型/地点 | 小玩法关系 |
|---|---|---|---|
| 4311 | 磨号手枪与枪内未击发余弹 | Clue；Morrison 书房尸体右手。 | 无 |
| 4312 | 伪造遗书 | Item；Morrison 书房书桌。 | 无 |
| 4313 | Pierce 档案移交通知（档案袋装） | Item；Morrison 书房档案袋。 | 无 |
| 4314 | 两只酒杯 | Clue；Morrison 宅邸门厅/电话桌与客厅。 | 无 |
| 4323 | 宅邸常用物件的偏左摆放 | Envir；Morrison 宅邸书房，客厅延续同一动线。 | 无 |
| 4324 | 门廊卷收式厚质防风帘 | Envir；Morrison 宅邸门外/爆炸后回收区。 | QTE环境铺垫，不作门槛 |
| 4315 | 古巴雪茄烟蒂 | Clue；第二只酒杯旁的湿杯垫。 | 跨玩法输入 |
| 4316 | 伪造市政煤气铅封与异常时钟接线 | Clue；Morrison 宅邸厨房检修区，爆炸前取得。 | 危机门控输入 |
| 4321 | 煤气阀门异常开启痕迹 | Envir；Morrison 宅邸煤气阀。 | 危机门控输入 |
| 4322 | 窗缝逆风与煤气味 | Envir；Morrison 宅邸背风侧窗。 | 危机门控输入 |
| 4317 | 214 号黄铜寄存柜钥匙 | Key Item；法院外圈调度台旁的临时物品盘。 | 容器钥匙输入 |
| 4318 | Harrison 案证物转运调度单 | Item；法院外圈调度材料。 | 无 |
| 4319 | 晚间报纸号外 | Item；法院外圈晚间报摊/散落报纸。 | 无 |
| 4320 | Morrison 写给 Zack 的未寄出口供 | Item；车站 214 号寄存柜。 | 容器输出 |

---

## 证据详细卡片

### 4311 - 磨号手枪与枪内未击发余弹

- 类型/地点：Clue；Morrison 书房尸体右手。
- `Name`：`磨号手枪与枪内未击发余弹` / `Defaced Pistol and Unfired Rounds`
- `Describe`：  
  `一把被放在 Morrison 尸体右手中的手枪。它不是 Morrison 的登记配枪，枪号已被磨去，手指也没有形成稳定握持。枪内仍有未击发余弹；这些事实说明现场使用了刻意切断来源的武器，但不能单独确定开枪者。`  
  `A pistol placed in Morrison's right hand. It is not his registered service weapon, its serial number has been ground away, and his fingers do not form a stable grip. Unfired rounds remain in the gun. These facts show an effort to sever the weapon's traceable origin, but do not identify the shooter.`
- `ShortDescribe`：  
  `非登记配枪，枪号被磨去，并被松散地放在 Morrison 右手。`  
  `An unregistered pistol with its serial ground off, loosely placed in Morrison's right hand.`
- 小玩法关系：`无`。属于爆炸前非进度型现场记录；爆炸后原现场被毁，不生成独立分析产物。

重点（信息表达必不可少）：

1. 取证构图必须同时看到“右手”“松散手指”“枪号磨损区”和手枪主体。
2. 枪号磨除应表现为新鲜机械刮磨，不是自然锈蚀。
3. 余弹作为同一证据的插图/剖开展示，可辨为未击发，但不画成能够直接锁定具体供枪者的独家标识。
4. 不出现 Mickey 指纹、姓名或“凶器属于某人”的标签。

美术参考（不影响推理）：

- Zack 爆炸前匆忙拍下的近景记录，黑白或低饱和闪光照片；手枪为 1920 年代常见半自动手枪/左轮，由武器设定统一。
- 尸体手部避免猎奇特写，重点是握持关系和可追溯编号被破坏。

---

### 4312 - 伪造遗书

- 类型/地点：Item；Morrison 书房书桌。
- `Name`：`伪造遗书` / `Forged Suicide Note`
- `Describe`：  
  `一封把 Morrison 的死亡写成旧案暴露后的畏罪自杀的遗书。字迹近似他的日常笔迹，但用词刻意粗暴，把二十年的系统性犯罪压缩成个人贪腐与精神崩溃。全文没有提及煤气、爆炸或报复社会。`  
  `A note framing Morrison's death as guilt-driven suicide after the exposure of old cases. The handwriting resembles his everyday script, but the wording is conspicuously crude, reducing twenty years of systemic crime to personal corruption and collapse. It makes no mention of gas, an explosion, or an attack on others.`
- `ShortDescribe`：  
  `字迹近似 Morrison，却用粗暴措辞把一切写成个人畏罪自杀。`  
  `The handwriting resembles Morrison's, but the crude wording reduces everything to a guilt-driven suicide.`
- 小玩法关系：`无`。作为伪造现场的辅助判断，不进入 Doris 三轮击穿。

重点（信息表达必不可少）：

1. 正文应使用第一人称认罪/崩溃口吻，但不得提煤气、爆炸或袭击他人。
2. 字迹“像 Morrison 但不自然”：整体字形近似，落笔节奏过于刻意，部分常用词用法不符。
3. 不直接标注 `FORGED`，玩家通过内容与现场自行判断。

美术参考（不影响推理）：

- 普通书桌信纸，蓝黑钢笔字，纸张摆得过分端正；与凌乱现场形成轻微违和。

---

### 4313 - Pierce 档案移交通知（档案袋装）

- 类型/地点：Item；Morrison 书房档案袋。
- `Name`：`Pierce档案移交通知（档案袋装）` / `Pierce File-Transfer Notice`
- `Describe`：  
  `一份要求 Morrison 次日上午交出旧案文件与配枪登记的正式通知，连同档案袋装订保存。签发时间早于 Whitfield 被带走补充笔录，说明对 Morrison 的接管不是庭审结束后才临时决定。通知只证明提前存在接管压力，不证明 Pierce 亲自在场杀人。`  
  `A formal notice ordering Morrison to surrender old-case files and firearm records the next morning, preserved in its official folder. It was issued before Whitfield was taken for further questioning, showing that the takeover of Morrison's files was not improvised after the hearing. It establishes prior pressure, not Pierce's physical presence at the killing.`
- `ShortDescribe`：  
  `要求 Morrison 次日交出旧案与配枪记录，签发早于 Whitfield 被带走。`  
  `It orders Morrison to surrender old-case and firearm records and was issued before Whitfield was taken in.`
- 小玩法关系：`无`。为 4320 的开口动机提供前置事实，不参与本轮指证。

重点（信息表达必不可少）：

1. 抬头体现警务/档案接管程序，正文可读 `SURRENDER OF OLD CASE FILES AND FIREARM RECORDS`。
2. 日期／时刻栏保留签发章与程序位置，但数字必须模糊不可辨；不得自行写入具体日期或钟点。先于 Whitfield 补充笔录的事实由配置文本承担，不依赖画面上可读数字。
3. Pierce 的签发身份可读，但不附在场证明或杀人指令。
4. 档案袋外封与通知内页需成套制作。

美术参考（不影响推理）：

- 深棕警局档案袋、棉线绕扣、打字通知和蓝色收文章；封口未完全封死，表现 Morrison 已经读过。

---

### 4314 - 两只酒杯

- 类型/地点：Clue；Morrison 宅邸门厅/电话桌与客厅。
- `Name`：`两只酒杯` / `Two Drinking Glasses`
- `Describe`：  
  `客厅里有两只酒杯。一只位于 Morrison 日常使用的位置，另一只仍有残酒，碎冰尚未完全融化，杯垫水痕仍湿。Doris 离家前的晚饭已过去三小时，第二杯不可能从晚饭时一直保持这种状态。`  
  `Two drinking glasses stand in the room. One is in Morrison's usual place; the other still holds liquor, with ice not fully melted and a wet ring on the coaster. More than three hours have passed since dinner before Doris left, too long for the second glass to remain in this state from that meal.`
- `ShortDescribe`：  
  `第二只酒杯仍有残酒、未融碎冰和湿水痕。`  
  `The second glass still holds liquor, partly unmelted ice, and a wet ring.`
- 小玩法关系：`无`。与 4315 共同用于 Doris Expose R2。

重点（信息表达必不可少）：

1. 两只杯子的位置和状态必须明显不同；第二杯是视觉焦点。
2. 第二杯可见残酒、碎冰和仍湿的杯垫水环，三项缺一不可。
3. 第一杯体现长期惯用位置，不用夸张标签标出 Morrison 所有权。
4. 4315 烟蒂在第二只杯旁，双方构图需能拼成同一次会面。

美术参考（不影响推理）：

- 厚底威士忌杯、木质电话桌/边几、暖色台灯；水珠与湿杯垫在近景中清楚但自然。

---

### 4323 - 宅邸常用物件的偏左摆放

- 类型/地点：Envir；Morrison 宅邸书房，门厅客厅延续同一生活动线。
- `Name`：`宅邸常用物件的偏左摆放` / `Left-Biased Placement of Everyday Household Objects`
- `Describe`：  
  `Morrison 宅邸书房的墨水瓶、警徽盒和常用杯垫长期集中在座位左侧的顺手区域，桌面相应位置留下反复取放形成的磨痕；客厅日常酒杯的位置延续同一偏左动线。这能证明宅邸内存在稳定的左侧使用习惯，但不能单独确认这一习惯由 Harold、Doris 或哪位住户形成，也不能直接判定任何人的惯用手。`  
  `In the Morrison study, the inkwell, badge case, and everyday coaster have long been kept within easy reach on the left side of the seat, with repeated handling marks on the corresponding part of the desk; the usual glass position in the sitting room continues the same left-biased pattern. This establishes a stable left-side household routine, but does not identify whether Harold, Doris, or another resident formed it, nor directly establish anyone's handedness.`
- `ShortDescribe`：  
  `墨水瓶、警徽盒和常用杯垫长期集中在左侧顺手区，磨痕显示并非临时摆放。`  
  `The inkwell, badge case, and everyday coaster have long occupied the left-hand reach zone; wear marks show the arrangement is not temporary.`
- 小玩法关系：`无`。作为爆炸前必查的环境观察，不收集、不进 CASE BOARD、不参与指证，也不与 4311 自动合成；Harold 惯用左手仍由 Doris 的 4063002 生活证词确认。

重点（信息表达必不可少）：

1. 书房座位、桌面左侧顺手区、墨水瓶、警徽盒和常用杯垫的空间关系必须能在同一构图中读懂。
2. 左侧桌面应有长期反复取放留下的磨亮、浅印或纸张避色差，不能像临时把物件挪到左边。
3. 客厅第一只日常酒杯的位置延续同一偏左动线，但不新增第二个 4323 交互点。
4. 不出现 `LEFT-HANDED`、Harold 姓名标注或系统自动结论，也不把本观察与右手枪位放进同一张答案式对照图。

美术参考（不影响推理）：

- 低瓦数台灯下的书桌环境局部，材质磨损克制、生活化；物件本身保持普通，不做高亮谜题陈列。
- 详情图以空间摆放和长期磨损为主，不制作可收集的独立物品图。

---

### 4324 - 门廊卷收式厚质防风帘

- 类型/地点：Envir；Morrison 宅邸门外/爆炸后回收区。
- `Name`：`门廊卷收式厚质防风帘` / `Roll-Down Heavy Porch Wind Curtain`
- `Describe`：  
  `Morrison宅邸外门廊横梁装有卷收式厚质防风帘；带配重的下沿连接控制绳，绳索收束在外侧门柱铜质绳扣上。爆炸后布面仅有烟尘和轻度破损，卷轴、控制绳与配重连接仍完整。`  
  `A heavy roll-down wind curtain is mounted beneath the outer porch beam of the Morrison residence. Its weighted lower edge is linked to a control rope secured around a brass cleat on the outer porch post. After the explosion, the fabric bears soot and minor damage, while the roller, rope, and weighted connection remain intact.`
- `ShortDescribe`：  
  `卷轴、配重下沿和外侧门柱绳扣连接完整，爆炸后仍可活动。`  
  `The roller, weighted lower edge, and outer-post cleat remain connected and operable after the explosion.`
- 小玩法关系：`QTE环境铺垫，不作门槛`。4029 抵达镜头不可漏地建立装置位置；4023 爆炸后允许玩家查看其现状。它不收集、不进 CASE BOARD、不挂疑点或指证；Pierce 开枪 QTE 不以玩家是否查看为触发条件。

重点（信息表达必不可少）：

1. 同一构图中清楚表现横梁卷轴、厚质帘体、带配重下沿、控制绳和外侧门柱铜质绳扣的连接关系。
2. 爆炸后布面只表现烟尘与轻度破损；卷轴、控制绳和配重连接仍完整。
3. 不出现拉绳撞偏持枪手臂、防弹、制服 Pierce 或其他答案式提示。
4. SC4029 爆炸前抵达镜头与 SC4023 爆炸后状态必须保持装置位置和结构连续。

美术参考（不影响推理）：

- 1920 年代宅邸门廊的厚帆布或厚棉布防风设施，黄铜绳扣与木质或金属配重杆有日常使用磨损。
- 详情图以客观结构为主，不制作成武器或机关说明图。

---

### 4315 - 古巴雪茄烟蒂

- 类型/地点：Clue；第二只酒杯旁的湿杯垫。
- `Name`：`古巴雪茄烟蒂` / `Cuban Cigar Butt`
- `Describe`：  
  `一截古巴雪茄烟蒂被按灭在第二只酒杯旁。烟灰粘在仍湿的杯垫水痕上。烟嘴右侧留有一组不寻常的咬痕：前段向内塌陷，后段少了一枚完整压痕，整体受力约呈三十度斜向。`  
  `A Cuban cigar butt was crushed out beside the second drinking glass, its ash stuck to the still-wet coaster ring. The right side of the mouth end bears an unusual compound bite pattern: the forward section collapses inward, one complete rear impression is absent, and the force runs at roughly a thirty-degree angle.`
- `ShortDescribe`：  
  `按灭在湿杯垫旁的古巴雪茄烟蒂，右侧留有异常复合咬痕。`  
  `A Cuban cigar butt crushed beside a wet coaster, with an unusual compound bite on the right.`
- 小玩法关系：`跨玩法输入`。L3 与 4314 证明近期访客；L5 身份锁链 4503 与 4512 比较品牌、直径、含咬位置和复合齿痕后生成 4708。原物不消耗。4704 只提供比较方向，不占提交位。

重点（信息表达必不可少）：

1. 雪茄烟蒂、第二只酒杯和仍湿的杯垫必须同框；烟灰粘在水痕边缘。
2. 右侧咬痕清楚表现“前段内陷、后段缺少一枚完整压痕、约三十度斜向受力”。
3. 品牌卷标、直径、茄衣颜色和含咬位置必须与 4512 精确对应。
4. L3 画面不能出现 Mickey 姓名、缩写、牙齿示意或身份结论。

美术参考（不影响推理）：

- 1920 年代手卷古巴雪茄，深棕茄衣，燃烧端被压扁；湿杯垫纤维发暗，烟灰受潮结块。
- 近距离斜俯拍，暖色室内灯光；另为 L5 比对界面提供烟嘴侧面标准化裁切图。

---

### 4316 - 伪造市政煤气铅封与异常时钟接线

- 类型/地点：Clue；Morrison 宅邸厨房检修区的煤气表与壁炉时钟，爆炸前取得。
- `Name`：`伪造市政煤气铅封与异常时钟接线` / `Forged Municipal Gas Seal and Abnormal Clock Wiring`
- `Describe`：  
  `煤气表上装着一枚带完整序号的市政式铅封，壁炉时钟背后却出现了新铜线和额外接点。Doris 没有申报故障。现有观察只能确认来访者动过煤气与时钟，不能确定装置何时启动或由谁下令。`  
  `A numbered municipal-style lead seal is fitted to the gas meter, while fresh copper wire and an added contact appear behind the mantel clock. Doris reported no fault. The observation establishes that the visitors altered the gas and clock, not when the device would activate or who ordered it.`
- `ShortDescribe`：  
  `伪造铅封旁出现新铜线和额外时钟接点。`  
  `Fresh copper wire and an added clock contact sit behind a forged municipal seal.`
- 小玩法关系：`危机门控输入`。爆炸前玩家完成铅封与接线两处检查后取得本记录；它与 4321、4322 共同支持 Emma 组织撤离。爆炸后残件只反馈“与此前照片一致”，不更新 4316，也不生成新证据。

重点（信息表达必不可少）：

1. 完整铅封序号、新铜线、时钟接点三项同时清楚，但不拼成可拆卸的完整现代炸弹。
2. 市政铅封外观必须“像真品但序号核验有问题”，不能直接印 `FAKE`。
3. 不得出现 Mickey、Miller 或具体命令者。
4. 爆炸后的焦黑残件属于 4023 场景反馈，不制作成 4316 的第二套详情状态。

美术参考（不影响推理）：

- 老式煤气表、铅封钳痕、壁炉机械时钟和布绝缘铜线；详情图保持爆炸前现场观察状态。

---

### 4321 - 煤气阀门异常开启痕迹

- 类型/地点：Envir；Morrison 宅邸煤气阀。
- `Name`：`煤气阀门异常开启痕迹` / `Forced-Open Gas Valve Marks`
- `Describe`：  
  `主煤气阀近期被工具强行转动，刻度停在异常开启位置，金属边缘留下新鲜刮痕。痕迹只能说明阀门被人为开启，不能说明操作人。`  
  `The main gas valve was recently forced with a tool. Its index rests at an abnormal open position, with fresh scrape marks on the metal edge. The marks establish deliberate opening, not who operated it.`
- `ShortDescribe`：  
  `主阀停在异常开启位置，边缘有新鲜工具刮痕。`  
  `The main valve rests abnormally open, with fresh tool scrapes on its edge.`
- 小玩法关系：`危机门控输入`。与 4322、4316 的现场检查共同支持 Emma 发现危险并触发撤离；不进背包、不生成证据卡结果。

重点（信息表达必不可少）：

1. 阀门开启刻度和新鲜刮痕清晰，旧锈与新痕材质有差别。
2. 现场构图能让玩家理解这是煤气主阀，不画成普通水阀。
3. 不留下专属工具、指纹或执行人标记。

美术参考（不影响推理）：

- 旧黄铜/铸铁阀、油污管线、侧光突出金属新痕；作为可交互环境局部放大图。

---

### 4322 - 窗缝逆风与煤气味

- 类型/地点：Envir；Morrison 宅邸背风侧窗。
- `Name`：`窗缝逆风与煤气味` / `Sealed Window Gap and Trapped Gas`
- `Describe`：  
  `背风侧窗缝被布条人为塞紧，正常通风受到阻碍；靠近时能闻到室内积聚的煤气味。该观察只确认危险正在累积，不能判断装置的命令源。`  
  `Cloth has been deliberately packed into the leeward window gap, restricting normal ventilation; accumulated gas can be smelled nearby. The observation establishes a growing hazard, not the source of the order.`
- `ShortDescribe`：  
  `背风窗缝被布条塞紧，室内煤气无法正常散去。`  
  `Cloth blocks the leeward window gap, preventing the gas from dispersing normally.`
- 小玩法关系：`危机门控输入`。与 4321、4316 的检查共同触发爆炸前撤离；气味以交互文案/音效反馈表达，不作为可画颜色。

重点（信息表达必不可少）：

1. 布条明显是后来塞入窗缝，不是窗帘或自然破布。
2. 窗外风向可通过窗帘、树影或纸片表现“外面有风、室内却不通”，不能用可见绿色毒气。
3. 不出现现代警示图标或自动结论提示。

美术参考（不影响推理）：

- 夜间冷风、旧木窗框、布条压塞和轻微玻璃震动；配合低沉气流与角色咳嗽/提示反馈。

---

### 4317 - 214 号黄铜寄存柜钥匙

- 类型/地点：Key Item；法院外圈调度台旁的临时物品盘，爆炸前取得。
- `Name`：`214号黄铜寄存柜钥匙` / `Brass Key to Locker 214`
- `Describe`：  
  `在法院外圈调度台旁的临时物品盘中发现的一把旧黄铜钥匙。号码牌上只刻有“214”，没有车站、铁路、行李寄存、姓名或用途文字。它可以打开对应的 214 号柜门，但钥匙本身不能说明所有者或柜内文件内容。`
  `An old brass key found in a temporary property tray beside the court-perimeter dispatch desk. Its tag bears only the number “214,” with no station, railway, luggage-storage, name, or purpose marking. It can open the matching locker door but does not establish ownership or reveal the contents.`
- `ShortDescribe`：  
  `号码牌上只刻有“214”的黄铜钥匙。`
  `A brass key whose tag bears only the number “214.”`
- 小玩法关系：`容器钥匙输入`。用于解锁车站 214 号寄存柜并取得 4320；开柜后钥匙可保留或标记已使用，不生成派生 ID。

重点（信息表达必不可少）：

1. 黄铜牌上的 `214` 必须是唯一清晰可读的文字；不得出现铁路、车站、行李寄存、法院或其他机构标识。
2. 保留长期使用形成的黄铜磨耗，但不得出现爆炸烟尘或爆炸损伤。
3. 不在钥匙牌上写姓名、用途、Brennan、口供或柜内内容。

美术参考（不影响推理）：

- 1920 年代扁钥匙，椭圆/八角黄铜号码牌，边缘长期摩擦发亮；外形可与寄存柜锁孔适配，但不以徽记直接暴露用途。
- 另需 214 柜门、锁孔、开柜动画和扎绳文件包的容器美术。

---

### 4318 - Harrison 案证物转运调度单

- 类型/地点：Item；法院外圈调度材料。
- `Name`：`Harrison案证物转运调度单` / `Harrison Evidence-Transfer Dispatch Sheet`
- `Describe`：  
  `Harrison 案的证物转运调度与交接材料。记录显示 21:30 至 23:20 期间，Pierce 负责法院东门与市政档案库交接，相关警员不得离岗。材料可以解释警局为何迟到，并排除 Pierce 在主要案发窗口亲自在宅邸布置现场，但缺少足以证明其全程在场的独立连续记录。`  
  `Dispatch and handover records for evidence in the Harrison case. They place Pierce in charge of the courthouse east-gate and municipal archive transfer from 9:30 to 11:20 p.m., with assigned officers ordered not to leave. The records explain the delayed police response and exclude Pierce from personally staging the house during the principal window, but they do not provide independent continuous proof of his presence every minute.`
- `ShortDescribe`：  
  `21:30至23:20，Pierce 被排在法院东门与市政档案库交接任务中。`  
  `Pierce was assigned to the courthouse and municipal archive transfer from 9:30 to 11:20 p.m.`
- 小玩法关系：`无`。提供枪杀与警务迟到的时间边界，不进入 Doris 指证。

重点（信息表达必不可少）：

1. `21:30–23:20`、Pierce 姓名、法院东门、市政档案库和“不得离岗”安排可读。
2. 交接栏存在空白/非连续签字，视觉上保留“不是绝对全程证明”的边界。
3. 不写 `ALIBI CONFIRMED` 或绝对“不在场”。

美术参考（不影响推理）：

- 多页警务调度夹板、碳纸副本、时间栏和交接签名；纸面因夜间现场使用略有雨点/泥痕。

---

### 4319 - 晚间报纸号外

- 类型/地点：Item；法院外圈晚间报摊/散落报纸。
- `Name`：`晚间报纸号外` / `Evening Extra`
- `Describe`：  
  `晚间号外报道西区工会互助站遭到冲击，参与者中有数名银月会常用打手。报道只能说明城市另一处正在牵制人手，不能把该事件直接归为 Morrison 案的命令或不在场证明。`  
  `An evening extra reports an attack on a West Side union mutual-aid station involving several men commonly used by the Silver Moon Society. It shows that manpower was being drawn elsewhere in the city, but does not establish an order in the Morrison case or a complete alibi.`
- `ShortDescribe`：  
  `西区工会互助站遭冲击，多名银月会常用打手出现在报道中。`  
  `A West Side union aid station was attacked, with several Silver Moon enforcers reported there.`
- 小玩法关系：`无`。跨 Loop 城市人手伏笔；L5 功业簿帮助解释其意义，但本件不进入固定身份链。

重点（信息表达必不可少）：

1. 报头 `EVENING EXTRA` 与西区工会互助站遇袭标题可读。
2. 正文只写“数名与银月会有关的常用打手”，不写 Mickey 调走或下令。
3. 时间戳与 L3 夜间时间线一致，具体发行时刻由时间线校准。

美术参考（不影响推理）：

- 廉价晚报、粗糙黑白铅印、大号号外标题；边缘被夜风吹卷，局部沾湿。

---

### 4320 - Morrison 写给 Zack 的未寄出口供

- 类型/地点：Item；车站 214 号寄存柜。
- `Name`：`Morrison写给Zack的未寄出口供` / `Morrison's Unsent Statement to Zack`
- `Describe`：  
  `Morrison 留给 Zack 的书面口供。他承认自己替 Pierce 与 Whale 压过旧案，也承认没有资格要求 Zack 相信。Whitfield 被交出后，他收到交出文件、接受接管的通知，才确认自己也进入下一批清理。他不愿警局把自己的最后选择写成自杀、疯狂或报复社会。`  
  `Morrison's written statement for Zack. He admits suppressing old cases for Pierce and Whale and acknowledges that Zack has no reason to trust him. After Whitfield was surrendered, Morrison received an order to hand over his files and accept replacement, convincing him that he was in the next group to be cleared. He refuses to let the police describe his final choice as suicide, madness, or an attack on others.`
- `ShortDescribe`：  
  `Morrison 承认替 Pierce 与 Whale 压案，并准备把未被改写的事实交给 Zack。`  
  `Morrison admits suppressing cases for Pierce and Whale and tries to leave Zack an unaltered account.`
- 小玩法关系：`容器输出`。玩家使用 4317 打开 214 号寄存柜后取得；用于 Doris Expose R3。钥匙和口供不合成为新物品。

重点（信息表达必不可少）：

1. 信封或扉页明确写 `FOR ZACK BRENNAN`，正文由 Morrison 亲笔签名。
2. 可读核心词组：`Pierce`、`Whale`、`old cases`、`surrender my files`、`do not call this suicide`。
3. 口供应有反复修改和停顿，表现一个有罪者试图留下事实，而不是洗白式英雄遗书。
4. 不写出 Whale 真实姓名，不写 Mickey 到访或开枪事实。

美术参考（不影响推理）：

- 多页手写陈述装在扎绳牛皮纸文件包中；车站柜内保存状态干燥整齐，与宅邸内的危机和混乱形成反差。

---
