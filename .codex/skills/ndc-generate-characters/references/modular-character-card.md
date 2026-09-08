# NDC 模块化高分辨率角色卡

## 适用条件

只有用户明确要求 4K、独立模块或分批生成并拼版时，使用本流程中的对应范围。单模块请求只进入该模块的来源、生成和验收，不自动扩大到整卡拼版。普通角色卡即使要正式使用，也默认采用 `prompt-library.md` 的锁定整卡提示词一次生成；不得仅因“正式”“高清”“最终”或一次生成存在可技术修复的问题就自动改走模块化。普通整卡不得直接插值放大后标为 4K。

4K整卡目标固定3840×2160；请求整卡拼版而未要求4K时按约定尺寸，未定时为既有2K 1920×1080。单模块按其当前约定或已批准同组模块规格交付，不套整卡横画布。触发、累计预算、视角字段与DAG见 [production-budgets-and-dependencies.md](production-budgets-and-dependencies.md)；其中整卡尺寸默认只作用于整卡输出。

## 模块清单

下列是完整模块库，不是每个任务的必交清单。只要求交付本次明确请求的模块；已有通过模块冻结并引用，不为查验重制。用户要求整卡拼版时才准备整卡所需全套模块。进入本次范围的模块分别保存；同角度头部可按下文复用合格原像素锚点而不重复生图：

1. `fullbody_front`：全身正面；
2. `fullbody_left`：全身严格左侧面，角色面朝画面左侧；
3. `fullbody_back`：全身背面；
4. `head_front`：头部正面，可直接取合格同源正面锚点；
5. `head_right`：严格展示角色解剖右脸；另记录画面朝向，不能由 `fullbody_left` 名称推定是同一可见面，亦不得镜像替代；
6. `head_back`：头部背面，完整展示后脑发型、耳位和后领；
7. `shoe`：角色实际穿着批准鞋型的双脚与小腿特写，完整展示裤脚、脚踝衔接和两只鞋；
8. `details`：零至三张批准配饰、便携道具或有核对价值的服装构造特写。

每个模块使用纯白背景，不含文字、边框、标签、水印、地面或投影。全身模块从头顶到鞋底完整入镜，双臂自然下垂、双手空置。鞋部模块从小腿中段或膝下开始，展示角色正常站立时穿着批准鞋型的双脚；批准配饰和便携道具细节仍须为不与人物接触的孤立物件。

## 身份与设计锁定

重要新角色从已通过的通用风格全身定稿及其同源面部锚点派生；既有角色从当前批准的通用风格角色卡派生。参考图中的其他视角只用于恢复同一设计，不得重做角色。

每次只生成一个模块。提示词必须写明该模块的唯一视角和以下不变量：同一张脸、同一发型、同一体型/头身比（全身模块）、同一服装层级、同一配色、同一固定徽章或配饰位置、同一鞋型、同一选择性线宽层级与硬边色块画法。服装转折使用少量明确的角状硬折面，非受力大面保持安静近黑；轮廓和内部墨线必须按剪影焦点、遮挡、受力角、次要边界和内部折线分级，并以加重、收尖、断续与明确收笔形成节奏。头发保持大束块面并只保留少量宽带状方向笔触，不画逐根发丝。普通布料保持哑光，漆皮鞋、金属和珠宝可保留小面积尖锐高光。禁止增加或删除设计元素。

### 全身头部细节锚点

生成当前请求的正式全身模块时，头部原始像素必须足以核对该视角实际可见的身份结构。正面核对脸型、眉眼关系、发际线等；侧面按实际可见面核对；背面核对后脑发型、耳位、后领和相关服装结构，正脸五官记为本图不可见并绑定批准正面身份依据，不要求回头或虚构眼鼻检查。这不是靠最终拼版缩小后“看起来清楚”来判断。当前全身模块通过后，保留不插值、不放大的同源头部裁片及原始尺寸作为过程证据；未请求独立头部时不因此新增正式头部交付。

后续头部三视图优先采用对应的已批准全身头部锚点：锚点原生清晰度已满足最终头部区时，可直接裁白边、等比例缩小后作为头部模块；若仅缺清晰度，可把该确切裁片作为锁定输入做一次单目的清晰度补充。补充只能增强可读性，必须逐项保留脸型、五官关系、发型轮廓与颜色、发际线、耳位、年龄、衣领和唯一视角；不得借“补细节”重画成另一个同类人。直接裁片或补充均须在回执中记录来源、原始尺寸、是否插值、以及身份逐项比对结果。补充失败时只返工头部清晰度阶段，不得改写已通过全身模块。

先批准 `fullbody_front`，再以身份源和已批准正面共同约束左侧与背面。正面头部依赖正面，后脑依赖背面，鞋和批准细节依赖批准身份及正面；左侧失败不阻断无依赖模块。`head_right` 先查已批准锚点是否展示同一右脸；有则原像素复用或一次清晰度补充，无则从批准身份与正面生成右脸新角度，记为艺术派生并消费其模块预算，不冒充裁片或镜像。单张失败只重做该张并使实际后代失效，其他通过模块冻结。

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

## 分辨率与拼版（仅请求整卡输出时）

单模块交付跳过本节的三视图对齐、整卡布局、拼版和card专用机械/回执工具；只核验自己的实际规格、完整主体、无非等比拉伸/低清放大、当前背景与边缘、阶段视觉记录及持久job当前依赖。不能把单背面PNG标为card来通过旧工具，也不补造未请求的其他模块。

- 最终 4K：3840×2160；最终 2K：1920×1080。
- 模块生成时让主体占据最大可用面积。全身建议使用竖向输出，并在原始像素中保留足够大的可检验头部；头部区优先采用已通过全身的同源头部锚点，只有原生清晰度不足时才进行锁定锚点的清晰度补充。头部和细节建议使用方形或接近方形输出。
- 三张全身必须先裁白边，再统一主体总高度；头顶与脚跟在最终拼版中精确共线，之后人工检查肩、腰、膝和服装构造线。不得按各自原始像素尺寸靠底摆放，也不得在三视图上方留下无用途空白。
- 最终拼版只进行裁白边、等比例缩放和定位。禁止非等比例拉伸，禁止用图像模型再次合成或重绘。
- 版式固定为：三张全身占画面左侧三分之二；三张头部占右侧区域上半部；穿鞋结构与其他批准细节占右侧余下区域。正式画布不绘制分格边框。位置落在槽位内不等于版式通过，人物必须以统一主体高度有效占据区域，不得以空白或边框制造“已占据”的假象。
- 拼版脚本必须对三张裁白边后的全身模块计算同一个可用主体高度，并以该高度统一缩放；不得分别按各自画布适配。任何模块不得插值放大。源模块不足以达到合理有效占比时停止并返回模块生成，而不是把其余模块一同缩小来掩盖低分辨率。
- 使用 `scripts/compose_character_card.py --manifest <manifest.json> --out <output.png>`。脚本默认输出 3840×2160；加 `--width 1920 --height 1080` 输出 2K。
- 可加 `--qa-overlay-out <qa.png>` 输出带水平基准线的内部检查图。该图只用于验收，不得作为正式交付。
- 拼版后运行 `scripts/audit_character_delivery.py --asset-type card ...`，保存人物区域测量和版式辅助图，再填写 `execution-gates.md` 中的角色卡回执。脚本机械通过不代表正式通过。

清单示例：

```json
{
  "minimum_fullbody_fill": 0.72,
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

`minimum_fullbody_fill` 是全身槽位高度中的最低共同主体占比，默认 `0.72`。如项目已从批准角色卡统计出更严格的共同下限，应写入清单覆盖默认值；不得为了让低清或过小模块通过而降低它。

相对路径以清单文件所在目录为基准。拼版后必须重新读取实际像素，并将最终图与所有模块一起保留。

## 逐张验收与返工

1. 方向是否为严格正投影，而非四分之三；
2. 当前视角可见的身份、发型和年龄表现是否与批准源一致；背面正脸五官不可见时继承来源，不将其列为当前图必须直接看清的内容；
3. 体型、头身比、服装层级、配色、固定配饰与鞋型是否一致；
4. 全身是否完整、空手、双臂下垂；
5. 请求整卡拼版时，三视图头顶、肩、腰、膝与脚跟是否共线，左上是否存在无设计用途的空白；单模块不以未请求的整卡布局拒收；
6. 鞋部是否为角色实际穿着状态，是否同时看见裤脚、脚踝衔接与两只鞋；
7. 风格是否保持少量受力点硬折面、安静大黑面、按剪影/遮挡/受力/次要边界分级且带明确收笔的墨线、结构硬边与大面内部短距离受控色阶、成组几何头发、布料哑光，以及只服务于漆皮/金属/珠宝的紧凑高光；
8. 白底是否干净，是否有多余文字、投影、地台、边框或物件；
9. 失败只返回当前模块及真实依赖后代；只验本次请求的模块。请求整卡且其所需模块均通过后，排版错误只返回拼版脚本。
10. 回执是否列出了各模块原始尺寸、裁白边后尺寸和最终缩放倍率；任一低清裁片被放大即失败。
