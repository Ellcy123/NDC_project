# 4515 Acquisition Coverage

- Unit / Episode / Loop: Unit4 / EPI04 / Loop5
- Scene / Item: SC4042 / 4515「手写功业簿」
- Source design: `剧情设计/Unit4/证据设计/Unit4_循环5_证据美术资产.md`
- State source: `剧情设计/Unit4/state/loop5_state.yaml`
- Acquisition event: 玩家在 `interaction_letter_safe` 输入 `FTMWPTF` 后，4513—4516 原子性一次交付。
- Runtime item type: `3` / item
- Delivery class: `detail-only`
- Visible event state: 字母锁保险柜打开后四份材料一次进入持有状态；4515 不留在世界或 Type 7 容器中供玩家二次点击，库存 Big 与身份锁裁切承担阅读。
- Parent interaction: SC4042 letter-lock safe；无 Type 6 → Type 7 子物件点击链。
- Map stem / Position: 明确省略；不为自动交付物虚构世界坐标。
- Big stem: `SC4042_item_4515_big`
- Icon stem: `SC4042_item_4515_icon`
- Required delivery: landscape ordinary Big + 130×130 Icon
- Auxiliary gameplay assets: Morrison 页重点裁切、4515 笔迹局部裁切。
- Compatibility note: 当前预览 ItemStaticData 行仍带 `obtainMethod: manual` 和预填 Map stem，但与定稿 State 的原子自动交付冲突；本 staged patch 以 State 路线为准，正式配置未修改。

## Information contracts

- 账簿按 `NAME / CASE`、`RESULT`、`INTERFACE RETAINED`、`COST` 记录私人行动，不是财务账本。
- O'BRIEN、WEBB、MOORE、HARRISON、MORRISON、ROSA、MARY 七条均可定位。
- Morrison 行完整保留 `MEETING LOST CONTROL / SCENE CLOSED UNDER SUICIDE NARRATIVE / HANDEDNESS DISCREPANCY REMAINED / UPPER-LEVEL INDEPENDENT CLEARANCE`。
- Harrison 行分开保留 `UPPER-LEVEL INDEPENDENT CLEARANCE` 与 `PIERCE — SCENE / FILES`。
- Rosa 与 Mary 条目保留 `HEARING PRESERVED / RELEASE SECURED` 等真实救援结果。
- 不出现作者姓名、`I AM WHALE` 或完整自白；作者识别留给 4511 + 4514 + 4515 的身份锁。
- 4515 笔迹裁切保留为 4502 的后续输入；4514 当前因案号真源缺失暂缓，三栏最终对比卡未提前伪造。

## Attempt budget

| Asset | Attempt 1 | Attempt 2 | Attempt 3 | Result |
|---|---|---|---|---|
| Big semantic master | 语义与全部关键文字通过，但背景为烘焙棋盘，不能直接作为透明 Big | 精确保留内容；仍为烘焙棋盘，随后使用可审计阈值确定性提取透明母图，页面与字迹未重绘 | — | accepted attempt 2 after deterministic alpha extraction |
| Icon | 通过：由批准的透明账簿母图确定性归一，保留开本、七枚页签和深色皮面身份，重建短左下阴影 | — | — | accepted deterministic derivative |
| Auxiliary crops | 通过：只从批准母图裁切 Morrison 页和同一笔迹局部，不生成新文本 | — | — | accepted deterministic derivative |

## Accepted delivery

- Big: `delivery/SC4042_item_4515_big.png`, 1000×571 RGBA
- Icon: `delivery/SC4042_item_4515_icon.png`, 130×130 RGBA
- Morrison page: `delivery/identity_lock_4502_4515_morrison_page.png`, 1200×560 RGBA
- Handwriting crop: `delivery/identity_lock_4502_4515_handwriting_crop.png`, 860×340 RGBA
- Map / Position: intentionally omitted for atomic automatic grant
- Staged patch: `delivery/ItemStaticData.patch.json`
- Delivery verification: `delivery/delivery_verification.json` (`passed: true`)
- Official scene and formal ItemStaticData / SceneConfig were not modified.
