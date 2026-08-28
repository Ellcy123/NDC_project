# 4516 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop5
- Scene / Item: SC4042 / 4516「Tidewater 南区商业开发执行卷」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环5_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop5_state.yaml`
- Acquisition event: 玩家在 `interaction_letter_safe` 输入 `FTMWPTF` 后，4513—4516 原子性一次交付。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Visible event state: 字母锁保险柜打开后四份材料一次进入持有状态；4516 在 L5 保持整卷封存，玩家不在办公室内点击或拆出底衬附件。
- Parent interaction: SC4042 letter-lock safe；无 Type 6 → Type 7 子物件点击链。
- Map stem / Position: 明确省略；不为自动交付物虚构世界坐标。
- Big stem: `SC4042_item_4516_big`
- Icon stem: `SC4042_item_4516_icon`
- Required delivery: landscape ordinary Big + 130×130 Icon
- Continuity boundary: 4518、4519 只在离开四十二层后的车内二次整理中出现；本包不含隐藏附件正文。
- Compatibility note: 当前预览 ItemStaticData 的 4516 路径字段为空且路线未完成；本 staged patch 仅提供按 State 判定的自动交付 Big/Icon，正式配置未修改。

## Information contracts

- 外卷只使用 Tidewater 抬头，显示 `SOUTH SIDE COMMERCIAL DEVELOPMENT / EXECUTION FILE`。
- `CONTIGUOUS TRACT REQUIRED BEFORE WORLD'S FAIR PLAN IS PUBLIC` 和时间压力清楚可读。
- 职责分工保留 `BANK DEBT / LAKESHORE FUNDING / VALUATION / TIDEWATER PROPERTY INTAKE / W / WHALE — LEGAL / POLICE OBSTACLES`。
- `CORE HOLDOUT: O'HARA — UNRESOLVED` 清楚可读。
- 不出现 Miller 名称、事故基金印章、分赃账户、Sean、水源点或 4518/4519 正文。
- 硬底衬与侧边暗夹保留为后续二次整理的物理伏笔，但 L5 初见不露纸、不露字。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 通过：Tidewater 外卷、连续地块目标、职责分工、O'Hara 拒售及隐藏附件边界全部成立；透明母图直接输出 -10° landscape Big | — | — | accepted attempt 1 |
| Icon | 通过：由批准 Big 透明母图确定性归一，保留深蓝外卷、黄铜夹、TIDEWATER 和执行页身份，重建短左下阴影 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4042_item_4516_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4042_item_4516_icon.png`, 130×130 RGBA
- Map / Position: intentionally omitted for atomic automatic grant
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
