# 4212 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop2
- Scene / Item: SC4011 / 4212「Isabel 用过的密封药瓶」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环2_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop2_state.yaml`
- Acquisition event: Rosa 在办公室对话中把 Isabel 用过的密封药瓶直接交给 Zack。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Visible event state: 对话演出直接取得；玩家不在场景空间中定位或点击药瓶。
- Map stem / Position: 明确省略；不为对话交付虚构世界坐标。
- Big stem: `SC4011_item_4212_big`
- Icon stem: `SC4011_item_4212_icon`
- Required delivery: portrait ordinary Big + 130×130 Icon

## Identity lock

- Hospital: `SACRED HEART HOSPITAL`
- Program: `MILLER CHARITY PROGRAM`
- Patient: `ISABEL MARTINEZ`
- Dispensing No.: `IS-28-052`
- Lot: `SHC-28-B17`
- Fill marker: `INITIAL FILL`
- 4217 病历与 4214 缴费存根必须复用 `IS-28-052`。
- 4118 冷藏箱内药瓶与 4702 容量分析必须复用本瓶的瓶型、标签、批号与使用状态。

## Information contracts

- 琥珀色医院药瓶、磨损纸标签、旧封口和剩余液体清楚可见。
- 当前液面低于 `INITIAL FILL`，但不印具体毫升数字，避免抢先锁定尚未定稿的容量小游戏刻度。
- 标签只提供来源、患者和批次身份，不在瓶身上直接写出剂量结论。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 文本、瓶型、批号和液位关系正确，但带具体 mL 刻度，会提前锁死后续容量机制 | 删除具体 mL 数字，保留无数字刻线；内容通过，提取透明背景后定稿 | — | accepted attempt 2 |
| Icon | 由批准 Big 透明母图确定性归一；第一次仅安全边界超出 4px，缩小同一母图后通过，不计新的图像实验 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4011_item_4212_big.png`, 571×1000 RGBA
- Icon: `delivery/SC4011_item_4212_icon.png`, 130×130 RGBA
- Map / Position: intentionally omitted for dialogue grant
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
