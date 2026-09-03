# Photoshop extraction, assembly, and QA

## Preserve recoverability

- Work in an actual layered PSD.
- Keep the original scene as the bottom layer and never paint on it.
- Keep one hidden unmodified registered actor layer before matte cleanup.
- Perform edge cleanup on a visible duplicate.
- Put contact/cast shadows on separate layers.
- Use deterministic layer names containing order, actor, stage, and registration state.

## Extract one actor at a time

1. Normalize the contextual candidate to the documented calibration canvas.
2. Run Photoshop Select Subject as the first selection only.
3. Convert the selection into transparency or a layer mask.
4. Inspect the complete actor at 100% and critical edges at 200%.
5. Save the raw transparent cutout before cleanup.

Do not include generated architecture, furniture, plants, rails, or floor pixels in an actor layer.

## Distinguish two edge failures

Color fringe:

- a thin white/gray/green rim around an otherwise correct silhouette;
- `Remove White Matte`, color decontamination, or a conservative 1–2 px Defringe may help;
- always preserve a hidden pre-cleanup layer.

Selection error:

- background foliage, railing, wall, or a hole is incorrectly included/excluded;
- Defringe cannot fix it;
- repair the layer mask manually with a hard or controlled brush/path.

NDC hair is a graphic mass rather than photoreal strands. When dark hair overlaps dark foliage, prioritize the approved card silhouette and clean intentional contour; do not preserve leaf fragments as “hair detail.”

## Register to the whitebox

Use one uniform scale plus translation per actor after extraction:

- full-body: register named feet/support center, then compare head box;
- half-body foreground: register head box, frame edge, and approved off-frame bottom;
- prop-bearing actor: verify the prop stays inside the approved action envelope;
- never use a fixed percentage for the whole cast;
- never use non-uniform scaling, warping, liquify, or limb repositioning to rescue a failed generation.

If pose or head ratio cannot fit the whitebox with one uniform transform, reject the generation and return to its frozen local handoff.

## Shadows

- Add subtle contact shadows only for visible support contacts.
- A foreground half-body actor whose feet are off-frame does not receive a fabricated floor-contact shadow.
- Keep shadows independent from actor pixels and below their owner.
- Match direction, softness, value, and receiving plane to the original scene.

## Scene occlusion

Reapply exact original-source occluder pixels where a character belongs behind a rail, plant, counter, doorway, or other foreground structure. Preserve holes and gaps. Do not use regenerated scene pixels as occluders.

## Final review

Whole image at 100%:

- left/right cast cluster reads clearly;
- silent-frame statement is understandable;
- negative space and selected UI side remain usable;
- depth and head-size relationships are credible;
- every gaze has the intended target;
- no accidental lineup, limb contact, or handoff pose;
- light and color grade belong to the fixed scene.

Local tiles at 200%:

- identity-critical face and hair;
- glasses and small accessories;
- hands and owned props;
- feet/support and contact shadow;
- transparent edge, matte holes, foliage/rail contamination;
- line weight, black masses, material texture, and sharpening consistency.

Final delivery is a layered PSD and flattened PNG on the untouched source canvas. Keep process artifacts and logs beside the working scene; do not copy to Unity without explicit authorization.

