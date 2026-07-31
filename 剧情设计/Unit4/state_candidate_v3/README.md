# Unit4 State v3 候选差异报告

## 状态

- 事实源：`canon_manifest.json` 登记的 `Unit4_大纲0723_逻辑重构版_v3.md`
- 候选范围：Loop1—Loop5，加 Loop5 所属的非 Loop 终幕
- 现行 `剧情设计/Unit4/state/`：保留为替换前基线，未覆盖
- 对白与 Unity 表：本轮未生成、未同步

## 为什么需要候选重生成

旧 State 的证据、疑点和指证核心大体可用，但 Opening 仍按人物拆分，强制事件与自由 NPC Talk 混用，且缺少跨场续接、控制权恢复点、大纲覆盖矩阵和完整交接链。Loop5 还加入了 v3 没有的夜班门房、公共前厅与放行逻辑。

## 逐 Loop 变化

### Loop1

- 将 Pierce、Mickey 人物 Opening 合并为 `L1_opening_courthouse_blockade`。
- 补齐 Mary 被强制改判过失杀人、Mickey 来意、Harrison 枪伤、圣心医院旧案、警方尚未进入办公室等必拍信息。
- 指证后新增明确事件归属：开保险柜、Morrison 犹豫、Rosa 次日听证。

### Loop2

- 将 Rosa、Mickey 合并为同场连续事件 `L2_opening_thirteen_day_hearing`。
- 明确 Mickey 的拖延听证、代理律师和邀请 Zack 担任二辩方案。
- Opening 结束后 Rosa 继续留在 4011，使用独立自由 Talk 说明红线用药、
  十三日开启记录和不存在第二只药瓶，并对话交付 4211、4212。
- 指证后固定为 Whitfield 结果、Rosa 拒签与回执、Morrison 走廊接触。
- 恢复 v3 的“停止广播和录音”，不沿用旧讨论中的媒介替换。

### Loop3

- 建立 `4021 来电 → 4022 宅邸门口` 的唯一根 Opening 连续链。
- Mickey 的“自己也刚到”改为必经掩护谎言，不再依赖玩家点击 NPC。
- 删除“线路已被人为切断”的提前结论。
- 撤离、爆炸和 Pierce 接管改为强制事件；Pierce 接管不再挂自由 NPC Talk。
- 将 Mickey 的爆炸反应和 Doris 的 18:12 市政工证词移到 4023 爆炸后自由
  Talk，不在 4022 提前播放。
- 指证后明确左右手证词冲突与官方自杀结案事件。

### Loop4

- Mickey、Emma、Doris 合并为 `L4_opening_office_confrontation`。
- 补回枪位追问、Morrison 会面追问、Patrick 冲突和 Mickey 沉默。
- Sarah 在前往 Margaret 家之前先由 Emma 送到 Rosa 家。
- 4033 补 Sarah 自由 Talk，先建立她认识 Rosa、曾在 Rosa 家留宿，避免安全屋
  安排凭空出现。
- 指证后明确 Patrick 真相、遗物匣唯一取得和 L5 独自前往四十二层的交接。

### Loop5

- 删除 Scene4041、夜班门房、公共前厅、放行、临时下楼和门未锁解释。
- Chapter 根入口直接落在 4042；最小到达事件结束后立即自由探索。
- Emma 先因 Zack 长时间未回而自主出发，抵达楼下后才发现 Miller 车辆增加。
- 4043→4044→4045 建立强制续接，U4 只在 O'Hara 家门外结束。
- 4517 在 4044 向 Emma、Watts 共享；4518、4519 被 Zack 扣下；4519 在 4045 发现街区症状后交给 Watts。

## 保留项

- 五个 Loop 的证据 ID 集合。
- L1—L4 的疑点 ID 集合。
- 五个 Loop 的证词 ID 集合；普通可获取证词全部在实际获取位置内联正文与来源锚点。
- 五个 Loop 的 Expose 谎言、可用证据与结果核心。
- L5 三条身份链、Mickey 价值对话、Miller 条件、主动松手和门外截止。

## 新合同

- 每 Loop 只有一个 `ChapterConfig.initTalk` 根入口。
- Opening Talk 按场景或事件命名，不按人物命名。
- 跨场强制剧情使用 `change_scene + next_talk`；完整事件播完后才恢复控制权。
- `outline_coverage` 追踪大纲必拍的主落点。
- active outline 中 13 处 `👤 NPC` marker 全部按出现位置绑定到自由 Talk；
  Opening/Event Talk 不能抵消 marker。
- “对话获取”证据通过 NPC `grants_evidence` 与证据 `acquisition.talk`
  双向绑定。
- active outline 中 14 处 `⚪` 全部进入 `testimony_required` 覆盖行，并
  绑定到获取位置的非空 `testimony_ids.content`。其中 13 个独立证言 ID；
  “Margaret 关于 Patrick 折返的证词”按大纲说明作为同一证言的正式摘要别名，
  不新增另一套事实。
- 当前共 22 条普通可获取/指证后可获取证言，全部以 `id + content` 内联；
  根级不再设置 `testimony_registry`。
- `narrative_continuity` 追踪每个连续场景包的入口、消费信息、出口和交接。
- Expose R1 `lie_source` 是普通 Talk 预先取得的谎言锚；R2 及以后是运行时
  动态退守，只登记在 `expose_lie_ids`，不进入普通 `testimony_ids`。每轮
  `usable_evidence` 仍必须进入疑点或 L5 身份链。
- `clue` 不允许 `analysis: true`；4701、4702、4703 在候选中修正为可分析产物 `item`。

## 校验

```powershell
python 剧情设计\Unit4\state\generate_state_candidates_v3.py
python 剧情设计\Unit4\state\validate_state_contract_v2.py
python -m unittest 剧情设计.Unit4.state.test_validate_state_contract_v2
```

Ruby 未安装，因此旧版 `validate_state_contract.rb` 本轮无法执行。候选 v2 使用可执行的 Python 校验器；正式替换时再决定是将 v2 规则回写 Ruby，还是以 Python 校验器作为新主入口。
