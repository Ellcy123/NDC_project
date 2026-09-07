# NDC emergency-art direction

## Reference roles

Inspect every selected reference before generation and state its role in the prompt:

- **Character card:** locks face, age, build, hair, clothing identity, and distinguishing props.
- **EPI02 background:** locks architecture, room geometry, furniture, era props, damage state, time of day, and lighting continuity.
- **Evidence art:** locks the count, silhouette, material, and story-critical details of a prop.
- **U1 emergency frame:** guides graphic weight, panel-minded composition, and read order only.

If a character card and scene NPC asset differ, preserve the character card's identity while using the scene asset only for scene-specific clothing or staging when the requirement supports it.

## Mandatory local-close-up prompt structure

Every emergency frame is a local or extreme-local close-up, including frames whose subject is the scene rather than a character. Fill exactly these two semantic fields from the frame plan:

- `【局部主体】`: the cropped focal region, such as a face, eyes, hand, shoe, evidence prop, door gap, floor trace, flame edge, or localized light/shadow.
- `【具体镜头内容】`: the action, expression, gaze, pose, and focal relationship visible in that crop.

Replace the brackets before submission. Do not turn either field into a medium, long, full-body, establishing, or panoramic composition.

Use one of these two openings:

**Ordinary generation**

> 生成【局部主体】的超近局部特写，内容为【具体镜头内容】。

**Scene + character composite**

> 以图1的场景作为背景，生成图2人物的【局部主体】超近局部特写，内容为【具体镜头内容】。

For the composite mode, image 1 owns scene geometry, contents, lighting context, and color grade; image 2 owns character identity, design, palette, strokes, and linework. If an input contains a red guide box, add `完成以上步骤后删除红框。` and ensure no red guide survives in the result.

Append the following shared calibration to **every** prompt, in both modes:

> 使用 ARRI 35MM 胶片机的摄影质感，F1.2–F1.8 的光圈设定。特写主体必须保持清晰，只有主体以外的焦外画面呈现模拟真实相机的虚化效果。整个场景的所有内容保持不变，除了给角色添加融入场景所必需的光影外。角色的所有设计、配色、笔触和线条等美术风格保持不变，且不增加额外的材质、纹理或细节。场景和角色的色阶保持一致，以场景的色阶为主。

Then append this English graphic-style block verbatim:

> highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour::1.5, exaggerated drastic line weight variation, distinct heavy layered ink contours for every visible garment layer and story-critical prop, bolder heavier internal ink lines, flat graphic monolithic hair mass, zero internal texture or detail in hair, single solid block of black or color for hair, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean features, extreme high contrast chiaroscuro lighting, heavy use of solid black shadows (spot blacks), intense deep shadow areas, minimal specular highlights, matte surfaces, film noir aesthetic, American 1928 period context

This block intentionally excludes composition-specific remnants from the source character-card prompt: full-body standing portrait, eye-level or straight-perspective shot, hand in pocket, leather briefcase, enumerated clothing, pure white background, and isolated white void. Do not reintroduce them unless a later user request explicitly overrides this close-up workflow.

Interpret `ARRI 35MM` as cinematic lens response, depth of field, exposure, and tonal rendering, not permission to add literal film grain. Keep the scene's motivated source—firelight, cold night, hospital light, dawn, or another approved background light—instead of forcing a universal amber grade.

## Anti-AI controls

- Keep large matte color planes and deliberately placed brush shapes.
- Concentrate detail at identity landmarks and story-critical props; reduce detail elsewhere.
- Avoid equal-density detail across face, clothes, floor, walls, and background.
- Avoid repeated triangular facets, random micro-cracks, strand-by-strand hair, pore-like dots, ornamental soot, fragmented reflections, and meaningless debris.
- Keep hands readable and task-specific; do not hide a failed hand under texture.
- Keep period objects functional and countable. Do not invent pseudo-lettering or symbols.
- Keep the primary visual read obvious at thumbnail size.
- Do not add film grain, noise, fog, yellowing, dirty texture, aging, paper spots, scratches, dark corners, hazy halos, turbid shadows, oversharpening, over-texturing, or complex decoration.

The first imagegen result remains a clean rectangular raw image. Once it passes narrative, identity, composition, spoiler, and mandatory-prompt checks, that exact raw image is the accepted art candidate. The mandatory prompt is the complete art-style calibration: do not automatically call a simplification skill or perform a second AI cleanup/style pass. Only deterministic panel packaging follows acceptance.
