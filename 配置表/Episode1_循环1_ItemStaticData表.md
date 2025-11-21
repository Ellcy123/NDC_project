# Episode 1 循环1 - ItemStaticData表（证据/物品静态数据表）

## 📋 表格说明

- **数据来源**: Episode 1 循环1 - Rosa现场目击指证
- **导出格式**: JSON
- **版本**: v1.0
- **日期**: 2025-11-12
- **循环名称**: Rosa现场目击指证
- **核心目标**: 到底是谁把我迷晕了,还想把杀人的罪名扣在我头上?
- **总计证据数量**: 8个

---

## 🔍 循环1证据静态数据表

| id | cnName | enName | itemType | cnDescribe1 | cnDescribe2 | cnDescribe3 | enDescribe1 | enDescribe2 | enDescribe3 | path1 | path2 | path3 |
|:---:|:---|:---|:---:|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| EV001 | 芝加哥警局通缉令 | Chicago Police Wanted Poster | envir | 通缉"疤面Tony"的悬赏金高达5000美元 | 报纸上刊登的通缉令,展示了1920年代芝加哥黑帮横行的社会背景 | | Wanted poster for "Scarface Tony" with a bounty of $5,000 | Wanted poster published in the newspaper, showing the social background of Chicago gangsters in the 1920s | | Art/UI/Item/WantedPoster | Art/UI/Item/WantedPoster_Detail | |
| EV002 | Rosa的女儿照片 | Rosa's Daughter Photo | clue | 照片背面写着"我的小天使Miguel,妈妈的一切希望",女儿生日0915 | 墙上相框中的温馨照片,展现了Rosa深深的母爱 | 这张照片的生日数字0915是工具箱密码锁的答案 | Photo back reads "My little angel Miguel, mother's everything hope", daughter's birthday 0915 | Warm photo in wall frame, showing Rosa's deep maternal love | The birthday number 0915 on this photo is the answer to the toolbox combination lock | Art/UI/Item/PhotoFrame | Art/UI/Item/PhotoFrame_Detail | |
| EV003 | Rosa的医院就诊清单 | Rosa's Hospital Bill | clue | 女儿Miguel的昂贵药物清单,经济压力巨大 | 清单上显示多种昂贵药物,总费用远超Rosa的工资收入 | 这解释了为什么Rosa会被Morrison威胁时选择妥协 | Expensive medication list for daughter Miguel, huge financial pressure | List shows various expensive medications, total cost far exceeds Rosa's salary | This explains why Rosa chose to compromise when threatened by Morrison | Art/UI/Item/MedicalBill | Art/UI/Item/MedicalBill_Detail | |
| EV004 | 沾有氯仿的毛巾 | Chloroform-Stained Towel | item | 一条普通的白色毛巾 | 接近闻嗅时有明显的甜腻化学味,是氯仿的味道,这不是清洁用品 | 这条毛巾是Morrison用来迷晕Zack的关键证据 | An ordinary white towel | Upon close sniffing, there's a distinctly sweet chemical smell, it's chloroform, not a cleaning product | This towel is key evidence that Morrison used to drug Zack | Art/UI/Item/Towel | Art/UI/Item/Towel_Analyzed | |
| EV005 | 工作记录卡 | Work Record Card | item | Rosa Martinez - 11月15日夜班:后台走廊清洁 23:00-01:00 | 这张工作记录卡明确显示Rosa的工作地点是后台走廊,而不是她声称的地下室酒窖 | 这是击破Rosa第一层谎言"一直在地下室"的关键证据 | Rosa Martinez - Night shift Nov 15: Backstage corridor cleaning 23:00-01:00 | This work record clearly shows Rosa's work location was the backstage corridor, not the basement wine cellar she claimed | This is key evidence to break Rosa's first lie "always in the basement" | Art/UI/Item/WorkCard | Art/UI/Item/WorkCard_Detail | |
| EV006 | 氯仿瓶 | Chloroform Bottle | item | 医用麻醉剂氯仿的玻璃瓶,瓶口有少量氯仿残留 | 在歌舞厅一楼走廊垃圾桶内发现,靠近Rosa的工作区域 | 与沾有氯仿的毛巾相互印证,证明Morrison在此处迷晕了Zack | Glass bottle of medical anesthetic chloroform, with small amount of chloroform residue at bottle mouth | Found in trash can in first floor corridor of dance hall, near Rosa's work area | Corroborates with chloroform-stained towel, proving Morrison drugged Zack here | Art/UI/Item/ChloroformBottle | Art/UI/Item/ChloroformBottle_Detail | |
| EV007 | 地板拖拽痕迹 | Floor Drag Marks | clue | 地板上的拖拽痕迹 | 压痕较深,经过分析发现被拖动的东西至少150磅,普通女性的力量基本无法完成这样的拖拽行为 | 这证明Rosa没有足够力量独自拖拽Zack(180磅),她的自认是为了保护Morrison | Drag marks on the floor | Deep indentation, analysis shows the dragged object weighs at least 150 pounds, ordinary female strength basically cannot accomplish such dragging | This proves Rosa doesn't have enough strength to drag Zack (180 pounds) alone, her confession was to protect Morrison | Art/UI/Item/DragMarks | Art/UI/Item/DragMarks_Detail | |
| EV008 | Tommy时间证词 | Tommy's Time Testimony | clue | 确实有一声枪响...但这声枪响和平时黑帮火拼的声音不太一样,只听到了一声 | Tommy在办公室整理账目时,于11点30分听到了枪声,这个时间点很关键 | 这条证词在循环6中将成为揭穿Jimmy伪造死亡时间的重要线索 | Indeed there was a gunshot... but this gunshot was different from the usual gang firefights, only heard one shot | Tommy heard the gunshot at 11:30 while organizing accounts in the office, this timing is crucial | This testimony will become important clue to expose Jimmy's faked death time in Loop 6 | Art/UI/Item/Testimony | Art/UI/Item/Testimony_Detail | |

---

## 📊 循环1证据分类统计

### 按证据类型分类

| 类型 | 证据ID | 数量 | 说明 |
|:---|:---|:---:|:---|
| **item (可收集物品)** | EV004, EV005, EV006 | 3 | 关键指证证据,可放入背包 |
| **clue (线索)** | EV002, EV003, EV007, EV008 | 4 | 推理线索,不一定是实体物品 |
| **envir (环境物品)** | EV001 | 1 | 环境叙事,只能查看不能收集 |

### 按证据作用分类

| 作用 | 证据ID | 数量 | 说明 |
|:---|:---|:---:|:---|
| **环境叙事** | EV001, EV002, EV003 | 3 | 建立情感背景和世界观 |
| **指证核心** | EV004, EV005, EV006, EV007 | 4 | 用于三轮指证Rosa |
| **伏笔线索** | EV008 | 1 | 为循环6埋下伏笔 |

### 按发现场景分类

| 场景 | 证据ID | 数量 |
|:---|:---|:---:|
| **Rosa储藏室** | EV001, EV002, EV003, EV004, EV005 | 5 |
| **歌舞厅一楼走廊** | EV006, EV007 | 2 |
| **Tommy办公室** | EV008 | 1 |

---

## 🎯 循环1指证逻辑关系

### 三轮指证证据使用

#### 第一轮指证：否定地点谎言
- **使用证据**: EV005 (工作记录卡)
- **Rosa谎言**: "我一直在地下室酒窖工作"
- **指证结果**: 击破地点谎言,Rosa被迫承认在后台走廊工作

#### 第二轮指证：否定目击谎言
- **使用证据**: EV004 (沾有氯仿的毛巾) + EV006 (氯仿瓶)
- **Rosa谎言**: "我很专心清洁,什么异常都没发生"
- **指证结果**: 击破目击谎言,Rosa承认迷晕了Zack,但声称是自己做的

#### 第三轮指证：否定自认,揭露真相
- **使用证据**: EV007 (地板拖拽痕迹)
- **Rosa谎言**: "是我把Zack拖到Webb办公室的"
- **指证结果**: 证明Rosa没有足够力量,揭露真正幕后黑手Morrison

---

## 🔐 特殊证据机制

### 解谜证据
**EV002 (Rosa的女儿照片)**
- **解谜类型**: 密码锁
- **密码答案**: 0915 (照片背面的女儿生日)
- **解锁内容**: 清洁工具箱
- **解锁后获得**: EV004 (毛巾) + EV005 (工作记录卡)

### 需要分析的证据
**EV004 (沾有氯仿的毛巾)**
- **分析前**: 一条普通的白色毛巾
- **分析操作**: 接近闻嗅
- **分析后**: 发现甜腻化学味,确认为氯仿
- **字段变化**: cnDescribe1 → cnDescribe2

**EV007 (地板拖拽痕迹)**
- **分析前**: 地板上的拖拽痕迹
- **分析操作**: 测量压痕深度
- **分析后**: 确认需要至少150磅力量
- **字段变化**: cnDescribe1 → cnDescribe2

---

## 💡 使用说明

### 字段说明

1. **id**: 证据唯一标识符,格式为EV + 3位数字
2. **cnName/enName**: 中英文物品名称
3. **itemType**: 物品类型
   - `item`: 可收集的实体物品
   - `clue`: 推理线索
   - `envir`: 环境物品(不可收集)
4. **cnDescribe1/2/3**: 中文描述
   - cnDescribe1: 初始状态描述
   - cnDescribe2: 分析后/不同状态描述
   - cnDescribe3: 特殊状态/背景信息
5. **enDescribe1/2/3**: 英文描述(对应中文)
6. **path1/2/3**: 美术资源路径

### 设计原则

✅ **描述分层** - 第一描述简洁,第二描述详细,第三描述特殊
✅ **类型明确** - 区分可收集物品、线索、环境物品
✅ **双语完整** - 中英文描述完整对应

---

## 🔗 关联配置表

- **NPC表**: EV002/EV003与NPC003(Rosa)相关
- **Talk表**: 指证对话中会引用这些证据ID
- **场景配置**: 证据在不同场景中的分布和获取方式

---

## 📝 数据完整性检查

- [x] 所有证据ID唯一
- [x] 中英文描述完整
- [x] itemType正确分类
- [x] 美术资源路径规范
- [x] 指证逻辑关系清晰
- [x] 解谜机制说明完整

---

**文档状态**: ✅ 循环1已完成
**下一步**: 生成循环2证据表(Morrison腐败网络调查)
**循环1证据总计**: 8个
