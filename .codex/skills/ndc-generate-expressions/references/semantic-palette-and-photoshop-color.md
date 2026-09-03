# Semantic palette cards and Photoshop color correction

## Core rule

The image-generation model is never a color-correction tool. Do not ask Image 2 or another generative model to restore hue, saturation, luminance, material colors, or tonal balance. Generation may produce the raw artistic candidate; all later color correction is deterministic or Photoshop-based.

Whole-subject histogram matching is diagnostic only. It cannot formally correct a set because expression performance, newly completed shoulders, and visible material-area ratios change the aggregate distribution. A dark jacket occupying more pixels must not be interpreted as a globally darker face.

## Approved semantic palette package

Before new expression generation, create reviewed semantic masks on the immutable approved portrait for every visible stable material:

- skin;
- hair and facial hair when materially distinct;
- jacket or primary outer garment;
- shirt/collar;
- tie, scarf, or other major accent;
- protected pale/white design;
- protected spot-black/ink linework;
- any character-specific material whose hue must remain stable.

Run `scripts/build_semantic_palette_card.py` after the masks are reviewed. For each material it records separate `shadow`, `midtone`, and `highlight` swatches using per-region L* terciles and robust median sRGB/CIELAB D65 values. Preserve:

- palette JSON and PNG card;
- approved portrait path and SHA-256;
- region-mask paths and SHA-256 values;
- sample counts and tone splits;
- working color space and ICC handling.

The palette card is the correction authority. A global whole-character average is not.

## Candidate comparison

Create equivalent semantic masks for the raw candidate. Compare each material and tone band against the palette card. Diagnose separately:

- tone error: shadow, midtone, or highlight L* drift;
- chroma error: saturation too weak/strong within a material;
- hue/cast error: a*/b* direction differs;
- material-boundary error: skin, hair, jacket, shirt, or accent pixels are mixed by an incorrect mask;
- rendering error: structure or lighting differs so much that color correction would repaint the image.

Use numeric Lab differences as screening and same-display side-by-side review as the final decision. Do not invent one universal Delta-E threshold before the approved role baseline is measured. Derive acceptable ranges from the approved portrait and, when available, multiple approved same-character expressions. Spot black, neutral white, and linework remain protected even when a numeric fit would move them.

## Photoshop routes

Preferred route when automation passes a one-file dry run:

`PHOTOSHOP_UXP_SEMANTIC_MASKED`

- use a standalone `.psjs` UXP script or a narrowly scoped action;
- create non-destructive adjustment layers grouped and masked by semantic material;
- use Curves/Levels for tone bands and Color Balance, Hue/Saturation, or Selective Color only inside the relevant mask;
- keep the raw candidate as a locked layer;
- save a layered PSD, exported PNG, adjustment recipe, before/after palette report, and hashes;
- never use a global Match Color result as automatic approval.

Fallback when Photoshop automation is unavailable, unstable, or cannot reproduce the dry run:

`PHOTOSHOP_MANUAL_SEMANTIC_MASKED`

- Codex provides the palette card, region masks, sampled values, and per-material correction sheet;
- the user performs the adjustments manually in Photoshop;
- Codex resumes only after receiving the exported PNG and, when available, PSD/recipe evidence;
- do not substitute a generative recolor.

Photoshop adjustment layers are required because they preserve the original pixels and make each correction inspectable. Flatten only a copied export; retain the layered working file under the work-process directory.

## Pass conditions

Formal color `PASS` requires:

- method is `PHOTOSHOP_UXP_SEMANTIC_MASKED`, `PHOTOSHOP_MANUAL_SEMANTIC_MASKED`, or `NO_CORRECTION_REQUIRED_SEMANTIC_PASS`;
- `generative_color_correction=false`;
- semantic palette anchor and every required region mask exist and match their hashes;
- before/after values are recorded per material and tone band;
- skin, hair, costume materials, protected whites, and spot black pass separately;
- Alpha and exterior edge pixels are unchanged unless a separately approved edge task exists;
- the expression and rendering structure remain unchanged;
- Codex visually reviews the corrected image against the approved portrait, palette card, and complete same-character set;
- any human Photoshop handoff is explicitly marked incomplete until the adjusted file returns.

If correction would require repainting form, changing lighting direction, or moving material boundaries, return to expression generation. Photoshop color work cannot repair a structurally wrong candidate.

