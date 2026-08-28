# 4211 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop2
- Scene / Item: SC4011 / 4211「医院配发红线注射器与十三日封签药盒」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环2_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop2_state.yaml`
- Acquisition event: Rosa 在 Zack 事务所的对话中交付注射器与药盒。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Map stem / Position: 明确省略。
- Big stem: `SC4011_item_4211_big`
- Icon stem: `SC4011_item_4211_icon`

## Information contracts

- 注射器红线与不可移动金属止动环同框，止动环为实体结构。
- 药盒恰好十三格，编号 1–13，全部有开启痕迹。
- 外沿指纹只表现接触痕迹，不表现十三枚日期认证章。
- 与 4212 使用同一 Sacred Heart / Miller 项目视觉体系。
- 不写毫升数、第十四针结论或责任判断。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 十三格成立，但上排重复 4、缺 5 | 仅修正第五格为 5，其余合同保持 | — | accepted attempt 2 |
| Icon | 由批准 Big 透明母图确定性归一 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4011_item_4211_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4011_item_4211_icon.png`, 130×130 RGBA
- Map / Position: intentionally omitted for dialogue grant
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json`
- Official scene and formal ItemStaticData / SceneConfig were not modified.
