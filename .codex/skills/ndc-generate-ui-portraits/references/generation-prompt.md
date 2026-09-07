# 生成提示词与约束解释

只有角色身份、上游批准资产和职业背景依据齐备后，才将下列变量替换为具体内容。每个可复制块之前列清参考图顺序。模型名称/入口遵从用户选择及当前可用生成工具，不将历史模型名硬编码为永久要求。

## 图像参考顺序

1. 该角色通用风格角色卡：身份、服装与设定权威，不带入视角和动作。
2. `assets/ui-portrait-style-reference.png`：只提供人物画风，不复制此男性的脸、年龄、发型、胡须或服装，不复制侧脸与白底。
3. 该角色已批准通用风格肖像：生成基础，保持其身份。

## 可复制任务段

```text
以图3的通用风格肖像为基础，为 NDC 角色【角色正式名称】生成一张带职业场景背景的 UI 胸像母图，画面比例 3:4。
图1是该角色的通用风格角色卡：参考相貌、服装与角色设定，不继承图1的视角和动作。
图2是头像肖像画风参考：只继承人物的美术表现，不继承参考人物的相貌、设定、姿势和白色背景。
图3是该角色的通用风格肖像：以其为生成基础，与图1保持同一人，禁止复制图2的身份。
策划确认的职业/身份是【职业/身份】。采用与其一致的背景【场景描述】，保持 NDC 策划中的时代与环境，不增加无依据的身份标识或剧情信息。
动作：身体向【左/右】一侧偏转约15度，头部正对镜头，面无表情，直视镜头。仅需胸腔以上的完整身体部分；两侧肩膀、上半部分手臂与完整外轮廓必须在母图画面内。保留后续裁切余量。
背景采用黑色电影照片写实，安静、无噪点和细碎纹理，85mm全画幅人像镜头、f/2.0–f/2.8的浅景深观感；背景必须覆盖全画面。人物保持参考图2的插画风格，不照片化。最终母图不含文字、边框、辅助线或多个版本拼图。
下方是原始人物美术风格提示词。本任务的背景以以上职业场景要求为准；其中 off-white blank background 和 clean negative space 不用于把背景变成白底。保留脸部结构和干燥哑光材质，避免把颗粒、纸纹或厚涂写成散乱噪点；人物笔触参考图2，背景不继承人物纹理。
【在此粘贴下面完整原始风格段】
```

左右方向是当前任务的构图选择；文档未规定必须向左或向右，不应固化成跨角色默认。

## 原始人物风格段（原样保留）

<!-- SOURCE_STYLE_BLOCK_BEGIN -->
```text
classic Film Noir aesthetic, 1930s vintage illustration style, No brushstrokes on the face, Smooth brushstrokes, Dry parchment-like skin（face only）, The outermost layer of skin is covered with what appear to be granular dots, American Comic Inking, variable line weight, bold dark outer contour, graphic geometry, hard-planed facial features, sculptural face planes, planar color blocking, faceted shading, Digital Impasto, visible directional brushstrokes, thick oil paint texture, matte dry skin finish, controlled rough brushwork, The hairstyle brushstrokes are simplified, hair simplified into large graphic masses, simplified/blocky hair, hair treated as a single solid mass, zero fine strand rendering, minimal internal hair texture, broad grouped hair shapes, clean large hair clumps, summarized hair volume, low-saturation earth tones, warm sepia browns, charcoal blacks,no highlights， subtle vintage paper grain, high-contrast chiaroscuro, dramatic side lighting, deep dramatic shadows, compressed values, off-white blank background, clean negative space
```
<!-- SOURCE_STYLE_BLOCK_END -->

此段取自 `UI肖像skill工作流程.docx`，不得在维护时静默删词、改字或改成表情/通用肖像提示词。职业场景对白底尾词的优先解释来自本文档明确的任务目的及现有全部示例。面部“无笔触”和“颗粒/厚涂”并存时以已给图像画风裁决，不抹平面部结构、不新增斑点噪声。`1930s vintage illustration style` 是艺术语言，不能据此改变策划中故事年代。
