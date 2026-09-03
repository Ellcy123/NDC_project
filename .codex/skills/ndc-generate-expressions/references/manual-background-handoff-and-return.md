# Manual background handoff and user-returned Alpha gate

## Scope

This workflow deliberately separates artistic expression production from background processing. Codex completes and reviews the expression artwork, hands off native images as a non-final package, and stops. The user manually removes the backgrounds by editing those exact PNG files in place. Once the user confirms completion, Codex reviews the edited Alpha and continues to delivery-profile composition only when every file passes. No second return folder or duplicate image set is created.

Codex must not remove backgrounds, create or paint masks, remove white fringe, run `remove_expression_background.py`, use another extraction script, control Photoshop for this stage, or invoke an Image model for Alpha work.

## `PRE_ALPHA_HANDOFF`

Create the handoff only after every requested state passes artistic review. Place it under:

```text
D:\Codex\NDC\工作过程文件\角色表情\Unit<n>\<character>\手工去底交接_非最终_<date>
```

The handoff contains:

- one unchanged native image per expression, including calm;
- a manifest recording expression ID, source path, handoff path, SHA-256, dimensions, mode, and artistic status;
- a short user-facing instruction file;
- the package markers `handoff_status=PRE_ALPHA_HANDOFF`, `final_delivery=false`, and `background_processing_status=PENDING_USER_MANUAL_PROCESSING`.

Do not resize, crop, sharpen, mask, recolor, or convert the artistic images for this handoff. Exact binary copies are preferred. The folder is a working handoff and must not be placed in `最终交付`. The user edits each handoff PNG directly in this directory; preserve its filename and canvas, and do not edit the manifest.

## In-place manual processing requirements

Ask the user to overwrite each handoff PNG in place with its RGBA manual-background version, preserving the native canvas dimensions, filename, and the subject's identity, expression, costume, lighting, color, texture, and opaque internal pixels. Edge RGB may differ only where manual decontamination is needed for partially transparent boundary pixels. The user then tells Codex to resume; this user confirmation satisfies `user_returned=true` even though no file was physically copied back.

Map each in-place edited file to its pre-edit handoff-manifest row and record:

- pre-edit handoff path and SHA-256 from the unchanged manifest;
- current edited RGBA path and SHA-256;
- `handoff_edit_mode=IN_PLACE_OVERWRITE`;
- unchanged canvas dimensions;
- `processor_authority=USER_MANUAL_BACKGROUND_PROCESSING`;
- `codex_background_removal_used=false`.

Missing, ambiguous, renamed, resized, cropped, or artistically changed in-place edits are `USER_ALPHA_RETURN_INVALID` and cannot enter profile composition.

## `ALPHA_EDGE_GATE`

Run `prepare_alpha_edge_review.py` only to create evidence. It may not modify the user-edited in-place file.

Inspect the returned RGBA at whole-image scale, native 100%, and nearest 200% on:

- white;
- 50% gray;
- dark gray;
- black;
- exact `#00FF2B`.

`PASS` requires no halo, matte contamination, remote island, hole, erosion, jagged contour, missing protected light design, or clipped hair, shoulder, costume, or accessory. It also requires identical artistic content to the accepted pre-Alpha handoff source.

If any check fails, return `USER_ALPHA_REWORK_REQUIRED`, preserve the user-edited file as a candidate, and stop. Codex does not repair it. When all files pass, freeze one user-edited native RGBA file and SHA-256 per expression for both delivery profiles.
