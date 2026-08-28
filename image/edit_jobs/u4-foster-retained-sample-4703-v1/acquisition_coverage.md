# 4703 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop2
- Scene / Item: SC4013 / 4703「经化验的医院冷藏库留样试剂」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环2_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop2_state.yaml`
- Acquisition event: Foster 对 4118 医院官方冷藏留样完成受控化验，回装并二次封签后生成 4703。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Visible event state: 分析结果直接进入物品栏；玩家不在世界空间中定位或点击本组合证物。
- Map stem / Position: 明确省略；不为分析输出虚构世界坐标。
- Big stem: `SC4013_item_4703_big`
- Icon stem: `SC4013_item_4703_icon`
- Required delivery: landscape ordinary Big + 130×130 Icon

## Information contracts

- 原瓶明确为 `SACRED HEART HOSPITAL / COLD-STORAGE RETAINED SAMPLE`，批号 `SHC-28-B17`，样本号 `SHC-28-B17-RS`。
- Foster 二次封签、签名、受控托盘、两支 1920 年代反应管、结果卡与冷藏交接附件同框。
- 异常析出只出现在受控测试管中，原瓶本身保持普通外观，不提前让玩家靠肉眼判断风险。
- 结果限于 `IRREGULAR POTENCY`、`ABNORMAL DEGRADATION`、受控测试中异常析出，以及连续使用的严重低血糖反应和器官损伤风险。
- 不出现投毒、故意、凶手、Whitfield 主观知情、家庭责任或同配方结论；也不编造交接时刻、温度、日期和经手人。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 整体语义与物理层通过，但瓶签把 `SAMPLE` 误写成 `SAMPLR` | 定点修词未成功，仍为 `SAMPLR` | 将字段拆成两行，正确得到 `COLD-STORAGE / RETAINED SAMPLE`；确定性清除棋盘背景后定稿 | accepted attempt 3 |
| Icon | 由批准 Big 透明母图确定性归一，保留官方留样瓶、反应管、结果卡和交接附件身份 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4013_item_4703_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4013_item_4703_icon.png`, 130×130 RGBA
- Map / Position: intentionally omitted for analysis output
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
