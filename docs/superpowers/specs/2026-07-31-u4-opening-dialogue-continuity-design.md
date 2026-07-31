# Unit4 Opening 与对白连续性约束设计

> 日期：2026-07-31  
> 范围：`unit-state-generator`、`team-dialogue`、AVG 对话命名规则、Unit4 State 合同与校验  
> 状态：待用户审查

## 一、问题与目标

Unit4 当前存在两个相互关联的系统性问题：

1. State 没有正式定义 Opening 是“场景级强制连续段”，生成者因而把开篇按 NPC 或地点拆成多个 Talk，甚至把强制节拍移入自由探索。
2. 对白流水线虽然要求读取大纲、检查承上启下和全局连续性，但仍按“每个 NPC Talk 一个写作单元”并行生成。每个小段可以局部合格，整场与整章却可能没有动作、物件、问题和情绪上的连续记忆。

目标不是把 State 写成剧本，而是建立两层约束：

- State 记录不可改写的剧情状态与交接合同。
- `team-dialogue` 根据这些合同、完整大纲、人物档案和前序实际对白，推演出具体的台词呼应、伏笔回收和情绪余波。

## 二、权威顺序

生成与审查必须遵守：

1. `canon_manifest.json` 指定的 active outline。
2. 用户明确批准的变更。
3. 对 active outline 歧义的讨论裁决。
4. State。
5. 对白草稿。

《讨论结论》不得成为可以覆盖 active outline 的独立 Canon。它只能：

- 整理大纲已明确内容；
- 裁决大纲明确标注的歧义；
- 将确需新增或改写的内容列为待用户批准项。

未经批准，不得新增地点、NPC、互动门槛、事件顺序或玩家控制阶段。

## 三、Opening 合同

每个 Loop 只有一个根级 Opening 流程。Opening 内可因地点切换、时间跳转或独立事件节拍拆成一个或多个有序 Talk，但 Talk 必须按场景或事件命名，不能按人物命名。

以 L3 的跨地点开篇为例：

```yaml
opening:
  type: cutscene_sequence
  sequence:
    - event_id: broken_call
      talk: L3_opening_broken_call
      scene_id: 4021
      location: "Zack 侦探事务所"
      cast: [Zack, Emma, Harold]
      required_beats:
        - "人工接线员接通 Morrison 宅邸来电"
        - "Harold 只来得及说出 Brennan"
        - "线路被人为切断，Zack 与 Emma 立即出发"
      transition_to: mansion_arrival
    - event_id: mansion_arrival
      talk: L3_opening_morrison_mansion_arrival
      scene_id: 4022
      location: "Morrison 宅邸门口"
      cast: [Zack, Emma, Mickey]
      required_beats:
        - "23:30，Zack 与 Emma 抵达宅邸"
        - "两人在门口撞见 Mickey"
        - "Mickey 强制说出自己也刚到、是 Morrison 叫他来的"
      transition_to: free_exploration_4022
  player_control_restored_after: mansion_arrival
```

规则：

- `opening` 是一个有序强制流程；`opening.sequence[]` 含一个或多个场景级/事件级 Talk。
- `sequence[].talk` 按场景或事件命名，不按某一名说话者命名。
- `sequence[].cast` 只表示该段强制演出中的出场者，不等于可点击 NPC。
- 地点、时间或事件切换可以拆 Talk，但不能因为说话人变化而拆 Talk。
- 同一物理场景内的连续群像对话默认保持为一个 Talk；只有发生明确转场或独立事件切点时才拆分。
- `scenes[].npcs` 只登记玩家恢复控制后可以主动交谈的 NPC。
- 同一角色若既参加 Opening，又在之后可自由交谈，必须明确分成“强制演出角色”与“自由交互 NPC”两种职责，不得默认复制 Talk。
- `player_control_restored_after` 指向 sequence 中最后一个强制节拍；在此之前不得进入普通自由 Talk。
- Opening 结束前不得出现普通 Talk 分支；需要玩家选择的特殊开篇玩法必须由大纲明确批准。

Talk 名称示例：

```text
L1_opening_courthouse_blockade
L1_opening_east_wing_entry
L2_opening_thirteen_days
L2_opening_hearing_window
L3_opening_broken_call
L3_opening_morrison_mansion_arrival
L4_opening_fracture
L4_opening_eviction_notice
L5_opening_forty_second_floor
```

## 四、State 连续性字段

新增顶层设计字段 `narrative_continuity`。它不进入 Unity 运行时配置表，只约束 State 与对白生成。

```yaml
narrative_continuity:
  units:
    - id: L2_harold_followup
      source_anchor: "Unit4 active outline / Loop2 / 散庭后"
      entry_state:
        - "Whitfield 已在法庭被击穿"
        - "Harold 对 Pierce 的不信任开始外露"
      consumes:
        - "Harrison 材料尚未进入 Pierce 的接管链"
      required_callbacks:
        - "Harold 明确要求 Zack 今晚守着事务所电话"
        - "Emma 要求所谓私下谈话必须包括自己"
      exit_state:
        facts:
          - "Harold 准备再次联系 Zack"
        relationship_changes:
          - "Harold 首次把 Zack 与 Pierce 区分开"
        unresolved_pressure:
          - "Harold 手中的密封材料尚未交出"
      hands_off_to: L3_opening
```

字段边界：

- 记录“发生了什么、谁知道什么、关系发生了什么变化、什么必须交给下一场”。
- 不预写具体台词，不规定修辞，不替玩家下结论。
- `required_callbacks` 表示下一场必须回应、拒答、升级或转义的压力，不要求原句复读。
- 每个 Opening、关键 Talk、Expose、post_expose 和 ending_sequence 至少有一个 continuity unit。
- 相邻 unit 必须通过 `hands_off_to` 形成可检查的有序链。

## 五、对白流水线改造

### Phase 0：整章深读包

除现有全局人物状态卡、Zack 知识账本、全局补笔清单、旧出场核对表和文笔校准卡外，强制新增：

1. 整章认知与情绪主轴：每个 Loop 的进入认知、认知变化、离开认知、情绪弧和禁止提前回收的答案。
2. 场景包清单：一个完整物理/叙事场景包含哪些 Talk/Expose 文件、进入状态、节拍顺序、退出状态及文件拆分理由。
3. 场景接缝账本：逐个相邻单元记录上一场遗留的问题、动作、物件和情绪，以及下一场的处理方式。
4. 伏笔/回收账本：首次埋入、再次提醒、意义变化、正式回收或转交后续 Unit。
5. 动态人物状态表：逐场记录欲望、防守、知识、关系温度、身体位置、手中物件和离场变化。
6. 前序实际对白摘要：写 Loop N 前读取本 Unit Loop1 至 Loop N-1 的现行手改稿，提取真实说过的话、未结束的争执、离场动作和未回收钩子。

### Phase 1：按场景包分组

- 默认一个连续场景由同一个 narrative-designer、puzzle-designer 和 dialogue-writer 负责。
- JSON 文件必须拆分时，先写完整场景 treatment，再按明确切点拆文件。
- 禁止按 NPC 名单直接把同一强制场景拆成多个独立写作单元。
- 同一 `scene_id` 同时出现在 Opening 与自由探索却没有明确的控制权交接、同一 NPC 在两处重复挂 Talk、State 缺少 `opening.sequence[]`、或 Opening Talk 以人物命名时，必须停止并回报上游缺陷。

### Phase 2：写作输入

Writer 除现有材料外，必须收到：

- 完整场景 treatment；
- 当前场景的 continuity unit；
- 上一单元结尾的实际对白尾段；
- 下一单元的进入合同；
- 本场必须回应的前文压力；
- 本场必须留下的后续压力；
- 物件与人物位置连续性。

### Phase 3：整场与整章缝合

- 不只补连接句；若接缝要求改变内部节拍，必须退回场景 writer 重写。
- 每个明确抛出的问句、动作或承诺，在后续对应位置必须出现“回应、拒答、打断、升级或转义”之一。
- 相邻文件重复询问、重复交代同一事实或重新进场，直接打回。

### Phase 4：全量接缝审查

- 承上启下不再随机抽两段，改为逐接缝全检。
- Timeline 审查增加对白层面的情绪债、承诺、物件和伏笔回收。
- 每个场景必须指出它消费了哪一项既有压力，并产生了什么新的状态变化；只传递本场信息点而没有状态变化，不能放行。

## 六、规则一致性修正

以下文件必须同步更新，避免三套互相冲突的格式：

- `.agents/skills/unit-state-generator/SKILL.md`
- `.agents/skills/team-dialogue/SKILL.md`
- `AVG/对话配置工作及草稿/AVG对话配置规则.md`
- Unit4 State contract 与 validator/tests

同时修正 `team-dialogue` 中过时的章节映射：Unit9 是 Unit1 的现行策划别名，Unit10 是 Unit2 的标题别名；章节身份和 active outline 一律以 Manifest 为准。

## 七、校验与测试

先编写失败测试，证明当前结构会被接受：

1. 缺少 `opening.sequence[]`，或 sequence 为空。
2. `sequence[].talk` 缺失、重复，或使用人物名而非场景/事件名。
3. Opening 下的 Talk 出现在 `sequence[]` 以外的按人物分组中。
4. 跨地点 Opening 的后半段被放入 `scenes[].npcs`。
5. 同一 scene/NPC 在 Opening 与自由探索重复挂 Talk，且没有明确控制权交接。
6. `player_control_restored_after` 未指向 sequence 中的最后一个强制节拍。
7. `narrative_continuity.units` 缺少 `hands_off_to` 目标或形成断链。
8. 《讨论结论》新增 active outline 不存在的 Opening NPC/地点。

实现后要求全部测试通过，并重新运行现有 Unit4 State 合同测试与跨 Loop 校验。

## 八、Unit4 返工范围

### State

局部重建但覆盖所有五个 Opening：

- L1：Opening + SC4001。
- L2：Opening + SC4011 的控制权边界。
- L3：Opening + SC4021→SC4022 的强制序列 + Mickey 归属。
- L4：Opening + SC4031 的固定三拍。
- L5：Opening + SC4041/SC4042；撤回未获大纲授权的门房前置。

保留已稳定的证据、疑点、指证和 ending_sequence。若局部重建发现证词/证据获取时序被实质污染，再升级相关模块返工。

### 对白

State 修正后，从 `team-dialogue` Phase 0 重跑 Loop1–Loop5：

- 现有草稿保留，不直接覆盖；
- 用户手改内容提取为文笔与人物约束；
- 新稿写入独立临时/候选文件；
- 完成逐接缝审查后再由用户决定替换范围。

## 九、验收标准

- 五个 Loop 都只有一个根级 Opening 流程；每个流程包含一个或多个按场景/事件命名的有序 Talk。
- Opening 的事件、地点、人物和顺序可逐项追溯到 active outline 或用户批准记录。
- Opening Talk 不以人物命名，且人物变化本身不能构成拆分理由。
- 强制 Opening 与自由探索 NPC 边界明确。
- 所有 continuity unit 形成有序交接链。
- 每个对白单元都能说明消费了什么既有压力、改变了什么状态、向下一场留下了什么。
- 所有相邻文件完成逐接缝审查，无重复询问、重复进场或遗忘上一场明确承诺。
- U4 新对白不覆盖现有手改稿，替换前提供差异对照。
