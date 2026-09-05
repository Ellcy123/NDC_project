# U2 AVG 交付 · 2026-09-05

本批完成 6 个场景/状态的 PNG、分层 PSD、独立透明人物与过程文件。用户已认可前一批白盒并授权连续制作；本轮按用户要求不运行自动校验，不宣称机器质量闸门通过。使用内置 image_gen 逐人生成，实际 Photoshop 选取主体、人工区域修边和坐标合成；未写入 Unity。

| 场景 | PNG | PSD |
|---|---|---|
| 铁盒三人 Lula / Mickey / Zack | SC2591/SC2591_final.png | SC2591/SC2591_final.psd |
| 终局病房 Margaret / Foster / Emma / Zack | SC2691/SC2691_final.png | SC2691/SC2691_final.psd |
| Earl 日间忙碌 | SC2215_idle/SC2215_idle_final.png | SC2215_idle/SC2215_idle_final.psd |
| Earl 日间被打断 | SC2215_clicked/SC2215_clicked_final.png | SC2215_clicked/SC2215_clicked_final.psd |
| Earl 夜间沉默 | SC2515_idle/SC2515_idle_final.png | SC2515_idle/SC2515_idle_final.psd |
| Earl 夜间护手 | SC2515_clicked/SC2515_clicked_final.png | SC2515_clicked/SC2515_clicked_final.psd |

总览：delivery_overview.png。每个文件夹的 *_UI_review.png 使用实际 left_BG.png，按高等比缩放；右侧 UI 水平镜像。它是美术预览，不是引擎验收。

## 保留与例外

- 正式背景来自 D:/NDC/Assets/Resources/Art/Scene/Backgrounds/EPI02；生成的整张背景未直接作为交付背景。
- 病房原图已烘焙三个旧人物，先生成清除参考，再在原图上仅用有界多边形修补旧人物/投影区域；PSD 保留原图和独立修补层。该区域无法保证与未知空背景一致，需美术最终审阅。
- 人物保持局部画布等比映射，未液化、拉伸或统一缩小 10%。局部 cropBBox 和参考路径在各 *_handoff/local-generation-handoff.json 内。
- 原始抠图、修边透明 PNG 与含隐藏原图/原始 alpha 的 *_extraction.psd 均保留。Select Subject 漏选的账本、电话及腿部进行了局部恢复；错误带入的床单碎片已清除。
- Earl 日间两态复用下半身，夜间两态复用下半身和桌上道具，避免状态切换时跳动。日间账本/电话形态仍存在生成差异，不宣称像素级道具连续性。
- 3 人及以上保留前景背身 Zack；无人物肢体接触。铁盒由 Lula 拿着，不是递交瞬间。病房采用用户认可的站姿改编。
- TideWater 的两个白盒仍暂缓，缺少正式身份/角色卡；没有把占位人物冒充正式角色。

## 提示词规则记录

Image 1 为逐人白盒局部裁切，Image 2 为原场景光影，Image 3 为角色卡/既有正式角色资产；Foster 另附正式近景脸部图。每次只替换一个人物，锁定头部大小、关节姿态、脚点/离屏支撑和构图；背景仅供参考。保留 NDC 粗外轮廓、强线宽变化、块面头发、硬边色块、深黑阴影与 1928 noir 风格，禁止新增服装细节及微纹理。各请求文件记录角色动作，完整调用提示词保留在本任务工具历史。

状态：制作交付，待用户视觉审阅；自动校验按用户要求跳过，未进行引擎导入验收。
