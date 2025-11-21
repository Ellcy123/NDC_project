# Voice Presets - 角色声音预设配置

## 📋 说明

本目录包含 NDC 项目所有角色的标准声音配置文件。

每个配置文件定义了:
- 角色基础信息
- ElevenLabs 声音参数
- 情绪预设参数
- 使用说明

---

## 👥 角色列表

| 代码 | 角色名 | 配置文件 | 状态 |
|-----|--------|---------|------|
| 001 | Zack Brennan | `Zack.json` | ✅ |
| 002 | Emma O'Malley | `Emma.json` | ✅ |
| 003 | Rosa Martinez | `Rosa.json` | ✅ |
| 004 | Morrison | `Morrison.json` | ✅ |
| 005 | Tommy | `Tommy.json` | ✅ |
| 006 | Jimmy | `Jimmy.json` | ⬜ 待创建 |
| 007 | Vivian | `Vivian.json` | ⬜ 待创建 |
| 008 | Anna | `Anna.json` | ⬜ 待创建 |
| 009 | Mrs.Morrison | `Mrs_Morrison.json` | ⬜ 待创建 |
| 010 | Webb | `Webb.json` | ⬜ 待创建 |

---

## 🎯 使用方法

### 1. 读取预设配置
```python
import json

with open('Voice_Presets/Zack.json', 'r', encoding='utf-8') as f:
    zack_preset = json.load(f)

# 获取默认参数
stability = zack_preset['voice_config']['default_stability']
voice_name = zack_preset['voice_config']['voice_name']
```

### 2. 使用情绪预设
```python
# 获取特定情绪参数
emotion = 'suspicious'
emotion_params = zack_preset['emotion_presets'][emotion]

# 使用情绪参数生成语音
# stability = emotion_params['stability']
# style = emotion_params['style']
# speed = emotion_params['speed']
```

### 3. 批量生成时应用预设
```python
def generate_voice(character_code, text, emotion='default'):
    # 加载角色预设
    preset_file = f'Voice_Presets/{character_map[character_code]}.json'
    with open(preset_file, 'r') as f:
        preset = json.load(f)

    # 使用预设参数
    config = preset['voice_config']

    # 如果有情绪,使用情绪参数
    if emotion != 'default' and emotion in preset['emotion_presets']:
        emotion_params = preset['emotion_presets'][emotion]
        config.update(emotion_params)

    # 调用 ElevenLabs API
    # ...
```

---

## 📝 配置文件结构

```json
{
  "character_code": "001",
  "character_name": "Zack Brennan",
  "character_name_cn": "扎克·布伦南",
  "description": "角色描述",
  "voice_config": {
    "voice_name": "Adam",
    "default_stability": 0.85,
    "default_similarity_boost": 0.80,
    "default_style": 0.35,
    "default_speed": 1.0,
    ...
  },
  "emotion_presets": {
    "calm": { "stability": 0.85, "style": 0.35, "speed": 1.0 },
    "angry": { "stability": 0.70, "style": 0.60, "speed": 1.15 },
    ...
  }
}
```

---

## 🎨 情绪预设规范

### 常用情绪标签

| 情绪 | Stability | Style | Speed | 说明 |
|-----|-----------|-------|-------|------|
| calm | 0.85 | 0.35 | 1.0 | 冷静平稳 |
| nervous | 0.55 | 0.55 | 1.05 | 紧张不安 |
| angry | 0.50 | 0.65 | 1.15 | 愤怒激动 |
| sad | 0.55 | 0.50 | 0.85 | 悲伤缓慢 |
| frightened | 0.40 | 0.65 | 1.10 | 恐惧慌乱 |
| confident | 0.75 | 0.40 | 1.05 | 自信坚定 |

---

**创建日期**: 2025-11-20
**维护者**: NDC项目组
