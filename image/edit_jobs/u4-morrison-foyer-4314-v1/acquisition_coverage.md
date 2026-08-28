# 4314 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop3
- Scene / Item: SC4027 / 4314「两只酒杯」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环3_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop3_state.yaml`
- Acquisition event: 玩家点击会客矮桌上的两只酒杯，拍照取得现场线索。
- Runtime item type: `1` / clue
- Delivery class: `scene-pickup`
- Visible state: 主人侧旧杯处于干燥惯用位置；访客侧酒杯保留残酒、未融碎冰、冷凝水与湿杯垫水环，两杯自然分开。
- Map stem: `SC4027_clue_4314`
- Position: 从最终验收原生分辨率场景自动推导。
- Big stem: `SC4027_clue_4314_big`
- Icon stem: `SC4027_clue_4314_icon`
- Required delivery: Map + Position + locked 620×620 clue Polaroid Big + 130×130 Icon
- Spoiler exclusions: 不出现访客姓名、Mickey、Whale、枪手、指纹、唇印鉴定或自动结论。

## Information contracts

- Map-scene: 两杯不并排陈列；主人杯靠单人椅一侧，访客杯靠沙发一侧，后者保留残酒和湿杯垫关系，并为 4315 烟蒂留出邻接空间。
- Big-detail: 低饱和匆忙取证照片同时呈现两杯位置差异；访客杯的残酒、未融碎冰和湿杯垫水环可辨。
- Icon-presentation: 独立两杯组合，空杯退后、访客杯前置；保持两杯分离轮廓，访客杯 amber 酒液、冰块和湿杯垫在 130px 下仍可读。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Scene Map anchor | 通过：两杯比例、透视、主人／访客位置与接触阴影成立；场景边界和零漂移检查通过 | — | — | accepted attempt 1 |
| Big clue photo | 通过：从验收场景确定性裁切、低饱和处理并写入锁定 Polaroid 模板 | — | — | accepted deterministic derivative |
| Icon semantic master | 通过：透明底双杯身份成立；确定性清理宽泛模型阴影并重建短左下阴影，130px 校验通过 | — | — | accepted attempt 1 |

## Accepted delivery

- Scene candidate: `02-scene-composition/final_scene_4314.png`
- Base verification: `final_verification.json` (`passed: true`)
- Map: `delivery/SC4027_clue_4314.png`, 587×322
- Position: `1032,627,-3`
- Big: `delivery/SC4027_clue_4314_big.png`, 620×620 RGBA
- Icon: `delivery/SC4027_clue_4314_icon.png`, 130×130 RGBA
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
