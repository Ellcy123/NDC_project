# Delivery profiles

## Shared-foreground rule

After `ALPHA_EDGE_GATE=PASS`, freeze one native RGBA foreground per expression. Both delivery profiles must reference that exact path and SHA-256. Profile-specific generation, masking, recoloring, or artistic repair is forbidden.

Profile normalization permits exactly one uniform LANCZOS scale with `0 < scale <= 1`, translation, and background composition. No upscaling, repeated resizing, sharpening, stretching, rotation, subject-pixel clipping, or generation is allowed.

## Transparent

- canvas: `1164x916`;
- mode: RGBA PNG;
- background: Alpha 0;
- subject: naturally reaches bottom edge;
- exception: `1152x900` only for an explicit Unit1 legacy match;
- guide: `assets/profile-guides/透明版表情辅助线-示意.png`.

Inspect the final transparent profile again on light and dark backgrounds. Profile composition may expose an edge issue even when native RGBA previously passed.

## Greenscreen

- canvas: `1536x1024`;
- mode: RGB PNG;
- background: exact `#00FF2B`;
- all corners exact `#00FF2B`;
- at least `99.8%` of screened background exact green, with tolerance limited to the anti-aliased subject fringe;
- subject: naturally reaches bottom edge;
- guide: `assets/profile-guides/绿幕版表情辅助线-示意.png`.

The green version is flattened from the same RGBA foreground after placement. It is never generated on green and never used as the source for the transparent version.

## Calm anchors and set stability

Create one calm transform per `character + profile` from the approved portrait's edge-passing RGBA. Reuse that exact scale and offsets for every expression in the corresponding profile set. Same-profile role-specific anchors outrank cross-character averages.

Run `audit_cross_profile_source_consistency.py` for every expression. Different profile canvases and transforms are expected; different native foreground hashes are `FAIL`.
