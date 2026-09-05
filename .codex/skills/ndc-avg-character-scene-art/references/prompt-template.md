# AVG key-dialogue per-character prompt templates

Replace every bracketed field from the accepted all-character plan. The complete ordered prompt set for **all** characters must already exist in `prompts.md` before the first image call. Every image call creates exactly one target person.

Before every per-character scene-context call, read [the mandatory character-in-scene wrapper](../../ndc-free-exploration-character-art/references/mandatory-character-in-scene-prompt.md), expand `【内容】` for the current target only, and prepend the complete resolved wrapper before `Use case:`. A missing wrapper, unresolved placeholder, missing physical-anchor scale sentence, or incomplete all-character plan blocks the call. Keyed-source calls are extraction calls and do not receive the wrapper.

## Per-character scene-context reference plate

```text
[PREPEND THE COMPLETE RESOLVED MANDATORY CHARACTER-IN-SCENE WRAPPER HERE]

Use case: compositing
Asset type: NDC Unity AVG key-dialogue per-character scene-context master
Input images:
- Image 1: exact prepared context crop; immutable camera, scene, geometry, and scale-anchor authority
- Image 2: [TARGET CHARACTER] card; identity, age, face, hair, body proportions, costume, accessories, and period authority
- Image 3: U1 AVG character asset; NDC rendering-density and facial-plane reference only; do not copy identity, clothing, pose, or scale
- Image 4 (optional): deterministic current composite or blocking overlay; accepted people and empty target box are coordinate, gaze, contact, and occlusion references only; do not redraw any existing person
Sequential-production authority: the all-character plan and every prompt are complete. This call adds exactly one new person, [TARGET CHARACTER]. Do not add, regenerate, redraw, or restyle another person.
Coordinate authority: Image 1 is full-source crop [CROP_X, CROP_Y, CROP_WIDTH, CROP_HEIGHT]. Return the complete crop with identical aspect ratio and no crop, padding, zoom, rotation, or reframing. Target master box [MASTER BOX], normalized box [NORMALIZED BOX], crop-space box [CROP BOX], foot/contact points [LANDMARKS].
Key-dialogue authority: core node/range [KEY NODE/RANGE], evidence [EXACT LINES], visual-center reason [SELECTION REASON]. At this instant [TARGET CHARACTER] knows/wants [KNOWLEDGE/OBJECTIVE]. Exclude these突发事件/cutaway beats: [EXCLUDED EVENT BEATS].
Scene-scale authority: scene type [SCENE TYPE]. Closest reliable same-depth anchor [OBJECT AND EXACT MEASURED DIMENSION] is estimated as [REAL-WORLD VALUE/RANGE] with [CONFIDENCE] confidence from [BASIS], spans [ANCHOR PIXELS] in the untouched crop, and relates to the target foot lane by [DEPTH CUE]. Secondary anchor when needed: [SECOND ANCHOR OR NONE].
Character scale authority: [TARGET CHARACTER] canonical height [HEIGHT CM] from [ACTIVE PROFILE PATH]. Explicit relationship: [COMPLETE CHARACTER-TO-OBJECT RATIO SENTENCE]. Target projected head-to-foot height [HEIGHT PX], shoes/contact at [FOOT POINT], perspective adjustment [ADJUSTMENT].
AVG UI-safe composition: reserve the [LEFT OR RIGHT] TalkPanel rectangle [SOURCE-SPACE RECT] free of the complete target silhouette, face, limb, assigned prop, shadow, and contact point.
Performance direction: based on [PERSONALITY TRAITS, POWER RELATION, AND IMMEDIATE OBJECTIVE], [ACTING VERB]. Express it through [WEIGHT, FEET, TORSO, SHOULDERS, HANDS/GESTURE, HEAD, CAMERA ORIENTATION, GAZE, EXPRESSION]. Orientation is [FRONT / THREE-QUARTER / PROFILE / SIDE-BACK / BACK] because [NARRATIVE/COMPOSITION REASON]. Supported sitting, half-crouching, bending, leaning, turning, looking back, or lowered-head poses are allowed when declared.
Blocking relationship: orient toward [PARTNER / FOCAL POINT] at fixed scene coordinate [TARGET COORDINATE] on [GAZE/TORSO AXIS]. Preserve [RELATIVE FOOT LANDMARKS], [INTERPERSONAL DISTANCE], [OCCLUSION/LAYER ORDER], [CROSS-LAYER CONTACTS], and assigned prop ownership [PROP OWNER]. Other people are references only and must not be generated in this call.
Scene support: [standing on recorded clear floor / exact existing support object and contact area]. Never create or modify support furniture.
Style/lighting: preserve NDC graphic-noir illustrated realism, crisp ink-like contours, deliberate color planes, restrained texture, natural anatomy, and [SOURCE LIGHT/SHADOW DIRECTION].
Hard invariants: preserve Image 1's camera, framing, architecture, furniture, props, palette, floor, and lighting. Include exactly one newly generated target person and only that person's assigned prop. Preserve the target's complete hair, fingers, clothing edges, and shoes. Keep the whole target outside the panel rectangle.
Avoid: extra person, regenerated accepted person, first-frame default posing, excluded event action, generic mannequin stance, unsupported back-facing pose, repeated nearby-character silhouette, disconnected gaze, wrong object-to-character ratio, arbitrary shrinkage, scene redesign, invented support, camera shift, crop, zoom, identity drift, costume redesign, duplicate limbs, text, UI, or watermark.
```

The reference plate is never the final background. Accept it only as the current target's pose, scale, contact, relationship, and lighting authority.

## Single-person keyed source

```text
Use case: background-extraction
Asset type: NDC Unity AVG key-dialogue single-character keyed source
Input images:
- Image 1: approved per-character scene-context master; target pose, camera orientation, scale, contact landmarks, and lighting authority
- Image 2: [TARGET CHARACTER] card; identity and costume verification only
Sequential-production authority: reproduce exactly one person, [TARGET CHARACTER]. Do not include any partner, accepted character, interaction group, or unassigned shared prop.
Coordinate contract: source crop [CROP RECT], master canvas [MASTER SIZE], frozen master-space box [MASTER BOX], normalized box [NORMALIZED BOX], mapped crop-space box [CROP BOX], mapped head/foot/body-axis landmarks [LANDMARKS].
Scene-scale contract: preserve canonical height [HEIGHT CM], physical anchor [OBJECT/DIMENSION/REAL VALUE], explicit ratio [RATIO SENTENCE], projected height [HEIGHT PX], and foot/contact point [FOOT POINT].
Key-dialogue state: preserve [ACTING VERB, POSE, CAMERA ORIENTATION, GAZE, EXPRESSION, ASSIGNED PROP, CONTACT LANDMARKS] from node [KEY NODE]. Do not neutralize or front-face the performance during extraction.
Primary request: reproduce only the target and assigned prop on one perfectly uniform flat [#00FF00 OR #FF00FF] background for deterministic Alpha extraction.
Composition/framing: use the source crop's aspect ratio and keep the target near [NORMALIZED BOX]. Preserve full-body scale, margins, body axis, shoes, and contacts so one uniform scale plus translation can match the frozen crop-space box.
Backdrop: uniform flat [KEY COLOR] edge to edge; no gradient, texture, floor, horizon, architecture, furniture, reflection, scene fragment, cast shadow, ambient shadow, or checkerboard.
Avoid: second person, interaction group, missing anatomy, clipped shoe, duplicate limb, key spill, scene remnant, centered portrait reset, camera/orientation change, identity drift, or new prop.
```

Generate a separate transparent/keyed shadow only when the placement contract requires one. Anchor it to an explicitly recorded shoe/contact point rather than a generic image-edge center.

## Targeted corrections

| Failure | Response |
|---|---|
| Character scale conflicts with nearby furniture | Re-check scene type, exact anchor dimension, real-world estimate/range, depth lane, source-pixel span, ratio sentence, and secondary anchor before regenerating. |
| More than one person appears | Reject the result and regenerate only the named target; never accept or extract a multi-person source. |
| Character defaults to a front-facing mannequin | Restore the personality/objective acting verb and declared asymmetric pose/camera orientation from the key-dialogue plan. |
| Back/side-back pose loses identity | Strengthen recorded silhouette, hair, costume, accessory, and posture cues without turning the person forward unless the plan changes. |
| Partner relationship is lost | Keep the partner as a fixed coordinate/gaze/contact target and regenerate only the current person; do not generate both together. |
| Shared hand/prop contact is wrong | Re-check prop ownership, both layers' contact landmarks, and occlusion; re-plan if independent layers cannot preserve the contact. |
| Master changes underfoot/support geometry | Reject it as a coordinate master before keyed generation; matching canvas dimensions are insufficient. |
| Keyed target shifts or resizes | Uniformly align the extracted Alpha to the frozen crop-space box and contacts; never infer placement from the key-canvas center. |
| Actor or prop enters the TalkPanel rectangle | Recompose at the correct height and reconfirm; do not shrink the actor to clear the UI. |
| Scene changes in the reference plate | Do not paste plate pixels. Composite only the accepted single-person RGBA layer onto the untouched source. |
| Character floats | Fix the per-character scene-master pose/contact line; do not hide it with a larger shadow. |
