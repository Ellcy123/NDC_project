# Unity Opening 运行时合同

本参考只解释 State 里的 Opening 如何映射到 `D:\NDC`。剧情事实仍以
`canon_manifest.json` 指定的 active outline 为准；运行时能力不能反向创造剧情。

## 数据源边界

- Unity 正式表源：`D:\NDC\res\xls\*.xlsx`。
- 正式生成物：`D:\NDC\Assets\table\*.json` 与
  `D:\NDC\Assets\Resources\table\*.bytes.txt`。
- 正式落表必须修改 Excel，再运行 `D:\NDC\res\Translate\bin\Debug\Translate.exe`。
- `avg_editor_v2/data/table` 是设计期副本；其中的 `openingScene`、
  `openingBrief`、`ArtRequirement` 等增强字段不等于 Unity 正式字段。
- State 的 `outline_coverage`、`narrative_continuity`、`runtime_root`、
  `required_beats` 等字段均为设计期合同，不直接进入 Unity 表。

## 四种对话入口

| 入口 | 运行时含义 | State 用途 |
|---|---|---|
| `ChapterConfig.initTalk` | 当前 Loop 的单一初始对话入口 | 根级 Opening 第一段 |
| `SceneConfig.firstEnterTalk` | 某场景第一次完成进入时播放一次，状态随存档保存 | 非根级、真正依赖“首次到访”的场景演出 |
| `NPCLoopData.TalkInfo` | 本 Loop 首次点击该 NPC | 自由探索普通 Talk |
| `NPCLoopData.LoopTalkInfo` | 本 Loop 后续点击该 NPC | Repeat / 再访 Talk |

不得把强制 Opening 剧情放进 `TalkInfo` 或 `LoopTalkInfo`。`videoScene`
只是 Talk 媒体分组字段，不决定该 Talk 从哪个入口触发。

工程另有 `SceneEnterTalkTriggerConfig` ScriptableObject。它按 `sceneId`、
`talkId` 和 `requiredItemIds` 条件触发，当前不是正式表字段，也没有通用剧情条件
或显式优先级。只有 active outline 明确需要“进入已开放场景后、满足道具条件自动
触发”且系统策划批准时才能使用；不得把它当作默认 Opening 入口。

### 自由探索中的强制事件

- State 的 `scenes[].event_triggers[].talk` 是场景级强制事件入口，不是 NPC
  `TalkInfo`。`team-dialogue` 必须生成它，但配置时不得把它挂成可点击 NPC。
- 使用 `SceneEnterTalkTriggerConfig` 时，State 必须直接写出全部
  `runtime_binding.required_item_ids`。当前运行时只支持这些道具条件的全 AND；
  “调查完成”“某段 Talk 已完成”“前一事件已发生”等自然语言条件不能直接落地。
- 大纲要求固定顺序且包含 Talk 完成条件时，State 仍须完整写出
  `required_talks → grants_evidence → previous_event_completed → next_talk`，并标记
  `special_adapter`。运行时缺能力是待实现项，不得反向删掉剧情顺序。
- 被前一 Talk 的 `next` 续接的 Event Talk，目标事件必须标记为 `chained_talk`；
  不得再作为独立条件事件重新触发。

## 根级 Opening 映射

每个 Loop 只有一个 `ChapterConfig.initTalk`，因此 State 也只有一个根级
`opening` 流程：

```yaml
opening:
  type: cutscene_sequence
  runtime_root:
    table: ChapterConfig
    init_scene: 4021
    init_talk: L3_opening_broken_call
  sequence:
    - event_id: broken_call
      talk: L3_opening_broken_call
      scene_id: 4021
      location: "Zack 侦探事务所"
      cast: [Zack, Emma, Harold]
      required_beats:
        - "人工接线员转入 Harold 的电话"
        - "Harold 只说出 Brennan 后断线"
      runtime_exit:
        action: change_scene
        target_scene_id: 4022
        continuation: next_talk
        next_talk: L3_opening_mansion_arrival
    - event_id: mansion_arrival
      talk: L3_opening_mansion_arrival
      scene_id: 4022
      location: "Morrison 宅邸门口"
      cast: [Zack, Emma, Mickey]
      required_beats:
        - "Zack 与 Emma 在门口撞见 Mickey"
        - "Mickey 强制声称自己也刚到"
      runtime_exit:
        action: release_to_exploration
  player_control_restored_after: mansion_arrival
```

映射规则：

1. `runtime_root.init_scene` → `ChapterConfig.initScene`。
2. `runtime_root.init_talk` → `ChapterConfig.initTalk` 对应 Talk 的首句 ID。
3. 同一场景内继续下一段，用普通 `Talk.next`。
4. 跨场强制续接时，当前 Talk：
   - `script = DialogueAction.change_scene`
   - `Parameters[0].ParameterInt = target_scene_id`
   - `next = next_talk` 对应 Talk 的首句 ID
5. `next > 0` 时，运行时会以 `skipFirstEnter: true` 切场，并在新场景继续
   `next` Talk；不得再让目标场景的 `firstEnterTalk` 承载同一剧情拍。
6. 最后一段结束后才释放玩家控制。自由探索 NPC 入口此后才生效。

同一角色可以同时参加 Opening 和之后的自由探索，但两个入口必须承担不同内容：
Opening 是不可跳过的事件拍，NPC Talk 是玩家恢复控制后的主动询问。不得复制同一
问句、事实交代或进场动作。

## 拆分 Talk 的判据

可以拆分：

- 地点切换并需要运行时 `change_scene`。
- 明确时间跳转。
- 独立事件切点需要不同媒体、资源或保存/恢复边界。

不能仅因为说话人变化而拆分。同一地点、同一时间、动作连续的多人对手戏默认是一段
场景级 Talk；即使制作上拆成多个文件，也必须先有一个完整场景 treatment 和明确切点。

Opening Talk 名按场景或事件命名：

```text
L1_opening_courthouse_blockade
L3_opening_broken_call
L3_opening_mansion_arrival
L4_opening_office_confrontation
```

禁止：

```text
L1_opening_mickey
L3_opening_emma
L4_opening_doris
```

## 运行时风险检查

- `initTalk` 与初始场景 `firstEnterTalk` 不得重复承载同一 Opening。
- `change_scene + next` 与目标 `firstEnterTalk` 不得重复承载同一续接段。
- 纯 AVG 场景也必须有有效 `SceneConfig.sceneId` 和 `LocationConfig`。
- `Talk.next`、`ChapterConfig.initTalk`、`SceneConfig.firstEnterTalk`、
  `NPCLoopData.TalkInfo/LoopTalkInfo` 引用的 Talk ID 必须存在。
- `change_scene.Parameters[0]` 指向的 SceneConfig 必须存在。
- non-Loop `ending_sequence` 必须由最后一个 post-expose Talk 通过
  `change_scene + next` 唯一进入；4043–4045 之类的连续终幕场景不得再生成
  `NPCLoopData.TalkInfo`。
- 当前 `DialogueAction` 使用 `loop_end` 结束最后一轮。State 若要表达章节边界，
  使用 `loop_end + chapter_boundary: true`，不能写运行时不存在的 `chapter_end`。
- 强制终幕开始后不得恢复玩家控制；中途存档恢复仍需 Unity 侧优先消费续播状态，
  不能重新执行 `ChapterConfig.initTalk`。
- State 生成阶段只能登记逻辑 Talk 名；正式 Talk ID 在对白与落表阶段分配后回填。
- Unity 代码或表结构若与本参考不一致，停止落表并以当前
  `D:\NDC\res\xls`、`res\xml` 和运行时代码重新核对，不沿用历史 State 猜测。
