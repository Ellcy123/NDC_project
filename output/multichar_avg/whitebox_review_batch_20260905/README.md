# U2 白盒构图复审 · 2026-09-05

状态：构图候选，待用户审核；不是 whitebox-approved 或正式人物交付。使用内置图像生成工具。

本批 8 张：SC2691 病房、SC2591 铁盒、Earl 昼夜各两态、TideWater 两态。

- SC2591：依据 opening_l5_frankhome.json 的 201005009–011。Lula 已进入房间，双手持闭合铁盒；Mickey 追问；Zack 低手势缓和。不是开场首帧，不提前展示盒内文件。
- SC2691：依据 opening_l6_hospital.json 的 201006014–017。Foster 说明通宵检查，Emma 打开笔记本；Margaret 清醒坐在床边。Zack 采用用户此前要求的站姿变体（台本 003 原为坐下）；站在床架外侧前景。这是演出站姿改编，需要本轮视觉审核。
- Earl：依据 U2_场景人物缺口与姿态需求_20260827.md 3.5 节。日间电话和账本工作；夜间沉默和护手。坐姿由工作位及剧情支持。
- TideWater：依据上述需求 3.6 节。面向吧台方向处理事务，文件保持本人持有；点击转头。178cm 只是延续上一批的空间占位假设，不是 canonical 身高；身份设定仍待补齐。

身高参考：Unit1/Characters/zack.md 180；emma.md 170；Unit2/Characters/mickey.md 183；lula.md 165；margaret.md 165；foster.md 170；earl_hirsch.md 164。旧审计中的较旧身高数值不沿用。

病房及其他场景都保留原有空间构成供审图；生成白盒不是原背景像素锁定的正式合成。正式生产仍需校准回原图、逐角色隔离白盒、头身测量、场景尺寸及 UI 机器验证。

review_all.png 为整体构图；review_UI.png 叠加实际 left_BG.png，右侧版本水平镜像并按图高等比缩放，供视觉检查。当前不宣称已完成引擎裁切或全部量化质量闸门。

所有候选均保留独立 PNG；旧版和 Unity 资源未替换。
