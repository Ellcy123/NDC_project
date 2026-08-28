# 4315 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop3
- Scene / Item: SC4027 / 4315「古巴雪茄烟蒂」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环3_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop3_state.yaml`
- Acquisition event: 玩家先拍摄访客杯、湿杯垫与烟蒂的现场关系，再将烟蒂装袋取得线索。
- Runtime item type: `1` / clue
- Delivery class: `scene-pickup`
- Visible state: 深棕古巴雪茄烟蒂被按灭在访客杯湿杯垫旁，潮湿烟灰与水痕相接。
- Map stem: `SC4027_clue_4315`
- Position: 从最终验收原生分辨率场景推导，采用人工审计 Map 矩形保留访客杯关系。
- Big stem: `SC4027_clue_4315_big`
- Icon stem: `SC4027_clue_4315_icon`
- Required delivery: Map + Position + locked 620×620 clue Polaroid Big + 130×130 Icon
- Cross-loop identity lock: 4512 必须复用同一深棕茄衣、粗细、含咬位置、酒红双金圈卷标和中央黑菱形。
- Spoiler exclusions: 不出现 Mickey、Whale、牙齿示意、身份标签或枪手结论。

## Information contracts

- Map-scene: 烟蒂保持物理小尺寸；与访客杯、湿杯垫同框，燃烧端邻接水环，不能变成桌面中央展示物。
- Big-detail: 固定三层取证卡——现场关系、带比例尺标准侧视微距、装入玻璃纸袋的原物。
- Icon-presentation: 独立标准侧视烟蒂，燃烧端在左、烟嘴在右；酒红双金圈卷标和中央黑菱形保留，短左下阴影。
- Bite identity: 烟嘴右侧前段内陷、后段缺一枚完整压痕，其余压痕约三十度斜向；未来 4512 必须用本包身份母图作参考。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Cigar identity | 未通过：不透明棚拍背景，烟嘴破损过度、显得猎奇 | 通过：缩短为自然烟蒂，保留固定卷标和克制的斜向复合咬痕；确定性提取 Alpha | — | accepted attempt 2 |
| Scene Map anchor | 未通过：烟蒂与湿杯垫关系偏松，接触不够明确 | 通过：缩小并靠近访客杯，潮湿烟灰、湿杯垫与烟蒂形成同一桌面事件；边界和零漂移检查通过 | — | accepted attempt 2 |
| Big macro photo | 通过：标准侧视、比例尺和固定身份成立 | — | — | accepted attempt 1 |
| Big bagged photo | 通过：同一身份烟蒂置于 1920s 玻璃纸证物袋，无现代封口与文字 | — | — | accepted attempt 1 |
| Icon | 通过：由获批透明身份母图确定性归一、旋转并重建短左下阴影 | — | — | accepted deterministic derivative |

## Accepted delivery

- Scene candidate: `02-scene-composition/final_scene_4315.png`
- Base verification: `final_verification.json` (`passed: true`)
- Map: `delivery/SC4027_clue_4315.png`, 310×210
- Position: `1320,690,-3`
- Big: `delivery/SC4027_clue_4315_big.png`, 620×620 RGBA
- Icon: `delivery/SC4027_clue_4315_icon.png`, 130×130 RGBA
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
