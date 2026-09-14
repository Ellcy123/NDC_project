# NDC 角色融入场景：网页版 GPT 通用提示词

来源：ndc-character-scene-production/assets/web-gpt-character-scene-prompt.template.md
版本：2026-09-13；用户侧副本必须与本模板一致，只有【】可改。

请依据下列三张按顺序上传的参考图，为指定角色生成一张用于 NDC 固定场景的正式角色图。不要把三张图拼接、混作或忽略任何一张。

1. 第一张：局部透明白模，只负责【角色／状态】的姿势、比例、落点、朝向与可见遮挡前提。
2. 第二张：未经修改的完整原场景，只负责机位、空间、透视、光照、色调、前景遮挡和真实 UI 安全区。
3. 第三张：已批准角色卡，只负责角色身份、脸部特征、发型、服装、年代与人物识别。

生成合同：

- 场景：【SCENE_ID】；revision：【REVISION】；角色：【ACTOR_ID】；姿势／状态：【POSE_OR_STATE】。
- 只生成该角色／不可分割状态的完整独立角色像素；不加入其他角色、文字、对话框、界面、边框、水印或新场景。
- 严格遵循白模的可见动作、头身比、落点、承托与朝向；不要重设计动作。角色须有可信的落地／坐／倚靠／持物关系，不得漂浮、穿模、缺失关键可见肢体或关键道具。
- 不改变原场景机位、场景内容或 UI；真实 UI 区域必须保持无角色遮挡。后续会独立提取透明层，不要把场景背景烘焙到角色身后。
- 【ACTIVE_OR_IDLE_OR_STORY_DIRECTION】。
- 输出应适配原场景的完整像素尺寸、景深层级与光照方向；不要裁切成头像、海报、角色卡或方形详情图。

以下英文段是唯一美术风格段，必须原样保留，不翻译、不删减、不归一化空格或标点：

highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour::1.5, exaggerated drastic line weight variation, distinct heavy layered ink contours for each garment layer (shirt, jacket, skirt, tie), bolder heavier internal ink lines, flat graphic monolithic hair mass, zero internal texture or detail in hair, single solid block of black or color for hair, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean features, extreme high contrast chiaroscuro lighting, heavy use of solid black shadows (spot blacks), intense deep shadow areas, minimal specular highlights, matte surfaces, film noir aesthetic, American 1928s era context, straight perspective, 

额外剧情／可见物约束：【ONLY_IF_FROZEN_AND_SCENE_SPECIFIC】
