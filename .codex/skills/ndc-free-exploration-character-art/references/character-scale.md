# NDC canonical character height and scene scale

Use this reference for every generated character, in free-exploration mode and in AVG-layer mode. A character's apparent size must come from a persistent real-world height plus scene perspective, never from whether the character feels important, secondary, or "in the background."

## Resolve one canonical height before staging

Search active character-design documents under `{PLANNING_ROOT}` first. Resolve the current episode and canonical English character name, then search active `剧情设计/Unit*/人物设定/` profiles and other current character briefs. Exclude paths containing `旧文档`, `_archive`, `backup`, `备份`, or `废弃` unless the user explicitly selects an archived source. Historical documents in `D:/NDC/NDC_project` are provenance only; resolve current authority through `{PLANNING_ROOT}/canon_manifest.json`.

Apply this authority order:

1. an explicit height in the current active character profile;
2. an explicit height in another active profile for the same canonical character;
3. a single art-unification inference made from the active profile's age, sex, build, relative-height language, role card, and reliable existing same-depth comparisons.

Never infer height from a newly generated image. If active documents contain conflicting explicit heights for the same character, stop before generation and ask which value is authoritative.

When no active profile states a height, infer one realistic integer-centimeter value once and write it directly into the canonical active character profile before generation, following the document's existing field style. Mark it as an art-unification inference, for example:

```text
- 身高：183 cm（美术统一推定，2026-08-24）
```

If the current episode has no active profile but its Unit number and active `人物设定` location are unambiguous, create the missing canonical profile there rather than modifying an archive. Preserve existing narrative content and add only the minimum identity context plus the height field. If the active destination is ambiguous, stop and ask instead of creating a new profile in a guessed folder.

After a height is written, reuse that exact value in every later scene and state until the user changes the profile. Do not infer a new height per scene or per asset.

## Build a semantic physical-anchor contract

Before estimating screen pixels or calling an image model, classify the location (for example residence, office, bank lobby, hospital, street, or bathroom) and choose the intended character foot point. Find the closest **reliable physical object at approximately the same floor depth**. "Closest" means useful for perspective and scale, not merely nearest in two-dimensional pixels.

Prefer objects with a defensible human-scale dimension and a clearly visible span, such as a door, sofa, chair, desk, counter, bed, railing, stair riser, or accepted same-depth character. Name the exact dimension being used: `sofa back height`, `seat height`, `desk work-surface height`, and `door opening height` are different measurements. Scene semantics affect the estimate; a bank teller counter and a residential side table must not inherit one generic value.

Record this contract for every planned character position:

- scene type and intended foot point;
- anchor object and exact measured dimension;
- estimated real-world height/value or defensible range;
- estimation basis and confidence (`high`, `medium`, or `low`);
- anchor span in untouched-source pixels;
- whether the anchor and character are on the same depth lane, with the floor/perspective cue used to decide;
- a second independent anchor when the first dimension, depth, or visibility is ambiguous;
- canonical character height, raw character-to-anchor ratio, perspective adjustment, and provisional head-to-foot pixels.

Use a range or second anchor instead of false precision. For example, a sofa may have a seat around human knee height while its back may approach one meter; the contract must identify which visible span is being measured. Reject an anchor whose base/contact point, dimension, or depth lane cannot be located reliably.

Write one explicit scale sentence into every character-in-scene prompt. For example:

```text
Scene-scale contract: the visible sofa-back span is estimated as 1.00 m and lies at approximately the same floor depth as Zack. Zack's canonical height is 1.70 m, so his shoe-to-head span should read at about 1.70 times that sofa-back span before the recorded perspective adjustment; target crop-space height 642 px with shoes at (x,y).
```

The numeric sentence guides image generation but is not final authority. The frozen crop-space box, foot/contact landmarks, and post-generation pixel QA remain mandatory.

## Convert height into projected scene pixels

Record these fields in every placement contract and AVG-layer handoff:

- canonical height in centimeters;
- source profile path and whether the value is explicit or inferred;
- floor-depth lane or standing contact point;
- projected head-to-foot height in source pixels;
- scene type, same-depth physical anchor, exact measured dimension, real-world estimate/range, basis, confidence, source-pixel span, optional secondary anchor, depth cue, ratio sentence, and perspective construction used to justify the scale.

At the same floor depth, preserve real-height ratios:

```text
target_projected_height_px = reference_projected_height_px * target_height_cm / reference_height_cm
```

When actors stand at different depths, apply the scene's actual floor perspective before the real-height ratio. Derive depth from foot positions, vanishing geometry, and existing floor/furniture scale. A rear actor may appear smaller only when the recorded foot position proves that the actor is farther away. "Observer," "secondary character," or "right-rear" is not permission to shrink a person arbitrarily.

When perspective cannot be established reliably, place compared standing actors on the same or nearly the same depth lane and preserve their centimeter ratio. Existing U1 art and furniture validate overall camera scale, but never override canonical relative heights.

Prefer a readable middle-ground placement with visible room context. Do not move actors close to the virtual camera merely to make faces larger. Reject staging that makes a normal standing person dominate the room, conflicts with door/sofa/counter scale, or makes a taller character visibly shorter at the same depth.

## Solve scale as a scene-and-camera problem

Never carry a fixed head-to-foot pixel height from one scene into another. Canonical centimeters constrain the relative body sizes; they do not directly determine screen pixels. Projected scale is the combined result of the source camera, the chosen floor contact, floor depth, vanishing geometry, local furniture/architecture scale, body orientation, and any high-angle foreshortening.

Use this two-stage construction:

1. **Provisional semantic scale construction before generation.** Choose the intended foot point on the untouched source, classify the location, complete the physical-anchor contract above, and derive a provisional envelope from the measured anchor span, canonical-height ratio, and local perspective. Use at least one depth cue such as floor seams, rug edges, wall/floor intersections, repeated tiles, or another vanishing line. A single global pixels-per-centimeter constant is invalid.
2. **Realized master lock after generation.** Once the initial scene-context plate has a visually plausible person scale, measure that plate rather than re-estimating the green-screen sprite. Record each person's visible head/top point, both foot/contact points, outer body envelope, body-axis direction, and group spacing in crop coordinates. The accepted master becomes the authoritative projected-scale and placement reference for extraction and compositing; canonical heights remain the authority for relative height consistency.

Freeze the crop-relative box before green generation. Record the source crop origin/size and the master canvas size, then map every master landmark separately:

```text
crop_x = master_x * crop_width  / master_width
crop_y = master_y * crop_height / master_height
```

This mapping is valid only when the master contains the complete source crop with the same aspect ratio and no padding, cropping, or reframing. Confirm the actor's underfoot/support contact and two nearby non-collinear source anchors against the untouched crop. A master with locally redrawn floor or support geometry is not a coordinate master, even if its canvas ratio matches.

The mapped crop-space actor box—not the center, padding, or apparent size of the later green canvas—determines the packaged `visible-height`, foot/contact anchor, and translation. If the extracted keyed pose cannot match the frozen box, contacts, and body axis with one uniform transform, reject that keyed pose rather than guessing another scale.

The generated master never authorizes its redrawn environment pixels. Its actor geometry may be used only when the foot/contact point maps unambiguously back to the untouched source. If the master changes the floor, support object, doorway, or local perspective enough that this mapping is ambiguous, reject it as a scale master even when the people look attractive.

For a high-angle or oblique scene, do not treat body height as a purely vertical screen segment. Preserve the master's projected body axis, head displacement from the feet, and foreshortened silhouette. A conventional upright character-card sprite pasted vertically into a steep overhead view is a perspective failure even when its numeric head-to-foot height seems reasonable.

For panoramas or non-`2560x1600` sources, resolve horizontal and vertical runtime mapping separately. Do not multiply character height by a width ratio unless the runtime actually applies uniform scaling on both axes; panning, cropping, or horizontal-only mapping does not justify a vertical scale change.

Write both the provisional and realized values to `placement.md`:

- foot point and floor-depth lane;
- scene type, scale anchor object, exact measured dimension, real-world estimate/range, basis, confidence, source-pixel span, secondary anchor when needed, character-to-anchor ratio sentence, and depth cue(s);
- provisional head-to-foot estimate;
- accepted scene-master path;
- master actor envelope, head point, foot/contact points, and body-axis vector;
- realized head-to-foot envelope used by packaging;
- same-depth relative-height calculation for every nearby actor;
- any runtime source-to-render mapping applied independently on X and Y.

After packaging, overlay the extracted actor on the accepted scene master using the recorded crop coordinates. The delivered layer must match the master foot/contact point within `3 px`, its head-to-foot envelope within `3%`, and its body-axis direction and group spacing closely enough that a 50%-opacity difference preview does not show a second displaced figure. A mismatch is a deterministic alignment failure; do not accept it because Alpha containment or TalkPanel QA passed.

## Scale QA

After packaging, measure every actor's Alpha head-to-foot height in the full-scene preview. Recompute the expected ratio for actors on comparable depth lanes and require the result to match the placement contract within normal edge/hat tolerance. A hat may extend the visual envelope but does not change the recorded body-height authority; record both body estimate and outer Alpha envelope when headwear is substantial.

Also re-measure the declared physical anchor in the untouched source and compare the delivered character-to-anchor pixel ratio with the recorded ratio after perspective adjustment. A visually plausible person still fails scale QA when the declared one-meter object and 1.70-meter person read at an incompatible same-depth ratio.

Correct scale only with uniform resize plus translation. Never stretch X/Y independently. If the accepted pose cannot fit the UI-safe composition at its correct height, change the floor position or composition and reconfirm it; do not solve the conflict by making the actor implausibly small.

Scale QA is independent from extraction, Alpha containment, and UI-safe checks. A layer can pass every technical pixel check and still fail delivery because its scene-relative size, depth, foreshortening, or body axis does not match the accepted master and source geometry.
