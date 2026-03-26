# Talk表配置规则文档

## 1. 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 对话唯一ID，7位数字，详见ID规则 |
| step | int | 是 | 本段对话的第几句，从1开始顺序填写 |
| speakType | int | 是 | 1=旁白, 2=正常人物说话, 3=空白 |
| waitTime | float | 否 | 这句话开始前等待的秒数 |
| IdSpeaker | string | 否 | 说话人ID，对应NPCStaticData表的ID |
| cnSpeaker | string | 是 | 说话人中文名 |
| enSpeaker | string | 是 | 说话人英文名 |
| cnWords | string | 是 | 中文台词 |
| enWords | string | 是 | 英文台词 |
| next | string | 是 | 下一句ID，0表示结束，分支用/分隔 |
| script | string | 否 | 调用代码类型，详见script规则 |
| ParameterStr0-2 | string | 否 | 字符串参数，根据script类型使用 |
| ParameterInt0-2 | int | 否 | 整数参数，根据script类型使用 |
| imagePath | string | 否 | 说话人头像路径（待补充） |
| voicePath | string | 否 | 语音文件路径（待补充） |

---

## 2. ID命名规则

**格式：`NNXXYYY`（7位数字）**

| 位置 | 含义 | 说明 |
|------|------|------|
| NN (前1-2位) | 角色编号 | 每个角色有专属编号 |
| XX (中3位) | 对话段落 | 该角色的第几段对话，001=第1段 |
| YYY (后3位) | 句子序号 | 该段对话的第几句，001=第1句 |

**示例：**
- `1001001` = 角色1 的 第1段对话 的 第1句
- `1001015` = 角色1 的 第1段对话 的 第15句
- `1002001` = 角色1 的 第2段对话 的 第1句
- `3001001` = 角色3 的 第1段对话 的 第1句

**角色编号参考（项目具体定义）：**
| 编号 | 角色 |
|------|------|
| 1 | 查克 (Zack Brennan) |
| 2 | 艾玛 (Emma O'Malley) |
| 3 | 罗莎 (Rosa Martinez) |
| 4 | 莫里森 (Morrison) |
| 5 | 汤米 (Tommy) |
| ... | 根据项目扩展 |

---

## 3. script调用代码规则

### 3.1 audio（音效）

播放音效。

| 参数 | 说明 |
|------|------|
| ParameterStr0 | 音效资源路径 |
| ParameterInt0 | 音量大小 |
| ParameterInt2 | 是否循环（0=否, 1=是） |

```yaml
- id: 1001005
  script: audio
  ParameterStr0: Audio/SFX/gunshot.mp3
  ParameterInt0: 80
  ParameterInt2: 0
```

### 3.2 shake（相机震动）

触发屏幕/相机震动效果。

| 参数 | 说明 |
|------|------|
| ParameterInt0 | 震动强度 |
| ParameterInt1 | 震动持续时间（秒） |

```yaml
- id: 1001010
  script: shake
  ParameterInt0: 5
  ParameterInt1: 1
```

### 3.3 fade（淡入淡出）

屏幕淡入淡出效果。

| 参数 | 说明 |
|------|------|
| ParameterInt0 | 持续时间（秒） |

```yaml
- id: 1001020
  script: fade
  ParameterInt0: 2
```

### 3.4 end（结束对话）

标记对话结束，需配合 `next: 0` 使用。

| 参数 | 说明 |
|------|------|
| ParameterStr0 | （可选）获取时间线的ID，如 TIM001 |

**基础用法：**
```yaml
- id: 1001030
  cnWords: 再见。
  next: 0
  script: end
```

**结束时获取时间线：**
```yaml
- id: 5001006
  cnWords: 11点半...应该是11点30分。我看了表。
  next: 0
  script: end
  ParameterStr0: TIM001
```

### 3.5 branches（分支选项）

弹出选项让玩家选择，**最多支持3个选项**。

| 参数 | 说明 |
|------|------|
| ParameterStr0 | 选项1的按钮文本 |
| ParameterInt0 | 选项1选中后，主角说话的ID |
| ParameterStr1 | 选项2的按钮文本 |
| ParameterInt1 | 选项2选中后，主角说话的ID |
| ParameterStr2 | 选项3的按钮文本 |
| ParameterInt2 | 选项3选中后，主角说话的ID |
| next | 用/分隔的3个ID，对应NPC回复 |

**分支流程图：**
```
触发分支的对话
    │
    ▼ 弹出选项按钮
┌──────────┬──────────┬──────────┐
│ 选项1     │ 选项2     │ 选项3     │
│ ParamStr0│ ParamStr1│ ParamStr2│
└────┬─────┴────┬─────┴────┬─────┘
     │          │          │
     ▼          ▼          ▼
 ParamInt0  ParamInt1  ParamInt2
 主角说选项1 主角说选项2 主角说选项3
     │          │          │
     ▼          ▼          ▼
  next[0]    next[1]    next[2]
  NPC回应1   NPC回应2   NPC回应3
     │          │          │
     └──────────┼──────────┘
                ▼
             汇合点
```

**完整示例：**
```yaml
# 触发分支的对话
- id: 3001001
  step: 1
  speakType: 2
  cnSpeaker: 查克
  enSpeaker: Zack Brennan
  cnWords: 你是这儿的清洁工?
  enWords: You're the janitor here?
  next: 3001005/3001006/3001007
  script: branches
  ParameterStr0: 询问工作时间
  ParameterInt0: 3001002
  ParameterStr1: 询问昨晚情况
  ParameterInt1: 3001003
  ParameterStr2: 直接质问
  ParameterInt2: 3001004

# 选项1：主角说的话
- id: 3001002
  step: 2
  speakType: 2
  cnSpeaker: 查克
  cnWords: 你平时几点上班？
  enWords: What time do you usually work?

# 选项2：主角说的话
- id: 3001003
  step: 3
  speakType: 2
  cnSpeaker: 查克
  cnWords: 昨晚你看到什么了？
  enWords: What did you see last night?

# 选项3：主角说的话
- id: 3001004
  step: 4
  speakType: 2
  cnSpeaker: 查克
  cnWords: 别装了，说实话。
  enWords: Stop pretending, tell the truth.

# 选项1对应的NPC回复
- id: 3001005
  step: 5
  speakType: 2
  cnSpeaker: 罗莎
  cnWords: 我晚上11点到凌晨1点...
  enWords: I work from 11pm to 1am...
  next: 3001008

# 选项2对应的NPC回复
- id: 3001006
  step: 6
  speakType: 2
  cnSpeaker: 罗莎
  cnWords: 昨晚...我什么都没看到...
  enWords: Last night... I didn't see anything...
  next: 3001008

# 选项3对应的NPC回复
- id: 3001007
  step: 7
  speakType: 2
  cnSpeaker: 罗莎
  cnWords: 我...我真的不知道...
  enWords: I... I really don't know...
  next: 3001008

# 汇合点：继续对话
- id: 3001008
  step: 8
  speakType: 2
  cnSpeaker: 罗莎
  cnWords: 是...是的，先生。
  enWords: Yes... yes, sir.
  next: 3001009
```

### 3.6 judgeConnection（触发事件）

触发游戏事件/判定连接。

| 参数 | 说明 |
|------|------|
| ParameterStr0 | 事件ID |

```yaml
- id: 3002010
  cnWords: 我知道真相了...
  script: judgeConnection
  ParameterStr0: EVT001
```

---

## 4. 常见配置模式

### 4.1 普通线性对话

```yaml
- id: 1001001
  step: 1
  speakType: 2
  cnSpeaker: 查克
  cnWords: 你好。
  next: 1001002

- id: 1001002
  step: 2
  speakType: 2
  cnSpeaker: 艾玛
  cnWords: 你好，有什么事？
  next: 1001003

- id: 1001003
  step: 3
  speakType: 2
  cnSpeaker: 查克
  cnWords: 我想问你几个问题。
  next: 0
  script: end
```

### 4.2 带旁白的对话

```yaml
- id: 1001001
  step: 1
  speakType: 1
  cnSpeaker: 旁白
  cnWords: 夜幕降临，查克走进了酒吧。
  next: 1001002

- id: 1001002
  step: 2
  speakType: 2
  cnSpeaker: 查克
  cnWords: 来杯威士忌。
  next: 0
  script: end
```

### 4.3 带特效的对话

```yaml
- id: 1001001
  step: 1
  speakType: 2
  cnSpeaker: 查克
  cnWords: 什么声音？！
  next: 1001002
  script: shake
  ParameterInt0: 3
  ParameterInt1: 1

- id: 1001002
  step: 2
  speakType: 1
  cnSpeaker: 旁白
  cnWords: 一声枪响划破夜空。
  next: 1001003
  script: audio
  ParameterStr0: Audio/SFX/gunshot.mp3
  ParameterInt0: 100
```

---

## 5. 注意事项

1. **ID必须唯一**：同一张表中不能有重复ID
2. **next指向必须存在**：next指向的ID必须在表中存在（除了0）
3. **分支必须闭合**：所有分支最终必须汇合或各自结束
4. **结束必须配对**：`next: 0` 必须配合 `script: end`
5. **step顺序填写**：每段对话的step从1开始递增
6. **中英文都要填**：cnWords和enWords都必须填写

---

## 6. 更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.1 | 2025-11-29 | 添加 judgeConnection 规则；end 合并获取时间线功能，删除 getTime |
| v1.0 | 2025-11-29 | 初始版本，基于现有Talk表整理 |
