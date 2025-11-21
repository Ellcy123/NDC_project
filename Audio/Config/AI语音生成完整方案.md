# NDC项目 - AI语音生成完整方案

## 📋 方案概述

本文档基于 NDC 项目特点,提供一套完整的 AI 语音生成工作流,包括文件组织、命名规范、配置格式和批量生成流程。

**目标:**
- ✅ 统一语音资产命名规范
- ✅ 与现有配置表无缝对接
- ✅ 支持多角色、多情绪、多循环管理
- ✅ 便于游戏引擎加载和调用

---

## 🎯 项目分析

### 项目结构特点

1. **6个循环 (Loop)**: Episode1 包含 Loop1-6,每个循环有独特的指证对话
2. **10个主要角色**: Zack, Emma, Rosa, Tommy, Jimmy, Vivian, Morrison, Anna, Mrs.Morrison, Webb
3. **场景编号系统**: SC[循环编号][场景固定编号] (如 SC101, SC201)
4. **对话ID系统**: 9位数字ID (如 001001001 = Zack第1次对话第1句)
5. **现有配置表**: Talk表已有 voicePath 字段,格式为 `Audio/Voice/Zack_001.mp3`

---

## 🗂️ 语音文件命名规范

### 方案A: 基于对话ID命名 (推荐)

#### 命名格式
```
{角色代码}_{对话ID后6位}.mp3
```

#### 解析规则
- **角色代码**: 3位数字 (001=Zack, 002=Emma, 003=Rosa, etc.)
- **对话ID后6位**: 取9位对话ID的后6位,表示第几次对话+第几句话

#### 示例
```
001001001 → Zack_001001.mp3
001001002 → Zack_001002.mp3
002001001 → Emma_001001.mp3
003002013 → Rosa_002013.mp3
005001001 → Tommy_001001.mp3
```

#### 优点
- ✅ 与现有配置表 ID 完全对应
- ✅ 文件名唯一,不会重复
- ✅ 可以通过 ID 快速定位到具体对话
- ✅ 支持程序自动化加载

---

### 方案B: 基于场景+角色+序号命名 (可读性更好)

#### 命名格式
```
{循环编号}_{场景代码}_{角色英文名}_{序号}.mp3
```

#### 示例
```
L1_Opening_Zack_01.mp3        → 循环1开场Zack第1句
L1_Opening_Emma_01.mp3        → 循环1开场Emma第1句
L1_Tommy_Zack_01.mp3          → 循环1 Tommy对话 Zack第1句
L1_Rosa1_Zack_01.mp3          → 循环1 Rosa初次对话 Zack第1句
L1_Rosa3_Accuse_Zack_16.mp3   → 循环1 Rosa指证第3轮 Zack第16句
```

#### 优点
- ✅ 可读性高,一眼看出哪个循环哪个场景
- ✅ 便于美术/策划手动查找和修改
- ✅ 分类清晰,易于文件管理

#### 缺点
- ⚠️ 需要额外的映射表关联对话ID
- ⚠️ 文件名较长

---

## 🎨 推荐方案: 混合命名法

### 目录结构
```
Audio/
└── Voice/
    ├── Episode1/
    │   ├── Loop1/
    │   │   ├── Opening/
    │   │   │   ├── Zack_001001.mp3
    │   │   │   ├── Zack_001002.mp3
    │   │   │   ├── Emma_001001.mp3
    │   │   │   └── Morrison_001001.mp3
    │   │   ├── Street/
    │   │   │   ├── Zack_001006.mp3
    │   │   │   └── Emma_002005.mp3
    │   │   ├── Tommy/
    │   │   │   ├── Tommy_001001.mp3
    │   │   │   └── Zack_002001.mp3
    │   │   ├── Rosa_First/
    │   │   │   ├── Zack_003001.mp3
    │   │   │   └── Rosa_001001.mp3
    │   │   ├── Rosa_Accuse/
    │   │   │   ├── Zack_003010.mp3
    │   │   │   ├── Rosa_002001.mp3
    │   │   │   └── Rosa_002027.mp3
    │   │   └── README.md
    │   ├── Loop2/
    │   ├── Loop3/
    │   ├── Loop4/
    │   ├── Loop5/
    │   └── Loop6/
    └── Voices_Presets/
        ├── Zack_voice_config.json
        ├── Emma_voice_config.json
        └── ...
```

### 命名优势
- ✅ **文件名**: 简洁的角色_ID格式,与配置表对应
- ✅ **目录结构**: 按循环/场景分类,方便管理
- ✅ **可追溯**: 通过ID可以定位到Talk表的具体对话
- ✅ **可扩展**: 支持未来新增循环和场景

---

## 📊 配置表集成

### Talk表字段映射

现有 Talk 表结构:
```markdown
| id | voicePath | cnSpeaker | enSpeaker | cnWords | enWords |
```

### 语音路径规则

#### 完整路径格式
```
Audio/Voice/Episode1/Loop{循环编号}/{场景分类}/{角色代码}_{ID后6位}.mp3
```

#### 实际示例
```markdown
| id        | voicePath                                                    |
|-----------|--------------------------------------------------------------|
| 001001001 | Audio/Voice/Episode1/Loop1/Opening/Zack_001001.mp3         |
| 002001001 | Audio/Voice/Episode1/Loop1/Opening/Emma_001001.mp3         |
| 005001001 | Audio/Voice/Episode1/Loop1/Tommy/Tommy_001001.mp3          |
| 003002027 | Audio/Voice/Episode1/Loop1/Rosa_Accuse/Rosa_002027.mp3     |
```

### 场景分类代码表

| 分类代码 | 中文名称 | 使用场景 |
|---------|---------|---------|
| Opening | 开场剧情 | 黑暗中觉醒,Morrison闯入 |
| Street | 街道对话 | 酒吧外与Emma搭档确立 |
| Tommy | Tommy对话 | Tommy办公室访谈 |
| Rosa_First | Rosa初次对话 | Rosa第一次撒谎 |
| Rosa_Accuse | Rosa指证对话 | 三轮指证完整流程 |
| Vivian | Vivian对话 | 与歌女对话 |
| Jimmy | Jimmy对话 | 与厨师对话 |
| Confrontation | 对峙场景 | 最终凶手对峙 |

---

## 🎙️ ElevenLabs 配置规范

### 角色声音预设表

基于项目现有的 `ElevenLabs声线生成提示词.md`,我们已经有10个角色的声音配置:

| 角色代码 | 角色名 | 推荐Voice | Stability | Style | Speed | 备注 |
|---------|-------|----------|-----------|-------|-------|------|
| 001 | Zack Brennan | Adam | 0.85 | 0.35 | 1.0 | 疲惫侦探,低沉稳重 |
| 002 | Emma O'Malley | Rachel | 0.70 | 0.40 | 1.0 | 年轻记者,温暖坚定 |
| 003 | Rosa Martinez | Bella | 0.40 | 0.65 | 0.95 | 清洁工,胆怯恐惧 |
| 004 | Morrison | Arnold | 0.55 | 0.50 | 1.05 | 腐败警探,强势威胁 |
| 005 | Tommy | Antoni | 0.60 | 0.50 | 1.05 | 经理,紧张谨慎 |
| 006 | Jimmy | Callum | 0.45 | 0.60 | 1.10 | 厨师,口吃紧张 |
| 007 | Vivian | Elli | 0.80 | 0.40 | 0.95 | 歌女,高冷疏离 |
| 008 | Anna | Bella | 0.75 | 0.45 | 0.95 | Jimmy妻子,温柔 |
| 009 | Mrs.Morrison | Rachel | 0.75 | 0.40 | 1.0 | Morrison妻子,礼貌 |
| 010 | Webb | Charlie | 0.65 | 0.55 | 1.0 | 夜总会老板,油滑 |

---

## 📝 标准配置文件格式

### 单句语音配置 (JSON)

```json
{
  "id": "001001001",
  "character_code": "001",
  "character_name": "Zack Brennan",
  "loop": 1,
  "scene": "Opening",
  "text_cn": "什么...该死...",
  "text_en": "What... damn it...",
  "voice_config": {
    "voice_name": "Adam",
    "model_id": "eleven_multilingual_v2",
    "stability": 0.85,
    "similarity_boost": 0.80,
    "style": 0.35,
    "use_speaker_boost": true,
    "speed": 1.0,
    "language": "en",
    "output_format": "mp3_44100_128"
  },
  "emotion_tags": ["confused", "shocked"],
  "output_filename": "Zack_001001.mp3",
  "output_path": "Audio/Voice/Episode1/Loop1/Opening/"
}
```

### 场景批量配置 (JSON Array)

```json
[
  {
    "id": "001001001",
    "character_code": "001",
    "scene": "Opening",
    "text_en": "What... damn it...",
    "voice_config": { "stability": 0.85, "speed": 1.0 },
    "output_filename": "Zack_001001.mp3"
  },
  {
    "id": "001001002",
    "character_code": "001",
    "scene": "Opening",
    "text_en": "Webb?! No... this isn't right...",
    "voice_config": { "stability": 0.80, "speed": 0.95 },
    "output_filename": "Zack_001002.mp3"
  }
]
```

---

## 🔄 批量生成工作流

### 流程图

```
1. 准备阶段
   ├─ 从 Talk表 导出对话数据
   ├─ 整理为标准 JSON 配置
   └─ 设置角色声音预设

2. 生成阶段
   ├─ 按循环分批生成
   ├─ 按场景分组处理
   └─ 调用 ElevenLabs MCP 工具

3. 后处理阶段
   ├─ 重命名为标准格式
   ├─ 移动到对应目录
   └─ 更新 Talk表 voicePath

4. 质检阶段
   ├─ 播放检查音质
   ├─ 检查情绪匹配度
   └─ 标记需要重新生成的文件
```

---

## 🛠️ 实际操作示例

### 示例1: 生成 Loop1 Opening 场景全部语音

#### 步骤1: 准备配置文件

创建 `Loop1_Opening_config.json`:
```json
[
  {
    "id": "001001001",
    "character_code": "001",
    "character_name": "Zack",
    "text": "What... damn it...",
    "voice_name": "Adam",
    "stability": 0.85,
    "style": 0.35,
    "speed": 1.0,
    "output": "Zack_001001.mp3"
  },
  {
    "id": "001001002",
    "character_code": "001",
    "character_name": "Zack",
    "text": "Webb?! No... this isn't right...",
    "voice_name": "Adam",
    "stability": 0.80,
    "style": 0.40,
    "speed": 0.95,
    "output": "Zack_001002.mp3"
  }
]
```

#### 步骤2: 使用 ElevenLabs MCP 批量生成

```python
import json

# 读取配置
with open('Loop1_Opening_config.json', 'r', encoding='utf-8') as f:
    dialogues = json.load(f)

# 遍历生成
for dialogue in dialogues:
    # 调用 MCP 工具
    # mcp__elevenlabs__text_to_speech(
    #     text=dialogue['text'],
    #     voice_name=dialogue['voice_name'],
    #     stability=dialogue['stability'],
    #     style=dialogue['style'],
    #     speed=dialogue['speed'],
    #     output_directory='Audio/Voice/Episode1/Loop1/Opening/'
    # )
    print(f"生成: {dialogue['output']}")
```

#### 步骤3: 验证文件

检查生成的文件是否存在:
```bash
Audio/Voice/Episode1/Loop1/Opening/
├── Zack_001001.mp3
├── Zack_001002.mp3
├── Emma_001001.mp3
└── Morrison_001001.mp3
```

---

## 📦 文件拆分策略

### 按循环拆分 (推荐)

```
配置文件结构:
├── Loop1_config/
│   ├── Opening.json         (17句)
│   ├── Street.json          (28句)
│   ├── Tommy.json           (13句)
│   ├── Rosa_First.json      (18句)
│   └── Rosa_Accuse.json     (79句)
├── Loop2_config/
├── Loop3_config/
├── Loop4_config/
├── Loop5_config/
└── Loop6_config/
```

**优点:**
- ✅ 每个文件大小适中 (10-80句)
- ✅ 便于分阶段生成和测试
- ✅ 修改某个场景对话不影响其他场景

---

### 按角色拆分 (适合多人协作)

```
配置文件结构:
├── Zack_Loop1.json          (所有Zack的对话)
├── Emma_Loop1.json          (所有Emma的对话)
├── Rosa_Loop1.json          (所有Rosa的对话)
├── Tommy_Loop1.json
└── Morrison_Loop1.json
```

**优点:**
- ✅ 便于统一调整角色声音
- ✅ 适合多人分工 (每人负责一个角色)
- ✅ 角色情绪变化更容易把控

---

## 🎯 最佳实践建议

### 1. 命名规范
- ✅ 文件名使用 `{角色代码}_{ID后6位}.mp3`
- ✅ 目录结构 `Episode{章节}/Loop{循环}/{场景分类}/`
- ✅ 与 Talk表 voicePath 字段保持一致

### 2. 配置管理
- ✅ 每个场景一个独立的 JSON 配置文件
- ✅ 使用 Git 管理配置文件版本
- ✅ 预设角色声音参数,减少重复配置

### 3. 生成策略
- ✅ 先生成关键场景 (开场、高潮、结尾)
- ✅ 使用 `eleven_flash_v2_5` 快速预览
- ✅ 确认效果后再用 `eleven_multilingual_v2` 正式生成

### 4. 质量控制
- ✅ 每生成10句检查一次情绪是否匹配
- ✅ 同一角色的连续对话要保持声音一致性
- ✅ 情绪转折点 (如崩溃、愤怒) 适当调整 stability

### 5. 成本优化
- ✅ 短句 (<10词) 可以合并生成后裁剪
- ✅ 重复台词 (如"什么?") 可以复用相同音频
- ✅ 测试时使用低质量格式,正式发布再用高质量

---

## 📈 项目进度追踪

### Episode1 语音生成清单

| 循环 | 场景 | 对话数 | 状态 | 备注 |
|-----|------|-------|------|------|
| Loop1 | Opening | 17 | ⬜ 待生成 | 开场剧情 |
| Loop1 | Street | 28 | ⬜ 待生成 | 搭档确立 |
| Loop1 | Tommy | 13 | ✅ 已配置 | scene1_tommy_dialogues.json |
| Loop1 | Rosa_First | 18 | ⬜ 待生成 | Rosa初次对话 |
| Loop1 | Rosa_Accuse | 79 | ⬜ 待生成 | 三轮指证 |
| Loop2 | Morrison指证 | ? | ⬜ 待生成 | |
| Loop3 | Harold指证 | ? | ⬜ 待生成 | |
| Loop4 | Danny指证 | ? | ⬜ 待生成 | |
| Loop5 | Vinnie指证 | ? | ⬜ 待生成 | |
| Loop6 | Jimmy指证 | ? | ⬜ 待生成 | |

**总计**: 约 500+ 句对话

---

## 🔧 工具和脚本

### 推荐工具

1. **ElevenLabs MCP** (已安装)
   - `mcp__elevenlabs__text_to_speech`
   - `mcp__elevenlabs__search_voices`
   - `mcp__elevenlabs__list_models`

2. **Python脚本** (待开发)
   - `talk_to_config.py` - 从Talk表导出配置
   - `batch_generate.py` - 批量生成语音
   - `rename_audio.py` - 批量重命名文件
   - `validate_audio.py` - 验证文件完整性

3. **Excel模板** (可选)
   - 用于策划手动编辑和校对配置

---

## 📞 常见问题

### Q1: 如何处理中英文混合对话?

**方案1**: 分别生成中英文版本
```
Zack_001001_CN.mp3  (中文版)
Zack_001001_EN.mp3  (英文版)
```

**方案2**: 只生成英文版,中文使用字幕
```
仅生成英文语音,游戏内显示中文字幕
```

**推荐**: 方案2,成本更低,且符合1920年代芝加哥背景

---

### Q2: 如何调整角色情绪变化?

**参考原 AVG内容.md 中的情绪标注**:
```json
"nervous_polite" → {"stability": 0.65, "style": 0.45, "speed": 1.0}
"panicked_pleading" → {"stability": 0.35, "style": 0.70, "speed": 1.15}
"cold_accusatory" → {"stability": 0.85, "style": 0.45, "speed": 0.9}
```

建立**情绪参数映射表**,根据 emotion_note 自动设置参数。

---

### Q3: 如何复用已生成的语音?

**建立复用规则**:
1. 短句重复 (如 "什么?", "好的") → 使用相同文件
2. 同一场景的背景音 → 循环播放
3. 不同循环的相同对话 → 软链接或复制

**记录在 `voice_reuse_map.json`**:
```json
{
  "Zack_001009.mp3": {
    "also_used_in": ["Zack_002015.mp3", "Zack_003022.mp3"],
    "reason": "相同内容"
  }
}
```

---

## 🎬 下一步行动

### 立即可做:
1. ✅ 创建 `Audio/Voice/Episode1/Loop1/` 目录结构
2. ✅ 从 `scene1_tommy_dialogues.json` 测试生成13句
3. ✅ 验证文件命名和路径是否正确

### 短期规划:
1. 完成 Loop1 所有场景的配置文件
2. 批量生成 Loop1 全部语音 (~150句)
3. 更新 Talk表 voicePath 字段

### 长期规划:
1. 开发自动化生成脚本
2. 建立情绪参数数据库
3. 完成 Episode1 全部6个循环语音

---

**文档版本**: v1.0
**创建日期**: 2025-11-20
**适用范围**: NDC Episode1 全部循环
**作者**: Claude AI Assistant
**审核状态**: 待项目组确认
