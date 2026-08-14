# Unit4 State 落表与特殊机制规范

> 日期：2026-08-14
> 当前审查范围：`剧情设计/Unit4/state/loop1_state.yaml` 至 `loop5_state.yaml`
> 机器契约：`剧情设计/Unit4/state/state_contract.yaml`
> 自动校验：`python 剧情设计/Unit4/state/validate_state_contract_v2.py`

## 1. 规范目的

本文件只规定 Unit4 State 进入配置阶段时各类字段的去向，以及两个特殊结构的运行合同。它不直接修改 Unity 代码，也不直接写入配置表 JSON。

Unit4 的剧情事实以 `canon_manifest.json` 登记的现行 v3 大纲为最高准则；候选 State 是对大纲的执行映射，不能反过来覆盖大纲。本规范解决的是“哪些字段能直接落表、哪些只供策划阅读、哪些必须由特殊适配器承接”。

## 2. 顶层字段去向

| State 顶层字段 | 分类 | 配置阶段处理 |
|---|---|---|
| `scenes` | runtime_source | 作为场景、NPC、证据取得位置的运行时来源 |
| `expose` | runtime_source | 作为指证轮次、谎言、可用证据和结果的运行时来源 |
| `doubts` | runtime_source | L1—L4 可进入普通疑点流程；L5 不得生成普通疑点 |
| `evidence_registry` | runtime_source | 作为物品与派生结论登记来源，并校验跨 Loop 继承 |
| `testimony_registry` | runtime_source | 作为正式证词登记来源，并校验跨 Loop 继承 |
| `opening` | structural | 用于开场结构与对白规划，不作为独立配置表整块写入 |
| `outline_coverage` | design_only | 逐条记录大纲必拍与 State 主落点，禁止漏拍、重复落地和无来源新增 |
| `narrative_continuity` | design_only | 记录场景包入口、消费信息、出口状态和下一个交接目标 |
| `player_context` | design_only | 供对白、知识边界与连续性审查，不直接落表 |
| `meta` | design_only | 供 Unit/Loop 识别和自检，不直接落表 |
| `doubt_progress` | design_only | 供策划核对普通疑点数量，不直接替代正式疑点条件 |
| `cross_loop_evidence` | design_only | 供策划查阅；实际保留规则以证据登记中的 `persistence` 为准 |
| `non_progress_investigation_records` | design_only | 进入调查日志表现，不写入普通 DoubtConfig |
| `special_mechanics` | special_adapter | 由 L5 身份锁专用适配器读取，禁止套入普通疑点或两槽合成 |
| `ending_sequence` | special_adapter | 由非 Loop 终幕适配器读取，继承 Loop5，不生成 Loop6 |

凡是五个 State 新增了未在 `state_contract.yaml.field_policy` 登记的顶层字段，自动校验必须失败。先补充去向裁决，再允许新增字段。

Expose R1 的 `lie_source` 可以是普通 Talk 中预先取得的 `collectible_lie_anchor`；当流程需要保证玩家先听见谎言时，它可以同时进入对应疑点 `condition`，L3 的 4063003 即属此例。R2 及以后由 NPC 在 Expose 中主动生成的 `dynamic_expose_lie` 仍不得预收集或挂入疑点。每轮 `usable_evidence` 则必须已由本 Loop 的疑点或 L5 身份链装载，避免游离指证证据。

## 3. 场景类型与表现标签

`scenes[].type` 只允许两个稳定值：

- `cutscene`：无自由调查的固定演出或过渡。
- `free_exploration`：允许调查、交互、对白、分析或指证的可控场景。

危机、分析、门锁、指证、过场余波等更细的设计意图统一写入 `design_tags`。例如：

```yaml
- id: 4022
  type: free_exploration
  design_tags: [investigation, timed_crisis, evacuation]
```

配置转换只能依据稳定 `type` 决定基础场景模式；`design_tags` 用于后续交互、美术、节奏和特殊脚本定位，不能把任意标签擅自解释成新的运行时场景枚举。

### 3.1 L3 爆炸前外部探索与柜门门控

L3 的阶段合同固定如下：

1. 4024 夜班电话交换台、4025 法院外圈调度台、4026 车站寄存区均属于爆炸前自由探索；4023 宅邸门外回收区属于爆炸后。
2. 4317 在 4025 取得，实体号码牌只刻 `214`，不得带车站、铁路或行李寄存标记。
3. 4026 场景在取得 4317 前已经开放，画面必须预先连续展示 210—220 号柜；不得给场景配置 `unlock_item: 4317` 或 `design_tags: [locked]`。
4. 4317 只挂在 `interaction_station_locker_214.required_item_ids`，用于打开 214 号柜并取得 4320。无钥匙时只返回柜门上锁反馈，不阻止进入场景。
5. 4063003 只由爆炸后 4023 的 Doris Talk 取得。4301 同时要求 4063003 与 4153001，保证玩家先听到谎言再看见疑点。
6. 爆炸事件使用 `ordered_story_event`，在宅邸危机材料、4024 Talk、4025 材料和 4026 的 4320 全部完成后才触发；这是一项剧情门槛，不是现实倒计时。

“场景开放”与“场景中的单个容器上锁”必须分别落表。转换器若只能把 `required_item_ids` 解释为场景级门锁，应视为阻塞错误，不能静默退回旧行为。

## 4. L5 身份锁运行合同

L5 暂采用方案 B。视觉布局、动效和具体控件仍可讨论，但以下玩法行为已经固定：

1. 三条证明链同时开放，玩家在每条链的固定槽位放入材料后主动确认提交。
2. 提交错误不消耗证据，也不清空已经完成的证明链。
3. 第一次错误只提示逻辑维度不成立；重复错误可提示缺少哪一类维度，但不直接揭示正确证据 ID。
4. 三条证明链全部完成后才解锁 Mickey Expose。
5. L5 不生成普通疑点，也不读取普通疑点进度作为门槛。

三条链分别回答：

| 链 | 证明问题 | 输出 |
|---|---|---|
| 4501 | Mickey 如何先控制法律资金接口、再接管 W / Whale | 4705 |
| 4502 | 功业簿是否由 Mickey 书写，以及其是否掌握参与者内部事实 | 4706、4707 |
| 4503 | Mickey 是否是 Harold 死前的近期访客 | 4708 |

身份锁属于专用玩法层，不得在落表时自动降级为普通 DoubtConfig，也不得用 CASE BOARD 的普通两槽合成替代。若未来决定更换玩法，必须先修改机器契约和 State，再调整适配器；不能只在配置表端静默改写。

## 5. 跨 Loop 材料保留

下列材料的来源登记均带有：

```yaml
persistence:
  scope: chapter
  reset_policy: retain_across_loops
  required_by:
    - identity_lock.chain_4501
```

实际 `required_by` 依材料用途变化。章节内循环重置不得删除这些材料：

| ID | 来源 | L5 用途 |
|---|---|---|
| 4112 | L1 | 4501 法律壳与身份演变 |
| 4153001 | L3 | 4503 电话到访窗口 |
| 4315 | L3 | 4503 现场访客遗留物 |
| 4416 | L4 | 4501 法律壳与身份演变 |
| 4418 | L4 | 打开字母锁保险柜 |

转换或运行时若只按当前 Loop 背包生成可用材料，必须显式合并 `scope: chapter` 且
`reset_policy: retain_across_loops` 的保留项。任何一项在 L5 前丢失，都应视为阻塞错误，不能靠 L5 临时重复发放补救。

## 6. L3 非进度调查记录

四条记录只用于保存玩家已经观察到、但不参与本轮指证门控的判断：

- 自杀现场矛盾
- 遗书与爆炸矛盾
- 煤气装置预装时序
- Pierce 调度可能性

统一表现合同为：

```yaml
presentation:
  channel: investigation_log
  blocking: false
  auto_unlock: true
  show_completion_toast: false
```

它们不得增加疑点分母、不得弹出“疑点完成”、不得阻塞 Doris Expose，也不得自动替玩家得出枪手或命令源结论。

## 7. 非 Loop 终幕

`ending_sequence` 仍属于 Loop5，运行合同固定为：

```yaml
runtime_contract:
  counts_as_loop: false
  inherit_loop: 5
  chapter_end_after: ending_4045
  next_unit_entry: enter_ohara_house
```

因此：

1. 不生成 Loop6。
2. 4043、4044、4045 继承 Loop5 的人物、证据和章节状态。
3. Unit4 只能在 `ending_4045` 完成后结束。
4. 最后一帧固定在 O'Hara 家门外。
5. Unit5 的第一个允许动作才是进入 O'Hara 家并开始屋内救援。

## 8. 校验与后续落表边界

执行：

```bash
ruby 剧情设计/Unit4/state/validate_state_contract.rb
ruby 剧情设计/Unit4/state/test_validate_state_contract.rb
```

两条命令均通过后，才可进入 State-to-table 或特殊机制适配阶段。

本轮只完成 State 与映射合同，不写入 `preview_new2/data/table/*.json`、`avg_editor_v2/data/table/*.json`、AVG 对话或 Unity 工程。
