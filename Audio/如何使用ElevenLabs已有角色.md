# 如何使用 ElevenLabs 中已有的角色音色

## 🎙️ 方法1: 使用预设声音 (voice_name)

### 可用的预设声音

刚才查询到您账户中的声音:

| Voice Name | Voice ID | 类型 | 适合角色 |
|-----------|----------|------|---------|
| **Adam** | pNInz6obpgDQGcFmaJgB | premade | ✅ Zack (成熟男性) |
| **Antoni** | ErXwobaYiN019PkySvjV | premade | ✅ Tommy (紧张男性) |
| **Arnold** | VR6AewLTigWG4xSOukaG | premade | ✅ Morrison (强势警探) |
| **Callum** | N2lVS1w4EtoT3dr4eOWO | premade | ✅ Jimmy (年轻口吃) |
| Alice | Xb7hH8MSUJpSbSDYk0k2 | premade | 可用 |
| Aria | 9BWtsMINqrJLrRacOk9x | premade | 可用 |
| Bill | pqHfZKP75CvOlQylNhV4 | premade | 可用 |
| Brian | nPczCjzI2devNBz1zQrb | premade | 可用 |

### 使用示例 (刚才测试成功)

```python
mcp__elevenlabs__text_to_speech(
    text="Brennan先生?这么晚了还来...有什么我能帮您的吗?",
    voice_name="Antoni",                    # 使用预设声音名称
    model_id="eleven_multilingual_v2",
    stability=0.65,
    similarity_boost=0.75,
    style=0.45,
    use_speaker_boost=True,
    speed=1.0,
    language="zh",
    output_format="mp3_44100_128",
    output_directory="D:\NDC_project\Audio\Voice\Episode1\Loop1\Tommy"
)
```

**结果**: ✅ 成功生成 `tts_Brenn_20251120_184035.mp3`

---

## 🎨 方法2: 使用自定义克隆声音 (voice_id)

### 步骤1: 查看您的自定义声音

如果您在ElevenLabs中创建了自定义角色声音,可以查询voice_id:

```python
# 查询所有声音(包括自定义)
mcp__elevenlabs__search_voices(search="")

# 搜索特定名称
mcp__elevenlabs__search_voices(search="Zack")
```

### 步骤2: 使用 voice_id 替代 voice_name

如果您已经为角色创建了专属声音,修改配置文件:

```json
{
  "voice_name": null,
  "voice_id": "YOUR_CUSTOM_VOICE_ID_HERE",  // 使用您的voice_id
  ...
}
```

### 示例:

假设您为Zack创建了自定义声音,ID是 `abc123xyz`:

```python
mcp__elevenlabs__text_to_speech(
    text="What... damn it...",
    voice_id="abc123xyz",          // 使用自定义voice_id
    voice_name=None,               // voice_name设为None
    ...
)
```

---

## 📁 方法3: 文件命名和整理

### 当前问题

生成的文件名是自动的: `tts_Brenn_20251120_184035.mp3`

### 解决方案: 生成后重命名

#### 方案A: 手动重命名 (适合测试)

```bash
# Windows
ren "tts_Brenn_20251120_184035.mp3" "Tommy_001001.mp3"

# 或在文件管理器中手动改名
```

#### 方案B: 使用Python脚本批量重命名

创建 `rename_audio.py`:

```python
import os
import json

# 读取配置文件
with open('scene1_tommy_dialogues.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 目录
audio_dir = r"D:\NDC_project\Audio\Voice\Episode1\Loop1\Tommy"

# 列出所有mp3文件,按时间排序
files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.mp3')])

# 重命名
for i, old_name in enumerate(files):
    if i < len(config):
        # 从ID提取文件名: scene1_tommy_01 → Tommy_001001
        dialogue = config[i]
        character = dialogue['character']
        # 简单映射ID
        new_name = f"{character}_{i+1:06d}.mp3"

        old_path = os.path.join(audio_dir, old_name)
        new_path = os.path.join(audio_dir, new_name)

        os.rename(old_path, new_path)
        print(f"Renamed: {old_name} → {new_name}")
```

---

## 🚀 完整测试工作流

### 测试流程 (推荐)

```
步骤1: 生成3句测试
  ├─ Tommy第1句
  ├─ Zack第1句
  └─ Tommy第2句

步骤2: 手动重命名
  ├─ tts_xxx.mp3 → Tommy_001001.mp3
  ├─ tts_yyy.mp3 → Zack_001001.mp3
  └─ tts_zzz.mp3 → Tommy_001002.mp3

步骤3: 验证音质和情绪
  ├─ 播放检查
  └─ 确认效果满意

步骤4: 批量生成剩余10句
  └─ 使用相同参数

步骤5: 批量重命名
  └─ 使用Python脚本
```

---

## 💡 实用技巧

### 技巧1: 使用女性声音

如果需要女性角色 (Emma, Rosa, Vivian):

```python
# Emma - 年轻记者
voice_name="Rachel"  或 voice_name="Alice"

# Rosa - 清洁工
voice_name="Bella"  或 voice_name="Domi"

# Vivian - 歌女
voice_name="Elli"  或 voice_name="Grace"
```

### 技巧2: 查询更多声音

```python
# 查看所有可用声音
mcp__elevenlabs__search_voices(search="", sort="name")

# 查看女性声音
mcp__elevenlabs__search_voices(search="female")
```

### 技巧3: 获取voice详细信息

```python
# 查看某个voice的详细配置
mcp__elevenlabs__get_voice(voice_id="pNInz6obpgDQGcFmaJgB")  # Adam
```

---

## 📊 角色声音映射表

| 角色代码 | 角色名 | 推荐Voice | 备选Voice | 使用方式 |
|---------|--------|----------|----------|---------|
| 001 | Zack | Adam | Arnold | voice_name="Adam" |
| 002 | Emma | Rachel | Alice | voice_name="Rachel" |
| 003 | Rosa | Bella | Domi | voice_name="Bella" |
| 004 | Morrison | Arnold | Bill | voice_name="Arnold" |
| 005 | Tommy | Antoni | Brian | voice_name="Antoni" ✅已测试 |
| 006 | Jimmy | Callum | Antoni | voice_name="Callum" |

---

## ⚠️ 注意事项

1. **voice_name vs voice_id**
   - 只能使用一个,不能同时使用
   - voice_name: 预设声音名称
   - voice_id: 自定义声音ID

2. **中文支持**
   - 必须使用 `model_id="eleven_multilingual_v2"`
   - language="zh" (中文) 或 "en" (英文)

3. **文件命名**
   - 工具自动生成的文件名不符合规范
   - 需要手动或脚本重命名

4. **输出目录**
   - 必须提前创建目录
   - 或设置为桌面: `output_directory=None`

---

## 🎯 下一步测试建议

### 立即测试 (3句)

1. **Tommy第1句** ✅已完成
   ```
   已生成: tts_Brenn_20251120_184035.mp3
   需重命名: Tommy_001001.mp3
   ```

2. **Zack第1句** (测试英文+不同声音)
   ```
   text: "I need to ask you a few questions about last night."
   voice_name: "Adam"
   language: "en"
   ```

3. **Tommy第2句** (测试不同情绪参数)
   ```
   text: "昨晚...真是太不幸了。Webb先生是个..."
   stability: 0.55 (更不稳定,表现悲伤)
   speed: 0.85 (语速更慢)
   ```

---

**创建日期**: 2025-11-20
**测试状态**: Tommy第1句 ✅成功
