# SC4027 两只酒杯与古巴雪茄烟蒂｜生成提示记录

## 淘汰方案｜built-in ImageGen edit

下面的整块场景编辑候选因移动并放大矮桌而淘汰，仅保留审查记录，未进入最终场景。

Use case: precise-object-edit
Asset type: NDC localized raster evidence placement
Input image: the exact prepared 1024x1024 context crop from the approved SC4027 native-resolution scene; edit target.
Primary request: add exactly two period-appropriate thick-bottomed whiskey tumblers and one partly smoked Cuban cigar butt on the existing central coffee table. Place the ordinary-use glass nearer the left armchair side. Place the visitor glass nearer the right sofa side with a small amount of amber liquor, a few partly unmelted ice fragments, condensation, and a damp round coaster ring. Put the extinguished dark-brown cigar butt beside that visitor glass, with a little ash adhering to the damp coaster edge.
Map-view information budget: communicate only two recently used glasses and a cigar beside the wetter visitor glass. Keep bite details too small to read in this scene view. No labels, names, initials, dates, writing, evidence cards, or conclusions.
Style/medium: preserve the source NDC illustration exactly—same inked line weight, subdued painterly texture, 1920s materials, palette, perspective, grain, and warm table-lamp lighting.
Perspective contract: ordinary physical scale; both glasses stand naturally on the sloped tabletop plane and obey its vanishing lines; the cigar lies flat; contact shadows and subtle reflections follow the lamp from upper right.
Placement contract: keep every glass, ice fragment, coaster edge, ash fragment, cigar tip, reflection, and contact shadow completely on the coffee tabletop and inside the authorized region.
Hard invariants: preserve the exact framing and camera. Keep the coffee-table shape and edge, armchair, sofas, rug, fireplace, clock, telephone cabinet, lamp, doors, walls, floor, and all lighting outside the tabletop props unchanged. Do not crop, zoom, rotate, shift, resize, add people, add extra glasses, bottles, trays, ashtrays, text, or unrelated objects. Return the full edited crop.

## 最终场景母版 A｜built-in ImageGen generation + 绿幕抠图

Use case: stylized-concept
Asset type: isolated NDC game prop master for chroma-key extraction
Input image: SC4027 source crop as style, palette, line-weight, lighting and camera-angle reference only.
Primary request: exactly one nearly empty 1920s thick-bottomed whiskey tumbler, seen from the source scene's slightly elevated three-quarter view.
Backdrop: perfectly uniform chroma green `#00FF00`, with generous padding and no table, floor, horizon or text.
Lighting: warm upper-right light and a short neutral shadow beneath-left.
Constraints: one glass only; no ice, coaster, cigar, bottle, table, text or watermark.

生成绿幕母版后，以确定性色键去绿、消除绿色溢色、保留玻璃和原生短阴影，输出透明母版；模型不再接触场景。

## 最终场景母版 B｜built-in ImageGen generation + 原生透明底

Use case: stylized-concept
Asset type: isolated NDC game prop cluster master
Input images: SC4027 source crop for style/camera; the accepted first tumbler for glass construction identity.
Primary request: exactly one matching visitor tumbler on a damp dark coaster, with amber residue, partly unmelted ice, condensation and wet ring; exactly one partly smoked Cuban cigar beside it, with damp ash at the coaster edge.
Backdrop: requested uniform chroma green, but built-in ImageGen returned a genuine transparent PNG; the native alpha was retained because it was cleaner than recreating a green backing.
Constraints: one glass, one coaster and one cigar only; no table, bottle, tray, ashtray, text or watermark.

## 最终场景合成｜deterministic

- A 透明层本地裁切坐标：`[410,408,472,477]`。
- B 透明层本地裁切坐标：`[600,392,696,491]`。
- 两层只做一次高质量缩放和 Alpha 合成；不重绘、不生成场景。
- 结果由坐标锁定工具按两个独立 composition mask 依次写入，并通过最终 union-mask 零漂移验证。

## 4314 clue photo｜built-in ImageGen generation

Use case: stylized-concept
Asset type: high-resolution first-person clue observation for a locked Polaroid card
Input images: accepted scene placement plus the exact ordinary and visitor glass masters.
Primary request: show the same two tumblers on the same pale coffee table, with unequal placement. The right/front visitor glass is the visual focus and must clearly show amber residue, partly unmelted ice, condensation and a damp coaster ring; the cigar remains supporting context.
Constraints: no extra glass, bottle, tray, ashtray, text, labels, ruler, lip-print identification, names or conclusions; no Polaroid frame in the generated master.

To be filled with the exact final production prompt used after the scene anchor is accepted.

## 4315 clue photo｜built-in ImageGen generation

Use case: stylized-concept
Asset type: high-resolution first-person forensic clue observation for a locked Polaroid card
Input images: accepted visitor-glass context and exact transparent cluster master.
Primary request: side-on macro of the same cigar lying horizontally beside the damp coaster and visitor glass. The charred end is at far left; the intact brown mouth end is at right, viewed from its wrapper side rather than its circular end face. Show shallow wrapper compression on the right side: a forward inward dent, a roughly thirty-degree line of oval pressure dents, and one absent rear dent leaving a gap. Keep amber residue, partly unmelted ice, wet ring and damp ash as context.
Constraints: no holes, punctures, torn filler, circular cut end facing camera, teeth, diagram, ruler, arrows, identity labels, text or conclusions; no Polaroid frame in the generated master.

前两张 4315 候选分别误画成燃烧端特写和端面破洞，均保存在 `review/`，未进入交付。
