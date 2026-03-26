# NPC系统

## 一、核心概念

NPC系统管理游戏中所有非玩家角色的静态属性和场景表现。数据分为两层：

- **NPCStaticData**（全局层）：角色的固有属性——名字、角色类型、头像、主题色。每个NPC在整个游戏中只有一条记录。
- **NPCLoopData**（实例层）：NPC在具体场景中的表现——绑定哪段对话、使用什么立绘、站在什么位置。同一个NPC在不同Loop/场景中有不同的实例。

NPC不直接出现在场景里，而是通过 `SceneConfig.NPCInfos[]` 引用 NPCLoopData 实例来间接绑定。

## 二、角色类型（role 枚举）

| role | 名称 | 说明 | 第一章角色 |
|------|------|------|-----------|
| 4 | protagonist | 主角 | Zack (101), Emma (102) |
| 2 | suspect | 嫌疑人 | Rosa (103), Morrison (104), Tommy (105), Vivian (106), Jimmy (107) |
| 1 | deceased | 死者 | Webb (109) |
| 3 | others | 其他（证人/幕后） | Anna (108), Mrs. Morrison (110), Whale (111) |

## 三、第一章NPC完整列表

| ID | 角色 | 身份 | role | 主题色 | 头像 |
|----|------|------|------|--------|------|
| 101 | Zack Brennan | 主角侦探 | 4 | — | 无 |
| 102 | Emma O'Malley | 搭档 | 4 | — | 无 |
| 103 | Rosa | 嫌疑人/清洁工 | 2 | #f47800 | rosa_small / rosa_big |
| 104 | Morrison | 嫌疑人/警探 | 2 | #6f83ff | morrison_small / morrison_big |
| 105 | Tommy | 嫌疑人/酒吧经理 | 2 | #d0c801 | tommy_small / tommy_big |
| 106 | Vivian | 嫌疑人/歌手 | 2 | #f753ed | vivian_small / vivian_big |
| 107 | Jimmy | 凶手/厨师 | 2 | #1d9600 | jimmy_small / jimmy_big |
| 108 | Anna | 证人 | 3 | — | anna_small / anna_big |
| 109 | Webb | 死者 | 1 | — | webb_small / webb_big |
| 110 | Mrs. Morrison | 证人 | 3 | — | mrsmorrison_small / mrsmorrison_big |
| 111 | Whale | 幕后主使 | 3 | — | 无 |

> Zack、Emma、Whale 没有 IconSmall/IconLarge，因为主角不作为可调查对象出现在案情板中。

## 四、数据结构

### 4.1 NPCStaticData — 全局属性表

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | int | NPC唯一ID（3位） | `"105"` |
| Name | string[] | [中文名, 英文名] | `["Tommy","Tommy"]` |
| role | enum | 角色类型 | `"2"` (suspect) |
| Chapter | string | 所属章节 | `"EPI01"` |
| IconSmall | string | 小头像资源名 | `"tommy_small"` |
| IconLarge | string | 大头像资源名 | `"tommy_big"` |
| color | string | 主题色 HEX | `"#d0c801"` |

### 4.2 NPCLoopData — 场景实例表

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | int | 实例ID（4位） | `"1001"` |
| NPC | NPCStaticData | 引用的NPC全局数据 | `{"id":"105",...}` |
| TalkInfo | Talk | 首次对话起始句 | `{"id":"105001001",...}` |
| LoopTalkInfo | Talk | 重复对话起始句 | `{"id":"105002001",...}` |
| ResPath | string | 待机立绘路径 | `"Art\Scene\NPC\EPI01\SC103_npc_Tommy1"` |
| ClickResPath | string | 点击后立绘路径 | `"Art\Scene\NPC\EPI01\SC103_npc_Tommy2"` |
| PosX / Posy / PosZ | float | 场景中坐标 | `"1101"`, `"681"`, `"-1"` |

**两层对话机制**：
- `TalkInfo`：玩家首次点击该NPC时进入的对话链（主线对话，包含剧情和证据获取）
- `LoopTalkInfo`：再次点击时进入的对话链（简短回顾，通常只有几句）

## 五、NPC与场景的绑定

NPC 通过 `SceneConfig.NPCInfos[]` 绑定到具体场景：

```
SceneConfig (sceneId=1103, Tommy办公室 Loop1)
└── NPCInfos[]
    └── NPCLoopData (id=1001)
        ├── NPC → NPCStaticData (id=105, Tommy)
        ├── TalkInfo → Talk (id=105001001, 首次对话)
        ├── LoopTalkInfo → Talk (id=105002001, 重复对话)
        ├── ResPath = SC103_npc_Tommy1 (待机立绘)
        └── PosX=1101, PosY=681 (场景位置)
```

同一个NPC在不同Loop中是不同的 NPCLoopData 实例。例如 Tommy(105) 在 Loop1 场景1103 中是实例 1001，在 Loop2 场景中可能是另一个实例 ID，绑定不同的对话和立绘。

## 六、完整配置实例

**NPCStaticData 示例**（Tommy）：
```json
{
  "id": "105",
  "Name": ["Tommy","Tommy"],
  "role": "2",
  "Chapter": "EPI01",
  "IconSmall": "tommy_small",
  "IconLarge": "tommy_big",
  "color": "#d0c801"
}
```

**NPCLoopData 示例**（Tommy 在 Loop1 Tommy办公室）：
```json
{
  "id": "1001",
  "NPC": {"id": "105", "Name": ["Tommy","Tommy"], "role": "2", ...},
  "TalkInfo": {"id": "105001001", "Words": ["谁？...楼下出了大事...","Who?..."], ...},
  "LoopTalkInfo": {"id": "105002001", "Words": ["又是您？我...我刚才都说过了...","You again?..."], ...},
  "ResPath": "Art\\Scene\\NPC\\EPI01\\SC103_npc_Tommy1",
  "ClickResPath": "Art\\Scene\\NPC\\EPI01\\SC103_npc_Tommy2",
  "PosX": "1101",
  "Posy": "681",
  "PosZ": "-1"
}
```

## 七、NPC交互流程

```
玩家点击场景中的NPC立绘
    ↓
判断对话状态
    ├── 首次对话 → 进入 TalkInfo 对话链（主线剧情）
    └── 已完成首次 → 进入 LoopTalkInfo 对话链（简短回顾）
    ↓
对话过程中可能触发：
    ├── script="3" (get) → 获得证词/物品
    ├── script="1" (branches) → 分支选择
    └── script="7" (expose) → 进入指证
    ↓
对话结束
```

## 八、ID编码规则

### NPC ID（NPCStaticData.id）：3位数

- 第一章：`1XX`（101-111）
- 第二章：`2XX`（201-212）

### NPCLoopData ID：4位数

格式为 `{序号}{实例编号}`，按场景配置顺序递增分配。

## 九、与其他系统的关联

| 系统 | 关联方式 |
|------|----------|
| **SceneConfig** | 通过 `NPCInfos[]` 引用 NPCLoopData，决定哪些NPC出现在哪个场景 |
| **Talk** | NPCLoopData 的 TalkInfo/LoopTalkInfo 指向对话链起点；Talk.Speaker 反向引用 NPCStaticData |
| **Testimony** | 证词的 `npc` 字段引用 NPCStaticData，标记这段证词属于谁 |
| **ChapterConfig** | `exposeNpcId` 指定本轮指证对象的 NPC ID |
| **GameFlowConfig** | `deceased` 引用 NPCStaticData，标记本章死者 |
