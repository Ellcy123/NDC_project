# 场景数据规范（Scenes Schema）

## 文件位置

```
Preview/data/UnitX/master/scenes.yaml
```

---

## 一、基础字段

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `name` | string | ✓ | 场景中文名称 | `Rosa储藏室` |
| `name_en` | string | ✓ | 场景英文名称（驼峰命名） | `RosaStorageRoom` |
| `asset_id` | string | ✓ | 美术资源ID | `SC001_bg_RosaStorageRoom` |
| `description` | string | ✓ | 场景描述（一句话） | `酒吧后方的储藏室...` |
| `state` | string | - | 场景状态（时间/天气/氛围） | `夜晚_下雨` |

---

## 二、ID命名规范

### 基础场景ID（scenes.yaml）

```
SC + 章节(1位) + 序号(3位)
```

**示例**：
- `SC1001` = 第1章 第001号场景
- `SC1017` = 第1章 第017号场景

### 循环场景ID（配置表输出）

```
SC + 章节(1位) + 循环(1位) + 序号(2位)
```

**转换规则**：
- `SC1001` + 循环1 → `SC1101`
- `SC1017` + 循环2 → `SC1217`
- 同循环重复场景 → `SC1117`、`SC1117_A`、`SC1117_B`

---

## 三、asset_id 格式

```
SC{序号}_bg_{英文场景名}
```

**示例**：
- `SC001_bg_RosaStorageRoom`
- `SC017_bg_BarStreet`

---

## 四、场景提取来源

转表工具从 loop 配置的 4 处提取场景：

| 来源 | 路径 | 默认 sceneType |
|------|------|----------------|
| 开篇 | `opening.scenes[].scene_id` | `dialogue` |
| 自由探索 | `free_phase.scenes[].scene` | 根据 type 字段 |
| 指证 | `expose.scene` | `dialogue` |
| 结尾 | `ending.scene` | `dialogue` |

---

## 五、sceneType 映射

| loop配置 type | 配置表 sceneType | 说明 |
|---------------|------------------|------|
| `search` | `search` | 搜证场景 |
| `npc` | `dialogue` | 对话场景 |
| `locked` | `lock` | 锁定场景 |
| 无/其他 | 空 | 默认 |

---

## 六、转表生成字段

以下字段由转表工具从 **loop配置** 中生成：

| 配置表字段 | 来源 | 规则 |
|-----------|------|------|
| `sceneId` | 生成 | `SC{章节}{循环}{序号}` 或 `_A/_B` 后缀 |
| `sceneName` | scenes.yaml | `name` |
| `sceneNameEn` | scenes.yaml | `name_en` |
| `sceneType` | loop配置 | `type` 字段映射 |
| `backgroundImage` | scenes.yaml | `asset_id` |
| `backgroundMusic` | - | 空（手动补充） |
| `ambientSound` | - | 空（手动补充） |
| `unlockCondition` | - | 空（手动补充） |
| `npcsPresent` | loop配置 | `npc` 字段 |
| `note` | loop配置 | 来源 + 详情 |

### 备注(note)内容

| 来源 | 备注格式 |
|------|----------|
| opening | `opening: {dialog_file}` |
| free_phase (search) | `free_phase: 搜索 EV1111,EV1112...` |
| free_phase (npc) | `free_phase: 与{NPC名}对话` |
| expose | `expose: 指证{target_name}` |
| ending | `ending: 过渡到{transition_to}` |

---

## 七、完整示例

### 示例1：基础场景定义（scenes.yaml）

```yaml
SC1001:
  name: Rosa储藏室
  name_en: RosaStorageRoom
  asset_id: SC001_bg_RosaStorageRoom
  description: 酒吧后方的储藏室，堆满杂物，是Rosa的私人空间
```

### 示例2：不同状态的同一场景

```yaml
SC2002:
  name: 城市公园
  name_en: CityPark
  asset_id: SC2002_bg_CityPark
  description: 芝加哥市中心的公共公园
  state: 白天_晴朗

SC2102:
  name: 城市公园
  name_en: CityPark_Night
  asset_id: SC2102_bg_CityPark_Night
  description: 芝加哥市中心的公共公园
  state: 夜晚_下雨
```

### 示例3：配置表输出

```
SC1101, Rosa储藏室, RosaStorageRoom, search, SC001_bg_RosaStorageRoom, , , , , free_phase: 搜索 EV1111,EV1112,EV1113
SC1103, Tommy办公室, TommyOffice, dialogue, SC003_bg_TommyOffice, , , , NPC105, free_phase: 与Tommy对话
SC1117, 酒吧外街道, BarStreet, dialogue, SC017_bg_BarStreet, , , , , opening: loop1/opening.yaml
SC1117_A, 酒吧外街道, BarStreet, dialogue, SC017_bg_BarStreet, , , , , ending: 过渡到Unit1_Loop2
```

---

## 八、注意事项

1. **跨循环共享**：scenes.yaml 定义基础场景，不绑定特定循环
2. **ID转换**：转表时自动将 `SC1001` 转为 `SC1101`（带循环编号）
3. **重复处理**：同循环多次出现的场景自动添加 `_A`、`_B` 后缀
4. **英文命名**：使用驼峰命名（PascalCase）
5. **状态区分**：用 `state` 字段区分同场景不同状态（时间/天气）
6. **音效配置**：`backgroundMusic`、`ambientSound` 需手动补充

---

## 九、与其他数据的关联

| 关联数据 | 关联方式 |
|---------|---------|
| 证据 | 证据的 `asset_id` 以场景编号开头，如 `SC101_clue_01` |
| Loop配置 | 从 `opening`/`free_phase`/`expose`/`ending` 引用场景ID |
| 对话文件 | 对话的 `scene` 字段引用场景ID |
| NPC | Loop配置中 `npc` 字段关联 NPC ID |

---

## 十、转表命令

```bash
python scripts/scene_converter.py
```

输出文件：`story/SceneConfig.xlsx`
