# Prompt modules

For new layered production, apply [layered-character-batches.md](layered-character-batches.md) before the templates below: name the current batch, generate only its actors with complete separable silhouettes, preserve the registered canvas/camera, and keep foreground furniture/actors out of the complete master layers. Earlier layers are contextual references, not subjects to redraw. Do not copy facial-expression or precise-eye-gaze fields into a whitebox prompt when they cannot be assessed at that stage; retain coarse head/body direction and carry fine targets into the formal-character handoff.

## Reference roles

State each role explicitly:

- scene: camera, geometry, local light, contact surfaces, and style;
- character card: identity, body type, costume, palette, and fixed accessories;
- Codex-reviewed exact-pose proxy: preliminary position, scale, pose landmarks, contacts, and action envelope only;
- depth map: continuous depth and occlusion only;
- Codex-reviewed exact-pose whitebox: primary structural authority for final pose, scale, generation position, body volume, contacts, prop envelope, and actor/scene overlap;
- action reference: secondary pose nuance only; it may not override the reviewed whitebox.

## Before-state generation

Require the camera-visible action, character identity, complete outer rectangle, safe margins, and correct support contacts. Identify the reviewed whitebox and pose ID explicitly. Require the same joint arrangement and occupied volume; generation uses the current registered scale and placement. If a valid actor later needs only uniform scale or translation correction, use the authorized Photoshop MCP route and update registration and contacts together; do not deform it to rescue wrong anatomy or acting. Do not ask the model to redraw the entire scene merely to place an actor.

Preserve explicit user locks and literal approved prompts; any permitted correction operates within that authorization. Use the review cadence in [production-cadence.md](production-cadence.md) rather than adding checks for every prompt field or technical operation.

## Three-reference local-scene generation

Run `prepare-local-generation-handoff` first and attach references in this exact order:

- Image 1: local crop containing the approved whitebox;
- Image 2: untouched full scene;
- Image 3: approved character card.

Use this prompt skeleton with the applicable camera-visible fields from the directing and placement contracts. Omit invisible facial/eye fields and unnecessary hand tasks rather than filling every slot:

```text
Base the result on Image 1. Replace only the reviewed whitebox with [CHARACTER] from Image 3. Show [CAMERA-RELATIVE BODY AND HEAD ORIENTATION], [VISIBLE ACTION OR RESTING STATE], and [VISIBLE SUPPORT/CONTACT RELATION]. [OPTIONAL VISIBLE FACE OR HAND DETAIL]. Preserve the approved whitebox pose, occupied volume, support contacts, depth, and local position. Let non-acting limbs rest with credible weight and joint relaxation rather than assigning them extra gestures.

Image 1 is a deterministic crop from Image 2. Keep camera geometry, fixed furniture topology, perspective, and all pixels outside [MINIMUM INTERACTION REGION, IF ANY] unchanged. Within that region, show [REQUIRED SOFT-SURFACE LOAD RESPONSE, IF ANY] together with the character's contact; preserve the underlying fixed structure. Use Image 2 to match scene geometry, full-scene lighting, palette, and color grade. Add only the necessary contact and lighting response.

Use Image 3 only for identity, face, body type, costume, fixed accessories, palette, brushwork, and line language. Do not invent material, costume, texture, or accessory detail. Nearby object height is only a sanity check against absurd character scale; the approved whitebox is the scale authority. Remove the whitebox/mannequin in the result.

Preserve the approved NDC character and scene style authorities exactly. Control only texture coherence and spatial detail density. Keep the character's large hair, face, costume, and shadow masses readable; retain the card's native line and brush language; place folds and texture only where pose, support, overlap, material, and local lighting require them. Match the scene depth by avoiding foreground-strength micro-detail on a distant actor. Do not invent repeated marks, random speckle, fragmented strokes, decorative micro-wrinkles, new seams, extra accessories, uniformly sharpened edges, or unsupported material texture. Keep all scene texture outside the minimum interaction component unchanged.

Style: highly stylized graphic illustration, extremely bold heavy inked outer silhouette contour::1.5, exaggerated drastic line weight variation, distinct heavy layered ink contours for each garment layer, bolder heavier internal ink lines, flat graphic monolithic hair mass, zero internal texture or detail in hair, single solid block of black or color for hair, simplified geometric planar shape blocking, distinct hard-edge color blocks, geometric face rendering with clean features, extreme high contrast chiaroscuro lighting, heavy use of solid black shadows (spot blacks), intense deep shadow areas, minimal specular highlights, matte surfaces, film noir aesthetic, American 1928s era context, straight perspective.
```

Translate the performance contract into visible orientation, action, support, and appropriate gesture size through `ndc-visual-description`; keep story objective, subtext, performance-family labels, and ten-second-hold reasoning out of the image prompt unless they add necessary context. A quiet explanatory hand motion can be valid, and an unoccupied hand may rest. Do not make every actor clasp hands, lower their head, or hold rigid arms; likewise do not prescribe staggered feet and tilted shoulders to everyone. Check the complete cast for both story fit and naturalness before extraction or polish.

For a lying actor, describe the actual back-of-head contact, neck/shoulder rest, pillow compression or wrapping, and nearby bedding response as one visible relationship. Keep the actor's complete master separate from the soft-surface response layer during extraction. Never freeze an unloaded original pillow merely to preserve source pixels; only the authorized soft-contact region may change, and fixed bed structure remains exact. Whitebox prompts carry only the support volume and coarse pose that can be judged at that stage.

Reject an output before extraction if applicable identity, costume structure, ink language, joint logic, support, visible direction, action/rest state, or occupied volume differs materially, or if the semantically correct action is still visibly rigid. Judge only details visible in this camera and stage. A prompt result is not approved merely because it resembles the general style.

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

Prompts must distinguish the original scene's reference role during generation from its exact-pixel role in final composition: never deliver the model's redrawn full scene. Preserve camera, architecture, fixed furniture, and lighting outside the authorized interaction region. Enforce zero outside changes against the untouched original with code, not wording alone.

The generated local scene is also reference-only. Only the approved extracted character or minimum interaction component may enter delivery. Fixed structural furniture such as chair frames, bed frames, desks, rails, and cabinets must never be bundled into a scalable actor component. Pillows, cushions, and bedding are soft interaction surfaces when their load response changes; retain them as bounded separate response layers and recheck their contact whenever the actor moves or scales. If a loose object must be moved before an actor uses the furniture, extract only the old-location repair patch and the relocated-object patch; keep the fixed furniture at source scale and coordinates. Reapply exact fixed occluder pixels from the untouched full scene, including openings between rails, chair backs, bed frames, leaves, or other perforated shapes; do not restore an obsolete unloaded soft surface over its approved response layer.

## Fixed-canvas model handoff

When the image generator cannot output the source aspect ratio directly, never let it silently squeeze a 16:10 scene into 3:2.

1. Deterministically resize the 16:10 source to 1536×960 and place it between 32px calibration bars on a 1536×1024 canvas.
2. Tell the model to preserve both bars and every content edge.
3. Reject the output if either bar is lost, the content is cropped, or support furniture changes topology.
4. Crop exactly `y=32..992` and resize back to the original 2560×1600 only for an auxiliary reference or candidate patch.
5. Never treat the resampled generated scene as final scene pixels. Composite only an approved interaction component back onto the untouched original-resolution source.

Depth and whitebox maps from a generative model remain auxiliary even when the bars pass. Their geometry may be simplified; the locked placement contract and original scene retain authority.
