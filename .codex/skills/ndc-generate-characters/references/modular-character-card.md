# NDC 模块化高分辨率角色卡

## 适用条件

正式交付要求 2K/4K、一次生成整卡出现小人低清/漏视角/身份漂移，或用户明确要求分批生成时，使用本流程。草稿可以继续一键整卡，但不得把草稿直接插值放大后标为正式 4K。

## 模块清单

必须单独生成并保存：

1. `fullbody_front`：全身正面；
2. `fullbody_left`：全身严格左侧面，角色面朝画面左侧；
3. `fullbody_back`：全身背面；
4. `head_front`：头部正面；
5. `head_right`：头部严格右侧面，展示角色右脸；
6. `head_back`：头部背面，完整展示后脑发型、耳位和后领；
7. `shoe`：角色实际穿着批准鞋型的双脚与小腿特写，完整展示裤脚、脚踝衔接和两只鞋；
8. `details`：零至三张批准配饰、便携道具或有核对价值的服装构造特写。

每个模块使用纯白背景，不含文字、边框、标签、水印、地面或投影。全身模块从头顶到鞋底完整入镜，双臂自然下垂、双手空置。鞋部模块从小腿中段或膝下开始，展示角色正常站立时穿着批准鞋型的双脚；批准配饰和便携道具细节仍须为不与人物接触的孤立物件。

## 身份与设计锁定

重要新角色从已通过的通用风格全身定稿及其同源面部锚点派生；既有角色从当前批准的通用风格角色卡派生。参考图中的其他视角只用于恢复同一设计，不得重做角色。

每次只生成一个模块。提示词必须写明该模块的唯一视角和以下不变量：同一张脸、同一发型、同一体型/头身比（全身模块）、同一服装层级、同一配色、同一固定徽章或配饰位置、同一鞋型、同一选择性线宽层级与硬边色块画法。服装转折使用少量明确的角状硬折面，非受力大面保持安静近黑；轮廓和内部墨线必须按剪影焦点、遮挡、受力角、次要边界和内部折线分级，并以加重、收尖、断续与明确收笔形成节奏。头发保持大束块面并只保留少量宽带状方向笔触，不画逐根发丝。普通布料保持哑光，漆皮鞋、金属和珠宝可保留小面积尖锐高光。禁止增加或删除设计元素。

先批准 `fullbody_front`，再以身份源和已批准正面共同约束左侧与背面；先批准 `head_front`，再以身份源和已批准正面头部共同约束右侧与背面。若单张失败，只重做该张，其他批准模块冻结。

## 可复制模块提示词骨架

参考顺序：图 1 为批准角色卡或通用风格全身身份源；图 2 为同源面部锚点（头部模块或全身脸过小时）；图 3 为已批准的同组正面模块（生成后续视角时使用）。

```text
Use case: identity-preserve
Asset type: NDC modular character-card panel
Primary request: Generate only 【模块名称与唯一视角】 of the same approved character shown in the references.
Scene/backdrop: pure white void, no floor, no cast shadow.
Identity and design lock: preserve the exact face, hair silhouette, body type and head-to-body ratio when visible, garment layers, palette, fixed badge/accessory placement, and shoe design. Preserve the NDC general style: selective variable ink hierarchy, with heavier marks at focal silhouette turns, occlusions and load-bearing folds, medium or fine tapered garment edges, and selectively broken internal fold lines; visible swell, taper and decisive hand-drawn endings without making every edge equally heavy; grouped geometric hair masses with only a few broad ribbon-like directional marks and no individual strand rendering; a few decisive angular garment-fold wedges at load points; broad quiet near-black garment planes; hard structural edges with short controlled tonal bridges inside larger planes; deep grouped spot blacks; material-specific finish, mostly matte cloth with compact sharp highlights reserved for approved polished leather, metal or jewelry. No long airbrushed cloth transitions, rounded melted folds, decorative micro-wrinkles, uniformly weighted vector contours, or generic glossy 3D shading.
Composition: one isolated subject only, centered, maximum useful scale, generous clean margin, no cropping.
Constraints: no redesign; no beautification; no age change; no three-quarter view; no extra object; no text; no border; no watermark. For a full-body module, show head to soles, both arms naturally lowered, both hands empty and visible, no held or attached portable prop.
```

将 `【模块名称与唯一视角】` 分别替换为：

- `complete full-body strict front orthographic view`；
- `complete full-body strict left-side orthographic view, character facing canvas left`；
- `complete full-body strict back orthographic view`；
- `neutral head-and-upper-neck strict front orthographic view`；
- `neutral head-and-upper-neck strict right-profile orthographic view, showing the character's right face`；
- `head-and-upper-neck strict back orthographic view, showing the complete rear hair silhouette, both ear positions, and rear collar`；
- 鞋部使用 `both lower legs from mid-calf to soles, strict front design-detail view, the character naturally standing in and visibly wearing the approved shoes, both trouser hems and ankle-to-shoe construction visible`；
- 其他批准细节使用准确名称与方向。

## 分辨率与拼版

- 最终 4K：3840×2160；最终 2K：1920×1080。
- 模块生成时让主体占据最大可用面积。全身建议使用竖向输出，头部和细节建议使用方形或接近方形输出。
- 三张全身必须先裁白边，再统一主体总高度；头顶与脚跟在最终拼版中精确共线，之后人工检查肩、腰、膝和服装构造线。不得按各自原始像素尺寸靠底摆放，也不得在三视图上方留下无用途空白。
- 最终拼版只进行裁白边、等比例缩放和定位。禁止非等比例拉伸，禁止用图像模型再次合成或重绘。
- 使用 `scripts/compose_character_card.py --manifest <manifest.json> --out <output.png>`。脚本默认输出 3840×2160；加 `--width 1920 --height 1080` 输出 2K。
- 可加 `--qa-overlay-out <qa.png>` 输出带水平基准线的内部检查图。该图只用于验收，不得作为正式交付。

清单示例：

```json
{
  "fullbody": {
    "front": "panels/fullbody_front.png",
    "left": "panels/fullbody_left.png",
    "back": "panels/fullbody_back.png"
  },
  "head": {
    "front": "panels/head_front.png",
    "right": "panels/head_right.png",
    "back": "panels/head_back.png"
  },
  "shoe": "panels/shoe.png",
  "details": ["panels/detail_badge.png", "panels/detail_folder.png"]
}
```

相对路径以清单文件所在目录为基准。拼版后必须重新读取实际像素，并将最终图与所有模块一起保留。

## 逐张验收与返工

1. 方向是否为严格正投影，而非四分之三；
2. 是否仍是同一张脸、同一发型和同一年龄；
3. 体型、头身比、服装层级、配色、固定配饰与鞋型是否一致；
4. 全身是否完整、空手、双臂下垂；
5. 三视图头顶、肩、腰、膝与脚跟是否共线，左上是否存在无设计用途的空白；
6. 鞋部是否为角色实际穿着状态，是否同时看见裤脚、脚踝衔接与两只鞋；
7. 风格是否保持少量受力点硬折面、安静大黑面、按剪影/遮挡/受力/次要边界分级且带明确收笔的墨线、结构硬边与大面内部短距离受控色阶、成组几何头发、布料哑光，以及只服务于漆皮/金属/珠宝的紧凑高光；
8. 白底是否干净，是否有多余文字、投影、地台、边框或物件；
9. 失败只返回当前模块；模块均通过后，排版错误只返回拼版脚本。
