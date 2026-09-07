# Prompt templates

Use these as structured templates. Replace bracketed values with the declared placement contract. Keep input-image roles explicit in every call.

The idle/click templates below are for free-exploration mode. For AVG-layer mode, use the named-state templates and the exact state list supplied by `ndc-avg-character-scene-art`; do not invent an idle/click pair.

The default extraction color is `#00FF00`. If green costume, hair, jewelry, or props touch the silhouette, replace every `#00FF00` below with uniform `#FF00FF` and run the packager with `--key magenta`.

For every template below whose heading contains `scene plate`, first read [mandatory-character-in-scene-prompt.md](mandatory-character-in-scene-prompt.md), expand `【内容】` from narrative and performance evidence, and prepend that complete resolved wrapper before `Use case:`. The wrapper is mandatory; a literal unresolved `【内容】` blocks the image call. Green/magenta source templates are keyed extraction calls and do not receive the scene-insertion wrapper.

## Idle scene plate

```text
[PREPEND THE COMPLETE RESOLVED MANDATORY CHARACTER-IN-SCENE WRAPPER HERE]

Use case: compositing
Asset type: NDC Unity free-exploration NPC idle-state scene plate
Input images:
- Image 1: exact scene crop; edit target and immutable scene base
- Image 2: character card; identity, age, body, hair, costume, jewelry, and period reference
- Image 3: U1 scene-NPC reference; rendering density, silhouette, scale, and environment-lighting reference only
Primary request: Insert exactly one full-body [CHARACTER] into Image 1 at the declared location as if painted for this existing NDC scene.
Scene-scale authority: scene type [SCENE TYPE]. Closest reliable same-depth anchor [OBJECT AND EXACT DIMENSION] is estimated as [REAL-WORLD VALUE/RANGE] with [CONFIDENCE] confidence from [BASIS], spans [ANCHOR PX] in the untouched crop, and relates to the target foot lane by [DEPTH CUE].
Character scale authority: canonical height [HEIGHT CM] from [ACTIVE PROFILE PATH]. Explicit ratio: [COMPLETE CHARACTER-TO-OBJECT SCALE SENTENCE]. Target projected head-to-foot height [HEIGHT PX] at [DEPTH/REFERENCE BASIS].
Composition/framing: preserve Image 1's exact crop and camera. Place the visible character around [VISIBLE BBOX OR LANDMARKS]. Shoes rest at source-scene y=[FOOT LINE]. Keep the entire body visible at the declared profile-derived scale and in readable middle ground.
Performance direction: from [PERSONALITY/LOCAL-ACTIVITY BASIS], [IDLE ACTING VERB / LOCAL ACTIVITY]. Express it through [WEIGHT, FOOT ANGLE, TORSO, SHOULDERS, HANDS, CAMERA ORIENTATION AND REASON, GAZE, EXPRESSION] with a natural asymmetric silhouette. A justified profile, side-back, or back-facing pose is allowed.
Style/medium: match NDC's graphic-noir illustrated realism: crisp ink-like edges, intentional color planes, restrained texture, natural full-body anatomy.
Lighting/mood: [LIGHT DIRECTION AND COLOR]; match the scene's shadow density and floor perspective.
Constraints: preserve the character card's identity and costume. Preserve scene architecture, furniture, camera, and framing. Exactly one person; no text, UI, watermark, extra props, duplicate limbs, or floating feet.
Avoid: mannequin stance, symmetrical parallel feet, both arms hanging straight, generic idle portrait, identity drift, arbitrary character shrinkage, near-camera crowding, generic young face, costume redesign, photorealism, anime styling, hard patch edges, scene redesign.
```

## Idle green source

```text
Use case: background-extraction
Asset type: NDC Unity free-exploration NPC idle green-screen source
Input images:
- Image 1: approved idle scene plate; rendered identity, pose, scale, and lighting master
- Image 2: character card; identity/costume verification only
Primary request: Extract exactly [CHARACTER] from Image 1 onto one perfectly uniform flat #00FF00 background.
Constraints: preserve face, age, hair, body proportions, costume, jewelry, pose, gaze, expression, lighting, full-body scale, margins, and foot line. Include all hair, fingers, skirt/trouser edges, and both shoes. No cast shadow.
Scene/backdrop: flat #00FF00 edge to edge; no gradient, texture, checkerboard, floor, horizon, or scene remnants.
Avoid: redraw, restyle, identity drift, crop change, green spill, printed transparency grid, text, UI, watermark.
```

## Click green source

```text
Use case: identity-preserve
Asset type: NDC Unity free-exploration NPC click-state green-screen source
Input images:
- Image 1: approved idle master; identity, rendering, costume, lighting, full-body scale, and framing master
- Image 2: character card; identity/costume verification
- Image 3: approved scene plate; camera-relative lighting and physical context
Primary request: Create the click-state variant of the same [CHARACTER]. Change only the pose and expression below.
Pose: [CLICK POSE]. Keep both shoes planted on the same horizontal foot line. Preserve full-body scale and contained body movement.
Subject invariants: same face, age, hair, body proportions, skin tone, costume, jewelry, and scene-relative light.
Composition/framing: full body visible with stable margins and foot anchor.
Scene/backdrop: one perfectly uniform flat #00FF00 background; no floor, horizon, scene, gradient, texture, checkerboard, or shadow.
Constraints: exactly one person; crisp silhouette; no extra accessories, text, UI, or watermark.
Avoid: identity drift, exaggerated gesture, walking, crossed feet, floating feet, costume change, camera change, crop change.
```

## AVG-layer reference scene plate

```text
[PREPEND THE COMPLETE RESOLVED MANDATORY CHARACTER-IN-SCENE WRAPPER HERE]

Use case: compositing
Asset type: NDC Unity AVG independently controlled character-layer reference plate
Input images:
- Image 1: exact active AVG scene crop; edit target and immutable camera/context base
- Image 2: character card; identity, age, body, hair, costume, jewelry, and period authority
- Image 3: U1 AVG or transparent-character reference; rendering density and facial-plane treatment only
- Image 4 (optional): deterministic current composite or blocking overlay; accepted people are fixed coordinate, gaze/contact, and occlusion references only and must not be redrawn
Primary request: Insert exactly one full-body [CHARACTER] into Image 1 in state [STATE NAME], at the declared AVG position, as a placement and lighting master for later transparent extraction.
Coordinate authority: Image 1 is full-source crop [CROP_X, CROP_Y, CROP_WIDTH, CROP_HEIGHT]. Return the complete crop with identical aspect ratio and no crop, padding, zoom, rotation, or reframing. Freeze the actor box and landmarks in this crop coordinate system before keyed generation.
Key-dialogue authority: the ensemble plan centers on [KEY NODE/RANGE AND EXACT DIALOGUE EVIDENCE]. This target expresses [KEYFRAME ROLE] and is visible from [FIRST NODE] through [LAST NODE]; [ENTRANCE / EXIT / REPLACEMENT BEHAVIOR]. Do not substitute the first visible state or an excluded突发事件/cutaway beat.
Sequential-production authority: the full ensemble plan and every character prompt are complete. This call generates exactly one new target, [CHARACTER]. Other characters exist only as fixed coordinate, gaze, contact, occlusion, or optional deterministic-composite references; do not add or redraw them.
Scene-scale authority: scene type [SCENE TYPE]. Closest reliable same-depth anchor [OBJECT AND EXACT DIMENSION] is estimated as [REAL-WORLD VALUE/RANGE] with [CONFIDENCE] confidence from [BASIS], spans [ANCHOR PX], and relates to the target foot lane by [DEPTH CUE].
Character scale authority: canonical height [HEIGHT CM] from [ACTIVE PROFILE PATH]. Explicit ratio: [COMPLETE CHARACTER-TO-OBJECT SCALE SENTENCE]. Target projected head-to-foot height [HEIGHT PX] at [DEPTH/REFERENCE BASIS]. Do not shrink this character because it is independent, observing, or rear-layered without a proven farther foot position.
AVG UI-safe composition: reserve the [LEFT OR RIGHT] TalkPanel rectangle [SOURCE-SPACE RECT]. The complete actor silhouette and any prop must remain outside it.
Composition/framing: preserve Image 1 exactly. Place the visible character around [VISIBLE BBOX OR LANDMARKS], with shoes at source-scene y=[FOOT LINE] and layer order [LAYER ORDER]. Use readable middle ground and the declared projected height.
Performance direction: from [PERSONALITY/POWER-RELATION BASIS], [ACTING VERB AND IMMEDIATE CONVERSATIONAL OBJECTIVE]. Express it through [WEIGHT, FOOT ANGLE, TORSO, SHOULDERS, HANDS/CONTAINED GESTURE, HEAD, CAMERA ORIENTATION AND REASON, GAZE, EXPRESSION]. Standing is not the default; a supported sitting, half-crouching, bending, leaning, turning, side-back, or back-facing key pose is allowed.
Blocking relationship: orient toward [CONVERSATION PARTNER / FOCAL POINT] on [GAZE/TORSO AXIS]. Preserve [RELATIVE FOOT LANDMARKS] and [INTENDED INTERPERSONAL DISTANCE / GROUP ENVELOPE] from the AVG handoff so this layer reads as part of the exchange rather than an isolated portrait.
Lighting/mood: [LIGHT DIRECTION AND COLOR]; match the active AVG plate's perspective and shadow density.
Constraints: preserve identity and costume; preserve all scene pixels except the target character preview region; exactly one newly generated person; no added/redrawn partner, text, UI, watermark, unassigned prop, duplicate limbs, or floating feet.
Avoid: baking other temporal states into the plate, mannequin stance, repeated nearby-character pose, disconnected gaze, detached edge placement, unjustified excessive conversational spacing, panel-safe overlap, arbitrary shrinkage, near-camera crowding, scene redesign, identity drift, costume redesign, hard patch edges.
```

## AVG-layer named-state green source

```text
Use case: background-extraction
Asset type: NDC Unity AVG independent character state [STATE NAME]
Input images:
- Image 1: approved AVG reference scene plate or previously approved state master
- Image 2: character card; identity/costume verification only
Primary request: Reproduce exactly [CHARACTER] in state [STATE NAME] on one perfectly uniform flat #00FF00 background for deterministic transparent extraction.
Timeline role: visible from [FIRST NODE] through [LAST NODE]; [ENTRANCE / EXIT / REPLACEMENT BEHAVIOR].
Scale authority: preserve canonical height [HEIGHT CM], physical-anchor ratio [ANCHOR/RATIO SENTENCE], approved projected height [HEIGHT PX], depth lane, and the panel-safe placement master.
Coordinate contract: source crop [CROP RECT], master canvas [MASTER SIZE], frozen master-space box [MASTER BOX], normalized box [NORMALIZED BOX], mapped crop-space box [CROP BOX], mapped head/foot/body-axis landmarks [LANDMARKS]. Use the crop's aspect ratio and place the actor near the same normalized box; do not center the actor by default.
Constraints: exactly one target person. Preserve face, age, hair, proportions, costume, lighting, full-body scale, declared acting posture and camera orientation, gaze target, center of gravity, margins, and foot line. Include all hair, fingers, clothing edges, and both shoes. No other person and no cast shadow unless explicitly requested as a separate asset. Final deterministic packaging will align the Alpha to the frozen crop-space box, so preserve a pose and camera angle that can match it with one uniform transform.
Scene/backdrop: flat #00FF00 edge to edge; no gradient, texture, checkerboard, floor, horizon, or scene remnants.
Avoid: invented idle/click pose, redraw, restyle, identity drift, crop change, green spill, printed transparency grid, text, UI, watermark.
```

## Targeted retries

Use one correction at a time and restate invariants.

| Failure | Targeted correction |
|---|---|
| Opaque checkerboard instead of alpha | Stop treating it as transparent; request a uniform `#00FF00` source and package deterministically. |
| Face/age drift | Re-anchor with the character card and accepted idle master; change only face identity/age while preserving pose and canvas. |
| Click state jumps | Re-anchor to idle full-body scale, both planted shoes, and the exact foot line; change only gesture/expression. |
| Green spill | Recreate a cleaner uniform green source before increasing key aggressiveness. Do not erase costume/hair to hide spill. |
| Scene is repainted | Keep the plate only as context. Final preview must composite the extracted sprite onto the untouched original scene. |
| Floating feet | Correct stance/contact in the scene plate first; do not solve a wrong pose with a larger procedural shadow. |
| Same-depth height ratio is wrong | Re-anchor to canonical profile heights and uniform scale; do not use role importance as a size cue. |
| Character scale conflicts with the nearby sofa/door/counter | Re-check scene type, the exact measured anchor dimension, real-world estimate, depth lane, pixel span, and ratio sentence; use a second anchor when ambiguous before regenerating. |
| AVG layer enters the panel-safe rectangle | Move it to a valid floor position at the same correct projected height and reconfirm; do not shrink it. |
| Character reads as a stiff generic cutout | Return to the reference scene plate and define one acting verb plus asymmetric weight, torso, hands, and gaze; preserve the corrected performance during key extraction. |
| Composition needs stronger depth or hierarchy | Use a narratively justified profile, side-back, or back-facing orientation and record the identity cues; do not merely turn a character away at random. |
| More than one person appears in a generation | Reject the result. Keep the all-character plan, but regenerate only the current target person; never accept a multi-person source or interaction-group Alpha. |
| AVG character feels isolated from the conversation | Reconnect gaze/torso to the declared partner and restore the handoff's relative foot points and group envelope; do not solve UI safety by pushing the actor to a distant edge. |
| AVG green source is centered and the scene-relative position is lost | Ignore the green-canvas center; align only from the previously frozen crop-space actor box and contact landmarks. If that contract was never recorded, return to the scene plate instead of guessing. |
| AVG scene master changes the local floor/support or nearby anchors | Reject the scene master before keyed generation; identical canvas shape does not make locally redrawn geometry mappable. |
