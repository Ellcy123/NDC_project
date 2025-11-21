# 我的 ElevenLabs 声音库

**查询时间**: 2025-11-20 18:46
**账户**: 您的ElevenLabs账户

---

## 📊 声音总览

**总数**: 10个预设声音 + 专业声音

---

## 🎙️ 可用声音列表

### 男性声音 (Male Voices)

| 序号 | Voice Name | Voice ID | 类型 | 建议用于 | 测试状态 |
|-----|-----------|----------|------|---------|---------|
| 1 | **Adam** | `pNInz6obpgDQGcFmaJgB` | premade | ✅ **Zack** (成熟侦探) | ✅ 已测试 |
| 2 | **Antoni** | `ErXwobaYiN019PkySvjV` | premade | ✅ **Tommy** (紧张经理) | ✅ 已测试 |
| 3 | **Arnold** | `VR6AewLTigWG4xSOukaG` | premade | ✅ **Morrison** (强势警探) | ⬜ 待测试 |
| 4 | **Bill** | `pqHfZKP75CvOlQylNhV4` | premade | 备选 (中年男性) | ⬜ 待测试 |
| 5 | **Brian** | `nPczCjzI2devNBz1zQrb` | premade | 备选 (年轻男性) | ⬜ 待测试 |
| 6 | **Callum** | `N2lVS1w4EtoT3dr4eOWO` | premade | ✅ **Jimmy** (厨师,口吃) | ⬜ 待测试 |
| 7 | **Burt Reynolds™** | `4YYIPFl9wE5c4L2eu2Gb` | professional | 特殊 (名人声音) | ⬜ 待测试 |

---

### 女性声音 (Female Voices)

| 序号 | Voice Name | Voice ID | 类型 | 建议用于 | 测试状态 |
|-----|-----------|----------|------|---------|---------|
| 8 | **Alice** | `Xb7hH8MSUJpSbSDYk0k2` | premade | 备选 (年轻女性) | ⬜ 待测试 |
| 9 | **Aria** | `9BWtsMINqrJLrRacOk9x` | premade | 备选 (通用女性) | ⬜ 待测试 |
| 10 | **Alexandra** | `kdmDKE6EkgrWrrykO9Qt` | professional | 专业女声 (对话风格) | ⬜ 待测试 |

---

## 🎯 NDC项目角色声音推荐

### 已确认角色 (男性)

| 角色 | 推荐Voice | Voice ID | 备选Voice | 状态 |
|-----|----------|----------|----------|------|
| 001 Zack Brennan | **Adam** | pNInz6obpgDQGcFmaJgB | Arnold | ✅ 已测试 |
| 005 Tommy | **Antoni** | ErXwobaYiN019PkySvjV | Brian | ✅ 已测试 |
| 004 Morrison | **Arnold** | VR6AewLTigWG4xSOukaG | Bill | ⬜ 待测试 |
| 006 Jimmy | **Callum** | N2lVS1w4EtoT3dr4eOWO | Antoni | ⬜ 待测试 |
| 010 Webb | Bill | pqHfZKP75CvOlQylNhV4 | Brian | ⬜ 待测试 |

---

### 待确认角色 (女性) - 需要查询

| 角色 | 需要的声音类型 | 候选Voice | 状态 |
|-----|--------------|----------|------|
| 002 Emma | 年轻记者,温暖坚定 | Alice / Aria / Alexandra | ⬜ 需测试 |
| 003 Rosa | 清洁工,胆怯恐惧 | Alice / Aria | ⬜ 需测试 |
| 007 Vivian | 歌女,高冷疏离 | Alexandra | ⬜ 需测试 |
| 008 Anna | Jimmy妻子,温柔 | Alice / Aria | ⬜ 需测试 |
| 009 Mrs.Morrison | Morrison妻子,礼貌 | Alexandra / Alice | ⬜ 需测试 |

---

## 💡 使用建议

### 如何选择声音?

1. **测试试听**: 先生成1-2句测试,确认声音是否合适
2. **情绪范围**: 确认声音能否表现所需情绪(紧张/愤怒/悲伤等)
3. **年龄匹配**: 选择与角色年龄相符的声音
4. **口音考虑**: 某些角色可能需要特定口音

---

### 查询更多声音

如果您想查看更多声音(如Rachel, Bella, Domi等):

```python
# 搜索所有女性声音
mcp__elevenlabs__search_voices(search="")

# 搜索特定名称
mcp__elevenlabs__search_voices(search="Rachel")

# 查看某个声音详情
mcp__elevenlabs__get_voice(voice_id="pNInz6obpgDQGcFmaJgB")
```

---

### 可能还有的声音

根据常见的ElevenLabs声音库,您可能还有:

**女性声音候选**:
- Rachel (温柔清晰) - 适合Emma
- Bella (甜美柔和) - 适合Rosa
- Domi (活泼开朗)
- Elli (成熟专业) - 适合Vivian
- Dorothy (年长智慧)
- Grace (优雅克制)

**男性声音候选**:
- Charlie (轻松随和) - 适合Webb
- Clyde (深沉成熟)
- Daniel (英式口音)
- Drew (年轻活力)
- Ethan (沉稳可靠)

---

## 🔍 如何查询特定声音

### 方法1: 搜索名称
```python
mcp__elevenlabs__search_voices(search="Rachel")
```

### 方法2: 查看详情
```python
mcp__elevenlabs__get_voice(voice_id="你的voice_id")
```

### 方法3: 测试生成
最准确的方法是直接生成测试:
```python
mcp__elevenlabs__text_to_speech(
    text="测试文本",
    voice_name="Rachel",
    language="en"
)
```

---

## 📝 测试记录

### 已测试声音

| Voice | 测试文本 | 效果评价 | 适用角色 |
|-------|---------|---------|---------|
| Adam | "I need to ask you..." | ✅ 优秀,低沉稳重 | Zack |
| Antoni | "Brennan先生?这么晚..." | ✅ 优秀,紧张感好 | Tommy |

### 待测试声音

- [ ] Arnold - Morrison
- [ ] Callum - Jimmy
- [ ] Alice - Emma/Rosa候选
- [ ] Aria - 通用女性
- [ ] Alexandra - Vivian候选

---

## 🎯 下一步测试建议

### 优先测试 (女性角色)

1. **测试Emma** (年轻记者)
   ```python
   text="Wait a minute!"
   voice_name="Alice"  或 "Aria"
   language="en"
   ```

2. **测试Rosa** (清洁工)
   ```python
   text="Yes... yes, sir."
   voice_name="Alice"
   language="en"
   ```

3. **尝试搜索Rachel**
   ```python
   mcp__elevenlabs__search_voices(search="Rachel")
   ```

---

## 📞 常见问题

### Q: 我有多少个自定义声音?
A: 从当前查询看,主要是预设声音。如果您创建了自定义克隆声音,它们也会出现在search_voices的结果中。

### Q: 如何区分预设和自定义声音?
A:
- `category: "premade"` = 预设声音
- `category: "professional"` = 专业声音
- `category: "cloned"` = 自定义克隆声音 (如果有)

### Q: 为什么看不到Rachel/Bella等声音?
A: 可能的原因:
1. 这些声音在您的账户中不可用
2. 需要单独搜索: `search_voices(search="Rachel")`
3. 可能需要特定订阅级别

---

**最后更新**: 2025-11-20 18:46
**查询结果**: 10个声音 (7男3女)
**已测试**: 2个 (Adam, Antoni)
