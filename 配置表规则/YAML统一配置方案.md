# YAML 统一配置方案

## 1. 目标

- **单一数据源**：所有配置数据以 YAML 为主，Preview 和 Unity 共用
- **省略空字段**：YAML 只写有值的字段，避免冗余
- **自动转换**：工具负责 YAML → Excel（给 Luban/Unity 用）

---

## 2. 数据目录结构

```
Preview/data/
├── master/                    # 基础数据（全局共享）
│   ├── npcs.yaml             # NPC 基础信息
│   ├── scenes.yaml           # 场景基础信息
│   ├── items.yaml            # 物品/证据信息
│   └── chapters.yaml         # 章节配置（新增）
│
├── Unit1/                     # 第一章
│   ├── loops/                # 循环配置
│   │   ├── loop1.yaml
│   │   ├── loop2.yaml
│   │   └── ...
│   ├── dialogs/              # 对话数据
│   │   ├── loop1/
│   │   ├── loop2/
│   │   └── ...
│   ├── tasks.yaml            # 任务表（新增）
│   ├── events.yaml           # 事件表（新增）
│   └── timeline.yaml         # 时间线事件（新增）
│
└── Unit2/                     # 第二章
    └── ...（同上结构）
```

---

## 3. 各表 YAML 结构设计

### 3.1 NPC表 (npcs.yaml)

```yaml
npcs:
  NPC101:
    name: Zack Brennan
    name_cn: 查克·布伦南
    role: protagonist
    description: 私家侦探，故事主角
    # 以下字段可选，不写则为空
    # path1, path2, path3: 资源路径
    # testimony_count: 证词数量
    # can_expose: 可指证编号

  NPC102:
    name: Emma O'Malley
    name_cn: 艾玛·奥马利
    role: key_npc
    description: 酒吧女招待
    info:
      loop1: ["艾玛在酒吧工作", "她认识Rosa"]
      loop2: ["艾玛提供了新线索"]
```

### 3.2 Scene表 (scenes.yaml)

```yaml
scenes:
  # 场景基础信息（不含循环相关的 sceneType/npcsPresent）
  SC01:
    name: Rosa储藏室
    name_en: RosaStorageRoom
    asset_id: SC001_bg_RosaStorageRoom
    description: 酒吧后方的储藏室
    background_music: BGM_Storage
    ambient_sound: AMB_Storage

  SC02:
    name: 歌舞厅一楼走廊
    name_en: CabaretFirstFloorCorridor
    asset_id: SC002_bg_CabaretFirstFloorCorridor
    description: 通往各个房间的走廊
```

### 3.3 循环配置 (loops/loopN.yaml)

```yaml
# loop1.yaml - 循环1的场景状态
loop: 1
chapter: 1

scenes:
  SC1101:                      # 完整 sceneId = SC + 章节 + 循环 + 场景序号
    base: SC01                 # 引用基础场景
    type: crime                # 本循环的场景类型
    # npcs_present: 不写则为空
    # unlock_condition: 不写则为空

  SC1103:
    base: SC03
    type: dialogue
    npcs_present: [NPC105]     # Tommy

  SC1104:
    base: SC04
    type: locked
    unlock_condition: loop2    # 循环2解锁

# 本循环可获取的证据
evidences_available:
  - EV111
  - EV112
  - EV113
```

### 3.4 Item/Evidence表 (items.yaml)

```yaml
evidences:
  EV111:
    name: 神秘信件
    name_en: Mysterious Letter
    type: note
    can_collected: true
    can_analyzed: true
    description:
      initial: 一封写给Rosa的信
      analyzed: 信中提到了秘密交易
    # 可选字段省略：can_combined, combine_params, paths...

  EV112:
    name: 血迹样本
    name_en: Blood Sample
    type: clue
    can_collected: true
    can_analyzed: true
```

### 3.5 Task表 (tasks.yaml) - 新增

```yaml
tasks:
  TASK1101:
    name: 调查储藏室
    name_en: Investigate Storage Room
    chapter: 1
    loop: 1
    type: investigation
    target_scene: SC1101
    description: 在Rosa的储藏室寻找线索
    # 可选：reward, unlock_condition, next_task...

  TASK1102:
    name: 与Tommy交谈
    name_en: Talk to Tommy
    chapter: 1
    loop: 1
    type: dialogue
    target_npc: NPC105
```

### 3.6 Event表 (events.yaml) - 新增

```yaml
events:
  EVT1101:
    name: 发现尸体
    trigger: enter_scene
    trigger_params:
      scene: SC1101
      first_time: true
    action: play_dialog
    action_params:
      dialog: opening
```

### 3.7 Talk表 (dialogs/loopN/*.yaml)

保持现有结构，已经比较完善：

```yaml
type: npc_dialog
npc: NPC105

greeting:
  lines:
    - speaker: NPC105
      text: 你好，有什么事吗？
      text_en: Hello, what can I do for you?
    - speaker: NPC101
      text: 我想问你几个问题。
```

---

## 4. 转换工具改造

### 4.1 新工具结构

```
scripts/
├── converters/               # 拆分为独立转换器
│   ├── __init__.py
│   ├── base.py              # 基类：读取YAML、输出Excel
│   ├── npc_converter.py     # NPC表转换
│   ├── scene_converter.py   # Scene表转换
│   ├── item_converter.py    # Item表转换
│   ├── talk_converter.py    # Talk表转换
│   ├── task_converter.py    # Task表转换
│   ├── event_converter.py   # Event表转换
│   └── ...
│
├── yaml_to_excel.py         # 主入口：调用各转换器
└── config_table_converter.py # 旧工具（可废弃或保留兼容）
```

### 4.2 基类设计

```python
# converters/base.py
class BaseConverter:
    """转换器基类"""

    TABLE_NAME = ""           # 表名
    EXCEL_COLUMNS = []        # Excel 列定义
    DEFAULT_VALUES = {}       # 空字段默认值

    def load_yaml(self, path):
        """加载 YAML 文件"""
        pass

    def convert(self, data) -> List[dict]:
        """转换为记录列表（子类实现）"""
        raise NotImplementedError

    def fill_defaults(self, record):
        """填充空字段默认值"""
        for col in self.EXCEL_COLUMNS:
            if col['name'] not in record:
                record[col['name']] = self.DEFAULT_VALUES.get(col['name'], '')
        return record

    def to_excel(self, records, output_path):
        """输出为 Luban 格式 Excel"""
        pass
```

### 4.3 Scene 转换器示例

```python
# converters/scene_converter.py
class SceneConverter(BaseConverter):
    TABLE_NAME = "SceneConfig"

    EXCEL_COLUMNS = [
        {'name': 'sceneId', 'type': 'string', 'desc': '场景ID'},
        {'name': 'sceneName', 'type': 'string', 'desc': '中文场景名'},
        {'name': 'sceneNameEn', 'type': 'string', 'desc': '英文场景名'},
        {'name': 'sceneType', 'type': 'string', 'desc': '场景类型'},
        {'name': 'backgroundImage', 'type': 'string', 'desc': '背景图路径'},
        {'name': 'backgroundMusic', 'type': 'string', 'desc': '背景音乐'},
        {'name': 'ambientSound', 'type': 'string', 'desc': '环境音效'},
        {'name': 'unlockCondition', 'type': 'string', 'desc': '解锁条件'},
        {'name': 'npcsPresent', 'type': 'string', 'desc': '场景NPC'},
        {'name': '备注', 'type': 'string', 'desc': '备注'},
    ]

    def convert(self, master_scenes, loop_configs):
        """
        合并 master/scenes.yaml 和 loops/loopN.yaml 生成完整场景表
        """
        records = []

        for loop_config in loop_configs:
            loop_num = loop_config['loop']
            chapter = loop_config['chapter']

            for scene_id, scene_data in loop_config['scenes'].items():
                base_id = scene_data['base']
                base = master_scenes[base_id]

                record = {
                    'sceneId': scene_id,
                    'sceneName': base['name'],
                    'sceneNameEn': base['name_en'],
                    'sceneType': scene_data.get('type', 'dialogue'),
                    'backgroundImage': f"Art/Scenes/{base['asset_id']}.png",
                    'backgroundMusic': base.get('background_music', ''),
                    'ambientSound': base.get('ambient_sound', ''),
                    'unlockCondition': scene_data.get('unlock_condition', ''),
                    'npcsPresent': '/'.join(scene_data.get('npcs_present', [])),
                    '备注': base.get('description', ''),
                }
                records.append(self.fill_defaults(record))

        return records
```

---

## 5. 使用方式

```bash
# 转换所有表
python yaml_to_excel.py

# 转换指定表
python yaml_to_excel.py --tables SceneConfig Talk

# 转换指定章节
python yaml_to_excel.py --unit Unit1

# 输出到指定目录
python yaml_to_excel.py --output D:/NDC/Config/Datas/story
```

---

## 6. 实施步骤

### 第一阶段：试点 Scene 表
1. [ ] 改造 `master/scenes.yaml` 结构
2. [ ] 在 `loops/loopN.yaml` 中添加场景状态配置
3. [ ] 编写 `scene_converter.py`
4. [ ] 验证生成的 Excel 与现有格式一致

### 第二阶段：迁移其他表
5. [ ] NPC表
6. [ ] Item表
7. [ ] Talk表（基本完成，小调整）
8. [ ] Task表（新建）
9. [ ] Event表（新建）

### 第三阶段：Preview 适配
10. [ ] 修改 Preview 读取新结构的 YAML
11. [ ] 测试 Preview 功能正常

---

## 7. 注意事项

1. **向后兼容**：改造期间保留旧工具，确保不影响现有流程
2. **渐进迁移**：一个表一个表地迁移，验证通过再继续
3. **YAML 校验**：可添加 schema 校验，防止配置错误
4. **ID 规则**：严格遵循各表的 ID 命名规则

---

## 更新日志

| 版本 | 日期 | 内容 |
|------|------|------|
| v1.0 | 2025-12-07 | 初版方案 |
