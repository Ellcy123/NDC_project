# 4215 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop2
- Scene / Item: SC4015 / 4215「缺失的第十九页（副本）」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环2_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop2_state.yaml`
- Acquisition event: Mickey 在法院会客室对话中把执行层项目批准副本的缺页部分单独交给 Zack 核对。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Visible event state: 对话直接取得；没有世界空间点击步骤。
- Map stem / Position: 明确省略。
- Big stem: `SC4015_item_4215_big`
- Icon stem: `SC4015_item_4215_icon`

## Information contracts

- 目录准确写 `PAGE 19 — BOARD SPECIAL PROCUREMENT APPROVAL`。
- 物理页序清楚显示 `18` 后直接是 `20`，中间连续装订孔内只有被抽走纸页的残边。
- 边界说明只写 `PAGE 19 NOT PRESENT IN EXECUTION COPY / ORIGINAL SIGNATURE NOT AVAILABLE`。
- 不出现第十九页正文、签字人、批准者剪影、Miller 或 Whitfield 高亮，也不暗示谁拿走了该页。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 目录、18→20 页序、装订缺口和证明边界一次成立；确定性清除棋盘背景后定稿 | — | — | accepted attempt 1 |
| Icon | 由批准 Big 透明母图确定性归一 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4015_item_4215_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4015_item_4215_icon.png`, 130×130 RGBA
- Map / Position: intentionally omitted for dialogue grant
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
