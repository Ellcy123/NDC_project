# 4513 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop5
- Scene / Item: SC4042 / 4513「1925 年内部接口接管记录」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环5_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop5_state.yaml`
- Acquisition event: 玩家在 `interaction_letter_safe` 输入 `FTMWPTF` 后，4513—4516 原子性一次交付。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Visible event state: 字母锁保险柜打开后四份材料一次进入持有状态；4513 不留在世界或 Type 7 容器中供玩家二次点击，详细内容通过库存 Big 展示。
- Parent interaction: SC4042 letter-lock safe；无 Type 6 → Type 7 子物件点击链。
- Map stem / Position: 明确省略；不为自动交付物虚构世界坐标。
- Big stem: `SC4042_item_4513_big`
- Icon stem: `SC4042_item_4513_icon`
- Required delivery: landscape ordinary Big + 130×130 Icon
- Compatibility note: 当前预览 ItemStaticData 行仍带 `obtainMethod: manual` 和预填 Map stem，但与定稿 State 的原子自动交付冲突；本 staged patch 以 State 路线为准，正式配置未修改。

## Information contracts

- `1925`、`W / WHALE` 及 `POLICE COORDINATION / SILVER MOON LIAISON / NON-CONTRACTUAL OBSTACLE HANDLING` 全部可读。
- 页首历史栏写明 `DONNELLY & ASSOCIATES — LEGAL BUSINESS SINCE 1919`，和 1925 接管日期分层表达。
- `TRANSFEREE` 只显示涂黑栏，不出现 Mickey 或任何接管者实名。
- 文件是内部机密登记表，不写给 Zack，也不出现 Charles、水源或未来行动。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 通过：日期、代号、三项职责、1919 历史栏和匿名接管栏成立；透明母图直接输出 -10° landscape Big | — | — | accepted attempt 1 |
| Dedicated Icon generation | 未通过：语义正确但透明棋盘被烘焙进 RGB，不能作为透明母图 | — | — | rejected attempt 1; deterministic fallback used |
| Icon deterministic derivative | 通过：从已批准 Big 透明母图归一，保留 1925、红色 W/WHALE 登记块与文件夹身份，并重建短左下阴影 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4042_item_4513_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4042_item_4513_icon.png`, 130×130 RGBA
- Map / Position: intentionally omitted for atomic automatic grant
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
