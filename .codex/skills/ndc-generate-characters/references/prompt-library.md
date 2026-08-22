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

保持以下角色风格：highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour::1.5, exaggerated drastic line weight variation, distinct heavy layered ink contours for each garment layer (shirt, jacket, skirt, tie), bolder heavier internal ink lines, flat graphic monolithic hair mass, zero internal texture or detail in hair, single solid block of black or color for hair, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean distinctive features, controlled high contrast chiaroscuro lighting, identity-readable facial planes with both eyes, nose, mouth and jaw contour visible, heavy use of solid black shadows (spot blacks) on clothing and silhouette, deep shadows kept away from identity-critical facial landmarks, minimal specular highlights, matte surfaces, film noir aesthetic, American 1928s era context, full-body portrait standing, eye-level shot, straight perspective, minimalist pure white background, isolated on white void.
```

### 既有角色的其他状态

参考图：图 1 必须是该角色当前已批准的通用风格角色卡。不要在角色卡存在时仅凭文本生成。

```text
以图1的现有角色卡作为角色身份、相貌、体型、基础服装、配色和美术风格的唯一基础参考。保持这个角色仍是同一个人，生成以下新状态：【状态需求】。

只改变状态需求明确指定的表情、动作、姿态、损伤、持物、服装差分或环境条件；未要求改变的相貌、发型、身体比例、基础服装结构、配色、笔触、线条和材质保持不变。不添加新的饰品、道具、伤疤、文字或剧情暗示。
```

## 2. 角色视觉设定

输入：角色策划案。

```text
【关于此角色的策划案】以上是一段角色的设定需求，给我一套在纯视觉设定上表现出这个角色的设定需求，从长相、发型到服装来分别整理结论给我，服装一定要包含上装、下装、以及鞋子。不要思考过程。
```

## 3. MJ 全身

网站：固定使用 `https://alpha.midjourney.com/imagine`。

参考图：点击页面右上角 `Images`，在下方已保存图片中选择与 `assets/mj-style-reference-1.png`、`assets/mj-style-reference-2.jpg` 对应的两张图片，两张均设为 Use style；正常流程不重新上传。

参数：1:2，Midjourney 当前默认模型，不添加模型版本参数。

给 ChatGPT 或 Gemini 的提示词模板：

```text
Full-body portrait standing (see head and feet), natural stance, camera at shoulder height, highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour, exaggerated drastic line weight variation, distinct heavy layered ink contours for each garment layer (shirt, jacket, skirt, tie), bolder heavier internal ink lines, flat graphic monolithic hair mass, zero fine strand texture, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean distinctive features, controlled high-contrast chiaroscuro lighting, heavy solid-black shadows on clothing and silhouette while keeping the complete face identity-readable: both eyes, brow spacing, nose bridge and tip, mouth or mustache shape, jaw and cheek contour, ears, and hairline simultaneously visible; no half-face blackout, no eye lost in shadow, minimal specular highlights, matte surfaces, film-noir aesthetic, American 1928s era context, eye-level shot, straight perspective, minimalist pure white background, isolated on white void.

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

风格描述：highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour, exaggerated drastic line weight variation, bolder heavier internal ink lines, flat graphic monolithic hair mass, zero fine strand texture, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean distinctive features, controlled high-contrast chiaroscuro lighting, bold shadows that model the face without hiding identity landmarks, both eyes and the complete nose, mouth or mustache, jaw/cheek contour, ears and hairline simultaneously readable, no half-face blackout, no eye lost in shadow, minimal specular highlights, matte surfaces, film noir aesthetic, American 1928s era context, eye-level shot, minimalist pure white background, isolated on white void.
```

不要要求生成结果与全身图长相一致。只要求它符合角色描述并能作为后续精修素材。

## 5. 通用风格全身转绘

参考顺序：

1. 图 1：MJ 阶段精修定稿；
2. 图 2：从图 1 同一张精修定稿裁出的面部身份锚点（当全身尺寸不足以可靠比较五官时使用；不是另一张未合成的 MJ 头像）；
3. 图 3：`assets/general-fullbody-style-reference.png`。若无需图 2，则风格参考顺延为图 2。

```text
将图1的风格朝着最后一张风格参考图转变。图1与图2（若提供）共同锁定同一个人的身份；最后一张图只控制画风，绝不采用其中人物的相貌。严格保留图1/图2中这个人的脸型和额头比例、眉眼间距、眼型、鼻梁与鼻尖轮廓、嘴部或胡须形状、颧骨与下颌轮廓、耳形、发际线和可见不对称特征；不能只保留“年龄、发型、胡须、服装相似”后重新画一张更规整或更普通的脸。保留图1的体型、头身比、服装、配饰和配色方案，不添加任何新的道具和设计。将角色调整为中性自然站姿，两只手臂都自然下垂，两只手完整露出；不得背手、插兜或用身体遮住手部。除手臂与手部姿态外，不改变图1的其他角色设计。并参考以下美术风格提示词进行调整：highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour::1.5, exaggerated drastic line weight variation, distinct heavy layered ink contours for each garment layer (shirt, jacket, skirt, tie), bolder heavier internal ink lines, flat graphic monolithic hair mass, zero internal texture or detail in hair, single solid block of black or color for hair, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean features, high contrast chiaroscuro that keeps all identity landmarks readable, heavy use of solid black shadows on clothing and silhouette, minimal specular highlights, matte surfaces, film noir aesthetic, American 1928s era context, full-body portrait standing, eye-level shot, straight perspective, minimalist pure white background, isolated on white void.
```

## 6. 通用风格角色卡

输入：

1. 图 1：已通过身份比对的通用风格全身定稿；
2. 图 2：从图 1 裁出的同源正面面部锚点（建议用于重要角色，帮助复杂版式继续锁脸）。

```text
保持图1当前风格，并用图1和图2共同锁定同一个人的具体长相。不得美化、年轻化、平均化或重新设计五官；正面全身与所有头部特写必须继承图1/图2的脸型、眉眼间距、眼型、鼻形、嘴部/胡须、颧颌轮廓、耳形和发际线。

生成横向 16:9 角色卡。左侧约三分之二必须包含三个等比例完整全身视图：正面、严格左侧面、背面；三个视角的头顶、肩膀、腰线、膝盖和脚跟高度完全一致，双臂自然下垂，不得背手或插兜；正面与背面必须看到两只下垂的手，严格侧视时远侧手允许因正投影自然重叠，但手臂不得藏到背后。右上必须同时包含两个面无表情的头部特写：纯正面，以及展示角色右脸的严格侧面；两者不能缺少、不能合并成一个四分之三头像。右下只展示正常站立的鞋子、设定中已批准的配饰，或确有设计核对价值的服装构造；没有批准配饰时宁可减少细节格，也不要用随机衣料、无意义袖口或重复大衣切片填空。平视镜头，纯白背景，不添加新材质、道具、装饰、文字、边框或水印，保持原图角色头身比。

并参考以下美术风格提示词确保风格统一：highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour::1.5, exaggerated drastic line weight variation, distinct heavy layered ink contours for each garment layer (shirt, jacket, skirt, tie), bolder heavier internal ink lines, flat graphic monolithic hair mass, zero internal texture or detail in hair, single solid block of black or color for hair, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean distinctive features, controlled high contrast chiaroscuro lighting, all identity-critical facial landmarks readable in every front head depiction, heavy use of solid black shadows (spot blacks) on clothing and silhouette, deep shadows kept away from the eyes, nose, mouth and jaw contour, minimal specular highlights, matte surfaces, film noir aesthetic, American 1928s era context, full-body portrait standing, eye-level shot, straight perspective, minimalist pure white background, isolated on white void.
```

若一次生成只缺少侧面头部、对齐或某个细节格，而身份与其余结构已通过，可用局部编辑只修该区域；若正面人脸已经漂移，则必须回到角色卡生成，不能靠新增侧脸掩盖身份错误。

## 7. 通用风格肖像

本节是条件分支。不重要角色默认跳过；只有重要、复用、界面展示或明确近景需求时执行。

参考顺序：

1. 图 1：通用风格角色卡；
2. 图 2：`assets/general-portrait-style-reference.png`。

```text
参考图1的角色相貌和设定（不包括视角和动作），然后参考图2的美术风格（不包括角色相貌和设定）。动作为纯正面视角，面无表情，目视前方。结合以下美术风格提示词，生成图片比例 4:5 的图1人物肖像图。

美术风格提示词：classic Film Noir aesthetic, 1930s vintage illustration style, No brushstrokes on the face, Smooth brushstrokes, Dry parchment-like skin (face only), The outermost layer of skin is covered with what appear to be granular dots, American Comic Inking, variable line weight, bold dark outer contour, graphic geometry, hard-planed facial features, sculptural face planes, planar color blocking, faceted shading, Digital Impasto, visible directional brushstrokes, thick oil paint texture, matte dry skin finish, controlled rough brushwork, The hairstyle brushstrokes are simplified, hair simplified into large graphic masses, simplified/blocky hair, hair treated as a single solid mass, zero fine strand rendering, minimal internal hair texture, broad grouped hair shapes, clean large hair clumps, summarized hair volume, low-saturation earth tones, warm sepia browns, charcoal blacks, no highlights, subtle vintage paper grain, high-contrast chiaroscuro, dramatic side lighting, deep dramatic shadows, compressed values, off-white blank background, clean negative space.
```

通用肖像从角色卡派生。不要把 MJ 头部素材当作图 1，也不要从 MJ 头部样本推断肖像精修规则。

若图 2 的参考人物导致角色身份漂移（性别、年龄、五官、发型或服装被替换），该结果直接拒收。重试时去掉图 2，仅保留批准的通用角色卡作为图片参考，并把本节“美术风格提示词”完整写入文字提示词。

## 8. 黑白红风格角色卡

本节仅作动画用途保留分支，不属于标准角色交付。只有角色明确进入动画制作时执行。

参考顺序：

1. 图 1：通用风格角色卡；
2. 图 2：`assets/black-white-red-style-reference.jpg`。

```text
Light & Color: High-Contrast Chiaroscuro with black, white, and red unmistakably dominant, Stark Shadows, Limited Color Palette with Dramatic Accents, Use a small amount of bright red as an accent. Keep clothing, props, and most rendering achromatic. Skin is almost grayscale with only a barely perceptible warm gray-brown or muted sepia bias, far less saturated than the general-style source. Do not restore natural brown/orange skin color. Avoid broad pure-white skin planes; retain the black-white graphic structure and use the faint skin hue only as a restrained tint.

Line & Form: Geometric Simplification of Forms, Generalization of details, Foreground and background completely silhouetted, Remove redundant fragmented structures, A sense of spatial structure is achieved through simple points, lines, and planes.

Texture & Method: Minimalist blocky, Geometric Simplification of Forms, Sharp outer contour edges, Everything except the key elements of the image is structurally simplified.

根据以上美术风格提示词，并参考图2的角色美术风格（不考虑参考图的内容），将图1的角色卡改为图2的美术风格，包含笔触、线条和颜色；黑、白、红必须是明显主色，服装、道具和大部分画面保持无彩色；瞳孔保留原本颜色；皮肤以近灰度为主，只带几乎不可察觉的暖灰褐/暗赭色偏，其饱和度必须远低于通用角色卡，不得恢复成正常棕色、橙色或自然肤色，也不得把大片皮肤亮面漂成纯白；其他内容保持不变；纯白色背景；图片比例 16:9。

红色只能用于细线、徽记或很小的局部点缀；禁止大面积红色背景、竖条、边框、地面块或服装面板。
```
