# Scene表配置规则文档

## 第一部分：配置表字段说明

### 1.1 字段列表

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sceneId | string | 是 | 场景唯一ID，格式：SC + 章节 + 循环 + 场景序号(2位) |
| sectionId | string | 是 | 子章节ID，如 SEC01 = 循环1 |
| sceneName | string | 是 | 中文场景名 |
| sceneNameEn | string | 是 | 英文场景名 |
| chapterId | string | 是 | 章节ID，如 CH001 = 第1章 |
| sceneType | string | 是 | 场景类型（crime/dialogue/locked） |
| backgroundImage | string | 是 | 背景图片路径 |
| backgroundMusic | string | 否 | 背景音乐ID |
| ambientSound | string | 否 | 环境音效ID |
| unlockCondition | string | 否 | 解锁条件 |
| npcsPresent | string | 否 | 场景中的NPC ID（多个用 `/` 分隔） |
| 备注 | string | 否 | 策划备注信息 |

---

### 1.2 ID命名规则

**格式：`SC` + `章节(1位)` + `循环(1位)` + `场景序号(2位)`**

| 位置 | 含义 | 说明 |
|------|------|------|
| SC | 固定前缀 | Scene |
| 第1位 | 章节 | 1-9 = 第1-9章 |
| 第2位 | 循环 | 1-6 = 循环1-6 |
| 第3-4位 | 场景序号 | 01-99，场景的固定编号 |

**示例：**
- `SC1101` = 第1章 循环1 场景01（Rosa储藏室）
- `SC1201` = 第1章 循环2 场景01（Rosa储藏室）
- `SC1308` = 第1章 循环3 场景08（Webb办公室）

**场景序号对照表（第1章）：**

| 序号 | 场景名 | 英文名 |
|------|--------|--------|
| 01 | Rosa储藏室 | RosaStorageRoom |
| 02 | 歌舞厅一楼走廊 | CabaretFirstFloorCorridor |
| 03 | Tommy办公室 | TommyOffice |
| 04 | Webb会客室 | WebbReceptionRoom |
| 05 | Morrison家中客厅 | MorrisonHomeLivingRoom |
| 06 | Morrison家中书房 | MorrisonHomeStudy |
| 07 | Vivian的化妆室 | VivianDressingRoom |
| 08 | Webb办公室 | WebbOffice |
| 09 | 酒吧歌舞厅 | BarCabaret |
| 10 | 酒吧大堂 | BarLobby |
| 11 | Jimmy的厨房 | JimmyKitchen |
| 12 | Jimmy家中卧室 | JimmyHomeBedroom |
| 13 | 酒吧外街道 | BarStreet |

---

### 1.3 sceneType 场景类型

| 类型 | 说明 | 用途 |
|------|------|------|
| crime | 搜证场景 | 玩家可以在此场景搜集证据 |
| dialogue | 对话场景 | 玩家可以与NPC对话获取证词 |
| locked | 锁定场景 | 该循环中此场景不可访问 |

---

### 1.4 sectionId 章节段落ID

| sectionId | 说明 |
|-----------|------|
| SEC01 | 循环1 |
| SEC02 | 循环2 |
| SEC03 | 循环3 |
| SEC04 | 循环4 |
| SEC05 | 循环5 |
| SEC06 | 循环6 |

---

### 1.5 backgroundImage 背景图片路径

**格式：** `Art/Scenes/SC{编号}_bg_{英文场景名}.png`

**示例：**
- `Art/Scenes/SC001_bg_RosaStorageRoom.png`
- `Art/Scenes/SC008_bg_WebbOffice.png`

---

### 1.6 完整配置示例

**搜证场景：**
```yaml
- sceneId: SC1101
  sectionId: SEC01
  sceneName: Rosa储藏室
  sceneNameEn: RosaStorageRoom
  chapterId: CH001
  sceneType: crime
  backgroundImage: Art/Scenes/SC001_bg_RosaStorageRoom.png
  backgroundMusic: BGM_Storage
  ambientSound: AMB_Storage
  备注: 循环1搜证场景,可获得证据111-115
```

**对话场景：**
```yaml
- sceneId: SC1103
  sectionId: SEC01
  sceneName: Tommy办公室
  sceneNameEn: TommyOffice
  chapterId: CH001
  sceneType: dialogue
  backgroundImage: Art/Scenes/SC003_bg_TommyOffice.png
  npcsPresent: NPC105
  备注: 循环1对话场景,与Tommy访谈
```

**锁定场景：**
```yaml
- sceneId: SC1104
  sectionId: SEC01
  sceneName: Webb会客室
  sceneNameEn: WebbReceptionRoom
  chapterId: CH001
  sceneType: locked
  backgroundImage: Art/Scenes/SC004_bg_WebbReceptionRoom.png
  unlockCondition: SEC02
  备注: 循环1该场景未开放,循环2解锁
```

---

## 第二部分：与 scenes.yaml 的对应关系

### 2.1 文件说明

| 文件 | 位置 | 用途 |
|------|------|------|
| SceneConfig.yaml | D:\NDC_project\story\ | 配置表（Excel转换） |
| scenes.yaml | D:\NDC_project\Preview\data\master\ | Preview网站使用的数据 |

---

### 2.2 字段对应关系

| SceneConfig（配置表） | scenes.yaml（Preview） | 说明 |
|----------------------|------------------------|------|
| sceneId | ID键名（如SC1101） | ID格式相同 |
| sceneName | name | 中文名 |
| sceneNameEn | name_en | 英文名 |
| backgroundImage | asset_id | 资源路径/ID |
| 备注 | description | 描述信息 |
| sceneType | - | 配置表特有 |
| sectionId | - | 配置表特有 |
| npcsPresent | - | 配置表特有 |
| - | state | Preview特有，场景状态 |

---

### 2.3 scenes.yaml 结构示例

```yaml
scenes:
  SC1101:
    name: Rosa储藏室
    name_en: RosaStorageRoom
    asset_id: SC001_bg_RosaStorageRoom
    description: 酒吧后方的储藏室，堆满杂物，是Rosa的私人空间

  SC1308:
    name: Webb办公室
    name_en: WebbOffice
    asset_id: SC008_bg_WebbOffice
    description: Webb的私人办公室，案发现场
```

---

## 3. 注意事项

1. **ID格式统一**：sceneId必须符合 `SC` + 章节(1位) + 循环(1位) + 场景序号(2位) 格式
2. **场景序号固定**：01-13对应固定场景
3. **NPC关联**：dialogue类型场景需要填写npcsPresent
4. **解锁条件**：locked类型场景可填写unlockCondition说明何时解锁
5. **音效配置**：backgroundMusic为背景音乐，ambientSound为环境音效

---

## 4. 更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.1 | 2025-11-29 | ID改为4位格式(章节+循环+场景序号)；删除LoopId、groundImage；添加backgroundMusic |
| v1.0 | 2025-11-29 | 初始版本 |
