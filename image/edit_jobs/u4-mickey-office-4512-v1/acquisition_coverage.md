# 4512 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop5
- Scene / Item: SC4042 / 4512「Mickey 的半支古巴雪茄」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环5_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop5_state.yaml`
- Acquisition event: 玩家检查 Mickey 私人书桌上的刻字烟灰缸，取得其中的半支古巴雪茄。
- Runtime item type: `3` / item
- Delivery class: `scene-pickup`
- Visible state: 深色石质私人烟灰缸位于书桌灯与字母锁保险柜之间，内放半支雪茄；前沿低调刻有 `M.F.D.`。
- Map stem: `SC4042_item_4512`
- Position: 从最终验收原生分辨率场景推导，人工审计 Map 矩形保留私人书桌、台灯与保险柜的所有权语境。
- Big stem: `SC4042_item_4512_big`
- Icon stem: `SC4042_item_4512_icon`
- Required delivery: Map + Position + landscape ordinary Big + 130×130 Icon
- Auxiliary gameplay asset: `identity_lock_4503_cigar_comparison.png`, 1200×600
- Spoiler exclusions: 不写“杀人者”、Whale、Morrison 访客结论或牙齿唯一鉴定。

## Information contracts

- Map-scene: 烟灰缸自然放在私人书桌上，靠近绿台灯与字母锁保险柜；物件小而可点，不覆盖原有保险柜和灯。
- Big-detail: `M.F.D.` 三字母与三个句点清晰可读；半支雪茄保留 4315 的茄衣、粗细、酒红双金圈卷标、中央黑菱形和右侧复合咬痕。
- Icon-presentation: 烟灰缸与半支雪茄保持同一身份组合；130px 下仍能读出深色石质轮廓、酒红卷标和 `M.F.D.`。
- Identity-lock comparison: 左侧为 4315 现场烟蒂，右侧为 4512 私人来源样本；按同一侧视尺度比较品牌、直径、含咬位置和复合变形，不加答案文字。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 通过：烟灰缸、半支雪茄、固定身份与精确 `M.F.D.` 成立；确定性移除烘焙棋盘底并输出 -10° landscape Big | — | — | accepted attempt 1 |
| Scene Map anchor | 通过：烟灰缸位于灯与保险柜之间，比例、透视、灯光与接触阴影成立；边界和零漂移检查通过 | — | — | accepted attempt 1 |
| Comparison side view | 通过：复用 4315 身份特征，生成较长的半支样本并完成无文字并排对照 | — | — | accepted attempt 1 |
| Icon | 通过：由 Big 透明母图确定性归一并重建短左下阴影 | — | — | accepted deterministic derivative |

## Accepted delivery

- Scene candidate: `02-scene-composition/final_scene_4512.png`
- Base verification: `final_verification.json` (`passed: true`)
- Map: `delivery/SC4042_item_4512.png`, 470×320
- Position: `1720,300,-3`
- Big: `delivery/SC4042_item_4512_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4042_item_4512_icon.png`, 130×130 RGBA
- Auxiliary comparison: `identity_lock_4503_cigar_comparison.png`, 1200×600 RGB
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
