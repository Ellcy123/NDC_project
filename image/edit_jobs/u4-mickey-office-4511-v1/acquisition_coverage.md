# 4511 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop5
- Scene / Item: SC4042 / 4511「Mickey 定制钢笔」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环5_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop5_state.yaml`
- Acquisition event: 玩家检查 Mickey 私人书桌，与 4512 一起取得定制钢笔。
- Runtime item type: `3` / item
- Delivery class: `scene-pickup`
- Visible state: 黑色雕纹钢笔与笔帽分开放在私人书桌纸堆、绿台灯和刻字烟灰缸之间；不遮挡保险柜与 4512。
- Map stem: `SC4042_item_4511`
- Position: 从接受场景按私人书桌语境人工审计，裁切同时保留钢笔、纸堆、台灯与 `M.F.D.` 烟灰缸。
- Big stem: `SC4042_item_4511_big`
- Icon stem: `SC4042_item_4511_icon`
- Required delivery: Map + Position + landscape ordinary Big + 130×130 Icon
- Auxiliary gameplay assets: `identity_lock_4502_nib_macro.png`、`identity_lock_4502_test_stroke.png`
- Spoiler exclusions: 钢笔只证明书写工具特征，不单独证明作者、文本真实性或 Whale 身份。

## Information contracts

- Map-scene: 钢笔自然位于 Mickey 私人书桌上，和 4512 共存；场景原有灯、纸堆、保险柜及其他结构不漂移。
- Big-detail: 笔帽 `M.F.D.` 三字母与三个句点清晰可读；右侧笔尖有长期缺口；不附推理结论文字。
- Icon-presentation: 未盖帽钢笔与笔帽保持紧凑对角构图；130px 下仍可分辨黑色雕纹、金色五金和 `M.F.D.`。
- Identity-lock auxiliary: 笔尖微距明确显示右侧缺口；标准试写线在相同右转折处稳定出现断墨/变细后续笔。4514、4515 制作时必须复用这一断墨签名并补齐各自笔迹裁切。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 未通过：物件身份正确，但为深色摄影棚背景，不能直接交付透明 Big | 通过：`M.F.D.`、缺口笔尖及钢笔身份成立；确定性提取透明母图并输出 +10° landscape Big | — | accepted attempt 2 |
| Scene Map anchor | 通过：钢笔位于纸堆与台灯之间，与烟灰缸和保险柜不冲突；边界与零漂移检查通过 | — | — | accepted attempt 1 |
| Test stroke | 通过：三处同类右转折稳定出现 2–3 mm 断墨/变细重启，无解释文字 | — | — | accepted attempt 1 |
| Icon | 通过：独立透明母图保持紧凑钢笔+笔帽构图，确定性重建短左下阴影 | — | — | accepted attempt 1 |

## Accepted delivery

- Scene candidate: `02-scene-composition/final_scene_4511.png`
- Base verification: `final_verification.json` (`passed: true`)
- Map: `delivery/SC4042_item_4511.png`, 490×290
- Position: `1530,390,-3`
- Big: `delivery/SC4042_item_4511_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4042_item_4511_icon.png`, 130×130 RGBA
- Auxiliary nib macro: `identity_lock_4502_nib_macro.png`, 620×620
- Auxiliary test stroke: `identity_lock_4502_test_stroke.png`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
