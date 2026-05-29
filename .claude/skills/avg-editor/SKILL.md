---
name: avg-editor
description: "NDC 网页配置编辑器设计稿——可视化 + 可编辑的'游戏中间态'，取代 preview_new2，替代多数'开 Unity 验收'反馈循环。本 skill 为设计 / 架构决策的权威文档，编辑器实现时按此规范展开。"
user-invocable: false
---

# AVG Editor —— 网页配置编辑器设计稿

> **本 skill 是设计稿，不是执行体**。记录目标 / 范围 / 决策 / 待定项，给未来实现和讨论引用。
> 实施代码不在本目录下；本文件只描述"要做什么、为什么这样做"。

---

## 0. 目标与定位

### 0.1 核心目标
- **取代 preview_new2**：成为可视化 + 可编辑的"游戏中间态"
- **替代多数"开 Unity 验收配置"反馈循环**：从分钟级（启动 + 找场景）降到秒级（刷网页）
- **面向非技术设计者**：让美术 / 策划 / 编剧能直观读懂游戏流程与隐藏关系

### 0.2 工作流定位

```
对话校准（AI 改） ─┐
                  ├─→ Assets/table/*.json （唯一真相源）
手动直改（网页改）─┘                          │
                                              ↓
                                     网页可视化 + 验收
                                              │
                                              ↓
                              （大多数情况无需开 Unity）
```

- **简单修改 = 手动改**（网页 Excel 字段表上直接改）
- **复杂改动 = AI 改**（用对话告诉 AI，网页只做验收）
- **JSON 是唯一真相源**：AI 每轮开工先读 JSON，不基于上一轮对话内存
- **网页验收 ≠ 游戏验收**：能验"配置结构 / 关系 / 自洽"，但 Talk 跳转 / UI 实表现 / 动画对位仍需阶段性开 Unity

---

## 1. 数据源与读写规则

### 1.1 架构（2026-05-28 v0.2 修订）

**编辑器持有独立副本**，不直接读写 Unity 表。理由：Unity 表的 schema 由 `res/xml/*.xml` 锁死，加设计期字段（如 ArtRequirement、openInLoops、循环目标、陷阱原因）需要改 XML + 重新生成 C# + 改运行时。我们的副本可自由加任意设计期字段。

```
avg_editor web UI（设计入口）
       ↕ 读写
d:/NDC_project/avg_editor/data/table/*.json （上游，SoT）
   · 沿用 Unity 字段
   · 加设计期字段（见 §1.4）
       │
       │ 同步工具（剥设计期字段）
       ▼
d:/NDC/Assets/table/*.json（Unity 下游，运行时消费）
       │
       │ 单向导出（按需）
       ▼
_snapshot.xlsx（只读快照，不反向写）
```

**preview_new2/data/table/ 不再用**——历史屎山，不沿用其数据。

### 1.2 种子迁移
`seed.py`：从 `d:/NDC/Assets/table/*.json` 拷过来，加默认空的设计期字段。幂等（已存在则跳过，`--force` 覆盖）。

### 1.3 写回规则（Phase 2 起）
- 保存按钮 → 写回 `d:/NDC_project/avg_editor/data/table/*.json`
- 手动按钮触发"同步到 Unity"（不自动），剥设计期字段后写到 `d:/NDC/Assets/table/`
- 写回前显示 diff 让用户审

### 1.4 设计期字段（不进 Unity 表）

| 表 | 字段 | 用途 |
|----|------|------|
| NPCStaticData | `ArtRequirement` | 立绘 / 头像 / 表情图美术需求 |
| ItemStaticData | `ArtRequirement` | 道具图标 / 模型美术需求 |
| SceneConfig | `ArtRequirement` | 场景背景 / 环境音效美术需求 |
| SceneConfig | `openInLoops: [N,...]` | 场景在哪些 Loop 实际开放（解决"门都配了但场景未必开放"的判断难题） |
| MapConfig | `ArtRequirement` | 地图小图标美术需求 |
| ChapterConfig | `ArtRequirement` | 章节封面 / 过场动画美术需求 |

后续可继续加；同步工具读这张表就知道要剥掉哪些。

### 1.5 弃用表清单（不种入副本）
Event / ExposeTalk / Task / TaskConfig / TimeLineEvent / UITextConfig（共 6 张，副本目录里不出现）

---

## 2. 导航主轴：场景为核心

### 2.1 树结构
```
Unit
└─ Loop
   ├─ 🎬 Scene（多个，按 unlock_condition 推算出的顺序）
   │   ├─ 📦 Items（SceneConfig.ItemIDs → ItemStaticData）
   │   ├─ 👤 NPCs（SceneConfig.NPCInfos → NPCLoopData → NPCStaticData）
   │   └─ 💬 Talk 段落（沿 Talk.next 链遍历归属，详见 §4）
   ├─ ❓ Doubts（Loop 级，挂在 Loop 节点）
   ├─ ⚔️ Expose 元数据（ChapterConfig.exposeNpcId / suspectVideoPos 等）
   └─ 🔗 跨 Loop handoff
```

### 2.2 为什么是场景而非 Talk 链
- 设计者心智模型 = "Loop1 会客室那个场景"，不是"Talk 105001001 链"
- Talk 链是 game spine（运行时主轴），但**配置 / 校对 / 验收的工作单元是场景**
- Talk 链是辅助工具，用来把对白正确归属到对应场景下

---

## 3. 场景类型与视觉编码

> ⚠️ **重要校正（2026-05-28 实测发现）**：state.yaml 里用的 `cutscene / timed_exploration / free_exploration / expose_scene` 这套类型枚举**不在正式配表中存在**。正式 `SceneConfig.json` 的场景类型挂在 `location.sceneType`，C# enum 只定义了 `dialogue = 1`，但实际数据里出现了 "1" 和 "3" 两个值。Phase 1 做"玩家视角分类"时不能直接读 sceneType，必须**从多个信号综合推导**：
> - `firstEnterTalk` 存在 → 场景含开篇 cutscene
> - `ItemIDs` 不空 → 含搜证
> - `NPCInfos` 不空 → 含 NPC 对话
> - 在 `ChapterConfig.exposeNpcId` 对应的 expose 流程中 → 指证场
> - 当前 sceneType="3" 含义待补充（可能是 expose 或 cutscene-only？需求时再 grep 确认）

### 3.1 推导后的玩家视角分类（Phase 1 实现目标）

| 玩家视角分类 | 图标 / 色 | 推导规则 |
|-------------|-----------|---------|
| 🎬 纯 AVG | 紫 | firstEnterTalk 存在 且 ItemIDs/NPCInfos 都为空 |
| 🔍 自由探索 | 蓝 | ItemIDs 或 NPCInfos 不空 |
| ⏱️ 限时探索 | 蓝+计时 | 自由探索 + 配表中有计时标记（具体字段待定） |
| ⚔️ 指证 | 红 | 与 ChapterConfig.exposes 关联的 Talk 链所属场景 |

### 3.2 Loop 典型结构（松散，不强制）
```
🎬 开篇 → 🔍 探索 ×N → ⚔️ 指证 → 🎬 指证后 AVG → [可能延续探索 / 二次指证]
```
**编辑器不能假设固定顺序**——按 unlock_condition 推流程图，按 SceneConfig.type 着色。

---

## 4. Talk 链遍历规则（核心算法）

### 4.1 Talk 归属 Scene 的规则
按优先级从上到下：

1. **Talk.videoScene 字段**——最可靠的直接归属信号
2. **NPCLoopData.TalkInfo / LoopTalkInfo**——场景里 NPC 的对话入口
3. **SceneConfig 的开篇 / cutscene Talk**——场景级入口
4. **ChapterConfig.exposes[*].talkId**——指证 Talk 入口

### 4.2 边界与分段规则
- `script=8 change_scene`：当前场景遍历终止，后续 Talk 归到目标 sceneId 名下
- `script=11 finalexpose`：标记为"指证结算点"，后续 next 链仍归当前指证场景，UI 上贴 "Post-Expose AVG" 标签
- `script=1 branches`：Parameters 里有多个 next 出口，每个分支独立递归遍历
- `script=7 expose`：进入指证子流程
- `script=2 end`：链终止
- **防环**：遍历时记录已访问 ID，循环引用要警告

### 4.3 post-Expose 不是独立配置
- ExposeData 表**没有** post_expose_talkId 字段
- post-expose 内容 = `script=11 finalexpose` 节点之后的 next 链
- 编辑器把这段贴 "Post-Expose AVG" 标签即可，不需要新建数据结构

---

## 5. ID 解析原则（强制）

### 5.1 展示规则
**所有 UI 字段都不能出现裸 ID**，必须解析为具名内容。

| 不要这样 | 要这样 |
|---------|--------|
| `condition: [2101, 2102]` | `[📷 尸体手指照片] [📓 Margaret 相册]` |
| `talkId: "105902001"` | `Tommy · L2 R1 指证（首句：…）` |
| `itemType: 1` | `📷 线索` |
| `condition.type: 1` | `📦 道具触发` |

### 5.2 ID 仍可见的场景
- 节点右上角小灰字（hover 才看清）
- 排查冲突 / 外部沟通时复制
- 永远不让用户手动输入 ID

### 5.3 编辑时
所有 ID 字段编辑 = 搜索弹窗按名字选 → 后端存 ID。
不允许直接输 ID 数字。

---

## 6. 编辑交互

### 6.1 字段编辑（Excel 风格）
- 文本字段：就地编辑
- 数字字段：就地编辑 + 数值校验
- 枚举字段：下拉（显示中文标签）
- ID 引用字段：搜索选择器（输名字定位）
- 数组字段：增删卡片

### 6.2 保存流程
1. 改完字段 → 红点提示"有未保存改动"
2. 点保存 → 弹 diff 预览
3. 用户确认 → 写回 JSON
4. 弹"是否同步 Excel" 询问

### 6.3 撤销 / 历史
- 本地保留最近 N 次改动栈
- 文件级 backup（沿用 `.bak` 后缀约定）

---

## 7. 校验徽章

节点右上角三色徽章：

| 状态 | 触发条件 |
|------|---------|
| 🟢 | 全部通过 |
| 🟡 | 时序问题 / 孤儿节点 / 死路对话 / 缺可选字段 |
| 🔴 | ID 重复 / 引用不存在 / 一对一冲突 / 必填字段缺失 |

实时校验（改完字段立刻跑），不等保存。

---

## 8. 配表约束（编辑器需要内置的"坑位"知识）

### 8.1 ID 编码规则
- **SceneConfig.id**：4 位 `{unit}{loop}{location:2d}`，如 2103 = U2L1Loc03
- **ItemStaticData.id**：4 位，11XX=U1L1，17XX=分析后证据，18XX=门 / 道具；6 位（110XXX）= 装饰
- **NPCStaticData.id**：3 位，101-111 已分配
- **DoubtConfig.id**：`{unit}{loop}{seq}`
- **TestimonyItem.id**：`{NPC3}{loop1}{seq3}`
- **Talk.id**：6-9 位，普通 `{NPC3}{group3}{seq3}`，指证 `{loop2}{seq4}`

### 8.2 业务规则
- **Expose 谎言收集规则**：只 R1 谎言锚作 Testimony；R2/R3 是 Expose 内部退守对白，无 testimony ID
- **Doubt condition 一对一挂载**：同一 Item / Testimony 不应被多个 Doubt 引用（编辑器要警告冲突）
- **证据时序**：condition 件必须在 posed_loop ≤ 使用 Loop 前可获取
- **SceneConfig 是超级容器**：NPC / Item 仅通过 NPCInfos[] / ItemIDs[] 挂载，无其他直接关系

### 8.3 跨表关系（编辑时要联动检查）
| 字段 | 引用目标 |
|------|---------|
| ChapterConfig.initTalk | Talk.id |
| ChapterConfig.initScene | SceneConfig.id |
| ChapterConfig.exposeNpcId | NPCStaticData.id |
| SceneConfig.NPCInfos[] | NPCLoopData |
| SceneConfig.ItemIDs[] | ItemStaticData.id |
| Talk.next | Talk.id（链） |
| Talk.Speaker | NPCStaticData.id |
| ExposeData.testimony | TestimonyItem.id |
| ExposeData.item[] | ItemStaticData.id |
| ExposeData.talkId | Talk.id |
| DoubtConfig.condition[].param | type 决定指向 Item / 关系网 / Testimony |

---

## 9. 分阶段推进计划

### Phase 0 —— 技术地基（半天）
- 本地 Python 后端（沿用 `json_to_excel.py` 的依赖）
- 前端 HTML/JS + Vue CDN（无构建工具）
- 跑通"读 Loop1 所有 Scene 输出 JSON"

### Phase 1 —— 只读视图（核心，先做）
- 游戏流程导航树
- 字段表（Excel 风格）只读展示
- **所有 ID 解析为具名内容**（§5）
- ID 字段点击跳转
- 校验徽章（红 / 黄 / 绿）

> **Phase 1 完工即上线**——这时已经能取代 preview_new2 + 取代大部分"开 Unity 验收"工作。

### Phase 2 —— 编辑模式
- 字段就地编辑
- ID 引用字段搜索选择器
- JSON 写回 + Excel 同步询问
- diff 预览 + 撤销栈

### Phase 3 —— AI 协作面
- 节点 TODO 标记
- 选中节点"导出 AI 上下文"按钮
- AI 写回 diff 审核

### Phase 4 —— 高级可视化
- 疑点触发链关系图
- Expose 证据池图（可击穿 vs 陷阱）
- 跨 Loop 伏笔图
- 全局搜索 / 多条件过滤

---

## 10. 与 preview_new2 的关系

### 10.1 不直接复用代码
- preview_new2/index.html 是 5657 行单文件，且同目录有多个废弃试验版本
- 数据源彻底变了（state.yaml → 直接 JSON），原管道不可沿用
- 旧版纯展示无后端，新版需要后端写 JSON

### 10.2 复用三样东西
1. **视觉语言**：颜色 / 布局 / Loop 卡片字段排版
2. **设计经验判断**：旧版反复迭代得出"哪些字段值得展示 / 哪些是噪音"
3. **图标 / 类型映射约定**：道具 / 线索 / 门 / 装饰图标

### 10.3 并行存在
preview_new2 暂不删除，直到 Phase 1 跑稳。

---

## 11. 待拍板事项（讨论时再决定，不阻塞 Phase 0/1）

### 11.1 跨 Loop 伏笔链是否在配表持久化？
- 选 A：不加。编辑器仅展示当前可推断的关系，伏笔信息丢失
- 选 B：新建 ForeshadowingConfig 表
- 选 C：在 ItemStaticData 加 `foreshadow_links` 字段（轻量）

### 11.2 循环目标（player_context.goals）是否加入 ChapterConfig？
目前只在 state.yaml，配表里没有。

### 11.3 Expose 陷阱原因是否加入 ExposeData？
目前 trap_reasons 只在 state.yaml。

### 11.4 突发事件小图字段
最近 git 提到新增"突发事件（小图）"机制，但未确认对应 Talk.script 值或新字段。实施 Phase 1 前需要 grep 一遍最近 Talk.json / SceneConfig.json diff 确认。

---

## 12. 实施位置（待 Phase 0 启动时填）
- 后端目录：(TBD)
- 前端目录：(TBD)
- 启动脚本：(TBD)
- 端口约定：(TBD，preview_new2 用 9527，新版考虑 9528)

---

## 修订记录
- 2026-05-28 v0.1：初版，沉淀讨论结论（Ellcy + Claude）
- 2026-05-28 v0.2：架构改为"编辑器持有独立副本"。§1 改写，新增 §1.4 设计期字段表；§3 校正 sceneType 实测发现；Phase 0 完成；Phase 1 完成（只读视图 + ID 解析 + 校验徽章）；种子迁移完成。
