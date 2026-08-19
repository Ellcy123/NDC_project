---
name: ndc-scene-cleanplate
description: "Analyze and edit NDC scene-background images into reusable clean plates by preserving architecture and necessary environmental objects while removing evidence, clue-bearing contents, excess decorative clutter, and later-placement props. Always split each source into three overlapping full-height vertical crops, reconstruct all three crops as complete images while removing detected content, then align and merge them into the final clean plate. Use when the user asks to 删除场景多余物品、清理证据、保留灯或电话等环境物、制作干净底图/clean plate, or prepare an NDC background for later evidence placement."
---

# NDC Scene Cleanplate

Turn an approved NDC scene image into a reusable clean background. Classify objects by gameplay role rather than by whether they are physically a “prop”: a lamp or telephone normally stays; a letter, photograph, signed book, readable poster, clue, or staged loose object normally goes.

Read [classification and edit contract](references/classification-and-edit-contract.md) before analyzing or editing an image.

## Establish the source contract

1. Inspect the original image at sufficient size. Use `view_image` for a local image that has not already been seen.
2. Read the current scene requirement when the user supplies a scene ID, document, or path. Treat it as the authority for location identity and necessary environmental storytelling.
3. Preserve the original file. Write every result as a separate versioned clean-plate file.
4. If no scene requirement is available, use the conservative default: keep plausible fixed and functional environment objects; remove only clearly clue-like, readable, staged, or loose content.

## Build a cleanup contract

Before editing, report four short lists:

- `KEEP_STRUCTURE`: architecture, built-ins, fixed services, large furniture, and spatial boundaries.
- `KEEP_ENVIRONMENT`: non-evidence objects required for function, era, composition, or scene identity.
- `REMOVE_CONTENT`: evidence, readable material, clue-bearing contents, later-placement props, and unnecessary loose decoration.
- `REVIEW`: objects whose gameplay role cannot be resolved from the image and scene requirement.

Lock the following separately: camera and crop, geometry and object placement, illumination and cast shadows, color grade, rendering style and brushwork, texture and wear, resolution and aspect ratio.

Before creating reconstruction crops, mark a bounding box for every `REMOVE_CONTENT` item. Move vertical cut lines when necessary so each detected object plus at least 48 pixels of reconstruction context lies completely inside one crop. Never split one removable object between neighboring crops.

Do not interpret `REMOVE_CONTENT` as permission to empty the scene. Keep lamps, telephones, radiators, curtains, sinks, stoves, tables, chairs, beds, and similar environmental infrastructure unless the user or source explicitly removes them.

## Handle containers and narrative environment

- Preserve a drawer, cabinet, box, envelope rack, shelf, or coat when it belongs to the environment; remove only its clue-bearing contents.
- Keep a container's open or closed state when that state communicates the room's ordinary condition. Change the state only when the user asks.
- Preserve scene-defining ordinary objects even when movable. For a two-day-old move, keep a restrained set of moving boxes but remove the evidence booklet, letter, photograph, or marked item inside them.
- Preserve infrastructure interactions such as a wall telephone. Being usable in gameplay does not by itself make an object evidence.
- Remove readable text, signatures, logos, portraits, posters, loose documents, labeled evidence, and conspicuously staged objects unless the source marks them as necessary environmental storytelling.

## Use the three-crop full reconstruction workflow

Treat the left, middle, and right full-height crops as three complete reconstruction units. Reconstruct every crop as a whole image; do not isolate or repaint individual objects with local masks.

1. Use the `imagegen` skill and image-editing tool for raster reconstruction. Use deterministic code only for splitting, exact crop resizing, overlap alignment, merging, and verification.
2. Read the source dimensions and record the exact pixel size and aspect ratio. Do not generate a low-resolution whole image and enlarge it for delivery.
3. Always split every source image into exactly three overlapping full-height vertical reconstruction crops (`3×1`), regardless of its dimensions or which dimensions exceed the model's useful generation size:
   - create left, middle, and right full-height reference crops;
   - do not use `1×3`, `3×2`, or an unsplit local crop;
   - keep overlap between neighboring crops;
   - move vertical cut lines when necessary so every removal plus at least 48 pixels of reconstruction context remains entirely inside one crop.
4. Analyze all three crops and detect the objects classified as `REMOVE_CONTENT` in each one.
5. Submit all three crops for full-crop reconstruction, including crops that contain no removable objects. Treat each crop as one coherent image-editing task.
6. For each crop, list the detected removals by crop-relative location, appearance, and neighboring landmark. Instruct the editor to remove them during the complete crop reconstruction.
7. Reconstruct the complete crop. Do not use object-level masks, polygons, local inpainting, isolated object patches, or source-pixel compositing.
8. Preserve the crop's composition, proportions, architecture, furniture, object placement, illumination, color relationships, rendering style, and period identity. Keep every unspecified element unchanged.
9. Accept small model output-size drift only in the reconstructed crop. Resize each reconstruction deterministically to its exact original crop dimensions.
10. Align the three reconstructed crops through their overlap regions, choose structurally consistent seam paths, and merge them into one full-resolution image. Do not merge across duplicated or mismatched structures.
11. Forbid new objects, furniture removal, rearrangement, relighting, reframing, text generation, sharpening, recoloring, or unrelated cleanup. Preserve natural highlight falloff, scratches, dust, edge wear, and material response.

Use `tile_cleanplate.py split` to prepare the three overlapping reconstruction crops and manifest. After all three complete crop reconstructions pass individual inspection, merge them with `tile_cleanplate.py merge --full-reconstruction`, which applies whole-crop overlap fitting and selects a non-blended seam through each overlap; never fall back to the local-region merge mode for this workflow.

Typical three-crop workflow:

```text
python scripts/tile_cleanplate.py split source.png --out-dir work --cols 3 --rows 1 --overlap 160
# Reconstruct work/left, work/middle, and work/right as three complete images.
python scripts/tile_cleanplate.py merge work/manifest.json --tiles-dir reconstructed --output cleanplate.png --full-reconstruction
# Resize each result to its exact manifest dimensions, inspect it, then fit color and select seams in the overlaps.
```

Use this prompt structure for each of the three complete crop reconstructions:

```text
Preserve the current composition, proportions, and art style. Reconstruct this entire full-height vertical reference crop as one coherent image.
Remove the following detected REMOVE_CONTENT objects during the complete reconstruction: <positioned REMOVE_CONTENT list>.
Do not repaint individual objects, use local masks, or perform isolated patch edits.
Preserve exactly: <important KEEP_STRUCTURE and KEEP_ENVIRONMENT list>.
Keep every unspecified element unchanged, including camera, crop, perspective, architecture, furniture placement, object scale, illumination direction and intensity, cast shadows, reflections, color relationships, palette, linework, brush texture, stylization, resolution, and aspect ratio.
Do not add, replace, rearrange, relight, sharpen, recolor, or restyle unrelated content. No people and no new readable text.
```

## Verify the result

Compare the source and result side by side. Reject or repair the edit when any of these occurs:

- a retained environmental object disappears or changes position;
- the room becomes implausibly empty or loses its scene identity;
- a clue, readable artifact, or later-placement prop remains;
- lighting, desk highlights, shadows, reflections, or window illumination change;
- color, line weight, painterly texture, period detail, camera, crop, or architecture drifts;
- removed regions become smeared, repeated, overly smooth, or introduce new objects.
- a removable object crosses a crop boundary or reappears in an overlap;
- an overlap merge introduces a horizontal or vertical band, line, softness change, color block, texture jump, double feature, duplicated structure, or lighting discontinuity;
- the three reconstructed crops disagree on architecture, furniture geometry, perspective, scale, shadows, or style;
- the reported pixel dimensions match only because a low-resolution whole-image result was upscaled.

Require the reconstruction report to include source dimensions, the exact bounds and output dimensions of all three crops, overlap widths, merge paths, and the final dimensions. Verify that each crop and the merged image preserve the intended composition, structure, furniture, lighting, and art style. Pixel-only checks are insufficient; perform visual inspection at every horizontal and vertical transition.

If one reconstructed crop contains a defect, discard that complete crop reconstruction and regenerate the whole crop with a shorter, stricter contract. If the merged image has a seam or structural mismatch, do not patch the seam locally; return to the affected complete crops, regenerate them, and merge again. Never stack repairs on a drifted reconstruction.

## Deliver

Return the clean-plate image and the final `KEEP_ENVIRONMENT` / `REMOVE_CONTENT` lists. State any unresolved ambiguous object. Do not add evidence, clickable props, borders, masks, labels, or overlays unless the user separately asks for them.
