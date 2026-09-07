---
name: ndc-free-exploration-character-art
description: "Create one scene-grounded NDC transparent character at a time for free-exploration idle/click sprites or AVG independent layers, using canonical profile height, semantic physical-object scale anchors, personality/story-driven posing, real-alpha extraction, shared canvas/foot alignment, panel-safe placement, and QA previews. Use for 自由探索场景NPC、待机/点击双状态、AVG人物进退场、AVG独立人物层. Do not use for permanently baked AVG characters,突发事件演出, or formal table mounting."
---


## Production paths and closeout

Run `python scripts/art_pipeline/ndc_art.py paths` from either configured repository root before reading or writing production files. The Git-managed launcher resolves `{PLANNING_ROOT}`, `{ENGINE_ROOT}`, and `{WORK_ROOT}` from this machine's ignored `ndc.local.json` or `NDC_PLANNING_ROOT` / `NDC_ENGINE_ROOT` / `NDC_ART_WORK_ROOT`. These names are logical roots, not literal folders or requirements for a drive letter or repository layout. Read `{PLANNING_ROOT}/docs/美术生产工作区.md` and the dependency setup it links. Never copy another person's machine paths into shared rules.

Create the task with `python scripts/art_pipeline/ndc_art.py workspace create --name NAME --kind KIND`. `{JOB_PAYLOAD}` means the exact returned `payload` path; put candidates, revisions, QA, copied inputs, and prepared delivery there. Use `python scripts/art_pipeline/ndc_art.py run SKILL_NAME SCRIPT_NAME ...` for this skill's versioned scripts. Resolve another skill with `python scripts/art_pipeline/ndc_art.py skill SKILL_NAME`; its `references/`, `scripts/`, and `assets/` are relative to the returned `skill_root`, never a compatibility entry's directory. All project-owned helper scripts and schemas must be present in Git; do not depend on private scripts in a home folder, scratch directory, or an old machine checkout. Install third-party runtimes and libraries as documented, without committing credentials or virtual environments.

Resolve character cards through `{PLANNING_ROOT}/美术资产交付/角色/角色索引.json` and expression pairs through `{PLANNING_ROOT}/美术资产交付/角色表情/表情索引.json`; retain the selected asset hash and approval state. A card does not imply approval of a portrait, expression set, or new generated asset. Other input placeholders in examples must be replaced with the task's explicitly selected, existing inputs before execution.

After the user approves the specific finished candidate, prepare and verify the engine delivery under the shared workflow. Clean closed-job payloads only through its state-aware closeout; preserve pending review and active work. These rules replace historical output-directory defaults in this skill, while all art-quality and user-approval gates still apply. Historical case paths remain provenance, not default output destinations. Missing external references or validators remain unresolved dependencies; never silently substitute another image or claim PASS.

# NDC Free-Exploration Character Art

Create scene-grounded transparent character art from an NDC character card. The workflow has two modes:

- **Free-exploration mode**: deliver two switch-safe sprites, idle (`ResPath`) and click (`ClickResPath`).
- **AVG-layer mode**: deliver exactly the independently controlled entrance, exit, dialogue, or action states required by the AVG timeline. Do not invent idle/click states when the AVG only needs named performance states.

Both modes may include an optional separate shadow and deterministic full-scene placement previews. Every generated person uses one canonical profile height and a perspective-derived projected height; independent or secondary status is never a reason to shrink a character arbitrarily.

Projected height is scene-specific. Never carry a fixed pixel height from another room or choose it only from canonical centimeters. Resolve the camera, floor contact, depth lane, vanishing geometry, local human-scale anchors, body orientation, and high-angle foreshortening together. When an approved scene-context plate exists, its measured actor envelope and contact geometry become the hard packaging target.

Before every scene-plate call, classify the scene and complete the semantic physical-anchor contract in [references/character-scale.md](references/character-scale.md): closest reliable same-depth object, exact measured dimension, estimated real-world value/range, basis, confidence, source-pixel span, depth cue, optional second anchor, and explicit character-to-object ratio sentence. Do not treat the nearest two-dimensional object as a valid scale reference when it is on another depth lane.

This is an art-production skill. Do not edit formal Excel, generated JSON/bytes, Unity import settings, prefabs, or table references unless the user separately asks for formal mounting. Do not use this skill for a character that must be permanently baked into an AVG background; use `ndc-avg-character-scene-art` for that portion. When that skill routes an `AVG-layer` handoff here, preserve its scene coordinates, timeline states, and layer order.

## Ground the character in existing scene geometry

The source scene is immutable. Use it to choose scale, foot line, occlusion, and acting, but never create, remove, move, repaint, or reshape its furniture, props, architecture, or layout in the generated reference plate or placement preview.

- A seated or supported pose requires a specific chair, sofa, bench, desk, rail, or prop that is visibly present in the source scene. Record the support object and contact area in `placement.md`.
- When no appropriate support exists, choose a standing pose on an unobstructed, readable floor plane. Do not ask the model to invent a chair, sofa, table, or other environmental support.
- Treat a newly invented or altered scene object as a generation failure, not as a valid background variation. The transparent deliverable must still be previewed against the untouched source scene.

## Select the mode from the deliverable

Use free-exploration mode when the runtime needs the conventional idle/click pair. Use AVG-layer mode whenever an AVG character must enter, exit, hide, reappear, change action/position, or remain independently controllable over a clean background. The scene type alone does not choose the skill; transparent character-layer delivery does.

For AVG-layer mode, require or derive a handoff containing the scene, character card, state names, visible dialogue-node ranges, pose/expression per state, crop, scene position, canvas, foot line, light/shadow, occlusion, and layer order. If these cannot be determined from the dialogue/configuration, stop before generation and request the missing staging decision.

The AVG-layer handoff must also contain the canonical height and active profile path, projected pixel height and depth basis, accepted scene-master path, master actor envelope/head/foot/body-axis measurements, registration tolerance, plus the selected TalkPanel side and mapped source-space safe rectangle. Preserve these values; do not reinterpret the layer as a smaller "background" performer.

For AVG-layer mode, also require one frozen coordinate chain from the parent AVG composition: full-source crop rectangle, scene-master canvas dimensions, actor box and landmarks in master pixels, their normalized coordinates, and the mapped crop-space actor box. Do not accept a handoff that contains only a guessed `visible-height` and foot line.

## Act the declared state, not a generic idle

Every state needs readable but contained body language. In free-exploration mode, derive idle/click acting from the character profile, personality, and local activity. In AVG-layer mode, preserve the selected key-dialogue acting verb and full-scene blocking supplied by `ndc-avg-character-scene-art`: personality basis, weight distribution, feet, torso, shoulders, hands, head/gaze, expression, conversation partner or focal point, relative foot/spacing landmarks, and occlusion.

Do not default to feet parallel, both arms hanging straight, a front-facing torso, or the same three-quarter pose used by nearby actors. Supported poses may be standing, sitting, half-crouching, bending, leaning, looking back, lowering the head, or another readable static key pose. `side-back` or `back` orientation is allowed when the story and composition justify it; record the reason and preserve identity through silhouette, hair, costume, and posture. A later-entering layer should look as though it belongs to the current exchange, not like a detached portrait pasted at the edge of the scene.

Every image call generated by this skill contains exactly one target person. In an AVG ensemble, the parent skill plans all people first, but this skill receives and produces one independent character layer at a time. Never create a multi-person source or interaction-group Alpha.

## Required companion skill

Use the available `imagegen` skill for every AI image generation or edit. Read its `SKILL.md` before the first image call. Stay on its built-in tool path unless the user explicitly chooses its CLI/API fallback.

Before generating, read:

- [references/ndc-asset-conventions.md](references/ndc-asset-conventions.md) for NDC paths, coordinate semantics, state pairing, and formal-scope boundaries.
- [references/character-scale.md](references/character-scale.md) to resolve/write the canonical profile height and derive scene-relative projected scale.
- [references/mandatory-character-in-scene-prompt.md](references/mandatory-character-in-scene-prompt.md) immediately before every scene-plate image call. Prepend its complete mandatory wrapper and expand `【内容】` from the active narrative/performance evidence. Do not send a scene-insertion prompt when the wrapper is absent or the placeholder remains unresolved.
- [references/prompt-templates.md](references/prompt-templates.md) for the applicable single-character image-generation prompts and targeted retries.

## Default output scope

Unless the user names another destination, stage free-exploration work under:

```text
<job>/payload/free_exploration_art/<character>_<scene>/
```

For AVG-layer mode, use the output location supplied by `ndc-avg-character-scene-art`; otherwise stage under:

```text
<job>/payload/avg-layer-<character>-<scene>/
```

Never overwrite a formal art asset during a test. Preserve every original character card and scene image.

## Workflow

### 1. Resolve the source set

Identify:

- narrative or test requirement;
- the active character-profile path and canonical height, writing one art-unification height into that active profile when no explicit value exists;
- one character card;
- one scene background;
- scene type, intended foot position, and candidate physical scale anchors near the same depth lane;
- one or two U1 transparent character references appropriate to the selected mode, with a similar full-body scale or pose;
- in AVG-layer mode, the dialogue nodes and action annotations that define every required state and its visibility range.

Inspect every selected image with `view_image`. When the user explicitly permits a random test, choose a character card and an empty scene with a readable floor plane and proceed without asking. Do not infer permission to mount the result formally.

Inspect any proposed support object at native size before choosing a seated or supported pose; otherwise select a clear standing position.

### 2. Declare the placement contract before generation

Tell the user the chosen scene and character, then state all of these before the first image call:

- source-scene pixel dimensions;
- scene type; canonical height, profile path, explicit-versus-inferred status; intended foot point and floor-depth lane; closest reliable same-depth physical anchor and exact measured dimension; estimated real-world value/range, basis, confidence, source-pixel span, optional second anchor, depth cue, explicit character-to-object ratio sentence, and provisional projected head-to-foot pixel height;
- working crop rectangle `(x, y, width, height)` in source pixels;
- target visible-character top-left or bounding region in source pixels;
- intended foot line in source pixels;
- selected mode and required state names;
- acting verb plus personality/story basis, weight distribution, foot angle, torso/shoulder angle, hand placement or contained gesture, camera orientation (`front`, `three-quarter`, `profile`, `side-back`, or `back`) and its reason, gaze, and expression for every required state;
- conversation partner or focal point and, in AVG-layer mode, the supplied conversational axis, relative foot landmarks, intended interpersonal distance or group envelope, and reason for any wide separation;
- standing foot-contact point, or the exact existing support object and its source-pixel contact area for a seated/supported pose;
- in AVG-layer mode, first/last visible node, entrance/exit or replacement behavior, and layer order;
- in AVG-layer mode, selected TalkPanel side and the render/source safe rectangles that the actor Alpha must not enter;
- gaze, lighting direction, and shadow direction;
- whether any foreground object should occlude the character.

Save the same information in `placement.md`. Coordinates use the top-left origin. The final runtime position is the transparent sprite canvas's top-left, not the visible subject's top-left; update the manifest after packaging.

Save the complete resolved prompt for every state in `prompts.md` before the first image call for this character. When invoked from an AVG ensemble, do not proceed until the parent all-character plan, generation order, shared-prop ownership, and every character prompt are already complete.

After the reference scene plate is accepted, update `placement.md` with its path and each actor's realized crop-relative envelope, head point, foot/support-contact points, projected body-axis direction, group offsets, and final packaging height. The initial estimate must not remain the only scale authority.

For AVG-layer mode, freeze the actor's box while the scene composition is made. Record all three representations before generating the key source:

- scene-master pixels;
- normalized coordinates relative to the complete master canvas;
- source-crop pixels obtained by separate X/Y mapping.

The full-source placement is the crop origin plus the crop-relative point. Never infer it from where the generator centers the subject on a later green canvas. If the master output is not the same pixel size as the crop, it is usable only when it preserves the complete crop with the same aspect ratio and no padding, cropping, or reframing. Validate the actor's local floor/support contact and nearby source anchors before accepting that mapping.

### 3. Make the exact scene crop

Crop the source background deterministically at the declared rectangle. Do not resize the crop before image generation. A `1536x1024` working crop is a useful default when it contains the full body, floor contact, nearby architecture, and main light source; use another size when the scene requires it.

Keep the original scene untouched. The generated scene plate is a lighting, scale, pose, and identity approval artifact, not the final free-exploration background.

### 4. Generate and approve the reference scene plate

Before composing the rest of the scene-plate prompt, expand and prepend the complete wrapper from `references/mandatory-character-in-scene-prompt.md`. Derive `【内容】` from the declared state, character profile, local activity or dialogue timeline, concrete body language, gaze/focal relationship, and deferred-action boundary. Save the exact resolved wrapper in `prompts.md`.

Call built-in image generation with explicitly labeled roles:

- Image 1: exact scene crop and edit target;
- Image 2: character identity and costume card;
- Image 3: U1 NPC rendering/scale reference only.
- Image 4 when supplied by an AVG parent plan: deterministic current composite or blocking overlay for fixed partner coordinates, gaze/contact targets, and occlusion only; do not redraw its people.

Place exactly one full-body target character in the required state at the declared location, physical-anchor ratio, canonical projected height, and personality/story-specific pose. Preserve the scene camera, geometry, furniture, props, and layout exactly. In AVG-layer mode, judge the actor against the frozen all-character plan or deterministic blocking preview: gaze and torso must connect to the declared partner/focal point, and separate extraction must preserve the accepted relationship distance. Reject an extra person, wrong object-to-character ratio, generic mannequin posture, unsupported back-facing pose, duplicated nearby-character posing, detached edge placement, identity drift, wrong period clothing, floating feet, incorrect perspective, arbitrary shrinkage, near-camera crowding, AVG safe-zone overlap, incompatible light, an invented/altered environmental object, missing anatomy, or a hard rectangular patch.

Treat scale as an integrated scene judgment. Check the actor against same-depth door/furniture/human-use anchors and the scene's depth construction, not a global pixels-per-centimeter preset. In steep overhead or oblique views, the approved plate must show the correct projected body axis and foreshortening rather than a conventional upright character-card silhouette.

Verify the generated plate against the recorded physical-anchor dimension and ratio sentence. If the anchor and actor are at comparable depth, their measured pixel ratio must agree with the real-world ratio within the declared perspective/tolerance; a plausible-looking figure is not enough.

Once the plate is visually accepted, measure its actor geometry. The plate is authoritative for projected scale, foot/contact placement, body axis, and blocking, while the untouched source remains authoritative for all environment pixels. If the plate changes the underfoot floor, support object, or local perspective enough to prevent exact source mapping, reject it as a scale master.

Do not proceed from a visually plausible plate directly to a centered green portrait. First freeze the actor box and landmarks in crop coordinates. For AVG-layer mode, prefer a green canvas with the same aspect ratio as the source crop and request the actor in the same normalized box, with the same margins, body axis, and contact geometry.

Do not continue to sprite generation until the plate is visually plausible. Make only one targeted correction per retry. After the same failure survives two targeted retries, stop blind regeneration and report the problem to the user.

### 5. Generate the required state sources

Use a uniform `#00FF00` source background for reliable deterministic extraction. If the character has substantial green along the silhouette, use uniform `#FF00FF` instead and package with `--key magenta`.

- In free-exploration mode, generate idle and click sources. Change only the declared click gesture/expression and keep the feet planted.
- In AVG-layer mode, generate exactly the named states in the handoff. A state may change gesture, expression, or declared position, but identity, costume, rendering density, and light direction must remain stable. Do not add a second state merely to satisfy the free-exploration convention.

The keyed canvas is not a placement authority, even when it uses the same aspect ratio as the crop. Image generation may shift or resize the person. After extraction, measure the Alpha and deterministically align it to the frozen crop-space box and contact landmarks. Do not derive scene scale from the green canvas center, padding, or outer dimensions.

Ask for genuine transparency only if useful, but verify the actual alpha channel. A drawn checkerboard or opaque pale background is a failure, not transparency. When that occurs, switch to a uniform chroma background rather than masking the painted checkerboard as a final asset.

### 6. Package with deterministic extraction

Use [scripts/package_sprites.py](scripts/package_sprites.py) instead of rewriting chroma-key and anchoring logic.

Example:

```powershell
python scripts/art_pipeline/ndc_art.py run ndc-free-exploration-character-art package_sprites.py package `
  --idle lula_idle_green.png `
  --click lula_click_green.png `
  --scene SC2314_bg_LakeshoreTrust_LeonardOffice.png `
  --output-dir output `
  --prefix lula `
  --canvas 320x960 `
  --visible-height 892 `
  --foot 160,918 `
  --position 2220,520 `
  --shadow left
```

Use its `crop` command when a deterministic working crop is needed:

```powershell
python scripts/art_pipeline/ndc_art.py run ndc-free-exploration-character-art package_sprites.py crop --scene scene.png --rect 1720,500,1536,1024 --output scene_crop.png
```

Choose the final canvas, visible height, foot anchor, and scene position from the measured accepted plate, canonical-height contract, scene perspective, and nearby U1 assets. The accepted plate's realized actor envelope is the primary packaging target; do not copy example numbers mechanically, reuse a height from another scene, independently invent a new `visible-height`, or reduce a performer just to fit the composition.

For AVG-layer mode, use the crop-space target box rather than an eyeballed size:

```text
crop_x = master_x * crop_width  / master_width
crop_y = master_y * crop_height / master_height
full_x = crop_origin_x + crop_x
full_y = crop_origin_y + crop_y
```

Map every box corner and contact landmark separately. Compute one uniform Alpha scale from the target body envelope, then translate the packaged layer so the feet/support contacts coincide. If the head, feet, body axis, and box cannot all match with one uniform scale and translation, reject the keyed pose or camera angle instead of stretching it.

After packaging, composite the actor over the accepted scene plate at the recorded crop coordinates to create a master-registration preview. Require the foot/support contact to match within `3 px`, the head-to-foot envelope within `3%`, and the projected body axis/group spacing to remain visually coincident at 50% opacity. Fix mismatches with uniform scale and translation; never accept them because the Alpha channel is clean.

For AVG-layer mode, pass each required named state with repeatable `--state name=path` arguments:

```powershell
python scripts/art_pipeline/ndc_art.py run ndc-free-exploration-character-art package_sprites.py package `
  --state enter=emma_enter_green.png `
  --state intervene=emma_intervene_green.png `
  --scene SC2191_avg_Opening_MorrisonBlocksZack.png `
  --output-dir output `
  --prefix emma `
  --canvas 420x960 `
  --visible-height 892 `
  --foot 210,918 `
  --position 180,520 `
  --shadow left
```

### 7. Validate the art package

The result passes only when:

- all required state PNGs have identical canvas dimensions;
- every state is RGBA and all four canvas corners have alpha `0`;
- neither state has green spill, white/checkerboard halo, scene fragments, missing hair/fingers/shoes, or a printed transparency grid;
- visible scale is consistent and the alpha bounding-box bottoms share the requested foot line, normally within one pixel;
- measured head-to-foot scale matches the canonical profile height and recorded depth construction; same-depth relative heights remain correct;
- the master-registration preview matches the accepted plate's foot/contact points within `3 px`, head-to-foot envelope within `3%`, and body axis/group spacing without a visible doubled figure;
- the AVG-layer manifest and `placement.md` preserve the full-source/crop/master/keyed coordinate chain, and no final placement was inferred from a centered green canvas or resized viewer preview;
- in AVG-layer mode, actor Alpha does not intersect the selected TalkPanel safe rectangle and the actual UI-overlay preview confirms the intended negative space;
- identity, age, hair, costume, jewelry, and body proportions remain recognizably the same;
- free-exploration idle/click poses read as contained personality-specific states; AVG states preserve the selected key-dialogue acting verb, justified camera orientation including side-back/back when planned, gaze/focal relationship, distinct silhouette, and blocking distance without becoming new character designs;
- the delivered character-to-physical-anchor pixel ratio matches the recorded real-world ratio after the declared depth/perspective adjustment;
- shadow, if used, is separate and aligned to the same canvas;
- full-scene previews keep the original scene dimensions;
- preview differences outside the declared sprite rectangle are zero;
- visual review confirms that no source furniture, prop, architecture, or layout was changed inside or outside the preview's declared character/shadow region;
- the character is grounded at native size and still reads at gameplay thumbnail size.

Inspect sprites on both dark and bright contrasting backgrounds. Do not accept an alpha check based only on how the app viewer renders transparency.

## Deliverables

Keep only meaningful artifacts:

- free-exploration mode: `<prefix>_idle.png` and `<prefix>_click.png`;
- AVG-layer mode: one `<prefix>_<state>.png` for every declared state, and no invented states;
- `<prefix>_shadow.png` when needed;
- one full-scene preview per delivered state;
- `placement.md` with canonical height/profile authority, projected height/depth basis, final canvas position, foot line, alpha bounds, crop rectangle, and AVG panel-safe rectangle when applicable;
- the same `placement.md` must record the scene type and complete physical-anchor contract: object, measured dimension, real-world estimate/range, basis, confidence, source-pixel span, depth relation, secondary anchor when needed, ratio sentence, and final ratio QA;
- the same `placement.md` must include the accepted scene-master path, provisional scene anchors, realized master actor measurements, and registration result;
- for AVG-layer mode, `placement.md` must also contain the crop rectangle, master canvas size, master-space box, normalized box, mapped crop-space box, local source-anchor validation, and final full-source canvas position;
- `prompts.md` with exact accepted prompts and input-image roles;
- the packaging manifest produced by the script.

Show the required scene previews in the final response. Report the selected mode, state-to-dialogue-node mapping when applicable, output paths, dimensions, alpha/foot-line verification, scene coordinates, generation mode, failed/retried categories, and whether formal project assets or configs were touched.
