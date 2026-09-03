# Prompt modules

## Reference roles

State each role explicitly:

- scene: camera, geometry, local light, contact surfaces, and style;
- character card: identity, body type, costume, palette, and fixed accessories;
- Codex-reviewed exact-pose proxy: preliminary position, scale, pose landmarks, contacts, and action envelope only;
- depth map: continuous depth and occlusion only;
- Codex-reviewed exact-pose whitebox: primary structural authority for final pose, scale, generation position, body volume, contacts, prop envelope, and actor/scene overlap;
- action reference: secondary pose nuance only; it may not override the reviewed whitebox.

## Before-state generation

Require the narrative action, character identity, complete outer rectangle, safe margins, and correct support contacts. Identify the reviewed whitebox and pose ID explicitly. Require the same joint arrangement and occupied volume; scale and placement remain locked by code. Do not ask the model to redraw the entire scene merely to place an actor.

## Three-reference local-scene generation

Run `prepare-local-generation-handoff` first and attach references in this exact order:

- Image 1: local crop containing the approved whitebox;
- Image 2: untouched full scene;
- Image 3: approved character card.

Use this prompt skeleton and replace every bracketed field from the directing and placement contracts:

```text
Base the result on Image 1. Replace only the reviewed whitebox with [CHARACTER] from Image 3. The character is [EXACT STORY PERFORMANCE], with [FACIAL EXPRESSION], [GAZE], [LEFT-HAND MOTIVATION], [RIGHT-HAND MOTIVATION], and weight supported by [NAMED SUPPORT]. Preserve the approved whitebox pose, occupied volume, support contacts, depth, and local position.

Image 1 is a deterministic crop from Image 2. Keep all scene pixels, camera geometry, furniture topology, perspective, and local object relationships unchanged. Use Image 2 only to match full-scene lighting, palette, and color grade. Add only the light and contact response necessary for the character.

Use Image 3 only for identity, face, body type, costume, fixed accessories, palette, brushwork, and line language. Do not invent material, costume, texture, or accessory detail. Nearby object height is only a sanity check against absurd character scale; the approved whitebox is the scale authority. Remove the whitebox/mannequin in the result.

Preserve the approved NDC character and scene style authorities exactly. Control only texture coherence and spatial detail density. Keep the character's large hair, face, costume, and shadow masses readable; retain the card's native line and brush language; place folds and texture only where pose, support, overlap, material, and local lighting require them. Match the scene depth by avoiding foreground-strength micro-detail on a distant actor. Do not invent repeated marks, random speckle, fragmented strokes, decorative micro-wrinkles, new seams, extra accessories, uniformly sharpened edges, or unsupported material texture. Keep all scene texture outside the minimum interaction component unchanged.

Style: highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour::1.5, exaggerated drastic line weight variation, distinct heavy layered ink contours for each garment layer, bolder heavier internal ink lines, flat graphic monolithic hair mass, zero internal texture or detail in hair, single solid block of black or color for hair, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean features, extreme high contrast chiaroscuro lighting, heavy use of solid black shadows (spot blacks), intense deep shadow areas, minimal specular highlights, matte surfaces, film noir aesthetic, American 1928s era context, straight perspective.
```

The `[EXACT STORY PERFORMANCE]` field must come from the approved performance contract, including silent-frame verb, beat energy, ongoing occupation, performance family, social territory, and ten-second hold. Do not replace it with a generic pose adjective. For still/low-energy beats, explicitly prohibit wide stance, open-hand reaching, braced combat posture, and camera-facing presentation unless the beat authorizes them.

Reject an output before extraction if the face/identity, costume structure, ink language, joint logic, support, gaze, hand motivation, or occupied volume differs materially. A prompt result is not approved merely because it resembles the general style.

<!-- NDC_TEXTURE_COHERENCE_MODULE:BEGIN -->
Also reject it when either `STYLE_LOCK_GATE` or `TEXTURE_COHERENCE_GATE` is not `PASS`. Do not use `simplify the art style`, global smoothing, global denoising, sharpening, texture overlays, or AI upscaling as a repair. A local texture defect returns to the frozen three-reference handoff with only that failure delta changed. Whole-character detail inflation restarts from the approved whitebox crop, untouched scene, and approved card; it never chains from the failed contextual result.
<!-- NDC_TEXTURE_COHERENCE_MODULE:END -->

## After-state patch

```text
Use the accepted before state as the only master. Modify only [allowed region] to show [new action]. Keep [anchor list], [frozen regions], canvas, scale, lower body, support contacts, prop anchors, and shadow unchanged. Return a patch on the exact master canvas; do not recrop or rescale.
```

Place the patch seam under natural structure such as collar, lapel, sleeve cuff, hairline, prop, or occlusion. Do not request a new full body when only the head or arm changes.

## Shadow candidate

Ask the model only to analyze or propose light direction and silhouette. The final prompt must include the approved foot contacts, receiving plane, direction, length, hardness, and whether the actor is actually inside the strong light. Final mask geometry is deterministic or manually approved.

## Scene protection

Prompts must say that the original scene is reference-only and cannot become delivery pixels. Preserve camera, architecture, furniture, and lighting outside the authorized interaction region. Enforce zero outside changes with code, not wording alone.

The generated local scene is also reference-only. Only the approved extracted character or minimum interaction component may enter delivery. Fixed structural furniture such as chairs, beds, desks, rails, and cabinets must never be bundled into a scalable actor component. If a loose object must be moved before an actor uses the furniture, extract only the old-location repair patch and the relocated-object patch; keep the furniture at source scale and coordinates. Reapply exact occluder pixels from the untouched full scene, including openings between rails, chair backs, bed frames, leaves, or other perforated shapes.

## Fixed-canvas model handoff

When the image generator cannot output the source aspect ratio directly, never let it silently squeeze a 16:10 scene into 3:2.

1. Deterministically resize the 16:10 source to 1536×960 and place it between 32px calibration bars on a 1536×1024 canvas.
2. Tell the model to preserve both bars and every content edge.
3. Reject the output if either bar is lost, the content is cropped, or support furniture changes topology.
4. Crop exactly `y=32..992` and resize back to the original 2560×1600 only for an auxiliary reference or candidate patch.
5. Never treat the resampled generated scene as final scene pixels. Composite only an approved interaction component back onto the untouched original-resolution source.

Depth and whitebox maps from a generative model remain auxiliary even when the bars pass. Their geometry may be simplified; the locked placement contract and original scene retain authority.
