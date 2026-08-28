# 4217 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop2
- Scene / Item: SC4011 / 4217「Isabel 的病历本」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环2_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop2_state.yaml`
- Acquisition event: Rosa 从随身旧包中取出 Isabel 的病历本并直接交给 Zack。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Visible event state: 对话演出直接取得；玩家不在场景空间中定位或点击病历本。
- Map stem / Position: 明确省略；不为对话交付虚构世界坐标。
- Big stem: `SC4011_item_4217_big`
- Icon stem: `SC4011_item_4217_icon`
- Required delivery: landscape ordinary Big + 130×130 Icon

## Information contracts

- `ISABEL MARTINEZ`、`THIRTEEN DAYS`、`DISPENSING NO: IS-28-052`、`LOT: SHC-28-B17`、`RED-LINE STOP` 同时可读。
- 逐日表恰好从 `DAY 1` 到 `DAY 13`，每行都有护士签注；没有第十四行。
- 不写死具体日历日期或毫升数，也不出现 Harrison、Whitfield、同批次结论或家属有罪／无罪判断。
- 本页只证明院方医嘱与登记内容；不把护士栏伪装成 Rosa 每次操作的独立证明。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 十三行、发放号与批号正确，但擅自锁定了 1928-10-14 至 10-26 的日历日期，且有实色背景 | 删除具体日期，仅保留十三日序列；内容通过，随后用保守外轮廓移除生成残留背景 | — | accepted attempt 2 |
| Icon | 由批准 Big 透明母图确定性归一，保留打开的病历夹、双页表格和侧边药房存根身份 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4011_item_4217_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4011_item_4217_icon.png`, 130×130 RGBA
- Map / Position: intentionally omitted for dialogue grant
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
