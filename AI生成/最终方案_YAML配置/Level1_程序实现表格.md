# Level1 程序实现表格

> 💡 **使用方法**:
> 1. 在Markdown编辑器中查看表格
> 2. 或直接复制表格内容粘贴到Excel
> 3. Excel会自动识别 `|` 分隔符转为单元格

---

## 表1: 基础信息

| 字段名 | 值 | 数据类型 | 是否必填 |
|--------|-----|---------|---------|
| unit_id | Unit1 | string | 是 |
| unit_name_zh | 血色酒吧·意外卷入 | string | 是 |
| unit_name_en | Blood Red Bar - Caught in the Trap | string | 是 |
| unit_name_en_filename | Blood Red Bar Caught in the Trap | string | 是 |

---

## 表2: 故事背景

| 字段名 | 值 | 数据类型 | 是否必填 |
|--------|-----|---------|---------|
| era | 1925年芝加哥，禁酒令时期 | string | 是 |
| location | 血色酒吧 (Webb's Red Bar / Blue Moon Cabaret) | string | 是 |
| historical_context | 芝加哥大桥建设项目正在进行 | string | 否 |
| time_span | 1925年11月15-18日 | string | 是 |
| duration_minutes | 60 | int | 是 |

---

## 表3: 主题

| 字段名 | 值 | 数据类型 | 是否必填 |
|--------|-----|---------|---------|
| main_theme | 栽赃陷害与权力阴谋 | string | 是 |
| core_mystery | Webb因偷听神秘商务会议被杀，Zack被陷害为凶手 | string | 是 |
| emotional_hook | 母亲生命受威胁，身边熟人成为敌人 | string | 否 |

---

## 表4: 难度模式配置

| 难度模式 | 是否启用 | 特性1 | 特性2 | 特性3 | 特性4 |
|---------|---------|------|------|------|------|
| normal | true | 场景中有线索提示（放大镜动画） | 搜索进度标识显示 | 指证失败允许2次重试 | 任务系统提供详细提示 |
| expert | true | 无线索提示 | 无搜索进度标识 | 指证失败不允许重试 | 任务系统不提供提示 |

---

## 表5: 循环概览

| Loop ID | 循环序号 | 循环名称 | 循环目标 | 预估时长(分钟) |
|---------|---------|---------|---------|--------------|
| Unit1_Loop1 | 1 | 栽赃陷害的真相 | 到底是谁把我迷晕了，还想把杀人的罪名扣在我头上？ | 10 |
| Unit1_Loop2 | 2 | 警官犯罪动机调查 | Morrison警官迷晕我的证据在哪里？他为什么要这么做？ | 12 |
| Unit1_Loop3 | 3 | Webb的秘密发现 | Webb为什么需要雇佣侦探？他发现了什么秘密？ | 12 |
| Unit1_Loop4 | 4 | 危险目标的身份 | Webb到底威胁了什么人？谁是幕后指使者？ | 15 |
| Unit1_Loop5 | 5 | 歌女的观察证词 | 验证Webb威胁大人物的说法，确认Smith的存在 | 10 |
| Unit1_Loop6 | 6 | 最终真相与致命威胁 | 揭露完整真相，面对终极威胁 | 15 |

---

## 表6: 主要角色

| NPC ID | 角色名称 | 角色类型 | 角色描述 |
|--------|---------|---------|---------|
| NPC009 | Zack O'Sullivan | protagonist | 私家侦探，实际为Patrick Brennan之子，被陷害为Webb谋杀案嫌疑人 |
| NPC010 | Emma O'Malley | protagonist | 记者，Miller集团派遣的无意识"洗白工具"，帮助Zack洗清嫌疑 |
| NPC001 | Webb Murdoch | victim | 血色酒吧老板，因偷听神秘商务会议被杀害 |
| NPC004 | Morrison | suspect | 芝加哥警局警探，负责案件的警官，实际参与栽赃Zack |
| NPC002 | Rosa Martinez | suspect | 50岁的清洁工，目击了Morrison迷晕Zack的过程 |
| NPC003 | Tommy | suspect | 45岁的酒吧经理，了解Webb的秘密行动 |
| NPC008 | Vivian | suspect | 酒吧歌女，目击案发当晚的关键事件 |
| NPC006 | Jimmy | suspect | 酒吧厨师，Webb的真正杀手 |

---

## 表7: 过场动画

| 过场类型 | 过场ID | 场景ID | 描述 | 触发时机 |
|---------|--------|--------|------|---------|
| opening | CS_Unit1_Opening | SC101 | Zack在Webb会客室醒来，发现Webb死亡，被Morrison逮捕 | 章节开始 |
| ending | CS_Unit1_Ending | SC109 | 发现录音带内容，接到Smith威胁电话，得知母亲失踪 | Loop6完成 |

---

## 表8: 叙事目标

| 目标类型 | 内容 |
|---------|------|
| immediate | 洗清Zack的谋杀嫌疑，找到Webb的真正凶手 |
| hidden | 揭露Miller集团的土地投机阴谋冰山一角 |
| emotional | 建立Zack与Emma的合作关系，发现母亲生命受威胁 |

---

## 表9: 结尾Hook

| Hook类型 | 内容 |
|---------|------|
| revelation | 录音带揭示神秘商务会议内容，提及Zack母亲Margaret O'Sullivan |
| threat | Smith的威胁电话，展示他对Zack私人生活的了解（苹果派细节） |
| next_unit | 母亲失踪，被Moore银行控制，引向Unit2的银行对决 |

---

## 表10: 元信息

| 字段名 | 值 |
|--------|-----|
| version | 1.0 |
| created_date | 2025-11-06 |
| author | NDC Content Team |
| last_modified | 2025-11-06 |

---

## 🎯 Unity C# 数据结构对应

```csharp
// 对应表1-3
public class UnitMetadata
{
    public string unit_id;
    public string unit_name_zh;
    public string unit_name_en;

    public StoryBackground story_background;
    public Theme theme;
}

// 对应表2
public class StoryBackground
{
    public string era;
    public string location;
    public string historical_context;
    public string time_span;
    public int duration_minutes;
}

// 对应表3
public class Theme
{
    public string main_theme;
    public string core_mystery;
    public string emotional_hook;
}

// 对应表4
public class DifficultyMode
{
    public bool enabled;
    public string[] features;
}

// 对应表5
public class LoopInfo
{
    public string loop_id;
    public int loop_number;
    public string name;
    public string objective;
}

// 对应表6
public class CharacterInfo
{
    public string npc_id;
    public string name;
    public string role; // "protagonist", "victim", "suspect"
    public string description;
}

// 对应表7
public class CutsceneInfo
{
    public string cutscene_id;
    public string scene;
    public string description;
    public string trigger;
}
```

---

## 📋 Excel导入步骤

### 方法1: 直接粘贴（推荐）

1. 在本Markdown文件中选择任意表格
2. 复制（Ctrl+C）
3. 打开Excel，粘贴（Ctrl+V）
4. Excel会自动识别表格结构

### 方法2: 导入Markdown

1. Excel → 数据 → 从文本/CSV
2. 选择本.md文件
3. 选择分隔符：`|`
4. 导入

### 方法3: 使用在线工具

1. 访问 https://tableconvert.com/markdown-to-excel
2. 粘贴Markdown表格
3. 下载Excel文件

---

## ⚠️ 注意事项

1. **数据类型**: Excel粘贴后检查数据类型
   - `duration_minutes` 应该是数字
   - `loop_number` 应该是数字
   - 其他都是文本

2. **布尔值**: Excel中 `true/false` 可能需要手动转换
   - 方案A: 保持文本 "true"/"false"
   - 方案B: 转换为 1/0

3. **数组字段**: 特性1-4 在程序中是数组
   - Excel中用多列展示
   - 程序读取时需要合并成数组

4. **换行符**: 长文本可能包含换行
   - Excel中双击单元格查看完整内容
   - 或调整行高显示

---

## 🔄 Excel → YAML 转换

如果您在Excel中修改后，我可以帮您转回YAML格式：

1. 您修改Excel
2. 复制Excel内容粘贴给我（或保存为CSV）
3. 我自动转换为YAML
4. 验证配置完整性
