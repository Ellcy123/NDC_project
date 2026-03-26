# Audio 文件夹快速开始指南

## 🚀 快速导航

- 📊 **进度追踪**: [Audio_Production_Progress.md](Audio_Production_Progress.md)
- 📖 **完整方案**: [../第一章内容（对话修正版）/AI语音生成完整方案.md](../第一章内容（对话修正版）/AI语音生成完整方案.md)
- 🎙️ **声音预设**: [Voice/Voice_Presets/](Voice/Voice_Presets/)
- ⚙️ **配置文件**: [../第一章内容（对话修正版）/scene1_tommy_dialogues.json](../第一章内容（对话修正版）/scene1_tommy_dialogues.json)

---

## 📁 目录结构概览

```
Audio/
├── Voice/                           # 配音文件
│   ├── Episode1/
│   │   ├── Loop1/
│   │   │   ├── Opening/            # 开场剧情 (17句)
│   │   │   ├── Street/             # 街道对话 (28句)
│   │   │   ├── Tommy/              # Tommy对话 (13句) ⭐已配置
│   │   │   ├── Rosa_First/         # Rosa初次 (18句)
│   │   │   └── Rosa_Accuse/        # Rosa指证 (79句)
│   │   ├── Loop2/                  # Morrison指证
│   │   ├── Loop3/                  # Harold指证
│   │   ├── Loop4/                  # Danny指证
│   │   ├── Loop5/                  # Vinnie指证
│   │   └── Loop6/                  # Jimmy真相
│   └── Voice_Presets/              # 角色声音预设
│       ├── Zack.json              ✅
│       ├── Emma.json              ✅
│       ├── Rosa.json              ✅
│       ├── Morrison.json          ✅
│       └── Tommy.json             ✅
├── BGM/                            # 背景音乐
├── SFX/                            # 音效
└── README.md
```

---

## 🎯 第一次使用?

### 步骤1: 测试生成 (5分钟)

使用已有的 Tommy 配置文件测试生成:

1. 打开 `../第一章内容（对话修正版）/scene1_tommy_dialogues.json`
2. 选择前3句对话
3. 使用 ElevenLabs MCP 工具生成
4. 验证文件保存到 `Voice/Episode1/Loop1/Tommy/`

### 步骤2: 查看进度 (1分钟)

打开 `Audio_Production_Progress.md`,了解:
- 总体进度
- Loop1 详细清单
- 待完成任务

### 步骤3: 配置下一个场景 (30分钟)

参考 `scene1_tommy_dialogues.json` 格式,创建:
- `Loop1_Opening.json` (17句)
- `Loop1_Street.json` (28句)

---

## 📊 当前状态一览

| 项目 | 状态 | 数量 |
|-----|------|------|
| 配音文件 | ⬜ 0/155 | 0% |
| 配置文件 | ✅ 1/5 | 20% |
| 角色预设 | ✅ 5/10 | 50% |

**下一步**: 测试生成 Tommy 场景 13句

---

## 🎙️ 文件命名速查

```
对话ID: 001001001
      ↓
文件名: Zack_001001.mp3
      ↓
路径: Voice/Episode1/Loop1/Opening/Zack_001001.mp3
```

---

## 👥 角色代码速查

| 代码 | 角色 | Voice |
|-----|------|-------|
| 001 | Zack | Adam |
| 002 | Emma | Rachel |
| 003 | Rosa | Bella |
| 004 | Morrison | Arnold |
| 005 | Tommy | Antoni |

---

## 🔧 常用工具

### ElevenLabs MCP 工具

```bash
# 文本转语音
mcp__elevenlabs__text_to_speech

# 查询可用声音
mcp__elevenlabs__search_voices

# 查看模型列表
mcp__elevenlabs__list_models
```

---

## 📞 需要帮助?

- 🐛 遇到问题: 在 `Audio_Production_Progress.md` 的问题追踪区记录
- 📖 查看文档: 参考 `AI语音生成完整方案.md`
- 💬 联系支持: 项目组

---

**快速提示**:
- ⭐ Tommy 场景配置已完成,可直接测试生成
- 📋 所有场景对话已在 Talk表 中定义
- 🎨 5个主要角色的声音预设已配置完成

**创建日期**: 2025-11-20
