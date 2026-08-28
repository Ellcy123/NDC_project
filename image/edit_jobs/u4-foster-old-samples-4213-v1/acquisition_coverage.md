# 4213 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop2
- Scene / Item: SC4013 / 4213「同配方药瓶封签组」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环2_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop2_state.yaml`
- Acquisition event: Foster 在法医实验室对话中交付已完成比对的两只废弃旧样本。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Visible event state: 对话演出直接取得；玩家不在实验室场景空间中定位或点击托盘。
- Map stem / Position: 明确省略；不为对话交付虚构世界坐标。
- Big stem: `SC4013_item_4213_big`
- Icon stem: `SC4013_item_4213_icon`
- Required delivery: landscape ordinary Big + 130×130 Icon

## Information contracts

- 左瓶旧患者标签为 `GIUSEPPE ROSSELLI`，另挂不同纸张的 `DEATH REG. SH-24-071` 吊签。
- 右瓶旧患者标签为 `BRIDGET O'SHEA`，另挂不同纸张的 `DEATH REG. SH-24-118` 吊签。
- 两只瓶只保留少量陈旧残迹与可比对封签结构；不画成装满药液，也不在瓶签上直接写配方一致结论。
- 画面没有 Isabel、`SHC-28-B17`、同批次或死因结论；旧样本不会错误继承 Loop2 现行批次身份。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 两时期标签关系与两个死亡编号正确；左患者姓名字形不够清楚，且有棕色生成背景 | 左姓名清楚修正为 `GIUSEPPE ROSSELLI`；内容通过，随后确定性清除烘焙棋盘背景 | — | accepted attempt 2 |
| Icon | 由批准 Big 透明母图确定性归一，保留两瓶、两张橙色吊签和木托盘身份 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4013_item_4213_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4013_item_4213_icon.png`, 130×130 RGBA
- Map / Position: intentionally omitted for dialogue grant
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
