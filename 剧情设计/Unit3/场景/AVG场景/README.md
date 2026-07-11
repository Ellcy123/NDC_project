# Unit3 AVG 场景目录

本目录只放需要独立画面产出的纯 AVG / 过场场景。AVG 场景的资源形态是“人物 + 场景 + 构图合成的完整剧情图”，不承载自由探索中的可点击 NPC、证据点或物件挂载。

如果某段指证后内容在游戏内默认是黑屏对白、两人聊天或普通 NPC 对话，不在本目录建 AVG 场景文件。

文件命名格式：

```text
AVG_L{loop}_{剧情位置}_{地点名}_{剧情用途}.md
```

配置场景ID、对应地点参考、ChapterConfig / ArtAssetConfig 用途写在文件正文里，不放进文件名。

## 当前文件

| 文件 | 配置场景ID | 内部英文名 | 用途 |
|---|---:|---|---|
| AVG_L1_开篇_Mickey车内_早报引案.md | 3017（暂定） | `u3_l1_open_car_news` | L1 开篇第一段，Emma 用早报引出 Thomas 坠楼新闻 |
| AVG_L1_开篇_Zack侦探事务所_正式委托.md | 3018（暂定） | `u3_l1_open_office_case` | L1 开篇第二段，Mickey 正式委托 Zack / Emma 调查 |
| AVG_L2_开篇_公寓楼下_回到现场.md | 3291（暂定） | `u3_l2_open_apartment` | L2 开篇，带着 Mary 脚印线索回到公寓楼 |
| AVG_L3_开篇_公寓楼内_扩大搜查.md | 3391（暂定） | `u3_l3_open_hall_search` | L3 开篇，决定扩大搜查公寓楼其他住户 |
| AVG_L4_开篇_Zack侦探事务所_Foster来电.md | 3491（暂定） | `u3_l4_open_office_call` | L4 开篇，Zack/Emma 回事务所复盘时 Foster 来电通知油痕检测仪到位 |
| AVG_L4_衔接_市政厅门口_判决方案.md | 3492（暂定） | `u3_l4_bridge_cityhall` | L4 指证后衔接，Mickey 与 Harrison 说明判决方案 |
| AVG_L4_衔接_报社_采访MaryHelen.md | 3493（暂定） | `u3_l4_bridge_newsroom` | L4 指证后衔接，Emma 采访 Mary 与 Helen |
| AVG_L5_开篇_Mickey办公室_Bernard线起点.md | 3591（暂定） | `u3_l5_open_mickey_bernard` | L5 开篇，Mickey 派 Zack / Emma 继续查 Bernard |
| AVG_L5_衔接_湖滨信托银行大厅_Charles带走Emma.md | 3592（暂定） | `u3_l5_bank_charles_emma` | L5 剧情衔接，Charles 在银行大厅带走 Emma，Zack 独自进入 Bernard 办公室 |
| AVG_L6_开篇_Mickey办公室_控辩前.md | 3691（暂定） | `u3_l6_open_mickey_trial` | L6 开篇，Mickey 提醒必须拿出事实证据 |
| AVG_L6_结局_Zack侦探事务所_EmmaMaryHelen.md | 3692（暂定） | `u3_l6_end_office_group` | L6 结尾衔接，Emma 回来后与 Zack 交谈，Mary 与 Helen 随后登门道谢 |
| AVG_L6_结局_事务所门口街道_Leonard送文件.md | 3693（暂定） | `u3_l6_end_street_leonard` | L6 结尾衔接，送别 Mary / Helen 后，Leonard 在街边交出内部文件 |

## 使用边界

- 开篇 AVG：通常挂 ChapterConfig.openingScene。
- 衔接 / 结局 AVG：用于明确需要独立画面的剧情段。
- 探索场景：仍看 `../探索场景/`，不要因为某地点在 AVG 中出现就拆 Loop 版本。
- 突发事件动态漫画：仍看 `../../美术需求/Unit3_AVG突发事件动态漫画.md`，不作为 AVG 场景文件。
- 指证背景 topBg：优先复用探索或 AVG 资产；只有独立画面需求明确时才单独补。

## 后续配置说明

这些文件是美术与配置前的场景需求拆分，配置场景ID均为暂定。正式落配置时再和 SceneConfig / ChapterConfig / ArtAssetConfig / Talk 文件名对齐。
