# 4317 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop3
- Scene / Item: SC4025 / 4317「214号黄铜寄存柜钥匙」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环3_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop3_state.yaml`
- Acquisition event: 玩家点击法院外圈调度台旁的临时物品盘，直接取得钥匙。
- Runtime item type: `3` / item
- Delivery class: `scene-pickup`
- Visible state: 一把正常尺寸的旧黄铜钥匙自然平放在金属临时物品盘中。
- Parent container: 无；物品盘是基础场景直接热点，不建立 Type 6 / Type 7。
- Map stem: `SC4025_item_4317`
- Position: 必须从最终验收原生分辨率场景自动推导。
- Big stem: `SC4025_item_4317_big`
- Icon stem: `SC4025_item_4317_icon`
- Required delivery: Map + Position + landscape ordinary Big + 130×130 Icon
- Required readable content in Big / Icon: `214`
- Spoiler exclusions: 不出现车站、铁路、行李寄存、法院、姓名、Brennan、口供或柜内内容文字／徽记。

## Information contracts

- Map-scene: 只需读出“旧黄铜钥匙＋号码牌”的物件类别；钥匙保持普通尺寸、沿托盘透视自然平放，`214` 可作为唯一极小标记，但不得做成面向镜头的展示牌。
- Big-detail: 清楚表现 1920 年代扁钥匙、长期使用的黄铜磨耗、适配寄存柜锁孔的齿形，以及号码牌上唯一可读的 `214`。
- Icon-presentation: 独立高清姿态，保留与 Big 一致的钥匙结构和磨耗；顶部光源、短小左下阴影，130px 下轮廓和 `214` 均可辨。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Scene Map anchor | 未通过：钥匙在全场景游戏尺寸下只读成金色小点，物件类别不可辨 | 通过：真实比例、托盘透视与接触关系成立；全场景可辨，边界及最终零漂移校验通过 | — | accepted attempt 2 |
| Big semantic master | 未通过：物件与“214”正确，但返回图是烘焙白色棋盘背景、无 Alpha | 通过：保留身份候选，确定性提取并收边 Alpha；landscape +10° Big 校验通过 | — | accepted attempt 2 |
| Icon semantic master | 通过：身份、结构和“214”一致；确定性移除白底并重建短左下阴影；130px 与多尺寸预览通过 | — | — | accepted attempt 1 |

## Accepted delivery

- Scene candidate: `02-scene-composition/final_scene_4317.png`
- Base verification: `final_verification.json` (`passed: true`)
- Map: `delivery/SC4025_item_4317.png`, 385×255
- Position: `1208,708,-3`
- Big: `delivery/SC4025_item_4317_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4025_item_4317_icon.png`, 130×130 RGBA
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
