# 4214 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop2
- Scene / Item: SC4015 / 4214「圣心医院慈善项目采购与发放记录」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环2_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop2_state.yaml`
- Acquisition event: Mickey 在法院会客室对话中交付医院提交法院的项目卷宗副本。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Visible event state: 对话演出直接取得；玩家不在场景空间中定位或点击合订本。
- Map stem / Position: 明确省略；不为对话交付虚构世界坐标。
- Big stem: `SC4015_item_4214_big`
- Icon stem: `SC4015_item_4214_icon`
- Required delivery: landscape ordinary Big + 130×130 Icon

## Information contracts

- `PURCHASE ORDER → HOSPITAL INTAKE → RETAINED SAMPLE / CHARITY DISPENSING` 四段链条清楚可读。
- `SHC-28-B17` 同时出现在采购、入库和慈善发放；官方留样编号为 `SHC-28-B17-RS`，Isabel 发放号为 `IS-28-052`。
- `PROGRAM LEAD`、`PROCUREMENT EXECUTION`、`INTAKE RECEIPT`、`CHARITY DISPENSING` 四个独立责任栏各自登记 `WHITFIELD`，没有第五个重复栏。
- 左页页码 `18`、右页页码 `20`，目录明确写 `PAGE 19 — SPECIAL PROCUREMENT APPROVAL`；装订中只见缺页残口，不出现第十九页正文、批准签字或更高层身份。
- 配方核对只连接官方留样和 Isabel 发放，不扩展到另外六名历史儿童。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 链条、批号、缺页结构成立，但只有三个 Whitfield 责任栏 | 补齐四个责任栏；左侧辅助页签把 PURCHASE 拼错 | 定点修正左侧 `PURCHASE ORDER` 页签，所有关键信息保持；确定性清除棋盘背景后定稿 | accepted attempt 3 |
| Icon | 由批准 Big 透明母图确定性归一，保留打开的 18／20 页合订本与中间缺页身份 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4015_item_4214_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4015_item_4214_icon.png`, 130×130 RGBA
- Map / Position: intentionally omitted for dialogue grant
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
