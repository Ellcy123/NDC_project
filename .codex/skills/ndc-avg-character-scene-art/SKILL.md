---
name: ndc-avg-character-scene-art
description: "Create NDC AVG key-dialogue scene art from a complete blocking plan, semantic scene-object scale anchors, canonical character heights, one-person-at-a-time keyed layers, TalkPanel-safe composition, deterministic lighting grades, and zero-drift compositing. Use for AVG角色入景、AVG整图人物、AVG人物进退场资产, or testing that workflow. Do not use for突发事件/cutaway演出, free-exploration idle/click sprites, ordinary local cleanup, or formal Unity mounting."
---


## Production paths and closeout

Run `python scripts/art_pipeline/ndc_art.py paths` from either configured repository root before reading or writing production files. The Git-managed launcher resolves `{PLANNING_ROOT}`, `{ENGINE_ROOT}`, and `{WORK_ROOT}` from this machine's ignored `ndc.local.json` or `NDC_PLANNING_ROOT` / `NDC_ENGINE_ROOT` / `NDC_ART_WORK_ROOT`. These names are logical roots, not literal folders or requirements for a drive letter or repository layout. Read `{PLANNING_ROOT}/docs/美术生产工作区.md` and the dependency setup it links. Never copy another person's machine paths into shared rules.

Create the task with `python scripts/art_pipeline/ndc_art.py workspace create --name NAME --kind KIND`. `{JOB_PAYLOAD}` means the exact returned `payload` path; put candidates, revisions, QA, copied inputs, and prepared delivery there. Use `python scripts/art_pipeline/ndc_art.py run SKILL_NAME SCRIPT_NAME ...` for this skill's versioned scripts. Resolve another skill with `python scripts/art_pipeline/ndc_art.py skill SKILL_NAME`; its `references/`, `scripts/`, and `assets/` are relative to the returned `skill_root`, never a compatibility entry's directory. All project-owned helper scripts and schemas must be present in Git; do not depend on private scripts in a home folder, scratch directory, or an old machine checkout. Install third-party runtimes and libraries as documented, without committing credentials or virtual environments.

Resolve character cards through `{PLANNING_ROOT}/美术资产交付/角色/角色索引.json` and expression pairs through `{PLANNING_ROOT}/美术资产交付/角色表情/表情索引.json`; retain the selected asset hash and approval state. A card does not imply approval of a portrait, expression set, or new generated asset. Other input placeholders in examples must be replaced with the task's explicitly selected, existing inputs before execution.

After the user approves the specific finished candidate, prepare and verify the engine delivery under the shared workflow. Clean closed-job payloads only through its state-aware closeout; preserve pending review and active work. These rules replace historical output-directory defaults in this skill, while all art-quality and user-approval gates still apply. Historical case paths remain provenance, not default output destinations. Missing external references or validators remain unresolved dependencies; never silently substitute another image or claim PASS.

# NDC AVG Character Scene Art

Create an AVG scene-art package from an untouched original scene. Select the scene's most narratively important stable dialogue beat as the core still; do not default to the first player-visible frame. Before any image call, analyze the scene's real-world scale and finish one all-character blocking plan plus every per-character prompt. Generate exactly one new character per image call and per keyed layer, then composite the independently accepted layers. Material beats that belong to突发事件/cutaway production remain outside this workflow unless the user separately requests that medium.

This is an art-only workflow. Do not create a transparent exploration sprite, overwrite the source background, mount the result into Unity, or edit Excel/JSON/bytes unless the user separately authorizes that work.

## Preserve the source scene geometry exactly

The source scene is a fixed stage, not a loose visual reference. The only permitted scene-pixel changes are character silhouettes, approved overlaps where a character naturally occludes the original scene, and a small declared contact shadow/reflection. Do not add, remove, move, resize, repaint, restyle, reveal, or conceal furniture, chairs, sofas, counters, doors, plants, props, architecture, lighting fixtures, or other scene layout.

Choose a pose from the geometry that actually exists in the source at native size:

- A seated, leaning, hand-on-object, or otherwise supported pose is allowed only when the exact supporting chair, sofa, bench, desk, rail, counter, or prop is visibly present and has enough space for the recorded character footprint.
- Record that existing support object and its source-pixel contact area in the placement contract. Never ask the model to supply a missing chair, sofa, table, or other support.
- If no compatible support object exists, use a standing pose on a clear floor position. Do not infer an off-camera seat or rearrange the room to accommodate the acting.

## Stage the key dialogue as a readable still

Choose the dialogue node that best expresses the scene's central conflict, revelation, decision, or relationship shift while still working as a stable AVG still. Every visible character needs a readable state grounded in that exact beat: for example hosting, assessing, pressing, listening, guarding, hesitating, resisting, recoiling, challenging, or deciding.

Translate that state into concrete body language: weight distribution, foot angle, torso angle, shoulder tension, head/gaze, hand placement or one contained gesture, and facial expression. Supported poses may include standing, sitting, half-crouching, bending, leaning, turning back, looking over a shoulder, or lowering the head when the scene geometry and dialogue justify them. A character may face away or partly away from the camera when that strengthens hierarchy, concealment, confrontation, or depth; record the narrative reason and preserve identity through silhouette, hair, costume, and blocking. Do not give multiple actors the same feet-parallel, arms-down, forward-facing pose family unless deliberate uniformity is required by the story.

Stage speaking or mutually attentive characters as one conversational blocking group even when they will be extracted as separate keyed layers. Lock their relative foot points, body envelopes, gaze axis, and interpersonal distance in the placement contract. In an unobstructed face-to-face middle-ground exchange, the empty silhouette gap should normally be no greater than roughly one actor shoulder width; a larger distance requires a recorded reason such as an existing desk, architectural barrier, threat distance, formal presentation, or an entrance beat. The reserved TalkPanel side is a composition constraint, not a reason to scatter actors toward opposite edges.

Use the active character profile, personality, power relationship, immediate objective, and exact key-dialogue lines to infer acting when the script is physically sparse. Do not invent an unsupported prop or action merely to intensify the image, and do not substitute a突发事件/cutaway beat for the selected stable dialogue still.

Zero drift outside the actor/shadow Alpha union is necessary but not sufficient. A result still fails visual QA when anatomy, contact, grounding, identity, or layer order is wrong, even when every outside-union containment metric passes.

## Default baked-character method: keyed actor layers

For newly generated people, do **not** paste any portion of the AI-redrawn scene crop and do **not** estimate a hand-drawn silhouette authorization mask. Use the scene edit only as a placement and lighting master, then reproduce the approved actors on a uniform key background and bake their extracted RGBA pixels onto the untouched source scene.

The default production sequence is:

1. classify the scene and build a semantic scale-anchor contract for every planned foot position;
2. select the key-dialogue node and finish the all-character blocking plan, layer order, shared-contact ownership, and every per-character prompt in `placement.md` and `prompts.md`;
3. generate and approve one target character's scene-context reference plate against the exact source crop or current deterministic placement preview;
4. reproduce only that character on uniform `#00FF00`, or `#FF00FF` when green would collide with the silhouette;
5. extract real Alpha with `ndc-free-exploration-character-art/scripts/package_sprites.py` and align it to that character's frozen box and contacts;
6. grade only the actor layer's RGB with `scripts/grade_rgba_lighting.py`, preserving Alpha, dimensions, and coordinates exactly;
7. composite the accepted RGBA layer onto the untouched source, then repeat Steps 3–7 for the next planned character;
8. create the final composite from all independently accepted character and shadow layers and require zero changed pixels outside their union Alpha.

The reference plate is an approval artifact, never the authoritative background. AI changes to its walls, floor, furniture, plants, reflections, or architecture are ignored because none of those pixels are pasted back.

### Build a semantic scale contract before the per-character scene master

Read [the canonical scale reference](../ndc-free-exploration-character-art/references/character-scale.md). For each target foot position, identify the closest **reliable same-depth physical anchor**, not merely the nearest object in two-dimensional image space. Classify the location first because a sofa in a residence, a teller counter in a bank, and a hospital bed imply different defensible dimensions.

Record the anchor object, the exact visible dimension being used (for example sofa seat height versus back height), estimated real-world value or range, estimation basis, confidence, measured source-pixel span, depth relationship, and one depth cue. Prefer a second anchor when the first is ambiguous. Convert the character's canonical height into a provisional scene ratio and write the explicit relationship into that character's prompt, for example: `sofa back 1.0 m; character 1.70 m at approximately the same floor depth; target head-to-foot height is about 1.7 times the sofa-back span before perspective correction.` Numeric prompt guidance never replaces the frozen box and pixel QA.

### The accepted per-character scene master is the realized scale lock

Do not use a reusable pixel-height preset, a character-card canvas, or an unrecorded visual guess to size the extracted actors. Before the scene master exists, derive only a **provisional** projected envelope from the untouched scene's intended foot point, floor depth, vanishing geometry, and same-depth human-scale anchors. Treat the complete camera and scene together: a person at the rear of a deep room, a person beside a doorway, and a person in a steep overhead bathroom cannot share one default head-to-foot pixel height.

When that character's initial scene-context plate looks correctly proportioned, measure and lock its actor geometry in crop coordinates:

- visible head/top point and outer Alpha envelope;
- left/right foot or support-contact points;
- projected body-axis direction, including high-angle foreshortening;
- each actor's depth lane and local scene anchor;
- relative foot offsets, silhouette gap, gaze axis, and group envelope.

### Lock crop-relative actor boxes before green generation

The deterministic source crop is the coordinate authority for the entire job. Before generating any keyed source, freeze this chain in `placement.md`:

```text
full source -> source crop -> scene-master actor box -> keyed Alpha -> full source
```

Record the full-source crop as `(crop_x, crop_y, crop_width, crop_height)` and the scene-master canvas as `(master_width, master_height)`. The scene master must depict the complete source crop with the same aspect ratio and no crop, padding, rotation, or reframing. Prefer an output with exactly the source-crop dimensions. If the generator returns a different resolution, convert every measured landmark separately into crop coordinates:

```text
crop_point_x = master_point_x * crop_width  / master_width
crop_point_y = master_point_y * crop_height / master_height
full_point_x = crop_x + crop_point_x
full_point_y = crop_y + crop_point_y
```

Apply this mapping to each actor-box corner, head point, both feet/support contacts, body-axis endpoints, and group landmark. Never measure a resized app preview or screenshot. Never use one guessed `visible-height` or a centered green-screen subject as a substitute for the mapped actor box.

Before accepting the mapping, compare the master with the untouched crop at the actor's local floor/support contact and at least two nearby non-collinear source anchors such as a doorway corner, tile intersection, bed rail, counter edge, or wall/floor junction. If those anchors reveal local redraw, padding, perspective drift, or an underfoot surface that does not exist in the untouched crop, the master is not a coordinate master and must be rejected before green generation.

For every actor, freeze both the master-space and crop-space values: `master_box`, `crop_box`, normalized box `(left/master_width, top/master_height, right/master_width, bottom/master_height)`, head point, contact points, body axis, and intended layer order. These values are decided while producing the scene composition, not reconstructed later from the keyed images.

Generate each keyed actor using the accepted scene master and its frozen crop-relative box. Prefer a key canvas with the same aspect ratio as the source crop and request the actor at the same normalized position, scale, body axis, and margins. The keyed canvas itself is still not authoritative: after extraction, uniformly scale and translate the Alpha so its measured body/contact landmarks match the frozen crop-space box. A pose or camera angle that cannot match those landmarks with one uniform scale and translation is a keyed-generation failure, not a sizing problem.

Use those realized measurements as the hard target for every green-screen source, packaged RGBA layer, and final composite. The master is authoritative for projected scale, placement, perspective pose, and group blocking; canonical profile heights are authoritative for real-height ratios. The master is never authoritative for background pixels.

If the master redraws the floor, doorway, support, or local perspective so that its actor foot/contact points cannot map back to the untouched source, reject it and generate a corrected master. If only unrelated environment pixels drift while the actor contacts still map exactly, ignore those environment pixels and retain the measured actor geometry.

After extraction, make a master-registration preview by overlaying the RGBA actor on the accepted master at the recorded crop position. Require foot/contact error no greater than `3 px`, head-to-foot envelope error no greater than `3%`, and no visually doubled body axis or widened conversational spacing at 50% opacity. Technical Alpha containment, source preservation, and TalkPanel clearance cannot substitute for this registration check.

### Plan the ensemble together, generate every person separately

- Complete the positions, scale anchors, poses, orientations, gaze targets, occlusion, contact landmarks, layer order, and final prompt text for **all** visible characters before the first image call.
- Every character-producing image call contains exactly one target character. Never ask the model to generate two or more people together, and never create a multi-person keyed source or interaction-group Alpha.
- A current deterministic composite may be supplied as a spatial relationship reference, but the call still adds or reproduces only the named target character. The untouched source remains the final background authority.
- For a handshake, handoff, restraint, embrace, or shared prop, assign the prop to exactly one character layer and freeze both actors' contact landmarks in the plan. Generate and register the layers separately. If the contact cannot be preserved through separate layers, stop and re-plan the pose rather than switching to joint generation.
- Preserve the planned ensemble through each actor's frozen foot points, body envelope, gaze target, interpersonal distance, and occlusion. Do not solve a mismatch by stretching a layer or moving another accepted character without updating the full plan.

Generate a contact shadow only when the staging needs it. Keep it as a separate transparent layer or as part of the current single character's keyed asset when explicitly planned; it must contain no floor texture or pixels from another person. Never paste generated floor pixels to obtain a shadow.

A keyed source fails when it has a gradient, horizon, scene residue, opaque checkerboard, clipped hair/fingers/shoes, enclosed key-color islands, visible chroma spill, or a key color used by the subject. Regenerate or change the declared key; do not fall back to a broad hand-drawn person mask. A verified genuinely transparent built-in output may replace chroma extraction, but it must pass the same Alpha and edge QA.

## Decide the AVG asset topology before judging or generating art

`画面人物` means the characters participating in the AVG scene. It does **not** mean every listed character must be permanently painted into one background.

Read [references/key-dialogue-staging.md](references/key-dialogue-staging.md), then select the most narratively important stable dialogue beat from the formal dialogue timeline, action annotations, character profiles, and existing configuration before classifying each character. Do not choose from the scene title alone.

- **Baked keyframe character**: visible at the selected key-dialogue node and stable for the intended plate interval. Bake only the supported keyframe pose and held props.
- **Independent AVG entrance/exit layer**: enters after the scene begins, exits before it ends, must be hidden/revealed by a node, or needs runtime-controlled occlusion. Generate the character in the exact scene context for profile height, perspective, light, and floor contact, then deliver a real-alpha cutout instead of permanently baking it into the base plate.
- **Mixed character**: the selected keyframe state may be baked while another entrance/exit or replacement state remains independent. Do not bake two temporal states of the same person into one plate.
- **Deferred-event action**: an attack, collapse, reveal, or other material beat whose intended medium is突发事件/cutaway rather than a stable AVG still. Record it but do not convert it into an AVG plate by default.
- **Voice-only/off-camera character**: do not invent a visible asset unless the requirement or staging explicitly calls for one.

For every scene, record an asset-topology table before generation with: character, selected key-dialogue pose/prop state, first and last visible nodes, entrance/exit/action changes, baked versus independent versus deferred-event, required asset name, and intended layer order. The clean base must retain any area that becomes visible before an independent character enters or after one exits.

When auditing existing AVG art:

- do not mark a background for rework merely because an entrance/exit character is absent from it;
- first verify whether the corresponding transparent character asset exists, has the required action state, and is wired at the correct dialogue nodes;
- report a missing temporal character as **missing independent character layer**, not as **background missing/incorrect**;
- report a background as incorrect only when a character classified as baked is absent, a temporal character was wrongly baked into a state where they should not yet be visible, or the clean scene/occlusion needed by the layered performance is unavailable;
- treat the scene as complete only when the required base plate, every independent layer, and their dialogue timing together reproduce the full performance.

For an independent AVG layer, keep a full-scene placement preview as proof of scale and lighting, but do not use that preview as the authoritative background. The delivered actor PNG must contain real transparency, preserve the approved scene-relative scale and foot line, and contain no scene fragments, painted checkerboard, halo, or chroma spill.

### Mandatory routing for independent characters

If any character is classified as an independent or mixed AVG layer, invoke `ndc-free-exploration-character-art` for that character's scene-grounded generation, chroma/alpha extraction, canvas anchoring, foot-line alignment, and placement previews. This routing is based on the required transparent-layer deliverable, not on whether the gameplay mode is free exploration.

Pass an `AVG-layer` handoff containing:

- immutable scene and character-card paths;
- selected key-dialogue node/lines and that character's personality basis, objective, acting verb, camera orientation, gaze/contact role, and full resolved prompt;
- scene type; canonical height and authoritative profile path; closest reliable same-depth object and exact measured dimension; real-world estimate/range, basis, confidence, pixel span, optional second anchor, depth cue, explicit ratio sentence, projected pixel height, and final scale-QA target;
- accepted scene-master path and its exact canvas dimensions;
- full-source crop rectangle; master-space, normalized, and crop-space actor envelopes; head point, foot/contact points, body-axis endpoints, realized projected height, local source-anchor checks, and registration tolerance;
- crop-space transparent canvas, visible envelope, full-source canvas position, and foot line;
- every required state name, concrete pose/body-language breakdown, camera orientation and reason, conversation partner or focal point, expression, and first/last visible dialogue node;
- conversational axis, intended interpersonal distance or group envelope, and the relative foot/contact landmarks that must survive separate extraction;
- entrance, exit, replacement, occlusion, and layer-order behavior;
- selected TalkPanel side plus render-space and source-space safe rectangles that the layer must not enter;
- lighting/shadow direction and U1 rendering references;
- output location and whether a separate shadow is required.

Do not reproduce the transparent-character workflow inside this skill. Use this skill for the baked plate and overall topology; use `ndc-free-exploration-character-art` in `AVG-layer` mode for each independently controlled character. A mixed scene therefore invokes both skills.

## Required companions

Use the available `imagegen` skill for every AI image call and read its `SKILL.md` before generation.

Read `{PLANNING_ROOT}/.codex/skills/ndc-free-exploration-character-art/SKILL.md` whenever any keyed or transparent actor source is required. For baked actors, reuse its scene-grounding, chroma extraction, Alpha QA, canvas anchoring, and placement-preview rules, then bake the accepted RGBA output here. For independent or mixed actors, invoke that skill in `AVG-layer` mode and keep the RGBA actor asset as the authoritative delivery. If it is unavailable, stop before generation and report the missing transparent-layer dependency.

Read `{PLANNING_ROOT}/.codex/skills/ndc-free-exploration-character-art/references/character-scale.md` before staging any person. Resolve or add the character's canonical height in the active `{PLANNING_ROOT}` profile before generation and pass that same authority into every baked or independent layer.

Use `ndc-coordinate-image-edit` only when the task also requires localized scene-pixel cleanup, material repair, or a deterministic structural bridge. Resolve its main implementation at `{PLANNING_ROOT}/.codex/skills/ndc-coordinate-image-edit/`.

Do not route ordinary newly generated character silhouettes through its hand-drawn authorization-mask workflow. When scene repair is genuinely needed, read its `SKILL.md` first and keep that repair as a separate confirmed job.

Read [references/key-dialogue-staging.md](references/key-dialogue-staging.md) before deciding the core still, ensemble blocking, generation order, or topology. Read [references/coordinate-packaging.md](references/coordinate-packaging.md) before preparing, extracting, or compositing actor layers. Read [references/prompt-template.md](references/prompt-template.md) immediately before each image call.

Immediately before every per-character scene-context call, also read `../ndc-free-exploration-character-art/references/mandatory-character-in-scene-prompt.md`. Prepend its complete mandatory wrapper and expand `【内容】` from the selected key-dialogue node, personality, objective, concrete body language, camera orientation, gaze/blocking relationship, scene geometry, and deferred-event boundary. Include the resolved physical-anchor scale sentence. Do not send a scene-insertion prompt when the wrapper is absent or any placeholder remains unresolved. Keyed green/magenta extraction calls preserve the approved design but do not use the scene-insertion wrapper.

## Workflow

### 1. Resolve and inspect the source set

Identify:

- the narrative or test requirement;
- the formal dialogue timeline and the selected key-dialogue node, exact lines, narrative reason, and boundary from突发事件/cutaway beats;
- the immediate conversational objective, personality basis, power relationship, and keyframe acting verb for every visible character;
- every active character-profile path and canonical height, writing one inferred height into the active profile when none exists;
- the scene type and candidate same-depth physical scale anchors around every intended foot position;
- the TalkPanel side used by the relevant nodes and the source-space safe rectangle that must remain empty;
- one immutable full-size scene background;
- one character card;
- one or two U1 AVG character assets for rendering density and facial-plane treatment;
- optionally, one accepted full-scene AVG image for scale and cinematic integration.

Also inventory existing independent entrance/exit layers and later event assets before deciding that the background is incomplete. Apply the asset-topology rule above and state whether this job is producing a baked key-dialogue plate, independent entrance/exit layers, or both. List cutaway/event beats separately rather than silently turning them into the AVG composition.

For an independent layer, prepare the `AVG-layer` handoff and route that work to `ndc-free-exploration-character-art`. Continue with Steps 3–7 here for the baked portion and its final full-scene plate.

Inspect every input with `view_image`. The scene is the edit target; the other images are references with explicitly different roles. If the user permits a random test, choose an empty scene with a legible floor plane and a character whose costume belongs in that setting.

Before selecting a seated or supported pose, inspect the proposed support object at native size. Prefer a clear standing location when the scene has no suitable existing support.

### 2. Declare and confirm the placement contract

Before the first image-file modification or generation, show the actual source and state:

- source path, pixel dimensions, and mode;
- selected key-dialogue node, exact dialogue evidence, one-sentence core-still description, selection reason, and excluded突发事件/cutaway beats;
- scene type and, for every person, canonical height, profile path, explicit-versus-inferred status, intended foot point and depth lane, closest reliable same-depth scale object, exact measured object dimension, estimated real height/range, basis, confidence, source-pixel span, secondary anchor when needed, depth cue, explicit character-to-object ratio sentence, and provisional projected pixel height;
- selected TalkPanel side, its actual render-space rectangle, its mapped source-space rectangle, and the formal `Talk.isRight` range checked for consistency;
- half-open generation crop `[left, top) -> [right, bottom)`;
- target character envelope and foot line in source pixels;
- acting verb/state plus personality basis, weight distribution, foot angle, torso angle, shoulder tension, hand placement/contained gesture, camera orientation (`front`, `three-quarter`, `profile`, `side-back`, or `back`), gaze, expression, lighting, shadow direction, and occlusion;
- each character's conversation partner or focal point, conversational axis, intended interpersonal distance or blocking-group envelope, and a reason for any unusually wide separation;
- the silhouette distinction between participating characters; do not approve repeated or mirrored mannequin poses by default;
- standing floor-contact point, or the exact existing support object and its approved contact area for a seated/supported pose;
- protected architecture, props, and scene boundaries;
- intended full-size output and the fact that the character will be baked in.
- for every participating character, whether the state is baked or independent, its visible-node range, intended layer order, and whether a clean background must remain visible before entry or after exit.
- a complete per-character generation order; every image call and keyed source contains exactly one named person;
- selected key color and any subject detail that makes green or magenta unsafe;
- exact shared prop owner, cross-layer contact landmarks, and whether a separate shadow layer is required;
- confirmation that the final prompt text for every character is already written in `prompts.md` and no actor/action Alpha enters the panel-safe rectangle.

For an independent character layer, replace “will be baked in” with the explicit statement that the full-scene composite is an approval preview and the authoritative delivery is a transparent actor asset.

Describe the concrete `before -> after` change and wait for explicit confirmation unless the same exact source, region, character, pose, and baked/layered classification were already confirmed in the current task. This confirmation authorizes only the stated art edit, not retries or formal mounting.

Save the accepted contract in `placement.md`, and save the complete ordered per-character prompts in `prompts.md`. Use a top-left origin throughout. Do not make the first image call while any visible character still has an unresolved scale anchor, pose/orientation, contact, layer order, or prompt placeholder.

The pre-generation projected height is provisional. After the scene master is accepted, update the same `placement.md` with the master path and the realized actor envelope, head point, foot/contact points, body axis, group spacing, and final packaging height. Do not leave only the provisional estimate in the contract.

Do not generate a keyed source until `placement.md` contains the accepted crop rectangle, master canvas dimensions, per-actor master-space box, mapped crop-space box, normalized box, contact points, and verified local source anchors.

### 3. Prepare the immutable scene context

Use a Python environment with the documented dependencies; a Codex bundled workspace runtime is also valid. Work non-destructively under the managed task output:

```text
{JOB_PAYLOAD}/
```

Create the exact real-source crop recorded in `placement.md`; do not resize it. Use the free-exploration packager's deterministic crop command:

```powershell
& $ndcImagePython scripts/art_pipeline/ndc_art.py run ndc-free-exploration-character-art package_sprites.py crop `
  --scene $source `
  --rect 768,64,1536,1536 `
  --output "$job/source_crop.png"
```

Prefer a square crop when it contains the complete key-dialogue composition, floor contacts, physical scale anchors, relevant support geometry, the dominant light source, and enough context to verify the reserved panel side. Inspect the crop at native size and confirm that every recorded body envelope fits at its profile-derived projected height without entering the safe rectangle.

### 4. Generate per-character scene masters and keyed sources

Before composing each target character's scene-master prompt, expand and prepend the complete wrapper from `../ndc-free-exploration-character-art/references/mandatory-character-in-scene-prompt.md`. `【内容】` describes only the named target character, including personality-grounded acting, camera orientation, gaze target, and the physical-anchor scale sentence. Other characters appear only as planned coordinates, gaze/contact targets, or already accepted reference layers; do not ask the model to create them again.

For each character in the frozen generation order, generate one scene-context reference plate with local `referenced_image_paths`:

1. exact `source_crop.png`: placement, camera, perspective, and lighting context;
2. the target character card: identity and costume authority;
3. U1 AVG asset: rendering reference only;
4. optional current deterministic composite or blocking overlay: other characters' accepted positions, gaze/contact targets, and occlusion only; it does not authorize redrawing them.

Ask for the complete reference crop with exactly one newly generated target character so the user can judge the selected key-dialogue acting, position, object-to-character ratio, identity, middle-ground camera distance, panel-safe negative space, ensemble relationship, camera orientation, light, and foot contact. Reject an extra person, wrong key-dialogue action, mannequin-like or duplicated posing, unsupported back-facing pose, disconnected gaze, unjustified spacing, arbitrary shrinkage, near-camera crowding, safe-zone overlap, or an invented/altered environmental object. Even an accepted plate remains a reference artifact and contributes no scene pixels to the final.

The generated plate must retain the complete crop framing. Record its actual pixel dimensions, map the actor boxes and landmarks back into source-crop coordinates, and validate the underfoot/support region plus nearby source anchors before any green-screen call. Visual approval of the people alone is not coordinate approval.

Judge projected scale as an integrated scene result, not as an isolated centimeter conversion. Verify the declared object dimension, character-to-object ratio, depth cue, and any secondary anchor. If the per-character plate is visually credible, measure that actor geometry and use it as the realized scale lock. Do not independently choose a new `visible-height` during green-screen packaging.

After that plate and coordinate mapping are accepted, reproduce only the same target person on a perfectly uniform key background using the plate as pose/layout/lighting authority, the character card as identity authority, and the recorded profile height plus physical scale contract as scale authority. Preserve the full body, hair, fingers, shoes, assigned prop, acting posture, camera orientation, gaze direction, margins, and contact landmarks. Do not include another person, an unassigned shared prop, floor, horizon, architecture, scene fragment, cast shadow, or unrelated object.

Immediately persist every returned plate or keyed source in the job directory. The confirmed two-stage workflow authorizes one call for each declared artifact; any retry after a rejected artifact requires user approval.

### 5. Extract, align, grade, and bake the RGBA layers

Use `ndc-free-exploration-character-art/scripts/package_sprites.py package` for deterministic key extraction, de-spill, transparent-canvas anchoring, dark/light QA, and a placement preview. Package every person independently at the recorded canvas position. Never pass a multi-person state or interaction group to the packager.

The generator may change output resolution or shift subjects within its green canvas. Measure the extracted Alpha box and recover its placement only from the frozen crop-space target box and contact landmarks. Correct it with one uniform scale plus translation; use the mapped master envelope as `visible-height` and the mapped contact point as `foot`. Do not fall back to a memorized value such as `576 px`, do not independently re-estimate the actor after extraction, and do not use the green image's center or outer canvas as a coordinate authority. Do not stretch X and Y independently or shrink a secondary character to fit.

Create and inspect a master-registration preview before the untouched-source composite. If the extracted actor does not land on the accepted master's feet, head, body axis, and group envelope within the recorded tolerance, fix uniform scale/translation or reject the keyed source. Do not proceed merely because the packager produced a valid RGBA PNG.

After registration passes, apply a deterministic **RGB-only scene-light grade** to each accepted actor layer before compositing. Green-screen extraction often leaves the actor brighter, warmer, and more saturated than the untouched NDC background; correct that mismatch without another image-generation call. Use this skill's helper and the SC2491 Mickey correction as the default-strength baseline:

```powershell
& $ndcImagePython scripts/art_pipeline/ndc_art.py run ndc-avg-character-scene-art grade_rgba_lighting.py `
  --input "$job/output/mickey_registered.png" `
  --output "$job/output/mickey_registered_graded.png" `
  --report "$job/output/mickey_lighting_grade.json" `
  --exposure-ev -0.60 `
  --gamma 1.08 `
  --contrast 0.98 `
  --saturation 0.88 `
  --rgb-gain 0.97,0.99,1.01
```

Treat these values as the standard starting profile, not a reason to ignore the scene. Judge the graded actor in a full-scene preview at native size and gameplay-thumbnail size. Keep approximately this correction strength unless the actor clearly becomes crushed or remains conspicuously brighter than same-depth surroundings; if adjustment is needed, change it minimally and record the actual parameters in `placement.md` and the grade report. Match local exposure and color temperature while preserving face readability and costume separation. Do not grade the untouched background, contact-shadow layer, mask, coordinates, or Alpha, and do not use brightness correction to hide extraction spill, bad anatomy, incorrect scale, or wrong placement.

The graded PNG—not the raw extracted layer—is the compositing input. For an independent AVG entrance/exit layer, the graded PNG is also the authoritative transparent delivery; its full-scene composite remains an approval preview. Require the grade report to show the same pixel dimensions and Alpha bounding box as the input, `alpha_unchanged == true`, `changed_rgb_pixels_outside_alpha == 0`, and `passed == true`. If any invariant fails, stop before compositing or delivery.

Bake the accepted packaged layers back-to-front with this skill's helper. Each `X Y` is the top-left of that transparent layer canvas in full-scene pixels:

```powershell
& $ndcImagePython scripts/art_pipeline/ndc_art.py run ndc-avg-character-scene-art composite_rgba_layers.py `
  --scene $source `
  --layer envelope_exchange "$job/output/envelope_exchange.png" 768 64 `
  --layer separate_shadow "$job/output/exchange_shadow.png" 768 64 `
  --output "$job/SC2292_avg_LeonardEnvelope_v1.png" `
  --union-mask "$job/final_union_alpha.png" `
  --report "$job/final_alpha_verification.json"
```

Pass `--layer` entries in back-to-front order. Do not include the optional shadow entry when no shadow asset exists. Never overwrite the source or an existing candidate.

Verify the selected UI side with `scripts/verify_avg_safe_zone.py`, using the full-size actor union mask from the composite. Run the same check on an independent-layer full-scene preview before delivery. For a one-to-one `2560x1600` scene the script knows the production 913-pixel side width; for any other mapped size, pass the source-space rectangle recorded in `placement.md`:

```powershell
& $ndcImagePython scripts/art_pipeline/ndc_art.py run ndc-avg-character-scene-art verify_avg_safe_zone.py `
  --image "$job/final.png" `
  --union-mask "$job/final_union_alpha.png" `
  --side left `
  --preview-output "$job/ui_safe_preview.png" `
  --report "$job/ui_safe_verification.json"
```

### 6. Diagnose and verify

Classify failures by stage:

- Missing hair, fingers, shoe, or shared prop in the keyed source is a generation failure.
- A complete keyed source with a bad edge, enclosed key-color island, or spill is an extraction/key-selection failure. Regenerate a cleaner uniform source or change the declared key instead of erasing anatomy.
- Correct actors at the wrong scene scale or position are a deterministic alignment problem; adjust uniform scale/translation without another image call.
- A correctly keyed and aligned actor that remains noticeably brighter, warmer, or more saturated than the same-depth scene is a lighting-grade failure; adjust the deterministic RGB-only grade and regenerate the preview without another image call.
- A grade that changes Alpha, canvas dimensions, Alpha bounds, coordinates, transparent RGB pixels, or the untouched background is invalid. Restore the registered layer and rerun the deterministic grader; do not compensate during compositing.
- A centered keyed actor whose crop-relative box was never frozen before generation is a missing-coordinate-contract failure; return to the accepted scene composition and record the box instead of guessing a new height.
- A master whose local floor/support or nearby anchors do not map back to the untouched crop is an invalid coordinate master; reject it even when its people look attractive.
- An extracted actor that no longer matches the accepted scene-master envelope, feet, body axis, foreshortening, or group spacing is a master-registration failure, even when its canonical height ratio and Alpha are valid.
- A taller character reading shorter at the same depth, or a rear character being reduced without proven floor depth, is a height/perspective failure; rebuild alignment from the canonical profile heights.
- Any actor, limb, gesture, or key prop entering the selected TalkPanel safe rectangle is a composition failure; change placement and reconfirm instead of shrinking the figure.
- A pose that does not express the selected key-dialogue node, or that imports an excluded突发事件/cutaway beat, is a timeline/topology failure.
- Blank mannequin acting, repeated pose families, disconnected gaze, or unjustified conversational distance are staging failures even when chronology, Alpha, height, and UI safety pass.
- An extra generated person or multi-person keyed source is a workflow failure. Wrong cross-layer spacing, hand contact, or shared-prop ownership requires re-planning or regenerating the affected single character.
- Floating feet are fixed through the master pose/contact line, not by enlarging a shadow.
- Any changed architecture or furniture in the final means the wrong artifact was composited. Rebuild from the untouched source and RGBA layers; never accept a scene-plate paste.

The result is deliverable only when:

- final size and mode match the source;
- every packaged layer is RGBA, has transparent corners, and contains no scene fragment, visible key spill, opaque checkerboard, clipped anatomy, or missing prop;
- every baked actor uses an accepted graded RGBA layer; its grade report preserves dimensions and Alpha exactly, reports zero RGB changes outside Alpha, and records the actual exposure/gamma/contrast/saturation/RGB-gain values;
- `changed_pixels_outside_union == 0`;
- `outside_union_max_channel_difference == 0`;
- `outside_union_pixels_bit_identical == true`;
- full-size and gameplay-thumbnail review show correct identity, personality-grounded key-dialogue acting, narratively justified front/side/back orientations, non-duplicated silhouettes, connected conversational axis, justified spacing, relative interaction, layer order, grounding, scale, and lighting;
- measured projected heights match the canonical-height/depth contract, characters remain in scene-appropriate middle ground, and no person is arbitrarily smaller because of narrative importance;
- every scale report names the scene type, physical anchor and measured dimension, estimated real height/range, confidence, pixel span, depth relationship, character-to-object ratio, and prompt sentence, with a second anchor when the first is ambiguous;
- the master-registration preview proves foot/contact error `<= 3 px`, head-to-foot envelope error `<= 3%`, and no doubled body axis or spacing drift at 50% opacity;
- `placement.md` proves the complete full-source/crop/master/keyed/full-source coordinate chain and contains no coordinate measured from a resized viewer screenshot;
- a full-frame preview with the actual mirrored/unmirrored `left_BG.png` shows zero actor/action Alpha inside the selected panel rectangle;
- `ui_safe_verification.json` reports `actor_alpha_pixels_inside_safe_rect == 0` and `passed == true`;
- the plate depicts the selected stable key-dialogue still and excludes beats assigned to突发事件/cutaway production;
- the untouched source is visibly unchanged everywhere not covered by actor/shadow Alpha.

When a separate scene repair was authorized, also run the coordinate skill's boundary/structure scans and final verification for that repair job. Do not make those scans a prerequisite for a pure RGBA actor bake that never modifies scene pixels outside Alpha.

### 7. Deliver

Show the accepted full-size image and a close crop. Report:

- source and final output paths;
- final dimensions/mode;
- exact scene-master and keyed-source prompts and built-in generation mode;
- generation-call count, rejected categories, and deterministic realignments;
- every accepted green/transparent source, packaged RGBA layer, canvas position, Alpha bounds, and package manifest;
- every accepted graded RGBA layer, its lighting-grade report and parameters, plus the full-scene native-size/thumbnail lighting comparison;
- the all-character blocking plan, per-character generation order, shared-prop ownership, and cross-layer contact landmarks;
- each character's canonical height, profile path, projected pixel height, and depth/scale basis;
- each accepted per-character scene-master path, physical-anchor construction, realized master envelope/contact measurements, and master-registration preview/result;
- the selected key-dialogue node and lines, selection reason, excluded event beats, selected TalkPanel side, checked `Talk.isRight` node range, safe rectangles, and UI-overlay preview;
- `ui_safe_verification.json` and its zero-intersection result;
- `final_union_alpha.png`, `final_alpha_verification.json`, and the three outside-union containment fields;
- any optional scene-repair masks, manifests, boundary scans, or structure scans;
- whether official art or formal configuration was touched.

Keep failed diagnostics when they explain a rejected keyed source, alignment, extraction, or optional repair, but label the single accepted output unambiguously.
