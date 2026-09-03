# Portrait comparison and character-card style fallback

## Purpose

Image 2 may preserve a broadly similar person while replacing person-specific facial geometry, or it may preserve identity while drifting away from the approved portrait's illustration language. Neither result is eligible for expression delivery. This reference adds a fail-closed comparison before color calibration and a narrow retry route for style-only failures.

## Required E5 comparison

Compare these three files side by side at matched display scale before any candidate can leave the artistic review stage:

1. The user-approved original portrait: identity and original portrait-style authority.
2. The source-locked calm RGBA derived from that portrait without generative repair: continuity control.
3. The raw native expression candidate: review target.

Record all three absolute paths, their SHA-256 values, reviewer=`Codex`, `whole_images_checked=true`, and both decisions below.

### Identity decision

Set `identity_vs_portrait=PASS` only when the candidate remains demonstrably the same person: head silhouette, forehead/hairline, brow spacing, eyes, nose bridge and tip, mouth baseline, cheek/jaw contour, ears when visible, age, costume, and fixed asymmetries must agree outside the requested expression and recorded small performance deltas. Category resemblance is insufficient.

The original portrait is also the sole viewpoint authority. The candidate must preserve its view family, viewing side, facial foreshortening, camera height, and projection. A front-view character-card panel cannot authorize rotating a three-quarter portrait to front. Character-card fallback contributes only the frozen text-only art-style paragraph; it never replaces portrait composition or viewpoint.

Set `identity_vs_portrait=FAIL` for a different person even if age, hairstyle, clothing, or profession still look plausible. Stop before background removal and regenerate directly from the approved portrait; never repair a failed person by color correction, profile normalization, or a second expression as reference.

### Style decision

Set `style_vs_portrait=PASS` only when the candidate matches the approved portrait's line hierarchy, grouped hair mass, hard facial planes, value compression, palette family, surface/brush texture, native detail density, and lighting language. This whole-image comparison is supplemented by the mandatory 100%/200% invariant-detail and lighting-topology review. A candidate that is recognizably the same person but reads as another illustration treatment, is materially softer in stable regions, or invents a new highlight/occlusion pattern is `FAIL`.

For a direct-mode style-only failure, keep the failure evidence and enter `CARD_STYLE_TEXT_ANCHOR`. It is unavailable when identity also failed; fix identity first.

## `CARD_STYLE_TEXT_ANCHOR` mode

This mode preserves the immutable approved portrait as the sole visual generation reference and as identity, style, and viewpoint authority. It appends a frozen text-only art-style anchor extracted from the approved general-style character-card prompt. It does not add the character-card image as a composition/viewpoint replacement, and it does not reuse any previous expression candidate.

1. Export the exact art-style paragraph from `ndc-generate-characters/references/prompt-library.md` using `scripts/export_character_card_style_anchor.py`.
2. Save the exported text and SHA-256 beside the attempt record.
3. Regenerate from the same approved portrait with the same expression signals. Append the exported paragraph verbatim; never append character-card layout, 16:9, three-view, full-body, hands, shoes, or detail-grid instructions.
4. Repeat the full three-up comparison. The fallback passes only when both identity and style pass against the original approved portrait.

The fallback consumes the next normal artistic attempt; it does not add attempts beyond the existing A1/A2/A3 budget.

## Current feedback evidence

- Seamus: the reviewed generated candidates did not establish the same person as the approved original portrait. Treat this as an identity-comparison failure, not as a palette or geometry issue.
- Harrison: the reviewed generated candidate had a material illustration-style difference against the approved original portrait. Treat this as a style-comparison failure; if identity remains readable, use `CARD_STYLE_TEXT_ANCHOR` on the permitted retry.

These named findings identify the current affected candidates. The gates above apply to every future expression candidate.
