# NDC 项目音频资源目录

## 📁 目录结构

```
Audio/
├── Voice/                  # 语音配音文件
│   ├── Episode1/          # 第一章语音
│   │   ├── Loop1/         # 循环1
│   │   ├── Loop2/         # 循环2
│   │   ├── Loop3/         # 循环3
│   │   ├── Loop4/         # 循环4
│   │   ├── Loop5/         # 循环5
│   │   └── Loop6/         # 循环6
│   └── Voice_Presets/     # 角色声音预设配置
├── BGM/                    # 背景音乐
├── SFX/                    # 音效文件
└── README.md              # 本文件
```

---

## 🎙️ 语音文件命名规范

### 格式
```
{角色代码}_{对话ID后6位}.mp3
```

### 示例
```
001001001 → Zack_001001.mp3
002001005 → Emma_001005.mp3
003002027 → Rosa_002027.mp3
005001001 → Tommy_001001.mp3
```

---

## 👥 角色代码表

| 代码 | 角色名 | 英文名 | 说明 |
|-----|--------|--------|------|
| 001 | Zack Brennan | Zack | 主角,私家侦探 |
| 002 | Emma O'Malley | Emma | 女记者,搭档 |
| 003 | Rosa Martinez | Rosa | 清洁工,目击者 |
| 004 | Morrison | Morrison | 警探,腐败 |
| 005 | Tommy | Tommy | 酒吧经理 |
| 006 | Jimmy | Jimmy | 厨师,真凶 |
| 007 | Vivian | Vivian | 歌女 |
| 008 | Anna | Anna | Jimmy妻子 |
| 009 | Mrs.Morrison | Mrs.Morrison | Morrison妻子 |
| 010 | Webb | Webb | 受害者老板 |

---

## 🔧 生成工具

- **平台**: ElevenLabs
- **工具**: ElevenLabs MCP (mcp__elevenlabs__text_to_speech)
- **模型**: eleven_multilingual_v2 (正式) / eleven_flash_v2_5 (测试)
- **格式**: MP3, 44.1kHz, 128kbps

---

## 📊 进度追踪

详见: `Audio_Production_Progress.md`

---

## 📝 更新日志

### 2025-11-20
- ✅ 创建完整目录结构
- ✅ 建立命名规范
- ✅ 生成进度追踪文件

---

**维护者**: NDC项目组
**最后更新**: 2025-11-20
