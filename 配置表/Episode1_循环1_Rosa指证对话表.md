# Episode 1 循环1 - Rosa三轮指证对话表

## 📋 表格说明

- **数据来源**: NDC_Episode_1_循环1_场景证据布局设计.md
- **导出格式**: JSON
- **版本**: v2.0
- **日期**: 2025-11-12
- **场景**: 酒吧大堂（Rosa指证）
- **总时长**: 约54秒
- **核心逻辑**: 三次证据否定，层层击破谎言

---

## 🎯 指证逻辑说明

### 三轮指证结构

**第一轮**: 否定地点谎言（使用证据115-工作记录卡）
- Rosa谎言: "一直在地下室酒窖工作"
- 指证结果: 击破地点谎言，Rosa承认在后台走廊

**第二轮**: 否定目击谎言（使用证据114-氯仿毛巾 + 证据121-氯仿瓶）
- Rosa谎言: "在后台走廊清洁，什么异常都没发生"
- 指证结果: Rosa承认迷晕了Zack，但声称是自己做的

**第三轮**: 否定自认，揭露真相（使用证据122-地板拖拽痕迹）
- Rosa谎言: "是我把Zack拖到Webb办公室的"
- 指证结果: 证明Rosa没有足够力量，揭露真正幕后黑手Morrison

---

## ⚔️ 第一轮指证：否定地点谎言

### 使用证据
- **证据115**: 工作记录卡（显示23:00-01:00在后台走廊清洁）

### 对话表

| id | step | speakType | waitTime | cnSpeaker | enSpeaker | imagePath | voicePath | cnWords | enWords | next | script | Parameter0 | Parameter1 | Parameter2 | Parameter3 |
|:---:|:---:|:---:|:---:|:---|:---|:---|:---|:---|:---|:---:|:---:|:---|:---|:---|:---|
| 001003010 | 1 | 2 | 2 | Zack Brennan | Zack Brennan | Art/UI/Character/Zack | Audio/Voice/Zack_040.mp3 | Rosa,这是你的工作安排表。上面明确写着你昨晚23:00到01:00在后台走廊清洁,不是地下室酒窖。 | Rosa, this is your work schedule. It clearly states you were cleaning the backstage corridor from 23:00 to 01:00 last night, not the basement wine cellar. | 001003011 | | | | | |
| 001003011 | 2 | 2 | 2 | Zack Brennan | Zack Brennan | Art/UI/Character/Zack | Audio/Voice/Zack_041.mp3 | 你为什么要撒谎? | Why are you lying? | 003002001 | | | | | |
| 003002001 | 3 | 2 | 3 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_010.mp3 | 哦...哦天哪,我...我可能记错了...最近太累了,总是搞混工作安排... | Oh... oh my god, I... I might have remembered wrong... been so tired lately, always mixing up work schedules... | 003002002 | | | | | |
| 003002002 | 4 | 2 | 2 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_011.mp3 | 对,我是在后台清洁... | Yes, I was cleaning backstage... | 0 | end | | | | |

### 阶段结果
- ✅ 地点谎言被戳穿
- Rosa被迫修正说法，承认在后台走廊工作
- Rosa开始出现紧张情绪，为下一轮指证做铺垫

---

## ⚔️ 第二轮指证：否定目击谎言

### 使用证据
- **证据114**: 沾有氯仿的毛巾（Rosa工具箱内发现）
- **证据121**: 氯仿瓶（后台走廊垃圾桶内发现）

### 对话表

| id | step | speakType | waitTime | cnSpeaker | enSpeaker | imagePath | voicePath | cnWords | enWords | next | script | Parameter0 | Parameter1 | Parameter2 | Parameter3 |
|:---:|:---:|:---:|:---:|:---|:---|:---|:---|:---|:---|:---:|:---:|:---|:---|:---|:---|
| 003002003 | 1 | 2 | 3 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_012.mp3 | 我在后台走廊工作,但我很专心清洁地板和墙壁,那里很安静,什么异常都没发生... | I was working in the backstage corridor, but I focused on cleaning the floor and walls, it was quiet there, nothing unusual happened... | 001003012 | | | | | |
| 001003012 | 2 | 2 | 1 | Zack Brennan | Zack Brennan | Art/UI/Character/Zack | Audio/Voice/Zack_042.mp3 | 专心清洁? | Focused on cleaning? | 001003013 | | | | | |
| 001003013 | 3 | 2 | 5 | Zack Brennan | Zack Brennan | Art/UI/Character/Zack | Audio/Voice/Zack_043.mp3 | Rosa,这条毛巾在你的工作区域被发现,上面有氯仿残留。而这个氯仿瓶是在后台走廊的垃圾桶内发现的。 | Rosa, this towel was found in your work area, with chloroform residue on it. And this chloroform bottle was found in the trash can in the backstage corridor. | 001003014 | | | | | |
| 001003014 | 4 | 2 | 4 | Zack Brennan | Zack Brennan | Art/UI/Character/Zack | Audio/Voice/Zack_044.mp3 | 你说当时你在后台清洁,你工作区域的毛巾沾染了案发现场附近的氯仿,氯仿是医用麻醉剂,不是清洁用品。 | You said you were cleaning backstage at the time, the towel from your work area is contaminated with chloroform near the crime scene, chloroform is a medical anesthetic, not a cleaning product. | 001003015 | | | | | |
| 001003015 | 5 | 2 | 2 | Zack Brennan | Zack Brennan | Art/UI/Character/Zack | Audio/Voice/Zack_045.mp3 | 如果你什么都没看到,怎么解释这个? | If you didn't see anything, how do you explain this? | 003002004 | | | | | |
| 003002004 | 6 | 2 | 3 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_013.mp3 | 我...我... | I... I... | 003002005 | | | | | |
| 003002005 | 7 | 2 | 4 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_014.mp3 | 好吧!是我!是我用这条毛巾迷昏了您! | Okay! It was me! I drugged you with this towel! | 003002006 | | | | | |
| 003002006 | 8 | 2 | 4 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_015.mp3 | 我儿子Miguel生病了,需要手术费,我实在没办法了... | My son Miguel is sick, needs surgery money, I really had no choice... | 003002007 | | | | | |
| 003002007 | 9 | 2 | 3 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_016.mp3 | 求求您别让我坐牢,Miguel还需要我照顾... | Please don't send me to prison, Miguel still needs my care... | 0 | end | | | | |

### 阶段结果
- ✅ 目击谎言被彻底击破
- Rosa承认使用氯仿迷晕Zack
- 揭露母爱动机：为生病儿子Miguel筹集手术费
- Rosa进入自我保护模式，编造自己是主犯的故事

---

## ⚔️ 第三轮指证：否定自认，揭露真相

### 使用证据
- **证据122**: 地板拖拽痕迹（压痕2.5厘米深，需要至少150磅力量）

### 对话表

| id | step | speakType | waitTime | cnSpeaker | enSpeaker | imagePath | voicePath | cnWords | enWords | next | script | Parameter0 | Parameter1 | Parameter2 | Parameter3 |
|:---:|:---:|:---:|:---:|:---|:---|:---|:---|:---|:---|:---:|:---:|:---|:---|:---|:---|
| 003002008 | 1 | 2 | 3 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_017.mp3 | 我等您路过走廊时,从背后用毛巾捂住您的嘴和鼻子...您昏倒后我把您拖到Webb先生的办公室... | I waited for you to pass the corridor, covered your mouth and nose from behind with the towel... after you passed out I dragged you to Mr. Webb's office... | 001003016 | | | | | |
| 001003016 | 2 | 2 | 4 | Zack Brennan | Zack Brennan | Art/UI/Character/Zack | Audio/Voice/Zack_046.mp3 | Rosa,我相信你爱你的儿子,但你不是凶手。 | Rosa, I believe you love your son, but you're not the killer. | 001003017 | | | | | |
| 001003017 | 3 | 2 | 5 | Zack Brennan | Zack Brennan | Art/UI/Character/Zack | Audio/Voice/Zack_047.mp3 | 看这些拖拽痕迹——需要150磅的力量才能造成2.5厘米的压痕。你体重不到120磅,根本做不到。 | Look at these drag marks — it takes 150 pounds of force to create a 2.5cm indentation. You weigh less than 120 pounds, you simply can't do it. | 001003018 | | | | | |
| 001003018 | 4 | 2 | 2 | Zack Brennan | Zack Brennan | Art/UI/Character/Zack | Audio/Voice/Zack_048.mp3 | 谁威胁你这样说的? | Who threatened you to say this? | 003002009 | | | | | |
| 003002009 | 5 | 2 | 3 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_018.mp3 | 是...是Morrison警官... | It's... it's Officer Morrison... | 001003019 | | | | | |
| 001003019 | 6 | 2 | 5 | Zack Brennan | Zack Brennan | Art/UI/Character/Zack | Audio/Voice/Zack_049.mp3 | 他...他说如果我不配合,就让我失去工作...他知道我儿子生病的事,知道我需要这份工作... | He... he said if I don't cooperate, he'll make me lose my job... he knows about my son's illness, knows I need this job... | 003002010 | | | | | |
| 003002010 | 7 | 2 | 4 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_019.mp3 | 我不知道他要做什么!我只是按他说的,如果有人问起,就说什么都没看到...如果实在瞒不住,就说是我做的... | I didn't know what he was going to do! I just did what he said, if anyone asks, say I didn't see anything... if I really can't hide it, say I did it... | 003002011 | | | | | |
| 003002011 | 8 | 2 | 3 | Rosa Martinez | Rosa Martinez | Art/UI/Character/Rosa | Audio/Voice/Rosa_020.mp3 | 求求您别让Morrison知道我说了...我真的不知道他具体做了什么...我发誓! | Please don't let Morrison know I told... I really don't know what he specifically did... I swear! | 0 | end | | | | |

### 阶段结果
- ✅ 自认谎言被彻底否定
- **真正幕后黑手揭露**: Morrison警官
- Rosa承认被威胁配合栽赃
- 为循环2的Morrison调查做完美铺垫

---

## 📝 证据与指证对应关系

| 指证轮次 | 使用证据 | 证据ID | 击破谎言 | 揭露内容 |
|:---:|:---|:---:|:---|:---|
| **第一轮** | 工作记录卡 | EV005 (证据115) | 地点谎言 | Rosa实际在后台走廊工作 |
| **第二轮** | 氯仿毛巾 + 氯仿瓶 | EV004 + EV006 (证据114+121) | 目击谎言 | Rosa目击了迷晕过程 |
| **第三轮** | 地板拖拽痕迹 | EV007 (证据122) | 自认谎言 | Morrison才是真正的执行者 |

---

## 📊 对话统计

**第一轮对话**: 4句（约10秒）
**第二轮对话**: 9句（约16秒）
**第三轮对话**: 8句（约16秒）
**总计**: 21句（约42秒）

---

## 💡 ID命名规则

- **001XXXXXX**: Zack Brennan
- **003XXXXXX**: Rosa Martinez
- 第4位开始为对话编号和句子编号

---

## 🎭 角色情绪变化

### Rosa情绪曲线
1. **第一轮**: 慌乱、试图狡辩 → 被迫承认地点
2. **第二轮**: 极度恐惧、心理防线崩溃 → 承认参与但声称是自己做的
3. **第三轮**: 彻底崩溃、说出真相 → 恐惧Morrison报复

### Zack策略变化
1. **第一轮**: 平静但严厉，直接出示证据
2. **第二轮**: 持续施压，展示物证逻辑链
3. **第三轮**: 温和但坚定，用专业分析打破自认

---

**文档状态**: ✅ 已完成
**版本说明**: 基于场景证据布局设计文档重新生成
**对话总数**: 21句
**核心特点**: 严格遵循三轮指证逻辑，证据-谎言-真相清晰对应
