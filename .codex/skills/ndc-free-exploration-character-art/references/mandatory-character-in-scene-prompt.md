# Mandatory character-in-scene prompt wrapper

Use this wrapper for **every image-generation call that places one character-card subject into an existing scene image**. This includes free-exploration idle scene plates, AVG-layer reference scene plates, and baked AVG per-character scene-context masters. Every call has exactly one target person; multi-character planning does not authorize multi-character generation.

The resolved wrapper must be the first block of the prompt sent to the image model. Replace `【内容】` with the scene-specific performance direction derived from current narrative evidence. Do not omit, summarize, translate, or silently rewrite the wrapper. A scene-insertion prompt that still contains the literal placeholder `【内容】`, or does not contain this complete wrapper, is invalid and must not be sent.

## Resolve `【内容】` from the story

Build `【内容】` from the active Talk/dialogue nodes, action annotations, character profile/personality, immediate conversational objective, scene geometry, and placement contract already required by the calling skill. For AVG work, use the selected key-dialogue node rather than defaulting to the first visible frame. State concrete visible acting rather than a generic mood:

- acting verb and immediate objective;
- weight distribution and planted/support contact;
- foot angle, torso and shoulder direction;
- hands or one contained gesture;
- head direction, gaze target, and facial expression;
- camera orientation (`front`, `three-quarter`, `profile`, `side-back`, or `back`) and the narrative reason for a partly/fully back-facing pose;
- interaction partner, prop, or focal point when supported by the selected dialogue beat;
- scene type plus the resolved physical-anchor scale sentence: object, exact measured dimension, real-world estimate, character height, depth relation, ratio, target pixel envelope, and foot point;
- any required restraint that keeps a突发事件/cutaway beat out of the current stable image.

For a multi-character composition, the all-character plan supplies the other actors' fixed coordinates, gaze/contact targets, occlusion, and layer order. The current `【内容】` names only the current target character. Do not ask the model to add, redraw, or restyle another person, and do not invent unsupported props or actions merely to make the target more dramatic.

## Mandatory wrapper

```text
将图2的唯一目标角色放到图1内，角色的动作为【内容】。本次只新增这一个角色，不生成、重画或改变其他人物。人物比例必须严格遵循后续提示词中声明的场景实物标尺、人物真实身高、景深关系、目标人物框和脚点。场景的所有内容保持不变，除了给目标角色添加必要的光影外。角色的所有设计和配色以及笔触和线条等美术风格保持不变，且不增加额外的材质和细节。场景和角色的色阶保持一致，以场景的色阶为主。确保人物风格不跑偏，提供角色的美术风格提示词：
highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour::1.5, exaggerated drastic line weight variation, distinct heavy layered ink contours for each garment layer (shirt, jacket, skirt, tie, briefcase), bolder heavier internal ink lines, flat graphic monolithic hair mass, zero internal texture or detail in hair, single solid block of black or color for hair, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean features, extreme high contrast chiaroscuro lighting, heavy use of solid black shadows (spot blacks), intense deep shadow areas, minimal specular highlights, matte surfaces, film noir aesthetic, American 1928s era context, full-body portrait standing, eye-level shot, straight perspective, hand in pocket, holding leather briefcase, minimalist pure white background, isolated on white void
```

## Conflict precedence

The wrapper is mandatory, but scene-specific evidence remains authoritative:

1. The resolved `【内容】`, declared support/contact, camera orientation, and scene geometry override the legacy style-tail pose tokens `full-body portrait standing`, `eye-level shot`, `straight perspective`, `hand in pocket`, and `holding leather briefcase` whenever the character is sitting, half-crouching, bending, leaning, looking back, side-back/back-facing, viewed from another camera angle, empty-handed, or performing another supported action.
2. The instruction to keep Image 1's scene unchanged overrides `minimalist pure white background` and `isolated on white void` during a character-in-scene call. Those two tokens do not authorize replacing the scene.
3. Pure green or magenta keyed-source calls are extraction/reproduction calls, not character-in-scene calls. Do not prepend this wrapper to them; instead preserve the approved wrapper-generated character design and use the calling skill's required uniform key background.

Record the exact resolved wrapper, including the expanded `【内容】`, in the job's `prompts.md`.
