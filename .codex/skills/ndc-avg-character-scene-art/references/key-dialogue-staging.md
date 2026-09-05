# NDC AVG key-dialogue staging and sequential character production

Read this reference before selecting the core still, declaring placement, writing prompts, or generating any character.

## Select the scene's core dialogue still

The AVG composition represents the most narratively important **stable dialogue beat** in the scene, not automatically the first player-visible frame. Read the formal Talk/dialogue order, action annotations, character profiles, and scene requirements, then select one node or short continuous exchange that best communicates the scene's central conflict, revelation, decision, or relationship shift.

Record:

- selected node/range and exact supporting lines;
- why this beat is the visual narrative center;
- what every visible character knows, wants, and is doing at that instant;
- which props and contacts already exist at that node;
- which attacks, collapses, reveals, exchanges, or other material beats belong to突发事件/cutaway production and therefore remain outside this stable AVG still.

Do not choose a dramatic asset name or requirement title without dialogue evidence. Do not import a later action into the still merely because it looks stronger. If the narratively central beat cannot be represented as a stable AVG tableau without becoming a separate event illustration, keep the event out and choose the strongest stable dialogue beat immediately around it.

## Build the full ensemble plan before any image call

Plan every visible character together even though production is strictly one character at a time. Write the complete plan to `placement.md` and every final prompt draft to `prompts.md` before generating the first person.

For each character, record:

- canonical height, profile authority, foot point, floor-depth lane, physical scale anchor, projected envelope, and layer order;
- personality traits that affect visible behavior, immediate objective, power relationship, and acting verb at the selected dialogue beat;
- weight distribution, feet, torso, shoulders, hands or contained gesture, head, gaze target, and expression;
- camera orientation: `front`, `three-quarter`, `profile`, `side-back`, or `back`;
- visible identity cues that survive the selected orientation, such as silhouette, hair, costume, accessory, or posture;
- conversation partner/focal point, gaze-and-torso axis, interpersonal distance, relative foot landmarks, occlusion, and any cross-layer contact;
- assigned prop ownership, shadow requirement, and final generation order.

Standing is not the default pose. When supported by the dialogue and unchanged scene geometry, the core still may use sitting, half-crouching, bending, leaning, bracing, turning back, looking over a shoulder, lowering the head, recoiling, or another readable static key pose. Preserve a clean silhouette and stable contact rather than using motion blur or an animation-like in-between.

A character may face partly or fully away from the camera when that improves depth, hierarchy, concealment, threat, reluctance, or relationship staging. Record the reason. Do not force every face toward the viewer, but do not hide an identity accidentally or use the same back-facing solution for multiple characters without purpose.

## Use a connected composition

Speaking and mutually attentive characters need one readable gaze/torso network at gameplay thumbnail size. The plan must freeze each actor's foot point, body envelope, orientation, gaze target, interpersonal distance, and occlusion before generation.

For an unobstructed face-to-face middle-ground exchange, use a default clear silhouette gap of no more than roughly one shoulder width. A wider gap requires an existing desk, counter, architecture, threat distance, formal presentation, entrance beat, or other recorded reason. UI-safe negative space comes from one selected TalkPanel side, not from scattering the cast.

## Generate exactly one person at a time

Every character-producing image call contains exactly one target character. Do not generate a multi-person scene master, interaction group, or multi-person keyed Alpha.

Use this sequence:

1. finish the all-character blocking plan and all final prompt drafts;
2. choose a back-to-front or relationship-driven generation order and freeze it;
3. generate the first target character alone in the exact scene crop;
4. extract, register, grade, and place that character as an independent RGBA layer;
5. create a deterministic current composite for spatial reference;
6. generate the next target alone, using the original crop plus the plan and optional current composite as relationship references;
7. repeat until every character has an independently accepted layer;
8. composite all accepted layers onto the untouched source.

An optional current composite never authorizes the model to regenerate an accepted person or replace background pixels. The prompt names one new target and treats existing people only as coordinate, gaze, contact, and occlusion references.

For a handshake, handoff, restraint, embrace, support pose, or shared object:

- assign the shared prop to exactly one character layer;
- record both actors' contact landmarks and occlusion order before generation;
- generate each actor separately against the frozen landmarks;
- reject or re-plan a pose that cannot preserve the contact through independent layers.

Do not recover by generating both people together.

## Reserve one real TalkPanel side

The production `TalkPanel` render root is `2560x1600`. Its side background is `Assets/Resources/Art/UI/AVG/left_BG.png`, sized `913x1600`, and the prefab mirrors it through `isLeftObj` / `isRightObj`.

For a one-to-one `2560x1600` source, reserve one of these actor/action-safe rectangles:

- left panel: `[0,0) -> [913,1600)`;
- right panel: `[1647,0) -> [2560,1600)`.

Map the rectangle into source pixels when the source is cropped, panned, or scaled. Every character, limb, face, prop, contact, and essential action must remain outside it. Verify the formal `Talk.isRight` values across the plate's active node range and review a full-frame overlay using the actual panel art.

## Required plan fields

Before generation, `placement.md` and `prompts.md` together must contain:

- selected key-dialogue node/range, exact lines, selection reason, and excluded event beats;
- scene type, source size/crop, TalkPanel side, render/source safe rectangles, and checked formal node range;
- every character's profile height, scale-anchor contract, foot point, projected box, pose, camera orientation, gaze, expression, layer order, and shadow decision;
- the full ensemble gaze/contact/occlusion graph, interpersonal distances, shared-prop ownership, and generation order;
- one complete resolved scene-master prompt and keyed-source prompt for every character, with no unresolved placeholder.

The first image call is blocked until this full-scene plan is complete.
