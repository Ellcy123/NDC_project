# 分类与产物规则

## 两条独立分类轴

### 资产性质 `semantic_class`

| 值 | 含义 | Big / Icon 规则 |
| --- | --- | --- |
| `ordinary_prop` | 普通实体道具或普通证物 | `ordinary_big`；Icon 按当前配置与玩法需要 |
| `photo_clue` | 游戏中按照片线索呈现的线索 | 必须 `clue_big_620x620`；Icon 按当前配置，不能因取得方式改变照片规格 |
| `environment_narrative` | 环境观察、痕迹或不可收集叙事物 | `environment_big`；不配置 Icon |
| `minigame_only` | 不进入 ItemStaticData 的玩法页、组件或结果 | 按玩法实际页面／状态／组件列角色，不套普通 Big/Icon/Map |
| `unresolved` | 当前来源不能确定 | 写明冲突来源、受影响角色与恢复条件 |

实体是“照片”不等于 `photo_clue`；照片线索的判定来自当前 `name/type`、剧情玩法和配置语义。反之，线索由 NPC 交付、自动生成或场景拾取，都不改变其照片线索 Big 规格。

### 取得路线 `acquisition_route`

| 值 | 判定 | 必需角色 |
| --- | --- | --- |
| `scene-pickup` | 玩家在基础探索场景直接看见并点击 | `scene_original`、`carrier_without_prop`、`pickup_layer`、`scene_before_pickup`、`map_hotspot`、`xy`，以及语义所需 Big/Icon |
| `container-state` | 玩家先打开抽屉、柜、箱、袋等二级容器再点击内容 | Type 6 容器入口、Type 7 打开视图、菜单预览、子道具 Map/XY，以及语义所需 Big/Icon |
| `detail-only` | 对话、分析、记忆、自动授予或演出结果；玩家不在世界场景寻找 | 不建立世界 Map/XY；保留实际 Big/Icon/演出态及无 Map 理由 |
| `environment` | 玩家观察背景或状态物，不作为背包物品取得 | 真实环境 Map/XY、环境 Big；无 Icon |
| `minigame-only` | 玩法内部页面／组件／结果 | 只列玩法实际角色；不得发明 ItemStaticData Map/Icon |
| `unresolved` | 取得事件冲突或缺失 | 未决问题非空，阻断受影响角色，不阻断无关项 |

不要用文件名、空 `mapSpritePath`、旧表里的 pickup 字样或现有文件数量判断取得路线。应读取实际事件、SceneConfig 与 ItemStaticData 链。

## 直接拾取重建合同

直接拾取的最小可核验链为：

```text
original_scene → carrier_without_prop → pickup_layer → scene_before_pickup
```

- `pickup_layer` 只含目标道具及其归属阴影；
- `carrier_without_prop` 保留承载体和承载体自身阴影；
- `scene_before_pickup` 必须由承载体场景与拾取层重建到原场景；
- Map/XY 绑定当前审核通过的原生分辨率，不能根据预览或肉眼猜坐标；
- 普通 Type 7 子菜单项是例外，按容器链检查，不套直接拾取四态。

## 人工动作分类

每个必需角色的 `manual_action` 只使用：

- `NONE`：当前有效资产已满足该角色，或此角色不适用；
- `SOURCE_RESEARCH`：缺权威来源或当前版本；
- `CONTENT_AUTHORING`：需人工确定可读文字、案号、日期、数量、笔迹等内容；
- `CREATE`：需人工制作新的视觉资产；
- `REPAIR`：现有源身份正确，但需局部修复；
- `ALPHA_EXTRACT`：需非生成式抠图／透明边缘处理；
- `PLACE_IN_SCENE`：需承托、比例、遮挡、光影与场景状态处理；
- `BUILD_MENU_STATE`：需 Type 6/7、菜单或演出状态；
- `HOTSPOT_XY`：需 Map、路径和原生分辨率坐标；
- `REVIEW`：需真实视觉／技术复核；
- `REPACK`：内容已存在但未按当前节点／命名／目录交接；
- `INTEGRATE`：图像完成，仍待工程接入。

任何非 `NONE` 动作都必须至少有一个 `human_task`。任务写“怎么做”和“怎样算完成”，不能只写状态名。

## 内容与验收

- A/H0：身份、日期、案号、数量、可读文字、状态、组件数、Alpha、Map/XY、阴影归属等零容差。
- B/H1：列出允许差异，默认关键可见内容。
- C/H2/H3：只允许画风范围内自由；H3 必须说明低显著依据。
- 地图场景只承担发现和物类识别，详细正文留在 Big；除非它本身是场景中必须读到的环境标识。
- 图像状态与工程接入分列；已完成 Big 不能抵扣缺失 Map，已完成 Map 也不能证明 Big 或 Icon 合格。
