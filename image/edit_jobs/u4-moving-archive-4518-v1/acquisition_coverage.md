# 4518 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop5 ending
- Scene / Item: SC4044 / 4518「Sean O'Malley 特殊处置页」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环5_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop5_state.yaml`
- Acquisition event: 行驶中的法院档案车内，Zack 借身体、肩包与昏暗环境遮挡，独自从 4516 暗部封夹取出 4518 并立即扣下。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Visible event state: 剧情演出直接取得；玩家不在世界空间或 Type 7 容器中定位／点击本页，Emma 与 Watts 在 U4 不知道其存在。
- Parent container: 4516 hidden backing clamp；为叙事发现，不建立自由探索 Type 6 → Type 7 链。
- Map stem / Position: 明确省略；不为 cutscene grant 虚构世界坐标。
- Big stem: `SC4044_item_4518_big`
- Icon stem: `SC4044_item_4518_icon`
- Required delivery: landscape ordinary Big + 130×130 Icon
- Compatibility note: 当前预览 ItemStaticData 行仍写 `obtainMethod: manual` 和预填 Map stem；本 staged patch 以定稿 State 的 cutscene grant 为准，正式配置未修改。

## Information contracts

- `DATE: 1912`、`SUBJECT: SEAN O'MALLEY`、`SEPARATE FROM WORK CREW`、`HANDLE HIS OBJECTION BEFORE ACCIDENT RECORD IS COMPLETED` 全部可读。
- Tidewater 工程体系印章、`CHARLES MILLER` 打字授权栏与老化正式签名、侧边 Miller 项目委员会内部传阅章分层可读。
- 正文保持行政委婉语，不出现 KILL、BODY、DUMP、MURDER、EXECUTE、DEATH 或具体方法／执行人／弃尸信息。
- 单页只证明 Sean 被隔离并在事故记录完成前要求处理异议，不提前公布完整事故真相。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 通过：1912、Sean、两条处置指令、Tidewater 工程章、老 Charles 签名和 Miller 传阅章全部成立；透明母图直接输出 +10° landscape Big | — | — | accepted attempt 1 |
| Icon | 通过：由批准 Big 透明母图确定性归一，保留单页、红色 SPECIAL HANDLING、蓝色 Tidewater 章和签名身份，重建短左下阴影 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4044_item_4518_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4044_item_4518_icon.png`, 130×130 RGBA
- Map / Position: intentionally omitted for cutscene grant
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
