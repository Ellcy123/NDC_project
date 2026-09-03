# NDC 角色提示词库

## 目录

1. 使用顺序与生产分流
2. 角色视觉设定
3. MJ 全身
4. 可选 MJ 头部
5. 通用风格全身转绘
6. 通用风格角色卡
7. 通用风格肖像
8. 黑白红风格角色卡

## 1. 使用顺序与生产分流

### 最高优先级：用户原始提示词

用户亲自提供的提示词是生产主版本，在用户明确声明停用或替换前不得改写、摘要、翻译、扩写或用模型推断的新提示词覆盖。角色设定中的性格词不允许反向改变锁定提示词规定的表情；当角色卡或肖像代码块要求“面无表情/中性”时，必须保持该要求。MJ 阶段缺失的可后补道具应登记给 Image 2，不得擅自把道具词塞回用户提示词并重新开始概念设计。

先判断角色类型：

```text
重要新角色
→ 完整 MJ 流程

不重要的新角色
→ 跳过 MJ
→ Image 2 直接生成通用风格角色
→ 生成通用风格角色卡；默认不生成肖像

既有角色的其他状态
→ 跳过 MJ
→ 以现有已批准的通用风格角色卡为基础参考
→ Image 2 生成指定状态

黑白红风格角色卡
→ 不在标准流程中生成
→ 仅在角色明确进入动画制作时单独触发
```

重要新角色的完整流程：

```text
角色视觉设定
→ MJ 全身
→ 头部质量闸门
→ 可选 MJ 头部
→ MJ 素材精修定稿
→ 通用风格全身转绘
→ 通用风格角色卡
→ 若为重要/复用/近景角色，生成通用风格肖像
→ 若明确进入动画制作，另行生成黑白红风格角色卡
```

强制覆盖规则：所有 MJ 提示词使用当前默认模型，不添加任何 `--v`、`--V 8.1` 或类似模型版本参数。旧 JSON 中的 V8.1 文本已经失效。

## 1.1 Image 2 快速路径

### 不重要的新角色

参考图：`assets/general-fullbody-style-reference.png`，即项目中的“全身像参考图”。

风格提示词：复用“通用风格全身转绘”和“通用风格角色卡”中的同一套角色风格描述，不另建一套轻量角色画风。

```text
参考图1的角色美术风格（不参考角色身份和具体服装），根据以下角色视觉设定生成一个单一角色：【角色视觉设定】。

完整展示角色头顶到鞋底，双脚完整入镜，平视镜头，自然站姿，纯白色背景。服装必须完整包含上装、下装和鞋子；只添加角色设定明确要求的配饰和道具，不添加新的身份、剧情或装饰信息。

保持以下角色风格：highly stylized graphic illustration, selective variable ink hierarchy with heavier marks at focal silhouette turns, occlusions and load-bearing corners, medium or fine tapered garment edges, selectively broken internal fold lines, visible swell, taper and decisive hand-drawn endings without making every edge equally heavy, grouped geometric hair masses with a few broad ribbon-like directional highlight shapes and no individual strand rendering, simplified geometric planar shape blocking, decisive angular shadow wedges at shoulders, elbows, cuffs, waist, knees and hems, broad quiet near-black garment planes, hard structural edges with short controlled tonal bridges inside larger skin or fabric planes, deep grouped spot blacks, identity-readable facial planes with both eyes, nose, mouth and jaw contour visible, material-specific finish with mostly matte cloth and compact sharp highlights reserved for approved polished leather, metal, jewelry or badges, selective detail density concentrated on identity-bearing accessories and construction, controlled high-contrast chiaroscuro, film-noir aesthetic, American 1928s era context, full-body portrait standing, eye-level shot, straight perspective, minimalist pure white background, isolated on white void.
```

### 既有角色的其他状态

参考图：图 1 必须是该角色当前已批准的通用风格角色卡。不要在角色卡存在时仅凭文本生成。

```text
以图1的现有角色卡作为角色身份、相貌、体型、基础服装、配色和美术风格的唯一基础参考。保持这个角色仍是同一个人，生成以下新状态：【状态需求】。

只改变状态需求明确指定的表情、动作、姿态、损伤、持物、服装差分或环境条件；未要求改变的相貌、发型、身体比例、基础服装结构、配色、笔触、线条和材质保持不变。不添加新的饰品、道具、伤疤、文字或剧情暗示。
```

<!-- NDC_TEXTURE_COHERENCE_MODULE:BEGIN -->
## 1.2 美术风格锁死下的纹理控制模块

下列模块只能用于未标记为“逐字锁定”的分支：Image 2 快速角色、既有角色状态、MJ 全身/头部的提示词整理、通用风格全身转绘、明确 4K 的模块化角色卡、已批准色相下的衣褶/墨线返工，以及明确触发的黑白红动画分支。它作为独立生成控制段追加，不删除、改写或摘要现有风格描述。

```text
Preserve the approved NDC character style authority exactly. The following instructions control only texture coherence and spatial detail density; they must not flatten, clean up, modernize, photorealize, soften, or otherwise restyle the character.

Keep identity-critical facial landmarks and approved costume details fully readable. Organize hair into the approved large geometric masses with only broad directional marks and no individual strands or granular filler. Keep broad garment planes quiet; place angular folds only at actual load points, joints, overlaps, closures, and material transitions. Material texture and ink marks must follow form, scale, lighting, and construction.

Do not distribute folds, highlights, grain, scratches, seams, ornaments, repeated marks, or accessory-like micro-detail uniformly across the body. Do not invent non-semantic micro-detail, fragmented short marks, decorative micro-wrinkles, random speckle, or unsupported surface construction.
```

不得将此模块追加到 `LOCKED_PROMPT:character-card-default` 或 `LOCKED_PROMPT:portrait` 的实际提交文本。这两条分支先按 `style-self-check.md` 执行双门禁；只有用户明确批准新的锁定版本后才能改变它们的哈希。
<!-- NDC_TEXTURE_COHERENCE_MODULE:END -->

## 2. 角色视觉设定

输入：角色策划案。

```text
【关于此角色的策划案】以上是一段角色的设定需求，给我一套在纯视觉设定上表现出这个角色的设定需求，从长相、发型到服装来分别整理结论给我，服装一定要包含上装、下装、以及鞋子。不要思考过程。
```

## 3. MJ 全身

重要新角色的完整流程从此处的实际 Midjourney 全身候选开始。ChatGPT Image 2 的全身图只适用于不重要角色的快通道，或在无法执行 MJ 时明确标记为模拟；模拟不得被写成已完成的 MJ 阶段。

网站：固定使用 `https://alpha.midjourney.com/imagine`。

参考图：点击页面右上角 `Images`，在下方已保存图片中选择与 `assets/mj-style-reference-1.png`、`assets/mj-style-reference-2.jpg` 对应的两张图片，两张均设为 Use style；正常流程不重新上传。

参数：1:2，Midjourney 当前默认模型，不添加模型版本参数。

给 ChatGPT 或 Gemini 的提示词模板：

```text
Full-body portrait standing (see head and feet), natural stance, camera at shoulder height, highly stylized graphic illustration, selective variable ink hierarchy with heavier marks at focal silhouette turns, occlusions and load-bearing corners, medium or fine tapered garment edges and selectively broken internal fold lines, visible swell, taper and decisive hand-drawn endings without making every edge equally heavy, grouped geometric hair masses with a few broad ribbon-like directional marks and no individual strand rendering, simplified planar shape blocking, decisive angular shadow wedges at load points, broad quiet near-black garment planes, hard structural edges with short controlled tonal bridges inside larger planes, deep grouped spot blacks while keeping the complete face identity-readable: both eyes, brow spacing, nose bridge and tip, mouth or mustache shape, jaw and cheek contour, ears, and hairline simultaneously visible; no half-face blackout, no eye lost in shadow, material-specific finish with mostly matte cloth and compact sharp highlights only on approved polished leather, metal, jewelry or badges, controlled high-contrast chiaroscuro, film-noir aesthetic, American 1928s era context, eye-level shot, straight perspective, minimalist pure white background, isolated on white void.

结合以上给出的美术风格提示词，给出一套符合以下角色描述的适用于 Midjourney 的提示词。尽量精简，排除多余且重复的提示词，需要中英双语版本，图片比例 1:2。使用 Midjourney 当前默认模型，不添加任何 --v、--V 或其他指定模型版本参数：

【角色描述】
```

## 4. 可选 MJ 头部

仅当全身图头部未通过质量闸门时使用。

网站与参考图：继续使用 `https://alpha.midjourney.com/imagine`，点击右上角 `Images`，从下方已保存图片中选择同一组两张 MJ 核心风格参考图，两张均设为 Use style；正常流程不重新上传。

参数：9:16，Midjourney 当前默认模型，不添加模型版本参数。

```text
现在我要生成这个角色的头部特写图，只需要头部（脖颈以上，完整展示的头部和发型，以及部分肩膀部位）部分的内容。

【补充头部的细节描述：】

结合以下新的头部特写风格描述提示词，以及对角色的特征补充，删除肩部以下的多余描述提示词，给我一套新的、用于 Midjourney 生成 9:16 图片的中英双语提示词。使用 Midjourney 当前默认模型，不添加任何 --v、--V 或其他指定模型版本参数。

风格描述：highly stylized graphic illustration, selective variable ink hierarchy with heavier marks at focal silhouette turns and occlusions, medium or fine tapered secondary contours and selectively broken internal lines, visible swell, taper and decisive hand-drawn endings without making every edge equally heavy, grouped geometric hair masses with a few broad ribbon-like directional marks and no individual strand rendering, simplified planar shape blocking, hard structural facial turns with short controlled tonal bridges inside larger planes, bold grouped shadows that model the face without hiding identity landmarks, both eyes and the complete nose, mouth or mustache, jaw/cheek contour, ears and hairline simultaneously readable, no half-face blackout, no eye lost in shadow, mostly matte skin and cloth with material-specific compact highlights only where justified, controlled high-contrast chiaroscuro, film noir aesthetic, American 1928s era context, eye-level shot, minimalist pure white background, isolated on white void.
```

不要要求生成结果与全身图长相一致。只要求它符合角色描述并能作为后续精修素材。

## 5. 通用风格全身转绘

参考顺序：

1. 图 1：MJ 阶段精修定稿；
2. 图 2：从图 1 同一张精修定稿裁出的面部身份锚点（当全身尺寸不足以可靠比较五官时使用；不是另一张未合成的 MJ 头像）；
3. 图 3：`assets/general-fullbody-style-reference.png`。若无需图 2，则风格参考顺延为图 2。

```text
将图1的风格朝着最后一张风格参考图转变。图1与图2（若提供）共同锁定同一个人的身份；最后一张图只控制画风，绝不采用其中人物的相貌。严格保留图1/图2中这个人的脸型和额头比例、眉眼间距、眼型、鼻梁与鼻尖轮廓、嘴部或胡须形状、颧骨与下颌轮廓、耳形、发际线和可见不对称特征；不能只保留“年龄、发型、胡须、服装相似”后重新画一张更规整或更普通的脸。保留图1的体型、头身比、服装、配饰和配色方案，不添加任何新的道具和设计。将角色调整为中性自然站姿，两只手臂都自然下垂，两只手完整露出；不得背手、插兜或用身体遮住手部。除手臂与手部姿态外，不改变图1的其他角色设计。并参考以下美术风格提示词进行调整：highly stylized graphic illustration, selective variable ink hierarchy with heavier marks at focal silhouette turns, occlusions and load-bearing corners, medium or fine tapered garment edges and selectively broken internal fold lines, visible swell, taper and decisive hand-drawn endings without making every edge equally heavy, grouped geometric hair masses with a few broad ribbon-like directional marks and no individual strand rendering, simplified planar shape blocking, decisive angular shadow wedges at load points, broad quiet near-black garment planes, hard structural edges with short controlled tonal bridges inside larger planes, high-contrast chiaroscuro that keeps all identity landmarks readable, deep grouped spot blacks on clothing and silhouette, material-specific finish with mostly matte cloth and compact sharp highlights reserved for approved polished leather, metal, jewelry or badges, selective identity-detail density, film noir aesthetic, American 1928s era context, full-body portrait standing, eye-level shot, straight perspective, minimalist pure white background, isolated on white void.
```

## 6. 通用风格角色卡

输入：

1. 图 1：已通过身份比对的通用风格全身定稿；
2. 图 2：从图 1 裁出的同源正面面部锚点（建议用于重要角色，帮助复杂版式继续锁脸）。

### 6.1 明确要求 4K 时的模块化角色卡

仅当用户明确写出 `4K` 时读取 `modular-character-card.md` 并执行本节。分别生成全身正面、严格左侧面、背面，并在每一张的原始像素中保留能核对脸型、发型、发际线和耳位的头部细节；全身模块通过后先裁出同源头部身份锚点。头部正面、严格右侧面、背面优先直接采用对应锚点，或仅以该锚点做清晰度补充；不得借此重画身份。再生成角色实际穿着批准鞋型的双脚/小腿特写，以及零至三张批准装饰/道具/构造特写。每次只生成一个模块并单独保存；已通过模块冻结，失败只返工当前模块。用户只说“正式”“高清”“最终”或“可用”时不得自动进入本节。

统一提示词骨架：

```text
以图1的批准角色作为身份、体型、服装、配色与美术风格源；图2（若提供）只补充同源面部身份；图3（若提供）是已经批准的同组正面模块，用于锁定后续视角。只生成一个【模块名称与唯一视角】，不要生成整张角色卡或多个视角。

严格保留同一个人的脸型、眉眼间距、鼻形、嘴部、颧颌轮廓、耳形、发际线和年龄；保留同一体型、头身比、发型轮廓、服装层级、配色、固定徽章/配饰位置与鞋型。保持选择性的线宽层级、成组几何头发、硬边结构转折、受控高反差明暗与服装大面积深色安静区。头发允许少量顺发流的宽带状亮暗笔触，不画逐根发丝。衣褶只在肩、肘、袖口、腰、膝和衣摆等受力点形成少量明确的角状硬转折与硬边明暗块，躯干与长衣大面保持安静，并允许大平面内部短距离、受控的色阶桥接；禁止长距离柔滑渐变、空气刷过渡、圆融融化式折痕和把普通布料画成亮面 3D 材质。轮廓与内部墨线必须有可见粗细节奏：剪影焦点、受力角和深遮挡处加重，长直服装边界中等或偏细且收尖，内部折线更细并选择性断开；线条需有鼓胀、收尖、断续和明确收笔，不得让所有边同样粗重或同样机械。普通布料与皮肤偏哑光，漆皮鞋、金属、珠宝和徽章可保留紧凑尖锐高光。纯白背景，一个孤立主体，最大有效尺寸，四周保留干净边距，不裁切，不添加文字、边框、水印、地面、投影、道具或新设计。

若为全身模块：完整展示头顶到鞋底，双臂自然下垂，双手空置并可见，不得背手、插兜、持物或让便携道具接触身体；头部必须以原生清晰度读出脸型、眉眼关系、发型大轮廓、发际线与耳位，以便裁出同源身份锚点。若为头部模块：只展示头部、颈部和极少量衣领，严格正投影，不得用四分之三视角代替；只使用对应全身身份锚点的直接裁片，或该裁片的单目的清晰度补充，不得改变脸、发型、发色、年龄、衣领和视角。若为鞋部模块：展示角色从小腿中段到鞋底的双腿，正常站立并实际穿着批准鞋型，同时看见裤脚、脚踝衔接与两只鞋。若为其他细节模块：只展示批准物件本身，不与人物接触。

【模块名称与唯一视角】
```

模块方向词必须逐项使用：

- `完整全身严格正面正投影视图`；
- `完整全身严格左侧面正投影视图，角色面朝画面左侧`；
- `完整全身严格背面正投影视图`；
- `中性头部与上颈严格正面正投影视图`；
- `中性头部与上颈严格右侧面正投影视图，展示角色右脸`；
- `头部与上颈严格背面正投影视图，完整展示后脑发型、两耳位置与后领`；
- `角色从小腿中段到鞋底的严格正面结构特写，正常站立并实际穿着批准鞋型，同时展示两侧裤脚、脚踝衔接与两只鞋`；
- 经批准的配饰、便携道具或服装构造的准确名称与方向。

模块全部通过后，按清单运行 `scripts/compose_character_card.py`。拼版阶段不再调用 Image 2，不重绘模块。

### 6.1.1 已批准色相下的衣褶与墨线返工

当用户已经调整或批准现有色相，只返工失败的全身模块；把该色相版本作为图 1，并追加同角色已通过的穿鞋裤腿模块与自检库样本作为风格证据。使用以下窄范围补充词：

```text
只修正衣褶折面与墨线节奏。严格保留图1现有角色身份、五官、体型、姿态、视角、服装设计、徽章位置、鞋型、构图、暖肤色相与近黑服装色相，不重新设计或重新配色。把残留的柔滑布料渐变改为少量明确的角状硬折面和硬边明暗块；肩、肘、袖口、腰、膝与衣摆为主要转折点，躯干和长衣大面保持安静近黑，不增加装饰性碎褶。强化墨线粗细节奏：受力角、重叠与深遮挡处加重，次要服装边界使用中等收尖线，内部折线更细并选择性中断；线条需有鼓胀、收尖、断续和明确手绘收笔。禁止空气刷渐变、圆融融化式衣褶、均匀矢量轮廓、亮面3D渲染。纯白背景，单个完整主体，不改变裁切与比例。
```

### 6.2 默认整卡生成（稳定优先）

用户未明确要求 `4K` 时默认使用本节。以下代码块以项目最初整卡提示词为基底，只保留用户后来明确确认的三头部视图、空手、穿鞋结构与版式要求；它是锁定的整卡主提示词。调用生成工具时逐字提交，不得改写、摘要、翻译、扩写或追加分辨率、透明、人物占比、抠图、扩图、补全和负面词。生成结果先检查身份、结构与画风；尺寸、比例和人物位置在通过后按 `post-generation-normalization.md` 技术整备。不得把普通整卡直接插值放大后作为 4K 交付。

<!-- LOCKED_PROMPT:character-card-default:BEGIN -->
```text
保持图1当前风格，并用图1和图2共同锁定同一个人的具体长相。不得美化、年轻化、平均化或重新设计五官；正面全身与所有头部特写必须继承图1/图2的脸型、眉眼间距、眼型、鼻形、嘴部/胡须、颧颌轮廓、耳形和发际线。

生成横向 16:9 角色卡。左侧约三分之二必须包含三个等比例完整全身视图：正面、严格左侧面、背面；三个视角的头顶、肩膀、腰线、膝盖和脚跟高度完全一致。三视图中的角色双臂自然下垂、双手空置，不得背手、插兜，不得手持、夹带、悬挂、接触或携带任何道具（包括文件夹、信封、记录盒、钥匙圈）；正面与背面必须看到两只下垂的空手，严格侧视时远侧手允许因正投影自然重叠，但手臂不得藏到背后。右上必须同时包含三个面无表情的头部特写：纯正面、展示角色右脸的严格侧面，以及完整展示后脑发型与后领的背面；不能缺少，不能用四分之三头像代替。细节区必须展示正常站立的鞋子，并且只展示零至三张设定中已批准的配饰、批准道具的孤立无人物接触细节，或确有设计核对价值的服装构造；道具不得与任何三视图人物身体或手部重叠。没有批准配饰或道具时宁可减少细节格，也不要用随机衣料、无意义袖口或重复大衣切片填空。平视镜头，纯白背景，不添加新材质、道具、装饰、文字、边框或水印，保持原图角色头身比。

并参考以下美术风格提示词确保风格统一：highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour::1.5, exaggerated drastic line weight variation, distinct heavy layered ink contours for each garment layer (shirt, jacket, skirt, tie), bolder heavier internal ink lines, flat graphic monolithic hair mass, zero internal texture or detail in hair, single solid block of black or color for hair, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean distinctive features, controlled high contrast chiaroscuro lighting, all identity-critical facial landmarks readable in every front head depiction, heavy use of solid black shadows (spot blacks) on clothing and silhouette, deep shadows kept away from the eyes, nose, mouth and jaw contour, minimal specular highlights, matte surfaces, film noir aesthetic, American 1928s era context, full-body portrait standing, eye-level shot, straight perspective, minimalist pure white background, isolated on white void.
```
<!-- LOCKED_PROMPT:character-card-default:END -->

若默认整卡只缺少某个头部视角、对齐、画布外缘或某个细节格，而身份与其余结构已通过，可用局部编辑只修该区域；若正面人脸已经漂移，则必须用同一锁定提示词返回整卡生成，不能靠新增其他视角掩盖身份错误。明确 4K 的模块化流程中始终只返工失败模块。

## 7. 通用风格肖像

本节是条件分支。不重要角色默认跳过；只有重要、复用、界面展示或明确近景需求时执行。

参考顺序：

1. 图 1：通用风格角色卡；
2. 图 2：`assets/general-portrait-style-reference.png`。

<!-- LOCKED_PROMPT:portrait:BEGIN -->
```text
参考图1的角色相貌和设定（不包括视角和动作），然后参考图2的美术风格（不包括角色相貌和设定），【动作为纯正面视角，面无表情目视前方】。结合以下给出的美术风格提示词，生成图片比例4：5的图1的人物肖像图；

美术风格提示词：classic Film Noir aesthetic, 1930s vintage illustration style, No brushstrokes on the face, Smooth brushstrokes, Dry parchment-like skin（face only）, The outermost layer of skin is covered with what appear to be granular dots, American Comic Inking, variable line weight, bold dark outer contour, graphic geometry, hard-planed facial features, sculptural face planes, planar color blocking, faceted shading, Digital Impasto, visible directional brushstrokes, thick oil paint texture, matte dry skin finish, controlled rough brushwork, The hairstyle brushstrokes are simplified, hair simplified into large graphic masses, simplified/blocky hair, hair treated as a single solid mass, zero fine strand rendering, minimal internal hair texture, broad grouped hair shapes, clean large hair clumps, summarized hair volume, low-saturation earth tones, warm sepia browns, charcoal blacks,no highlights， subtle vintage paper grain, high-contrast chiaroscuro, dramatic side lighting, deep dramatic shadows, compressed values, off-white blank background, clean negative space
```
<!-- LOCKED_PROMPT:portrait:END -->

以上代码块是锁定的肖像主提示词。调用生成工具时必须逐字提交，不得添加透明背景、肩部范围、尺寸修复、角色外貌复述、负面词或任何自行优化内容。图 1 提供角色身份和设定，图 2 只控制画风。生成结果先完成身份与肖像画风检查；比例、尺寸、透明、人物占比和可见边缘在通过后按 `post-generation-normalization.md` 处理。原生构图中的缺肩或截肩不补全。

通用肖像从角色卡派生。不要把 MJ 头部素材当作图 1，也不要从 MJ 头部样本推断肖像精修规则。

若图 2 的参考人物导致角色身份漂移（性别、年龄、五官、发型或服装被替换），该结果直接拒收。重试时去掉图 2，仅保留批准的通用角色卡作为图片参考，并把本节“美术风格提示词”完整写入文字提示词。

## 8. 黑白红风格角色卡

本节仅作动画用途保留分支，不属于标准角色交付。只有角色明确进入动画制作时执行。

参考顺序：

1. 图 1：通用风格角色卡；
2. 图 2：`assets/black-white-red-style-reference.jpg`。

```text
Light & Color: High-Contrast Chiaroscuro with black, white, and red unmistakably dominant, Stark Shadows, Limited Color Palette with Dramatic Accents. Use a small amount of bright red with a clear spatial or identity purpose: favor an asymmetric shadow-side rim, local separation light, or a tie, emblem, eye, or small approved accessory; do not trace every edge with an even red outline. Keep clothing, props, and most rendering achromatic, but retain low-contrast gray or faint warm-gray internal facets inside near-black garments so the body and clothing layers do not collapse into a featureless silhouette. Skin is almost grayscale with only a barely perceptible warm gray-brown or muted sepia bias, far less saturated than the general-style source. Do not restore natural brown/orange skin color. Avoid broad pure-white skin planes; retain the black-white graphic structure and use the faint skin hue only as a restrained tint.

Line & Form: Geometric Simplification of Forms, Generalization of details, Foreground and background completely silhouetted, Remove redundant fragmented structures, A sense of spatial structure is achieved through simple points, lines, and planes.

Texture & Method: Minimalist blocky, Geometric Simplification of Forms, Sharp outer contour edges, Everything except the key elements of the image is structurally simplified.

根据以上美术风格提示词，并参考图2的角色美术风格（不考虑参考图的内容），将图1的角色卡改为图2的美术风格，包含笔触、线条和颜色；黑、白、红必须是明显主色，服装、道具和大部分画面保持无彩色；瞳孔保留原本颜色；皮肤以近灰度为主，只带几乎不可察觉的暖灰褐/暗赭色偏，其饱和度必须远低于通用角色卡，不得恢复成正常棕色、橙色或自然肤色，也不得把大片皮肤亮面漂成纯白；其他内容保持不变；纯白色背景；图片比例 16:9。

红色只能用于具有明确光向、空间分离或身份提示作用的阴影侧局部轮廓、细线、徽记、眼部或很小的配件点缀；不要求对称，不得沿所有边形成均匀完整红描边。禁止大面积红色背景、竖条、边框、地面块或服装面板；只有用户明确选择极简海报分支时，才可单独放开大红底。
```
